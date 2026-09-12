#include <charconv>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

#include "wz/WzDirectory.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"
#include "wz/WzImageProperty.h"
#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzIntProperty.h"
#include "wz/Properties/WzPngProperty.h"
#include "wz/Properties/WzStringProperty.h"
#include "wz/Properties/WzSubProperty.h"
#include "wz/Properties/WzVectorProperty.h"

namespace fs = std::filesystem;

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

bool IsCleanSlashPath(const std::string& value) {
    return !value.empty() && value.front() != '/' && value.back() != '/' &&
           value.find('\\') == std::string::npos &&
           value.find("//") == std::string::npos;
}

bool ParseInt(const std::string& text, int& value) {
    const char* begin = text.data();
    const char* end = begin + text.size();
    const auto parsed = std::from_chars(begin, end, value);
    return parsed.ec == std::errc() && parsed.ptr == end;
}

bool ParseVector(const std::string& text, int& x, int& y) {
    const auto parts = Split(text, ',');
    return parts.size() == 2 && ParseInt(parts[0], x) && ParseInt(parts[1], y);
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
        if (!IsCleanSlashPath(fields[0]) || !fields[0].ends_with(".img")) {
            std::cerr << "invalid WZ image path at line " << lineNumber << "\n";
            return false;
        }
        const auto imageParts = Split(fields[0], '/');
        if (imageParts.empty() || imageParts.back().empty()) {
            std::cerr << "invalid WZ image path at line " << lineNumber << "\n";
            return false;
        }
        for (const auto& segment : imageParts) {
            if (segment.empty() || segment == "." || segment == "..") {
                std::cerr << "invalid WZ image path segment at line " << lineNumber << "\n";
                return false;
            }
        }
        if (!IsCleanSlashPath(fields[1])) {
            std::cerr << "invalid property path at line " << lineNumber << "\n";
            return false;
        }
        const auto propertyParts = Split(fields[1], '/');
        for (const auto& segment : propertyParts) {
            if (segment.empty() || segment == "." || segment == "..") {
                std::cerr << "invalid property path segment at line " << lineNumber << "\n";
                return false;
            }
        }
        if (fields[2] != "string" && fields[2] != "int" &&
            fields[2] != "canvas" && fields[2] != "vector") {
            std::cerr << "unsupported property type at line " << lineNumber << ": " << fields[2] << "\n";
            return false;
        }
        if (fields[2] == "canvas" && fields[3].empty()) {
            std::cerr << "canvas source path is empty at line " << lineNumber << "\n";
            return false;
        }
        int parsedA = 0;
        int parsedB = 0;
        if (fields[2] == "int" && !ParseInt(fields[3], parsedA)) {
            std::cerr << "invalid integer at line " << lineNumber << "\n";
            return false;
        }
        if (fields[2] == "vector" && !ParseVector(fields[3], parsedA, parsedB)) {
            std::cerr << "invalid vector at line " << lineNumber << " (expected x,y)\n";
            return false;
        }

        entries.push_back({
            std::move(fields[0]),
            std::move(fields[1]),
            std::move(fields[2]),
            std::move(fields[3])
        });
    }

    if (entries.empty()) {
        std::cerr << "manifest contains no EverLeaf-owned WZ entries\n";
        return false;
    }
    return true;
}

wz::WzImageProperty* FindDirectChild(
    wz::IPropertyContainer* container,
    const std::string& name) {
    if (!container) return nullptr;
    auto* properties = container->WzProperties();
    if (!properties) return nullptr;
    for (auto* property : *properties) {
        if (property && property->Name() == name) return property;
    }
    return nullptr;
}

wz::IPropertyContainer* AsContainer(wz::WzImageProperty* property) {
    if (!property) return nullptr;
    switch (property->PropertyType()) {
        case wz::WzPropertyType::SubProperty:
            return static_cast<wz::WzSubProperty*>(property);
        case wz::WzPropertyType::Canvas:
            return static_cast<wz::WzCanvasProperty*>(property);
        default:
            return nullptr;
    }
}

