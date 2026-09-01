#include <cctype>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include <pugixml.hpp>

#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzIntProperty.h"
#include "wz/Properties/WzNullProperty.h"
#include "wz/Properties/WzShortProperty.h"
#include "wz/Properties/WzStringProperty.h"
#include "wz/Properties/WzSubProperty.h"
#include "wz/Properties/WzUOLProperty.h"
#include "wz/Properties/WzVectorProperty.h"
#include "wz/WzDirectory.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"

namespace fs = std::filesystem;

namespace {

std::size_t g_pngCounter = 0;

std::vector<std::uint8_t> DecodeBase64(const std::string& input) {
    static constexpr unsigned char kInvalid = 0xFF;
    static const auto table = [] {
        std::array<unsigned char, 256> result{};
        result.fill(kInvalid);
        const std::string alphabet =
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        for (std::size_t i = 0; i < alphabet.size(); ++i) {
            result[static_cast<unsigned char>(alphabet[i])] = static_cast<unsigned char>(i);
        }
        return result;
    }();

    std::vector<std::uint8_t> output;
    output.reserve(input.size() * 3 / 4);
    std::uint32_t accumulator = 0;
    int bits = 0;
    for (unsigned char ch : input) {
        if (std::isspace(ch)) continue;
        if (ch == '=') break;
        const unsigned char value = table[ch];
        if (value == kInvalid) throw std::runtime_error("invalid base64 character in canvas data");
        accumulator = (accumulator << 6) | value;
        bits += 6;
        if (bits >= 8) {
            bits -= 8;
            output.push_back(static_cast<std::uint8_t>((accumulator >> bits) & 0xFF));
        }
    }
    return output;
}

void Require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}

std::unique_ptr<wz::WzImageProperty> ParseProperty(const pugi::xml_node& node,
                                                   const fs::path& tempDir) {
    const std::string tag = node.name();
    const std::string name = node.attribute("name").as_string();

    if (tag == "imgdir") {
        auto prop = std::make_unique<wz::WzSubProperty>(name);
        for (const auto& child : node.children()) {
            auto added = prop->AddProperty(ParseProperty(child, tempDir));
            Require(added.has_value(), "failed to add imgdir child property: " + name);
        }
        return prop;
    }

    if (tag == "canvas") {
        const auto basedata = node.attribute("basedata");
        Require(basedata, "canvas is missing basedata: " + name);
        const auto pngBytes = DecodeBase64(basedata.as_string());
        Require(!pngBytes.empty(), "canvas basedata decoded empty: " + name);

        const fs::path pngPath = tempDir / ("canvas-" + std::to_string(++g_pngCounter) + ".png");
        {
            std::ofstream stream(pngPath, std::ios::binary);
            Require(static_cast<bool>(stream), "could not create temporary PNG");
            stream.write(reinterpret_cast<const char*>(pngBytes.data()),
                         static_cast<std::streamsize>(pngBytes.size()));
        }

        auto pngResult = wz::WzPngProperty::FromPngFile(pngPath.string());
        std::error_code ignored;
        fs::remove(pngPath, ignored);
        Require(pngResult.has_value(), "libwz could not import canvas PNG: " + name);

        auto prop = std::make_unique<wz::WzCanvasProperty>(name);
        prop->SetPngProperty(std::move(pngResult.value()));
        for (const auto& child : node.children()) {
            auto added = prop->AddProperty(ParseProperty(child, tempDir));
            Require(added.has_value(), "failed to add canvas child property: " + name);
        }
        return prop;
    }

    if (tag == "int") {
        return std::make_unique<wz::WzIntProperty>(name, node.attribute("value").as_int());
    }
    if (tag == "short") {
        return std::make_unique<wz::WzShortProperty>(
            name, static_cast<std::int16_t>(node.attribute("value").as_int()));
    }
    if (tag == "string") {
        return std::make_unique<wz::WzStringProperty>(name, node.attribute("value").as_string());
    }
    if (tag == "uol") {
        return std::make_unique<wz::WzUOLProperty>(name, node.attribute("value").as_string());
    }
    if (tag == "vector") {
        return std::make_unique<wz::WzVectorProperty>(
            name, node.attribute("x").as_int(), node.attribute("y").as_int());
    }
    if (tag == "null") {
        return std::make_unique<wz::WzNullProperty>(name);
    }

    throw std::runtime_error("unsupported Evan XML property type: " + tag);
}

