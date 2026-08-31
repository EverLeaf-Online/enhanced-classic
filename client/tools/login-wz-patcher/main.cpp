#include <filesystem>
#include <iostream>
#include <memory>
#include <string>
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

static wz::WzImageProperty* FindDirectProperty(wz::WzImage* image,
                                               const std::string& name) {
    if (!image) return nullptr;
    auto result = image->GetPropertyByName(name);
    if (result && result.value()) return result.value();
    return nullptr;
}

static wz::WzCanvasProperty* FindUniqueCanvasInProperty(wz::WzImageProperty* root,
                                                        int width,
                                                        int height,
                                                        const char* label) {
    if (!root) return nullptr;
    std::vector<wz::WzCanvasProperty*> matches;
    CollectCanvasByDimensions(root, width, height, matches);
    if (matches.size() != 1) {
        std::cerr << "Expected exactly one " << width << "x" << height
                  << " canvas under " << label << ", found " << matches.size()
                  << ".\n";
        return nullptr;
    }
    return matches.front();
}

static wz::WzImageProperty* FindBackgroundProperty(wz::WzImage* backLogin) {
    if (!backLogin) return nullptr;

    // Some tooling exposes this as back/login.img/11, but libwz parses this
    // v83 file with two top-level groups: `back` and `ani`. The static login
    // background belongs to the `back` subtree; `ani` contains animation data.
    if (auto* direct = FindDirectProperty(backLogin, "11")) {
        return direct;
    }

    auto* backGroup = FindDirectProperty(backLogin, "back");
    if (!backGroup) {
        std::cerr << "back/login.img is missing the parsed top-level `back` group.\n";
        return nullptr;
    }

    return FindUniqueCanvasInProperty(backGroup,
                                      kLoginBackgroundWidth,
                                      kLoginBackgroundHeight,
                                      "back/login.img/back");
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
    return HasCanvas(background) && HasCanvas(logo);
}

int main(int argc, char** argv) {
    if (argc != 5) {
        std::cerr << "Usage: everleaf-login-wz-patcher <Map.wz> <background.png> "
                     "<logo.png> <output Map.wz>\n";
        return 2;
    }

    const fs::path mapPath = argv[1];
    const fs::path backgroundPath = argv[2];
    const fs::path logoPath = argv[3];
    const fs::path outputPath = argv[4];

    if (!fs::is_regular_file(mapPath) ||
        !fs::is_regular_file(backgroundPath) ||
        !fs::is_regular_file(logoPath)) {
        std::cerr << "Map.wz or EverLeaf login artwork is missing.\n";
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
        std::cerr << "Could not resolve the v83 800x600 login background safely.\n";
        return 7;
    }
    const int backgroundFrames = PatchCanvasTree(background, backgroundPath);
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
    const int logoFrames = PatchCanvasTree(logo, logoPath);
    if (logoFrames <= 0) {
        std::cerr << "Title/logo did not contain a patchable canvas; property type="
                  << static_cast<int>(logo->PropertyType()) << "\n";
        return 10;
    }
    objLogin->SetChanged(true);

    auto saved = mapFile.SaveToDisk(
        outputPath.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not save patched Map.wz: "
                  << saved.error().message() << "\n";
        return 11;
    }

    if (!VerifyPatchedMap(outputPath)) {
        std::cerr << "Saved Map.wz failed the post-write validation pass.\n";
        return 12;
    }

    std::cout << "Patched EverLeaf login background canvas frame(s): "
              << backgroundFrames << "; logo canvas frame(s): " << logoFrames
              << "; saved validated Map.wz.\n";
    return 0;
}
