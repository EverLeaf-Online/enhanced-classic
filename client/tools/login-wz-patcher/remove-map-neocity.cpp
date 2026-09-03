#include <filesystem>
#include <iostream>
#include <string>
#include <utility>

#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzPngProperty.h"
#include "wz/Properties/WzSubProperty.h"
#include "wz/WzDirectory.h"
#include "wz/WzEnums.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"
#include "wz/WzImageProperty.h"

namespace fs = std::filesystem;

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

static bool PatchTree(wz::WzImageProperty* property, const fs::path& transparentDir,
                      int& patched) {
    if (!property) return true;

    if (property->PropertyType() == wz::WzPropertyType::Canvas) {
        auto* canvas = static_cast<wz::WzCanvasProperty*>(property);
        auto* current = canvas->PngProperty();
        if (!current || current->Width() <= 0 || current->Height() <= 0) return false;

        const fs::path pngPath = transparentDir /
            (std::to_string(current->Width()) + "x" + std::to_string(current->Height()) + ".png");
        if (!fs::is_regular_file(pngPath)) {
            std::cerr << "Missing transparent replacement for " << property->FullPath()
                      << " size=" << current->Width() << "x" << current->Height() << "\n";
            return false;
        }

        auto png = wz::WzPngProperty::FromPngFile(pngPath.string(), wz::WzPngFormat::Format2);
        if (!png) {
            std::cerr << "Could not encode transparent Neo City replacement: "
                      << png.error().message() << "\n";
            return false;
        }
        canvas->SetPngProperty(std::move(png.value()));
        ++patched;

        for (auto* child : *canvas->WzProperties()) {
            if (!PatchTree(child, transparentDir, patched)) return false;
        }
        return true;
    }

    if (property->PropertyType() == wz::WzPropertyType::SubProperty) {
        auto* sub = static_cast<wz::WzSubProperty*>(property);
        for (auto* child : *sub->WzProperties()) {
            if (!PatchTree(child, transparentDir, patched)) return false;
        }
    }
    return true;
}

static int CountCanvases(wz::WzImageProperty* property) {
    if (!property) return 0;
    int count = 0;
    if (property->PropertyType() == wz::WzPropertyType::Canvas) {
        ++count;
        auto* canvas = static_cast<wz::WzCanvasProperty*>(property);
        for (auto* child : *canvas->WzProperties()) count += CountCanvases(child);
    } else if (property->PropertyType() == wz::WzPropertyType::SubProperty) {
        auto* sub = static_cast<wz::WzSubProperty*>(property);
        for (auto* child : *sub->WzProperties()) count += CountCanvases(child);
    }
    return count;
}

int main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "Usage: everleaf-remove-map-neocity <Map.wz> <transparent png directory> <output Map.wz>\n";
        return 2;
    }

    const fs::path input = argv[1];
    const fs::path transparentDir = argv[2];
    const fs::path output = argv[3];
    if (!fs::is_regular_file(input) || !fs::is_directory(transparentDir)) return 3;

    wz::WzFile map(input.string(), 83, wz::WzMapleVersion::GMS);
    const auto parsed = map.ParseWzFile();
    if (parsed != wz::WzFileParseStatus::Success) return 4;

    auto* obj = FindDirectory(map.GetWzDirectory(), "obj", "Obj");
    auto* login = FindLoginImage(obj);
    if (!login) return 5;
    auto imageParsed = login->ParseImage();
    if (!imageParsed || !imageParsed.value()) return 6;

    auto* neoCity = login->GetFromPath("WorldSelect/neoCity");
    if (!neoCity || neoCity->PropertyType() != wz::WzPropertyType::SubProperty) {
        std::cerr << "Expected Map.wz\\Obj\\login.img\\WorldSelect\\neoCity subtree was not found.\n";
        return 7;
    }

    const int expected = CountCanvases(neoCity);
    if (expected != 32) {
        std::cerr << "Unexpected Neo City canvas count " << expected << "; refusing broad patch.\n";
        return 8;
    }

    int patched = 0;
    if (!PatchTree(neoCity, transparentDir, patched) || patched != expected) return 9;
    login->SetChanged(true);

    auto saved = map.SaveToDisk(output.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not save Neo City-free Map.wz: " << saved.error().message() << "\n";
        return 10;
    }

    wz::WzFile verify(output.string(), 83, wz::WzMapleVersion::GMS);
    if (verify.ParseWzFile() != wz::WzFileParseStatus::Success) return 11;
    auto* vobj = FindDirectory(verify.GetWzDirectory(), "obj", "Obj");
    auto* vlogin = FindLoginImage(vobj);
    if (!vlogin) return 12;
    auto vp = vlogin->ParseImage();
    if (!vp || !vp.value()) return 13;
    auto* vneo = vlogin->GetFromPath("WorldSelect/neoCity");
    if (!vneo || CountCanvases(vneo) != expected) return 14;

    std::cout << "MAP_WORLDSELECT_NEOCITY_REMOVED path=Obj/login.img/WorldSelect/neoCity canvases="
              << patched << "\n";
    return 0;
}
