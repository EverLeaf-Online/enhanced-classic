#include <filesystem>
#include <iostream>
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
static constexpr int kMaxDepth = 24;

static wz::WzImage* FindLoginImage(wz::WzDirectory* root) {
    if (!root) return nullptr;
    if (auto* image = root->GetImageByName("Login.img")) return image;
    return root->GetImageByName("login.img");
}

static wz::WzImageProperty* ResolveUol(wz::WzUOLProperty* uol) {
    if (!uol) return nullptr;
    auto* linked = uol->LinkValue();
    if (!linked || linked->ObjectType() != wz::WzObjectType::Property) return nullptr;
    return static_cast<wz::WzImageProperty*>(linked);
}

static bool SetCanvas(wz::WzCanvasProperty* canvas, const fs::path& pngPath) {
    if (!canvas || !fs::is_regular_file(pngPath)) return false;
    auto result = wz::WzPngProperty::FromPngFile(pngPath.string(), wz::WzPngFormat::Format2);
    if (!result) {
        std::cerr << "Could not encode " << pngPath << ": " << result.error().message() << "\n";
        return false;
    }
    canvas->SetPngProperty(std::move(result.value()));
    return true;
}

static int PatchTree(wz::WzImageProperty* property, const fs::path& pngPath, int depth = 0) {
    if (!property || depth > kMaxDepth) return 0;
    switch (property->PropertyType()) {
        case wz::WzPropertyType::Canvas:
            return SetCanvas(static_cast<wz::WzCanvasProperty*>(property), pngPath) ? 1 : -1;
        case wz::WzPropertyType::SubProperty: {
            int changed = 0;
            for (auto* child : *static_cast<wz::WzSubProperty*>(property)->WzProperties()) {
                int result = PatchTree(child, pngPath, depth + 1);
                if (result < 0) return -1;
                changed += result;
            }
            return changed;
        }
        case wz::WzPropertyType::UOL: {
            auto* target = ResolveUol(static_cast<wz::WzUOLProperty*>(property));
            if (!target || target == property) return 0;
            return PatchTree(target, pngPath, depth + 1);
        }
        default:
            return 0;
    }
}

static bool PatchPath(wz::WzImage* login, const std::string& path, const fs::path& pngPath) {
    auto* property = login ? login->GetFromPath(path) : nullptr;
    if (!property) {
        std::cerr << "Required UI path missing: " << path << "\n";
        return false;
    }
    const int changed = PatchTree(property, pngPath);
    if (changed <= 0) {
        std::cerr << "Required UI path has no patchable canvas: " << path << "\n";
        return false;
    }
    login->SetChanged(true);
    return true;
}

static bool HasCanvas(wz::WzImageProperty* property, int depth = 0) {
    if (!property || depth > kMaxDepth) return false;
    switch (property->PropertyType()) {
        case wz::WzPropertyType::Canvas:
            return true;
        case wz::WzPropertyType::SubProperty:
            for (auto* child : *static_cast<wz::WzSubProperty*>(property)->WzProperties())
                if (HasCanvas(child, depth + 1)) return true;
            return false;
        case wz::WzPropertyType::UOL: {
            auto* target = ResolveUol(static_cast<wz::WzUOLProperty*>(property));
            return target && target != property && HasCanvas(target, depth + 1);
        }
        default:
            return false;
    }
}

static bool Verify(const fs::path& output) {
    wz::WzFile file(output.string(), 83, wz::WzMapleVersion::GMS);
    if (file.ParseWzFile() != wz::WzFileParseStatus::Success) return false;
    auto* login = FindLoginImage(file.GetWzDirectory());
    if (!login) return false;
    auto parsed = login->ParseImage();
    if (!parsed || !parsed.value()) return false;
    const std::vector<std::string> required = {
        "Common/BtWselect/normal", "Common/BtWselect/mouseOver",
        "Common/BtStart/normal", "Common/BtExit/normal", "Common/BtStart2/normal",
        "Common/selectWorld", "CharSelect/charInfo"
    };
    for (const auto& path : required)
        if (!HasCanvas(login->GetFromPath(path))) return false;
    return true;
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: everleaf-login-flow-ui <input UI.wz> <art dir> <output UI.wz>\n";
        return 2;
    }
    const fs::path input = argv[1], art = argv[2], output = argv[3];
    if (!fs::is_regular_file(input) || !fs::is_directory(art)) return 3;

    wz::WzFile file(input.string(), 83, wz::WzMapleVersion::GMS);
    const auto status = file.ParseWzFile();
    if (status != wz::WzFileParseStatus::Success) {
        std::cerr << "Could not parse UI.wz: " << wz::GetErrorDescription(status) << "\n";
        return 4;
    }
    auto* login = FindLoginImage(file.GetWzDirectory());
    if (!login) return 5;
    auto parsed = login->ParseImage();
    if (!parsed || !parsed.value()) return 6;

    const std::vector<std::string> states = {"normal", "mouseOver", "pressed", "disabled"};
    const std::vector<std::pair<std::string, std::string>> buttons = {
        {"Common/BtWselect", "world-select"},
        {"Common/BtStart", "start"},
        {"Common/BtExit", "exit"},
        {"Common/BtStart2", "start2"},
    };
    for (const auto& [node, asset] : buttons) {
        for (const auto& state : states) {
            if (!PatchPath(login, node + "/" + state,
                           art / ("flow-" + asset + "-" + state + ".png"))) return 7;
        }
    }
    if (!PatchPath(login, "Common/selectWorld", art / "flow-select-world.png")) return 8;
    if (!PatchPath(login, "CharSelect/charInfo", art / "flow-char-info.png")) return 9;

    auto saved = file.SaveToDisk(output.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not save UI.wz: " << saved.error().message() << "\n";
        return 10;
    }
    if (!Verify(output)) {
        std::cerr << "Reparse verification failed for world/character-flow UI.wz\n";
        return 11;
    }
    std::cout << "EVERLEAF_LOGIN_FLOW_UI_PATCHED buttons=4 panels=2\n";
    return 0;
}
