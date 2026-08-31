#include <filesystem>
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzPngProperty.h"
#include "wz/Properties/WzSubProperty.h"
#include "wz/Properties/WzUOLProperty.h"
#include "wz/WzDirectory.h"
#include "wz/WzEnums.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"
#include "wz/WzImageProperty.h"
#include "wz/WzObject.h"

namespace fs = std::filesystem;

static constexpr int kMaxPropertyDepth = 24;
static constexpr int kLoginBackgroundWidth = 800;
static constexpr int kLoginBackgroundHeight = 600;

static wz::WzDirectory* FindDirectory(wz::WzDirectory* root,
                                      const std::string& lower,
                                      const std::string& upper) {
    if (!root) return nullptr;
    if (auto* dir = root->GetDirectoryByName(lower)) return dir;
    return root->GetDirectoryByName(upper);
}

static wz::WzImage* FindLoginImage(wz::WzDirectory* dir) {
    if (!dir) return nullptr;
    if (auto* image = dir->GetImageByName("login.img")) return image;
    return dir->GetImageByName("Login.img");
}

static bool SetCanvasPng(wz::WzCanvasProperty* canvas, const fs::path& pngPath) {
    if (!canvas) return false;
    auto pngResult = wz::WzPngProperty::FromPngFile(
        pngPath.string(), wz::WzPngFormat::Format2);
    if (!pngResult) {
        std::cerr << "Could not encode artwork " << pngPath.string()
                  << ": " << pngResult.error().message() << "\n";
        return false;
    }
    canvas->SetPngProperty(std::move(pngResult.value()));
    return true;
}

static wz::WzImageProperty* ResolveUolProperty(wz::WzUOLProperty* uol) {
    if (!uol) return nullptr;
    auto* linked = uol->LinkValue();
    if (!linked || linked->ObjectType() != wz::WzObjectType::Property) {
        return nullptr;
    }
    return static_cast<wz::WzImageProperty*>(linked);
}

static int PatchCanvasTree(wz::WzImageProperty* property,
                           const fs::path& pngPath,
                           int depth = 0) {
    if (!property || depth > kMaxPropertyDepth) return 0;

    switch (property->PropertyType()) {
        case wz::WzPropertyType::Canvas: {
            auto* canvas = static_cast<wz::WzCanvasProperty*>(property);
            return SetCanvasPng(canvas, pngPath) ? 1 : -1;
        }
        case wz::WzPropertyType::SubProperty: {
            auto* sub = static_cast<wz::WzSubProperty*>(property);
            int patched = 0;
            for (auto* child : *sub->WzProperties()) {
                const int result = PatchCanvasTree(child, pngPath, depth + 1);
                if (result < 0) return -1;
                patched += result;
            }
            return patched;
        }
        case wz::WzPropertyType::UOL: {
            auto* target = ResolveUolProperty(
                static_cast<wz::WzUOLProperty*>(property));
            if (!target || target == property) return 0;
            return PatchCanvasTree(target, pngPath, depth + 1);
        }
        default:
            return 0;
    }
}

static void CollectCanvasByDimensions(wz::WzImageProperty* property,
                                      int width,
                                      int height,
                                      std::vector<wz::WzCanvasProperty*>& matches,
                                      int depth = 0) {
    if (!property || depth > kMaxPropertyDepth) return;

    switch (property->PropertyType()) {
        case wz::WzPropertyType::Canvas: {
            auto* canvas = static_cast<wz::WzCanvasProperty*>(property);
            auto* png = canvas->PngProperty();
            if (png && png->Width() == width && png->Height() == height) {
                matches.push_back(canvas);
            }
            return;
        }
        case wz::WzPropertyType::SubProperty: {
            auto* sub = static_cast<wz::WzSubProperty*>(property);
            for (auto* child : *sub->WzProperties()) {
                CollectCanvasByDimensions(child, width, height, matches, depth + 1);
            }
            return;
        }
        case wz::WzPropertyType::UOL: {
            auto* target = ResolveUolProperty(
                static_cast<wz::WzUOLProperty*>(property));
            if (target && target != property) {
                CollectCanvasByDimensions(target, width, height, matches, depth + 1);
            }
            return;
        }
        default:
            return;
    }
}

