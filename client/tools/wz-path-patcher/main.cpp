#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include "wz/WzDirectory.h"
#include "wz/WzEnums.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"

namespace fs = std::filesystem;

struct Entry { bool onlyIfMissing; std::string path; };

static std::vector<std::string> Split(const std::string& s) {
    std::vector<std::string> out; std::stringstream ss(s); std::string part;
    while (std::getline(ss, part, '/')) if (!part.empty()) out.push_back(part);
    return out;
}

static bool ReadSpec(const fs::path& p, std::vector<Entry>& entries) {
    std::ifstream f(p); if (!f) return false; std::string line;
    while (std::getline(f,line)) {
        if (!line.empty() && line.back()=='\r') line.pop_back();
        auto first=line.find_first_not_of(" \t"); if(first==std::string::npos || line[first]=='#') continue;
        line.erase(0,first);
        const std::string add="image:"; const std::string missing="missing-image:";
        if(line.rfind(add,0)==0) entries.push_back({false,line.substr(add.size())});
        else if(line.rfind(missing,0)==0) entries.push_back({true,line.substr(missing.size())});
        else { std::cerr << "Invalid spec: " << line << "\n"; return false; }
    }
    return !entries.empty();
}

static wz::WzDirectory* ResolveDir(wz::WzDirectory* root, const std::vector<std::string>& parts, bool create) {
    auto* cur=root;
    for(const auto& name:parts) {
        auto* next=cur->GetDirectoryByName(name);
        if(!next && create) {
            auto made=cur->CreateDirectory(name);
            if(!made) { std::cerr << "Could not create directory " << name << ": " << made.error().message() << "\n"; return nullptr; }
            next=made.value();
        }
        if(!next) return nullptr;
        cur=next;
    }
    return cur;
}

static bool EnsureParsed(wz::WzImage* image, const std::string& label) {
    if(!image) return false;
    auto r=image->ParseImage();
    if(!r || !r.value()) { std::cerr << "Could not parse " << label << "\n"; return false; }
    image->SetChanged(true);
    return true;
}

static bool CopyImage(wz::WzDirectory* baseRoot, wz::WzDirectory* donorRoot, const Entry& e) {
    auto parts=Split(e.path);
    if(parts.size()<2 || parts.back().find(".img")==std::string::npos) { std::cerr << "Bad image path " << e.path << "\n"; return false; }
    const std::string imageName=parts.back(); parts.pop_back();
    auto* donorDir=ResolveDir(donorRoot,parts,false);
    auto* baseDir=ResolveDir(baseRoot,parts,true);
    if(!donorDir || !baseDir) { std::cerr << "Missing parent directory for " << e.path << "\n"; return false; }
    auto* source=donorDir->GetImageByName(imageName);
    if(!source) { std::cerr << "Donor missing " << e.path << "\n"; return false; }
    auto* existing=baseDir->GetImageByName(imageName);
    if(existing && e.onlyIfMissing) { std::cout << "Dependency already present, preserved: " << e.path << "\n"; return true; }
    if(!EnsureParsed(source,"donor/"+e.path)) return false;
    if(existing) {
        auto removed=baseDir->RemoveImage(existing);
        if(!removed) { std::cerr << "Could not remove " << e.path << ": " << removed.error().message() << "\n"; return false; }
    }
    auto moved=donorDir->RemoveImage(source);
    if(!moved) { std::cerr << "Could not detach donor " << e.path << ": " << moved.error().message() << "\n"; return false; }
    auto added=baseDir->AddImage(std::move(moved.value()));
    if(!added) { std::cerr << "Could not add " << e.path << ": " << added.error().message() << "\n"; return false; }
    std::cout << (existing?"Replaced: ":"Added: ") << e.path << "\n";
    return true;
}

static bool VerifyPath(wz::WzDirectory* root, const std::string& path) {
    auto parts=Split(path); if(parts.size()<2) return false;
    auto image=parts.back(); parts.pop_back();
    auto* dir=ResolveDir(root,parts,false);
    return dir && dir->GetImageByName(image);
}

int main(int argc,char** argv) {
    if(argc!=7) {
        std::cerr << "Usage: everleaf-wz-path-patcher <base.wz> <base-version> <donor.wz> <donor-version> <spec> <output.wz>\n";
        return 2;
    }
    const fs::path basePath=argv[1], donorPath=argv[3], specPath=argv[5], outputPath=argv[6];
    const int baseVer=std::stoi(argv[2]), donorVer=std::stoi(argv[4]);
    std::vector<Entry> entries; if(!ReadSpec(specPath,entries)) { std::cerr << "Could not read spec\n"; return 3; }
    wz::WzFile base(basePath.string(),baseVer,wz::WzMapleVersion::GMS);
    wz::WzFile donor(donorPath.string(),donorVer,wz::WzMapleVersion::GMS);
    if(base.ParseWzFile()!=wz::WzFileParseStatus::Success) { std::cerr << "Base parse failed\n"; return 4; }
    if(donor.ParseWzFile()!=wz::WzFileParseStatus::Success) { std::cerr << "Donor parse failed\n"; return 5; }
    for(const auto& e:entries) if(!CopyImage(base.GetWzDirectory(),donor.GetWzDirectory(),e)) return 6;
    auto saved=base.SaveToDisk(outputPath.string(),false,wz::WzMapleVersion::GMS);
    if(!saved) { std::cerr << "Save failed: " << saved.error().message() << "\n"; return 7; }
    wz::WzFile verify(outputPath.string(),baseVer,wz::WzMapleVersion::GMS);
    if(verify.ParseWzFile()!=wz::WzFileParseStatus::Success) { std::cerr << "Output reparse failed\n"; return 8; }
    for(const auto& e:entries) {
        if(!VerifyPath(verify.GetWzDirectory(),e.path)) { std::cerr << "Output missing " << e.path << "\n"; return 9; }
        std::cout << "Verified: " << e.path << "\n";
    }
    return 0;
}
