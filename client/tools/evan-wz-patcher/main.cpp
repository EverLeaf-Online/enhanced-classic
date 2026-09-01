#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "wz/WzDirectory.h"
#include "wz/WzEnums.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"

namespace fs = std::filesystem;

struct CopyEntry {
    enum class Kind { Image, Directory };
    Kind kind;
    std::string name;
};

static bool ParseSpec(const fs::path& path, std::vector<CopyEntry>& entries) {
    std::ifstream input(path);
    if (!input) {
        std::cerr << "Could not open copy spec: " << path.string() << "\n";
        return false;
    }

    std::string line;
    int lineNo = 0;
    while (std::getline(input, line)) {
        ++lineNo;
        if (!line.empty() && line.back() == '\r') line.pop_back();
        const auto first = line.find_first_not_of(" \t");
        if (first == std::string::npos || line[first] == '#') continue;
        line.erase(0, first);
        const auto colon = line.find(':');
        if (colon == std::string::npos || colon == line.size() - 1) {
            std::cerr << "Invalid spec line " << lineNo << ": " << line << "\n";
            return false;
        }
        const std::string type = line.substr(0, colon);
        const std::string name = line.substr(colon + 1);
        if (type == "image") {
            entries.push_back({CopyEntry::Kind::Image, name});
        } else if (type == "directory") {
            entries.push_back({CopyEntry::Kind::Directory, name});
        } else {
            std::cerr << "Unknown spec type on line " << lineNo << ": " << type << "\n";
            return false;
        }
    }

    if (entries.empty()) {
        std::cerr << "Copy spec contains no entries.\n";
        return false;
    }
    return true;
}

static bool ParseAllImages(wz::WzDirectory* dir) {
    if (!dir) return false;
    auto result = dir->ParseImages();
    if (!result) {
        std::cerr << "Could not parse donor directory images: " << result.error().message() << "\n";
        return false;
    }
    return true;
}

static void MarkAllImagesChanged(wz::WzDirectory* dir) {
    for (auto* image : dir->WzImages()) {
        image->SetChanged(true);
    }
    for (auto* child : dir->WzDirectories()) {
        MarkAllImagesChanged(child);
    }
}

static void RetargetDirectory(wz::WzDirectory* dir, wz::WzFile* targetFile) {
    dir->SetWzFile(targetFile);
    for (auto* child : dir->WzDirectories()) {
        RetargetDirectory(child, targetFile);
    }
}

static bool ReplaceImage(wz::WzDirectory* base, wz::WzDirectory* donor, const std::string& name) {
    auto* source = donor->GetImageByName(name);
    if (!source) {
        std::cerr << "Donor is missing required image: " << name << "\n";
        return false;
    }

    auto parsed = source->ParseImage();
    if (!parsed || !parsed.value()) {
        std::cerr << "Could not parse donor image: " << name << "\n";
        return false;
    }
    source->SetChanged(true);

    if (auto* existing = base->GetImageByName(name)) {
        auto removed = base->RemoveImage(existing);
        if (!removed) {
            std::cerr << "Could not remove existing base image " << name << ": "
                      << removed.error().message() << "\n";
            return false;
        }
    }

    auto moved = donor->RemoveImage(source);
    if (!moved) {
        std::cerr << "Could not detach donor image " << name << ": "
                  << moved.error().message() << "\n";
        return false;
    }
    auto added = base->AddImage(std::move(moved.value()));
    if (!added) {
        std::cerr << "Could not add donor image " << name << " to base: "
                  << added.error().message() << "\n";
        return false;
    }

    std::cout << "Replaced image: " << name << "\n";
    return true;
}

static bool ReplaceDirectory(wz::WzDirectory* base, wz::WzDirectory* donor, const std::string& name) {
    auto* source = donor->GetDirectoryByName(name);
    if (!source) {
        std::cerr << "Donor is missing required directory: " << name << "\n";
        return false;
    }

    if (!ParseAllImages(source)) return false;
    MarkAllImagesChanged(source);

    if (auto* existing = base->GetDirectoryByName(name)) {
        auto removed = base->RemoveDirectory(existing);
        if (!removed) {
            std::cerr << "Could not remove existing base directory " << name << ": "
                      << removed.error().message() << "\n";
            return false;
        }
    }

    auto moved = donor->RemoveDirectory(source);
    if (!moved) {
        std::cerr << "Could not detach donor directory " << name << ": "
                  << moved.error().message() << "\n";
        return false;
    }
    RetargetDirectory(moved.value().get(), base->WzFileParent());
    auto added = base->AddDirectory(std::move(moved.value()));
    if (!added) {
        std::cerr << "Could not add donor directory " << name << " to base: "
                  << added.error().message() << "\n";
        return false;
    }

    std::cout << "Replaced directory: " << name << "\n";
    return true;
}

int main(int argc, char** argv) {
    if (argc != 7) {
        std::cerr << "Usage: everleaf-evan-wz-patcher <base.wz> <base-version> <donor.wz> <donor-version> <copy-spec.txt> <output.wz>\n";
        return 2;
    }

    const fs::path basePath = argv[1];
    const int baseVersion = std::stoi(argv[2]);
    const fs::path donorPath = argv[3];
    const int donorVersion = std::stoi(argv[4]);
    const fs::path specPath = argv[5];
    const fs::path outputPath = argv[6];

    if (!fs::is_regular_file(basePath) || !fs::is_regular_file(donorPath)) {
        std::cerr << "Base or donor WZ is missing.\n";
        return 3;
    }
    if (fs::equivalent(basePath, donorPath)) {
        std::cerr << "Base and donor WZ must be different files.\n";
        return 4;
    }

    std::vector<CopyEntry> entries;
    if (!ParseSpec(specPath, entries)) return 5;

    wz::WzFile baseFile(basePath.string(), baseVersion, wz::WzMapleVersion::GMS);
    wz::WzFile donorFile(donorPath.string(), donorVersion, wz::WzMapleVersion::GMS);

    const auto baseStatus = baseFile.ParseWzFile();
    if (baseStatus != wz::WzFileParseStatus::Success) {
        std::cerr << "Could not parse base WZ: " << wz::GetErrorDescription(baseStatus) << "\n";
        return 6;
    }
    const auto donorStatus = donorFile.ParseWzFile();
    if (donorStatus != wz::WzFileParseStatus::Success) {
        std::cerr << "Could not parse donor WZ: " << wz::GetErrorDescription(donorStatus) << "\n";
        return 7;
    }

    auto* base = baseFile.GetWzDirectory();
    auto* donor = donorFile.GetWzDirectory();
    for (const auto& entry : entries) {
        bool ok = entry.kind == CopyEntry::Kind::Image
            ? ReplaceImage(base, donor, entry.name)
            : ReplaceDirectory(base, donor, entry.name);
        if (!ok) return 8;
    }

    auto saved = baseFile.SaveToDisk(outputPath.string(), false, wz::WzMapleVersion::GMS);
    if (!saved) {
        std::cerr << "Could not save patched WZ: " << saved.error().message() << "\n";
        return 9;
    }

    std::cout << "EverLeaf Evan WZ patch complete: " << outputPath.string() << "\n";
    return 0;
}
