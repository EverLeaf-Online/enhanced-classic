#include <filesystem>
#include <iostream>
#include <string>

#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzPngProperty.h"
#include "wz/WzDirectory.h"
#include "wz/WzEnums.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"
#include "wz/WzImageProperty.h"

namespace fs = std::filesystem;

struct SysOptBackground {
    wz::WzImage* image = nullptr;
    wz::WzCanvasProperty* canvas = nullptr;
};

static bool Resolve(wz::WzFile& file, SysOptBackground& out) {
    auto* root = file.GetWzDirectory();
    if (!root) return false;
    out.image = root->GetImageByName("UIWindow.img");
    if (!out.image) return false;
    auto parsed = out.image->ParseImage();
    if (!parsed || !parsed.value()) return false;
    auto* prop = out.image->GetFromPath("SysOpt/backgrnd");
    if (!prop || prop->PropertyType() != wz::WzPropertyType::Canvas) return false;
    out.canvas = static_cast<wz::WzCanvasProperty*>(prop);
    return out.canvas->PngProperty() != nullptr;
}

static int Inspect(const fs::path& uiPath) {
    wz::WzFile file(uiPath.string(), 83, wz::WzMapleVersion::GMS);
    if (file.ParseWzFile() != wz::WzFileParseStatus::Success) return 10;
    SysOptBackground bg;
    if (!Resolve(file, bg)) return 11;
    auto* png = bg.canvas->PngProperty();
    std::cout << "WIDTH=" << png->Width() << "\nHEIGHT=" << png->Height() << "\n";
    return 0;
}

static int Extract(const fs::path& uiPath, const fs::path& pngPath) {
    wz::WzFile file(uiPath.string(), 83, wz::WzMapleVersion::GMS);
    if (file.ParseWzFile() != wz::WzFileParseStatus::Success) return 20;
    SysOptBackground bg;
    if (!Resolve(file, bg)) return 21;
    auto saved = bg.canvas->PngProperty()->SaveToFile(pngPath.string());
    if (!saved) {
        std::cerr << "Could not export System Options background: " << saved.error().message() << "\n";
        return 22;
    }
    std::cout << "EXTRACTED=" << bg.canvas->PngProperty()->Width() << "x"
              << bg.canvas->PngProperty()->Height() << "\n";
    return 0;
}

static int Patch(const fs::path& uiPath,
                 const fs::path& replacementPng,
                 const fs::path& outputPath) {
    wz::WzFile file(uiPath.string(), 83, wz::WzMapleVersion::GMS);
    if (file.ParseWzFile() != wz::WzFileParseStatus::Success) return 30;
    SysOptBackground bg;
    if (!Resolve(file, bg)) return 31;

    const int oldWidth = bg.canvas->PngProperty()->Width();
    const int oldHeight = bg.canvas->PngProperty()->Height();
    auto replacement = wz::WzPngProperty::FromPngFile(
        replacementPng.string(), wz::WzPngFormat::Format2);
    if (!replacement) {
        std::cerr << "Could not encode System Options PNG: "
                  << replacement.error().message() << "\n";
        return 32;
    }
    const int newWidth = replacement.value()->Width();
    const int newHeight = replacement.value()->Height();
    if (oldWidth != 299 || oldHeight != 366 || newWidth != 299 || newHeight != 396) {
        std::cerr << "Expected stock 299x366 -> native-row 299x396, got "
                  << oldWidth << "x" << oldHeight << " -> "
                  << newWidth << "x" << newHeight << "\n";
        return 33;
    }

    bg.canvas->SetPngProperty(std::move(replacement.value()));
    bg.image->SetChanged(true);
    auto saved = file.SaveToDisk(outputPath.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not write patched UI.wz: " << saved.error().message() << "\n";
        return 34;
    }

    wz::WzFile verify(outputPath.string(), 83, wz::WzMapleVersion::GMS);
    if (verify.ParseWzFile() != wz::WzFileParseStatus::Success) return 35;
    SysOptBackground check;
    if (!Resolve(verify, check)) return 36;
    auto* png = check.canvas->PngProperty();
    if (!png || png->Width() != 299 || png->Height() != 396) return 37;

    std::cout << "SYSTEM_OPTIONS_RESOLUTION_ROW_OK 299x366 -> 299x396\n";
    return 0;
}

int main(int argc, char** argv) {
    if (argc == 3 && std::string(argv[1]) == "inspect") return Inspect(argv[2]);
    if (argc == 4 && std::string(argv[1]) == "extract") return Extract(argv[2], argv[3]);
    if (argc == 5 && std::string(argv[1]) == "patch") return Patch(argv[2], argv[3], argv[4]);
    std::cerr << "Usage:\n"
              << "  everleaf-system-options-wz inspect <UI.wz>\n"
              << "  everleaf-system-options-wz extract <UI.wz> <sysopt.png>\n"
              << "  everleaf-system-options-wz patch <UI.wz> <sysopt-native.png> <output UI.wz>\n";
    return 2;
}
