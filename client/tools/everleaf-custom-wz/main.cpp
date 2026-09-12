#include <charconv>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

#include "wz/WzDirectory.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"
#include "wz/WzImageProperty.h"
#include "wz/Properties/WzIntProperty.h"
#include "wz/Properties/WzStringProperty.h"
#include "wz/Properties/WzSubProperty.h"

namespace {

constexpr short kEverLeafWzVersion = 83;

struct ManifestEntry {
    std::string image;
    std::string path;
    std::string type;
    std::string value;
};

std::vector<std::string> Split(const std::string& value, char delimiter) {
    std::vector<std::string> parts;
    size_t start = 0;
    while (true) {
        const size_t end = value.find(delimiter, start);
        parts.push_back(value.substr(start, end == std::string::npos ? end : end - start));
        if (end == std::string::npos) break;
        start = end + 1;
    }
    return parts;
}

bool ReadManifest(const std::string& path, std::vector<ManifestEntry>& entries) {
    std::ifstream input(path);
    if (!input) {
        std::cerr << "unable to open manifest: " << path << "\n";
        return false;
    }

    std::string line;
    size_t lineNumber = 0;
    while (std::getline(input, line)) {
        ++lineNumber;
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty() || line[0] == '#') continue;

        auto fields = Split(line, '\t');
        if (fields.size() != 4 || fields[0].empty() || fields[1].empty() || fields[2].empty()) {
            std::cerr << "invalid manifest row at line " << lineNumber << "\n";
            return false;
        }
        if (fields[0].find('/') != std::string::npos || fields[0].find('\\') != std::string::npos) {
            std::cerr << "image names cannot contain path separators at line " << lineNumber << "\n";
            return false;
        }
        if (!fields[0].ends_with(".img")) {
            std::cerr << "image must end with .img at line " << lineNumber << "\n";
            return false;
        }
        if (fields[1].front() == '/' || fields[1].back() == '/' || fields[1].find("//") != std::string::npos) {
            std::cerr << "invalid property path at line " << lineNumber << "\n";
            return false;
        }
        if (fields[2] != "string" && fields[2] != "int") {
            std::cerr << "unsupported property type at line " << lineNumber << ": " << fields[2] << "\n";
            return false;
        }
        entries.push_back({std::move(fields[0]), std::move(fields[1]), std::move(fields[2]), std::move(fields[3])});
    }

    if (entries.empty()) {
        std::cerr << "manifest contains no EverLeaf-owned WZ entries\n";
        return false;
    }
    return true;
}

wz::WzImageProperty* FindDirectChild(wz::IPropertyContainer* container, const std::string& name) {
    if (!container) return nullptr;
    auto* properties = container->WzProperties();
    if (!properties) return nullptr;
    for (auto* property : *properties) {
        if (property && property->Name() == name) return property;
    }
    return nullptr;
}

wz::IPropertyContainer* EnsureParentContainer(
    wz::WzImage* image,
    const std::vector<std::string>& pathParts) {
    if (!image || pathParts.empty()) return nullptr;

    wz::IPropertyContainer* container = image;
    for (size_t i = 0; i + 1 < pathParts.size(); ++i) {
        const std::string& name = pathParts[i];
        if (name.empty()) return nullptr;

        wz::WzImageProperty* existing = FindDirectChild(container, name);
        if (existing) {
            if (existing->PropertyType() != wz::WzPropertyType::SubProperty) {
                std::cerr << "property path collides with non-container node: " << name << "\n";
                return nullptr;
            }
            container = static_cast<wz::WzSubProperty*>(existing);
            continue;
        }

        auto sub = std::make_unique<wz::WzSubProperty>(name);
        wz::WzSubProperty* raw = sub.get();
        if (!container->AddProperty(std::move(sub)).has_value()) {
            std::cerr << "failed to create property container: " << name << "\n";
            return nullptr;
        }
        container = raw;
    }
    return container;
}

