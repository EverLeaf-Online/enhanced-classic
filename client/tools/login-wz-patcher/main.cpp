#include <filesystem>
#include <iostream>
#include <memory>
#include <string>

#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzPngProperty.h"
#include "wz/WzDirectory.h"
#include "wz/WzEnums.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"

namespace fs = std::filesystem;

static wz::WzDirectory* FindBackDirectory(wz::WzDirectory* root) {
    if (!root) return nullptr;
    if (auto* dir = root->GetDirectoryByName("back")) return dir;
    if (auto* dir = root->GetDirectoryByName("Back")) return dir;
    return nullptr;
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: everleaf-login-wz-patcher <Map.wz> <login.png> <output Map.wz>\n";
        return 2;
    }

    const fs::path mapPath = argv[1];
    const fs::path pngPath = argv[2];
    const fs::path outputPath = argv[3];

    if (!fs::is_regular_file(mapPath) || !fs::is_regular_file(pngPath)) {
        std::cerr << "Map.wz or login artwork is missing.\n";
        return 3;
    }

    wz::WzFile mapFile(mapPath.string(), 83, wz::WzMapleVersion::GMS);
    const auto parseStatus = mapFile.ParseWzFile();
    if (parseStatus != wz::WzFileParseStatus::Success) {
        std::cerr << "Could not parse Map.wz: " << wz::GetErrorDescription(parseStatus) << "\n";
        return 4;
    }

    auto* back = FindBackDirectory(mapFile.GetWzDirectory());
    if (!back) {
        std::cerr << "Map.wz does not contain the expected back directory.\n";
        return 5;
    }

    auto* login = back->GetImageByName("login.img");
    if (!login) login = back->GetImageByName("Login.img");
    if (!login) {
        std::cerr << "Map.wz does not contain back/login.img.\n";
        return 6;
    }

    auto parsed = login->ParseImage();
    if (!parsed || !parsed.value()) {
        std::cerr << "Could not parse back/login.img.\n";
        return 7;
    }

    auto canvasResult = login->GetPropertyByName("11");
    if (!canvasResult) {
        std::cerr << "back/login.img does not contain canvas 11.\n";
        return 8;
    }

    auto* canvas = dynamic_cast<wz::WzCanvasProperty*>(canvasResult.value());
    if (!canvas) {
        std::cerr << "back/login.img/11 is not a canvas property.\n";
        return 9;
    }

    auto pngResult = wz::WzPngProperty::FromPngFile(pngPath.string(), wz::WzPngFormat::Format2);
    if (!pngResult) {
        std::cerr << "Could not encode EverLeaf login artwork: " << pngResult.error().message() << "\n";
        return 10;
    }

    canvas->SetPngProperty(std::move(pngResult.value()));
    login->SetChanged(true);

    auto saved = mapFile.SaveToDisk(outputPath.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not save patched Map.wz: " << saved.error().message() << "\n";
        return 11;
    }

    std::cout << "Patched back/login.img/11 with EverLeaf artwork: "
              << pngPath.string() << "\n";
    return 0;
}
