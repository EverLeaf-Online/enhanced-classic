#include <filesystem>
#include <iostream>
#include <string>

#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzPngProperty.h"
#include "wz/Properties/WzVectorProperty.h"
#include "wz/WzDirectory.h"
#include "wz/WzEnums.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"
#include "wz/WzImageProperty.h"

namespace fs = std::filesystem;

struct LoginBackground {
    wz::WzImage* image = nullptr;
    wz::WzCanvasProperty* canvas = nullptr;
    wz::WzVectorProperty* origin = nullptr;
};

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

static bool ResolveBackground(wz::WzFile& file, LoginBackground& result) {
    auto* back = FindDirectory(file.GetWzDirectory(), "back", "Back");
    result.image = FindLoginImage(back);
    if (!result.image) return false;
    auto parsed = result.image->ParseImage();
    if (!parsed || !parsed.value()) return false;

    auto* property = result.image->GetFromPath("back/11");
    auto* origin = result.image->GetFromPath("back/11/origin");
    if (!property || property->PropertyType() != wz::WzPropertyType::Canvas ||
        !origin || origin->PropertyType() != wz::WzPropertyType::Vector) {
        return false;
    }

    result.canvas = static_cast<wz::WzCanvasProperty*>(property);
    result.origin = static_cast<wz::WzVectorProperty*>(origin);
    return result.canvas->PngProperty() && result.origin->X && result.origin->Y;
}

static int Inspect(const fs::path& mapPath) {
    wz::WzFile file(mapPath.string(), 83, wz::WzMapleVersion::GMS);
    if (file.ParseWzFile() != wz::WzFileParseStatus::Success) return 10;
    LoginBackground bg;
    if (!ResolveBackground(file, bg)) return 11;
    auto* png = bg.canvas->PngProperty();
    std::cout << "WIDTH=" << png->Width() << "\n"
              << "HEIGHT=" << png->Height() << "\n"
              << "ORIGIN_X=" << bg.origin->X->Value() << "\n"
              << "ORIGIN_Y=" << bg.origin->Y->Value() << "\n";
    return 0;
}

static int Extract(const fs::path& mapPath, const fs::path& pngPath) {
    wz::WzFile file(mapPath.string(), 83, wz::WzMapleVersion::GMS);
    if (file.ParseWzFile() != wz::WzFileParseStatus::Success) return 20;
    LoginBackground bg;
    if (!ResolveBackground(file, bg)) return 21;
    auto saved = bg.canvas->PngProperty()->SaveToFile(pngPath.string());
    if (!saved) {
        std::cerr << "Could not export login background: " << saved.error().message() << "\n";
        return 22;
    }
    auto* png = bg.canvas->PngProperty();
    std::cout << "EXTRACTED=" << png->Width() << "x" << png->Height()
              << " ORIGIN=" << bg.origin->X->Value() << "," << bg.origin->Y->Value() << "\n";
    return 0;
}

static int PatchResponsive(const fs::path& mapPath,
                           const fs::path& replacementPng,
                           const fs::path& outputPath) {
    wz::WzFile file(mapPath.string(), 83, wz::WzMapleVersion::GMS);
    if (file.ParseWzFile() != wz::WzFileParseStatus::Success) return 30;
    LoginBackground bg;
    if (!ResolveBackground(file, bg)) return 31;

    const int oldWidth = bg.canvas->PngProperty()->Width();
    const int oldHeight = bg.canvas->PngProperty()->Height();
    const int oldOriginX = bg.origin->X->Value();
    const int oldOriginY = bg.origin->Y->Value();

    auto replacement = wz::WzPngProperty::FromPngFile(
        replacementPng.string(), wz::WzPngFormat::Format2);
    if (!replacement) {
        std::cerr << "Could not encode responsive login PNG: "
                  << replacement.error().message() << "\n";
        return 32;
    }
    const int newWidth = replacement.value()->Width();
    const int newHeight = replacement.value()->Height();
    if (newWidth < oldWidth || newHeight != oldHeight) {
        std::cerr << "Responsive login PNG must keep height " << oldHeight
                  << " and may only widen the canvas. Got " << newWidth << "x"
                  << newHeight << ".\n";
        return 33;
    }

    const int horizontalInset = (newWidth - oldWidth) / 2;
    const int newOriginX = oldOriginX + horizontalInset;
    bg.canvas->SetPngProperty(std::move(replacement.value()));
    bg.origin->X->SetValue(newOriginX);
    bg.image->SetChanged(true);

    auto saved = file.SaveToDisk(outputPath.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not write responsive Map.wz: " << saved.error().message() << "\n";
        return 34;
    }

    wz::WzFile verify(outputPath.string(), 83, wz::WzMapleVersion::GMS);
    if (verify.ParseWzFile() != wz::WzFileParseStatus::Success) return 35;
    LoginBackground check;
    if (!ResolveBackground(verify, check)) return 36;
    auto* checkPng = check.canvas->PngProperty();
    if (checkPng->Width() != newWidth || checkPng->Height() != oldHeight ||
        check.origin->X->Value() != newOriginX || check.origin->Y->Value() != oldOriginY) {
        return 37;
    }

    std::cout << "RESPONSIVE_LOGIN_OK old=" << oldWidth << "x" << oldHeight
              << " new=" << newWidth << "x" << newHeight
              << " origin=" << oldOriginX << "," << oldOriginY
              << " -> " << newOriginX << "," << oldOriginY << "\n";
    return 0;
}

int main(int argc, char** argv) {
    if (argc >= 3 && std::string(argv[1]) == "inspect") {
        return Inspect(argv[2]);
    }
    if (argc == 4 && std::string(argv[1]) == "extract") {
        return Extract(argv[2], argv[3]);
    }
    if (argc == 5 && std::string(argv[1]) == "patch") {
        return PatchResponsive(argv[2], argv[3], argv[4]);
    }

    std::cerr << "Usage:\n"
              << "  everleaf-responsive-login-wz inspect <Map.wz>\n"
              << "  everleaf-responsive-login-wz extract <Map.wz> <background.png>\n"
              << "  everleaf-responsive-login-wz patch <Map.wz> <responsive.png> <output Map.wz>\n";
    return 2;
}