bool AddEntry(wz::WzImage* image, const ManifestEntry& entry) {
    auto parts = Split(entry.path, '/');
    if (parts.empty() || parts.back().empty()) return false;

    wz::IPropertyContainer* parent = EnsureParentContainer(image, parts);
    if (!parent) return false;

    const std::string& leaf = parts.back();
    if (FindDirectChild(parent, leaf)) {
        std::cerr << "duplicate property path in manifest: " << entry.image << '/' << entry.path << "\n";
        return false;
    }

    if (entry.type == "string") {
        return parent->AddProperty(
            std::make_unique<wz::WzStringProperty>(leaf, entry.value)).has_value();
    }

    int value = 0;
    const char* begin = entry.value.data();
    const char* end = begin + entry.value.size();
    const auto parsed = std::from_chars(begin, end, value);
    if (parsed.ec != std::errc() || parsed.ptr != end) {
        std::cerr << "invalid integer value: " << entry.value << "\n";
        return false;
    }
    return parent->AddProperty(
        std::make_unique<wz::WzIntProperty>(leaf, value)).has_value();
}

bool BuildWz(const std::vector<ManifestEntry>& entries, const std::string& outputPath) {
    wz::WzFile output(kEverLeafWzVersion, wz::WzMapleVersion::GMS);
    wz::WzDirectory* root = output.GetWzDirectory();
    if (!root) {
        std::cerr << "libwz did not create a root directory\n";
        return false;
    }

    std::unordered_map<std::string, wz::WzImage*> images;
    for (const auto& entry : entries) {
        wz::WzImage* image = nullptr;
        const auto found = images.find(entry.image);
        if (found != images.end()) {
            image = found->second;
        } else {
            auto created = root->CreateImage(entry.image);
            if (!created.has_value() || !created.value()) {
                std::cerr << "failed to create image: " << entry.image << "\n";
                return false;
            }
            image = created.value();
            images.emplace(entry.image, image);
        }

        if (!AddEntry(image, entry)) {
            std::cerr << "failed to add manifest entry: " << entry.image << '/' << entry.path << "\n";
            return false;
        }
    }

    auto saved = output.SaveToDisk(outputPath, false, wz::WzMapleVersion::GMS);
    if (!saved.has_value()) {
        std::cerr << "failed to save EverLeaf custom WZ\n";
        return false;
    }
    return true;
}

bool VerifyWz(const std::vector<ManifestEntry>& entries, const std::string& outputPath) {
    wz::WzFile verify(outputPath, kEverLeafWzVersion, wz::WzMapleVersion::GMS);
    if (verify.ParseWzFile() != wz::WzFileParseStatus::Success) {
        std::cerr << "built WZ did not parse as v83 GMS\n";
        return false;
    }

    wz::WzDirectory* root = verify.GetWzDirectory();
    if (!root) return false;

    std::unordered_map<std::string, wz::WzImage*> parsedImages;
    for (const auto& entry : entries) {
        wz::WzImage* image = nullptr;
        const auto found = parsedImages.find(entry.image);
        if (found != parsedImages.end()) {
            image = found->second;
        } else {
            image = root->GetImageByName(entry.image);
            if (!image) {
                std::cerr << "verification missing image: " << entry.image << "\n";
                return false;
            }
            auto parsed = image->ParseImage();
            if (!parsed.has_value()) {
                std::cerr << "verification could not parse image: " << entry.image << "\n";
                return false;
            }
            parsedImages.emplace(entry.image, image);
        }

        wz::WzImageProperty* property = image->GetFromPath(entry.path);
        if (!property) {
            std::cerr << "verification missing property: " << entry.image << '/' << entry.path << "\n";
            return false;
        }
        if (entry.type == "string") {
            if (property->PropertyType() != wz::WzPropertyType::String || property->GetString() != entry.value) {
                std::cerr << "verification string mismatch: " << entry.image << '/' << entry.path << "\n";
                return false;
            }
        } else {
            int expected = 0;
            const char* begin = entry.value.data();
            const char* end = begin + entry.value.size();
            const auto parsed = std::from_chars(begin, end, expected);
            if (parsed.ec != std::errc() || parsed.ptr != end ||
                property->PropertyType() != wz::WzPropertyType::Int ||
                property->GetInt() != expected) {
                std::cerr << "verification integer mismatch: " << entry.image << '/' << entry.path << "\n";
                return false;
            }
        }
    }
    return true;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "usage: everleaf-custom-wz-builder <manifest.tsv> <EverLeaf_Custom.wz>\n";
        return 2;
    }

    std::vector<ManifestEntry> entries;
    if (!ReadManifest(argv[1], entries)) return 3;
    if (!BuildWz(entries, argv[2])) return 4;
    if (!VerifyWz(entries, argv[2])) return 5;

    std::cout << "EverLeaf_Custom.wz built and verified from "
              << entries.size() << " EverLeaf-owned manifest entries\n";
    return 0;
}
