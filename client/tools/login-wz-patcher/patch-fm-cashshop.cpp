#include <filesystem>
#include <iostream>
#include <string>

#include "wz/Properties/WzIntProperty.h"
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

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: everleaf-patch-fm-cashshop <input Map.wz> <output Map.wz>\n";
        return 2;
    }

    const fs::path input = argv[1];
    const fs::path output = argv[2];

    if (!fs::is_regular_file(input)) {
        std::cerr << "Input Map.wz not found\n";
        return 3;
    }

    wz::WzFile map(input.string(), 83, wz::WzMapleVersion::GMS);
    if (map.ParseWzFile() != wz::WzFileParseStatus::Success) {
        std::cerr << "Could not parse Map.wz\n";
        return 4;
    }

    auto* mapDir = FindDirectory(map.GetWzDirectory(), "map", "Map");
    if (!mapDir) return 5;
    auto* map1 = FindDirectory(mapDir, "map9", "Map9");
    if (!map1) return 6;

    int patched = 0;
    for (int id = 910000001; id <= 910000022; ++id) {
        const std::string name = std::to_string(id) + ".img";
        auto* image = map1->GetImageByName(name);
        if (!image) return 7;
        auto parsed = image->ParseImage();
        if (!parsed || !parsed.value()) return 8;
        auto* prop = image->GetFromPath("info/fieldLimit");
        if (!prop || prop->PropertyType() != wz::WzPropertyType::Int) return 9;
        auto* fieldLimit = static_cast<wz::WzIntProperty*>(prop);
        const int before = fieldLimit->Value();
        const int after = before & ~0x10;
        if (before != after) {
            fieldLimit->SetValue(after);
            image->SetChanged(true);
            ++patched;
        }
        std::cout << id << " fieldLimit " << before << " -> " << after << "\n";
    }

    if (patched != 22) {
        std::cerr << "Expected 22 patches, got " << patched << "\n";
        return 10;
    }

    auto saved = map.SaveToDisk(output.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << saved.error().message() << "\n";
        return 11;
    }
    std::cout << "FM_CASHSHOP_PATCH_OK rooms=" << patched << "\n";
    return 0;
}
