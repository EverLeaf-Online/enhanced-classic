#include <filesystem>
#include <iostream>
#include <utility>

#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzPngProperty.h"
#include "wz/WzDirectory.h"
#include "wz/WzEnums.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"

namespace fs = std::filesystem;

// The legacy open-book chrome is a separate Map.wz layer from UI.wz/Common/frame.
// Patch only this audited 799x599 canvas; do not touch the EverLeaf background or controls.
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

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: everleaf-remove-map-login-frame <Map.wz> <transparent 799x599 png> <output Map.wz>\n";
        return 2;
    }

    const fs::path input = argv[1];
    const fs::path transparent = argv[2];
    const fs::path output = argv[3];
    if (!fs::is_regular_file(input) || !fs::is_regular_file(transparent)) {
        std::cerr << "Input Map.wz or transparent frame PNG is missing.\n";
        return 3;
    }

    wz::WzFile map(input.string(), 83, wz::WzMapleVersion::GMS);
    const auto parsed = map.ParseWzFile();
    if (parsed != wz::WzFileParseStatus::Success) {
        std::cerr << "Could not parse Map.wz: " << wz::GetErrorDescription(parsed) << "\n";
        return 4;
    }

    auto* obj = FindDirectory(map.GetWzDirectory(), "obj", "Obj");
    auto* login = FindLoginImage(obj);
    if (!login) {
        std::cerr << "Map.wz is missing Obj/login.img.\n";
        return 5;
    }
    auto imageParsed = login->ParseImage();
    if (!imageParsed || !imageParsed.value()) {
        std::cerr << "Could not parse Obj/login.img.\n";
        return 6;
    }

    auto* property = login->GetFromPath("Common/frame/0/0");
    if (!property || property->PropertyType() != wz::WzPropertyType::Canvas) {
        std::cerr << "Expected canvas Map.wz\\Obj\\login.img\\Common\\frame\\0\\0 was not found.\n";
        return 7;
    }
    auto* canvas = static_cast<wz::WzCanvasProperty*>(property);
    auto* current = canvas->PngProperty();
    if (!current || current->Width() != 799 || current->Height() != 599) {
        std::cerr << "Unexpected login frame dimensions; refusing broad patch.\n";
        return 8;
    }

    auto png = wz::WzPngProperty::FromPngFile(transparent.string(), wz::WzPngFormat::Format2);
    if (!png) {
        std::cerr << "Could not encode transparent frame: " << png.error().message() << "\n";
        return 9;
    }
    canvas->SetPngProperty(std::move(png.value()));
    login->SetChanged(true);

    auto saved = map.SaveToDisk(output.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not save patched Map.wz: " << saved.error().message() << "\n";
        return 10;
    }

    wz::WzFile verify(output.string(), 83, wz::WzMapleVersion::GMS);
    if (verify.ParseWzFile() != wz::WzFileParseStatus::Success) return 11;
    auto* vobj = FindDirectory(verify.GetWzDirectory(), "obj", "Obj");
    auto* vlogin = FindLoginImage(vobj);
    if (!vlogin) return 12;
    auto vp = vlogin->ParseImage();
    if (!vp || !vp.value()) return 13;
    auto* vprop = vlogin->GetFromPath("Common/frame/0/0");
    if (!vprop || vprop->PropertyType() != wz::WzPropertyType::Canvas) return 14;
    auto* vpng = static_cast<wz::WzCanvasProperty*>(vprop)->PngProperty();
    if (!vpng || vpng->Width() != 799 || vpng->Height() != 599) return 15;

    std::cout << "MAP_LOGIN_BOOK_FRAME_REMOVED path=Obj/login.img/Common/frame/0/0 size=799x599\n";
    return 0;
}