static void CollectPropertiesByName(wz::WzImageProperty* property,
                                    const std::string& name,
                                    std::vector<wz::WzImageProperty*>& matches,
                                    int depth = 0) {
    if (!property || depth > kMaxPropertyDepth) return;
    if (property->Name() == name) {
        matches.push_back(property);
    }

    switch (property->PropertyType()) {
        case wz::WzPropertyType::SubProperty: {
            auto* sub = static_cast<wz::WzSubProperty*>(property);
            for (auto* child : *sub->WzProperties()) {
                CollectPropertiesByName(child, name, matches, depth + 1);
            }
            return;
        }
        case wz::WzPropertyType::UOL: {
            auto* target = ResolveUolProperty(
                static_cast<wz::WzUOLProperty*>(property));
            if (target && target != property) {
                CollectPropertiesByName(target, name, matches, depth + 1);
            }
            return;
        }
        default:
            return;
    }
}

static wz::WzImageProperty* FindDirectProperty(wz::WzImage* image,
                                               const std::string& name) {
    if (!image) return nullptr;
    auto result = image->GetPropertyByName(name);
    if (result && result.value()) return result.value();
    return nullptr;
}

static wz::WzImageProperty* FindBackgroundProperty(wz::WzImage* backLogin) {
    if (!backLogin) return nullptr;

    if (auto* direct = FindDirectProperty(backLogin, "11")) {
        return direct;
    }

    auto* backGroup = FindDirectProperty(backLogin, "back");
    if (!backGroup) {
        std::cerr << "back/login.img is missing the parsed top-level `back` group.\n";
        return nullptr;
    }

    std::vector<wz::WzImageProperty*> named11;
    CollectPropertiesByName(backGroup, "11", named11);
    if (named11.size() == 1) {
        return named11.front();
    }
    if (!named11.empty()) {
        std::cerr << "Expected exactly one property named 11 under back/login.img/back, found "
                  << named11.size() << ":";
        for (auto* property : named11) {
            std::cerr << " [" << property->FullPath() << ":type="
                      << static_cast<int>(property->PropertyType()) << "]";
        }
        std::cerr << "\n";
        return nullptr;
    }

    std::vector<wz::WzCanvasProperty*> canvases;
    CollectCanvasByDimensions(backGroup,
                              kLoginBackgroundWidth,
                              kLoginBackgroundHeight,
                              canvases);
    std::cerr << "No property named 11 under back/login.img/back. 800x600 candidates:";
    for (auto* canvas : canvases) {
        std::cerr << " [" << canvas->FullPath() << "]";
    }
    std::cerr << "\n";
    return nullptr;
}

static bool HasCanvas(wz::WzImageProperty* property, int depth = 0) {
    if (!property || depth > kMaxPropertyDepth) return false;
    switch (property->PropertyType()) {
        case wz::WzPropertyType::Canvas:
            return true;
        case wz::WzPropertyType::SubProperty: {
            auto* sub = static_cast<wz::WzSubProperty*>(property);
            for (auto* child : *sub->WzProperties()) {
                if (HasCanvas(child, depth + 1)) return true;
            }
            return false;
        }
        case wz::WzPropertyType::UOL: {
            auto* target = ResolveUolProperty(
                static_cast<wz::WzUOLProperty*>(property));
            return target && target != property && HasCanvas(target, depth + 1);
        }
        default:
            return false;
    }
}

static wz::WzImage* FindRootImage(wz::WzDirectory* root,
                                  const std::string& lower,
                                  const std::string& upper) {
    if (!root) return nullptr;
    if (auto* image = root->GetImageByName(lower)) return image;
    return root->GetImageByName(upper);
}

static bool PatchRequiredPath(wz::WzImage* image,
                              const std::string& path,
                              const fs::path& pngPath) {
    if (!image || !fs::is_regular_file(pngPath)) {
        std::cerr << "Missing image or artwork for " << path << ": "
                  << pngPath.string() << "\n";
        return false;
    }
    auto* property = image->GetFromPath(path);
    if (!property) {
        std::cerr << "Required WZ path was not found: " << path << "\n";
        return false;
    }
    const int patched = PatchCanvasTree(property, pngPath);
    if (patched <= 0) {
        std::cerr << "Required WZ path contains no patchable canvas: " << path << "\n";
        return false;
    }
    image->SetChanged(true);
    return true;
}