std::unique_ptr<wz::WzImage> ParseImageXml(const fs::path& path, const fs::path& tempDir) {
    pugi::xml_document document;
    const auto result = document.load_file(path.string().c_str(), pugi::parse_default | pugi::parse_eol);
    Require(result, "could not parse XML " + path.string() + ": " + result.description());

    const auto root = document.child("imgdir");
    Require(root, "XML root is not imgdir: " + path.string());
    const std::string name = root.attribute("name").as_string();
    Require(!name.empty(), "XML image has no name: " + path.string());

    auto image = std::make_unique<wz::WzImage>(name);
    for (const auto& child : root.children()) {
        auto added = image->AddProperty(ParseProperty(child, tempDir));
        Require(added.has_value(), "failed to add image property to " + name);
    }
    image->SetChanged(true);
    image->SetParsed(true);
    return image;
}

void AddXmlFiles(wz::WzDirectory* directory,
                 const fs::path& sourceDir,
                 const fs::path& tempDir) {
    Require(fs::is_directory(sourceDir), "missing XML source directory: " + sourceDir.string());
    std::vector<fs::path> files;
    for (const auto& entry : fs::directory_iterator(sourceDir)) {
        if (entry.is_regular_file() && entry.path().extension() == ".xml") {
            files.push_back(entry.path());
        }
    }
    std::sort(files.begin(), files.end());
    Require(!files.empty(), "no XML images found in " + sourceDir.string());
    for (const auto& path : files) {
        auto image = ParseImageXml(path, tempDir);
        const std::string name = image->Name();
        auto added = directory->AddImage(std::move(image));
        Require(added.has_value(), "failed to add image " + name);
        std::cout << "XML donor image: " << name << "\n";
    }
}

void SaveCategory(const fs::path& output,
                  const fs::path& rootImages,
                  const fs::path& nestedImages,
                  const std::string& nestedName,
                  const fs::path& tempDir) {
    wz::WzFile file(84, wz::WzMapleVersion::GMS);
    auto* root = file.GetWzDirectory();
    AddXmlFiles(root, rootImages, tempDir);
    if (!nestedImages.empty()) {
        auto childResult = root->CreateDirectory(nestedName);
        Require(childResult.has_value(), "failed to create donor directory " + nestedName);
        AddXmlFiles(childResult.value(), nestedImages, tempDir);
    }
    auto saved = file.SaveToDisk(output.string(), false, wz::WzMapleVersion::GMS);
    Require(saved.has_value(), "failed to save donor WZ: " + output.string());
    Require(fs::is_regular_file(output) && fs::file_size(output) > 0,
            "saved donor WZ is empty: " + output.string());
}

void SaveSingleImageCategory(const fs::path& output,
                             const std::vector<fs::path>& xmlFiles,
                             const fs::path& tempDir) {
    wz::WzFile file(84, wz::WzMapleVersion::GMS);
    auto* root = file.GetWzDirectory();
    for (const auto& path : xmlFiles) {
        Require(fs::is_regular_file(path), "missing XML source: " + path.string());
        auto image = ParseImageXml(path, tempDir);
        const std::string name = image->Name();
        auto added = root->AddImage(std::move(image));
        Require(added.has_value(), "failed to add image " + name);
    }
    auto saved = file.SaveToDisk(output.string(), false, wz::WzMapleVersion::GMS);
    Require(saved.has_value(), "failed to save donor WZ: " + output.string());
    Require(fs::is_regular_file(output) && fs::file_size(output) > 0,
            "saved donor WZ is empty: " + output.string());
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        std::cerr << "Usage: everleaf-evan-xml-donor-builder <extracted-Evan-dir> <output-dir>\n";
        return 2;
    }

    try {
        const fs::path evanRoot = fs::absolute(argv[1]);
        const fs::path outputDir = fs::absolute(argv[2]);
        Require(fs::is_directory(evanRoot), "missing extracted Evan directory");
        fs::create_directories(outputDir);
        const fs::path tempDir = outputDir / ".png-tmp";
        fs::remove_all(tempDir);
        fs::create_directories(tempDir);

        SaveCategory(outputDir / "Skill.wz",
                     evanRoot / "Skill",
                     evanRoot / "Skill" / "Dragon",
                     "Dragon",
                     tempDir);
        SaveCategory(outputDir / "Character.wz",
                     evanRoot / "Character",
                     evanRoot / "Character" / "Dragon",
                     "Dragon",
                     tempDir);
        SaveSingleImageCategory(outputDir / "UI.wz",
                                {evanRoot / "UI" / "Basic.img.xml",
                                 evanRoot / "UI" / "UIWindow.img.xml"},
                                tempDir);
        SaveSingleImageCategory(outputDir / "String.wz",
                                {evanRoot / "String" / "Skill.img.xml"},
                                tempDir);

        fs::remove_all(tempDir);
        std::cout << "EverLeaf Evan XML donor build: PASS\n";
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Evan XML donor build failed: " << ex.what() << "\n";
        return 1;
    }
}