wz::IPropertyContainer* EnsureParentContainer(
    wz::WzImage* image,
    const std::vector<std::string>& pathParts) {
    if (!image || pathParts.empty()) return nullptr;

    wz::IPropertyContainer* container = image;
    for (size_t i = 0; i + 1 < pathParts.size(); ++i) {
        const std::string& name = pathParts[i];
        wz::WzImageProperty* existing = FindDirectChild(container, name);
        if (existing) {
            container = AsContainer(existing);
            if (!container) {
                std::cerr << "property path collides with non-container node: " << name << "\n";
                return nullptr;
            }
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

fs::path ResolveSourcePath(const fs::path& manifestPath, const std::string& value) {
    fs::path source(value);
    if (source.is_absolute()) return source.lexically_normal();
    return (manifestPath.parent_path() / source).lexically_normal();
}

bool AddEntry(
    wz::WzImage* image,
    const ManifestEntry& entry,
    const fs::path& manifestPath) {
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

    if (entry.type == "int") {
        int value = 0;
        if (!ParseInt(entry.value, value)) return false;
        return parent->AddProperty(
            std::make_unique<wz::WzIntProperty>(leaf, value)).has_value();
    }

    if (entry.type == "vector") {
        int x = 0;
        int y = 0;
        if (!ParseVector(entry.value, x, y)) return false;
        return parent->AddProperty(
            std::make_unique<wz::WzVectorProperty>(leaf, x, y)).has_value();
    }

    const fs::path sourcePath = ResolveSourcePath(manifestPath, entry.value);
    std::error_code fileError;
    if (!fs::is_regular_file(sourcePath, fileError) || fileError) {
        std::cerr << "canvas PNG is missing: " << sourcePath.string() << "\n";
        return false;
    }
    auto png = wz::WzPngProperty::FromPngFile(
        sourcePath.string(), wz::WzPngFormat::Format2);
    if (!png.has_value()) {
        std::cerr << "failed to encode canvas PNG: " << sourcePath.string() << "\n";
        return false;
    }
    auto canvas = std::make_unique<wz::WzCanvasProperty>(leaf);
    canvas->SetPngProperty(std::move(png.value()));
    return parent->AddProperty(std::move(canvas)).has_value();
}

wz::WzDirectory* EnsureDirectoryPath(
    wz::WzDirectory* root,
    const std::vector<std::string>& imageParts) {
    if (!root || imageParts.empty()) return nullptr;
    wz::WzDirectory* directory = root;
    for (size_t i = 0; i + 1 < imageParts.size(); ++i) {
        const std::string& name = imageParts[i];
        wz::WzDirectory* child = directory->GetDirectoryByName(name);
        if (!child) {
            auto created = directory->CreateDirectory(name);
            if (!created.has_value() || !created.value()) {
                std::cerr << "failed to create WZ directory: " << name << "\n";
                return nullptr;
            }
            child = created.value();
        }
        directory = child;
    }
    return directory;
}

wz::WzImage* GetOrCreateImage(
    wz::WzDirectory* root,
    const std::string& imagePath) {
    const auto parts = Split(imagePath, '/');
    if (parts.empty()) return nullptr;
    wz::WzDirectory* directory = EnsureDirectoryPath(root, parts);
    if (!directory) return nullptr;

    const std::string& imageName = parts.back();
    if (auto* existing = directory->GetImageByName(imageName)) return existing;
    auto created = directory->CreateImage(imageName);
    return created.has_value() ? created.value() : nullptr;
}

wz::WzImage* FindImage(
    wz::WzDirectory* root,
    const std::string& imagePath) {
    const auto parts = Split(imagePath, '/');
    if (!root || parts.empty()) return nullptr;

    wz::WzDirectory* directory = root;
    for (size_t i = 0; i + 1 < parts.size(); ++i) {
        directory = directory->GetDirectoryByName(parts[i]);
        if (!directory) return nullptr;
    }
    return directory->GetImageByName(parts.back());
}

bool BuildWz(
    const std::vector<ManifestEntry>& entries,
    const fs::path& manifestPath,
    const std::string& outputPath) {
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
            image = GetOrCreateImage(root, entry.image);
            if (!image) {
                std::cerr << "failed to create WZ image: " << entry.image << "\n";
                return false;
            }
            images.emplace(entry.image, image);
        }

        if (!AddEntry(image, entry, manifestPath)) {
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

bool VerifyEntry(wz::WzImageProperty* property, const ManifestEntry& entry) {
    if (!property) return false;

    if (entry.type == "string") {
        return property->PropertyType() == wz::WzPropertyType::String &&
               property->GetString() == entry.value;
    }
    if (entry.type == "int") {
        int expected = 0;
        return ParseInt(entry.value, expected) &&
               property->PropertyType() == wz::WzPropertyType::Int &&
               property->GetInt() == expected;
    }
    if (entry.type == "vector") {
        int expectedX = 0;
        int expectedY = 0;
        if (!ParseVector(entry.value, expectedX, expectedY) ||
            property->PropertyType() != wz::WzPropertyType::Vector) {
            return false;
        }
        auto* vector = static_cast<wz::WzVectorProperty*>(property);
        return vector->X && vector->Y &&
               vector->X->GetInt() == expectedX &&
               vector->Y->GetInt() == expectedY;
    }
    if (property->PropertyType() != wz::WzPropertyType::Canvas) return false;
    auto* canvas = static_cast<wz::WzCanvasProperty*>(property);
    auto* png = canvas->PngProperty();
    return png && png->Width() > 0 && png->Height() > 0;
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
            image = FindImage(root, entry.image);
            if (!image) {
                std::cerr << "verification missing image: " << entry.image << "\n";
                return false;
            }
            auto parsed = image->ParseImage();
            if (!parsed.has_value() || !parsed.value()) {
                std::cerr << "verification could not parse image: " << entry.image << "\n";
                return false;
            }
            parsedImages.emplace(entry.image, image);
        }

        wz::WzImageProperty* property = image->GetFromPath(entry.path);
        if (!VerifyEntry(property, entry)) {
            std::cerr << "verification mismatch: " << entry.image << '/' << entry.path << "\n";
            return false;
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

    const fs::path manifestPath = fs::path(argv[1]).lexically_normal();
    std::vector<ManifestEntry> entries;
    if (!ReadManifest(manifestPath.string(), entries)) return 3;
    if (!BuildWz(entries, manifestPath, argv[2])) return 4;
    if (!VerifyWz(entries, argv[2])) return 5;

    std::cout << "EverLeaf_Custom.wz built and verified from "
              << entries.size() << " EverLeaf-owned manifest entries\n";
    return 0;
}