static bool VerifyPatchedMap(const fs::path& outputPath) {
    wz::WzFile verify(outputPath.string(), 83, wz::WzMapleVersion::GMS);
    if (verify.ParseWzFile() != wz::WzFileParseStatus::Success) return false;

    auto* back = FindDirectory(verify.GetWzDirectory(), "back", "Back");
    auto* obj = FindDirectory(verify.GetWzDirectory(), "obj", "Obj");
    auto* backLogin = FindLoginImage(back);
    auto* objLogin = FindLoginImage(obj);
    if (!backLogin || !objLogin) return false;

    auto backParsed = backLogin->ParseImage();
    auto objParsed = objLogin->ParseImage();
    if (!backParsed || !backParsed.value() || !objParsed || !objParsed.value()) {
        return false;
    }

    auto* background = FindBackgroundProperty(backLogin);
    auto* logo = objLogin->GetFromPath("Title/logo");
    auto* signboard = objLogin->GetFromPath("Title/signboard");
    return HasCanvas(background) && HasCanvas(logo) && HasCanvas(signboard);
}

static bool VerifyPatchedUi(const fs::path& outputPath) {
    wz::WzFile verify(outputPath.string(), 83, wz::WzMapleVersion::GMS);
    if (verify.ParseWzFile() != wz::WzFileParseStatus::Success) return false;
    auto* login = FindRootImage(verify.GetWzDirectory(), "login.img", "Login.img");
    if (!login) return false;
    auto parsed = login->ParseImage();
    if (!parsed || !parsed.value()) return false;
    const std::vector<std::string> required = {
        "Common/frame", "Title/BtLogin/normal", "Title/BtLogin/mouseOver",
        "Title/BtLogin/pressed", "Title/BtLogin/disabled",
        "Title/BtLoginIDSave/normal", "Title/BtLoginIDLost/normal",
        "Title/BtPasswdLost/normal", "Title/BtNew/normal",
        "Title/BtHomePage/normal", "Title/BtQuit/normal",
        "Title/check/0", "Title/check/1"
    };
    for (const auto& path : required) {
        if (!HasCanvas(login->GetFromPath(path))) return false;
    }
    return true;
}

int main(int argc, char** argv) {
    if (argc != 6) {
        std::cerr << "Usage: everleaf-login-wz-patcher <Map.wz> <UI.wz> "
                     "<art directory> <output Map.wz> <output UI.wz>\n";
        return 2;
    }

    const fs::path mapPath = argv[1];
    const fs::path uiPath = argv[2];
    const fs::path artPath = argv[3];
    const fs::path outputMapPath = argv[4];
    const fs::path outputUiPath = argv[5];

    if (!fs::is_regular_file(mapPath) ||
        !fs::is_regular_file(uiPath) || !fs::is_directory(artPath)) {
        std::cerr << "Map.wz, UI.wz, or EverLeaf login artwork is missing.\n";
        return 3;
    }

    wz::WzFile mapFile(mapPath.string(), 83, wz::WzMapleVersion::GMS);
    const auto parseStatus = mapFile.ParseWzFile();
    if (parseStatus != wz::WzFileParseStatus::Success) {
        std::cerr << "Could not parse Map.wz: "
                  << wz::GetErrorDescription(parseStatus) << "\n";
        return 4;
    }

    auto* back = FindDirectory(mapFile.GetWzDirectory(), "back", "Back");
    auto* obj = FindDirectory(mapFile.GetWzDirectory(), "obj", "Obj");
    auto* backLogin = FindLoginImage(back);
    auto* objLogin = FindLoginImage(obj);
    if (!backLogin || !objLogin) {
        std::cerr << "Map.wz is missing back/login.img or obj/login.img.\n";
        return 5;
    }

    auto backParsed = backLogin->ParseImage();
    auto objParsed = objLogin->ParseImage();
    if (!backParsed || !backParsed.value() || !objParsed || !objParsed.value()) {
        std::cerr << "Could not parse login images.\n";
        return 6;
    }

    auto* background = FindBackgroundProperty(backLogin);
    if (!background) {
        std::cerr << "Could not resolve the v83 login background node 11 safely.\n";
        return 7;
    }
    const int backgroundFrames = PatchCanvasTree(background, artPath / "background.png");
    if (backgroundFrames <= 0) {
        std::cerr << "Resolved login background contained no patchable canvas; property type="
                  << static_cast<int>(background->PropertyType()) << "\n";
        return 8;
    }
    backLogin->SetChanged(true);

    auto* logo = objLogin->GetFromPath("Title/logo");
    if (!logo) {
        std::cerr << "obj/login.img/Title/logo was not found.\n";
        return 9;
    }
    const int logoFrames = PatchCanvasTree(logo, artPath / "logo.png");
    if (logoFrames <= 0) {
        std::cerr << "Title/logo did not contain a patchable canvas; property type="
                  << static_cast<int>(logo->PropertyType()) << "\n";
        return 10;
    }
    objLogin->SetChanged(true);

    if (!PatchRequiredPath(objLogin, "Title/signboard", artPath / "signboard.png")) {
        return 11;
    }

    auto saved = mapFile.SaveToDisk(
        outputMapPath.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not save patched Map.wz: "
                  << saved.error().message() << "\n";
        return 12;
    }

    if (!VerifyPatchedMap(outputMapPath)) {
        std::cerr << "Saved Map.wz failed the post-write validation pass.\n";
        return 13;
    }

    wz::WzFile uiFile(uiPath.string(), 83, wz::WzMapleVersion::GMS);
    const auto uiParseStatus = uiFile.ParseWzFile();
    if (uiParseStatus != wz::WzFileParseStatus::Success) {
        std::cerr << "Could not parse UI.wz: "
                  << wz::GetErrorDescription(uiParseStatus) << "\n";
        return 14;
    }
    auto* uiLogin = FindRootImage(uiFile.GetWzDirectory(), "login.img", "Login.img");
    if (!uiLogin) {
        std::cerr << "UI.wz is missing Login.img.\n";
        return 15;
    }
    auto uiParsed = uiLogin->ParseImage();
    if (!uiParsed || !uiParsed.value()) {
        std::cerr << "Could not parse UI.wz/Login.img.\n";
        return 16;
    }

    if (!PatchRequiredPath(uiLogin, "Common/frame", artPath / "frame.png")) return 17;
    const std::vector<std::pair<std::string, std::string>> controls = {
        {"BtLogin", "login"}, {"BtLoginIDSave", "save-id"},
        {"BtLoginIDLost", "find-id"}, {"BtPasswdLost", "reset-password"},
        {"BtNew", "register"}, {"BtHomePage", "homepage"}, {"BtQuit", "quit"}
    };
    const std::vector<std::string> states = {"normal", "mouseOver", "pressed", "disabled"};
    for (const auto& [node, asset] : controls) {
        for (const auto& state : states) {
            if (!PatchRequiredPath(uiLogin, "Title/" + node + "/" + state,
                                   artPath / (asset + "-" + state + ".png"))) {
                return 18;
            }
        }
    }
    if (!PatchRequiredPath(uiLogin, "Title/check/0", artPath / "check-0.png") ||
        !PatchRequiredPath(uiLogin, "Title/check/1", artPath / "check-1.png")) {
        return 19;
    }

    auto uiSaved = uiFile.SaveToDisk(
        outputUiPath.string(), false, wz::WzMapleVersion::GMS);
    if (!uiSaved) {
        std::cerr << "Could not save patched UI.wz: "
                  << uiSaved.error().message() << "\n";
        return 20;
    }
    if (!VerifyPatchedUi(outputUiPath)) {
        std::cerr << "Saved UI.wz failed the post-write validation pass.\n";
        return 21;
    }

    std::cout << "Patched EverLeaf login background canvas frame(s): "
              << backgroundFrames << "; logo canvas frame(s): " << logoFrames
              << "; saved validated Map.wz and UI.wz theme.\n";
    return 0;
}
