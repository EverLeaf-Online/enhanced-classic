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
#include "wz/WzImageProperty.h"

namespace fs = std::filesystem;

enum class EntryType { Image, Property };
struct Entry { EntryType type; bool onlyIfMissing; std::string path; };

static std::vector<std::string> Split(const std::string& s) {
    std::vector<std::string> out; std::stringstream ss(s); std::string part;
    while (std::getline(ss, part, '/')) if (!part.empty()) out.push_back(part);
    return out;
}

static std::string Join(const std::vector<std::string>& parts, size_t begin, size_t end) {
    std::string out;
    for (size_t i = begin; i < end; ++i) {
        if (!out.empty()) out += '/';
        out += parts[i];
    }
    return out;
}

static bool ReadSpec(const fs::path& p, std::vector<Entry>& entries) {
    std::ifstream f(p); if (!f) return false; std::string line;
    while (std::getline(f,line)) {
        if (!line.empty() && line.back()=='\r') line.pop_back();
        auto first=line.find_first_not_of(" \t"); if(first==std::string::npos || line[first]=='#') continue;
        line.erase(0,first);
        const std::string image="image:";
        const std::string missingImage="missing-image:";
        const std::string property="property:";
        const std::string missingProperty="missing-property:";
        if(line.rfind(image,0)==0) entries.push_back({EntryType::Image,false,line.substr(image.size())});
        else if(line.rfind(missingImage,0)==0) entries.push_back({EntryType::Image,true,line.substr(missingImage.size())});
        else if(line.rfind(property,0)==0) entries.push_back({EntryType::Property,false,line.substr(property.size())});
        else if(line.rfind(missingProperty,0)==0) entries.push_back({EntryType::Property,true,line.substr(missingProperty.size())});
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

static bool ResolveImagePath(wz::WzDirectory* root, const std::vector<std::string>& parts,
                             bool createDirs, wz::WzImage*& image, size_t& imageIndex) {
    image = nullptr; imageIndex = 0;
    for(size_t i=0;i<parts.size();++i) {
        if(parts[i].size() >= 4 && parts[i].substr(parts[i].size()-4)==".img") {
            std::vector<std::string> dirs(parts.begin(),parts.begin()+i);
            auto* dir=ResolveDir(root,dirs,createDirs);
            if(!dir) return false;
            image=dir->GetImageByName(parts[i]);
            imageIndex=i;
            return image!=nullptr;
        }
    }
    return false;
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

static wz::WzImageProperty* ResolveProperty(wz::WzImage* image, const std::vector<std::string>& parts,
                                            size_t imageIndex, size_t endExclusive) {
    if(endExclusive <= imageIndex + 1) return nullptr;
    return image->GetFromPath(Join(parts,imageIndex+1,endExclusive));
}

static bool CopyProperty(wz::WzDirectory* baseRoot, wz::WzDirectory* donorRoot, const Entry& e) {
    auto parts=Split(e.path);
    wz::WzImage *baseImage=nullptr,*donorImage=nullptr; size_t baseIdx=0,donorIdx=0;
    if(!ResolveImagePath(baseRoot,parts,false,baseImage,baseIdx)) { std::cerr << "Base image missing for property " << e.path << "\n"; return false; }
    if(!ResolveImagePath(donorRoot,parts,false,donorImage,donorIdx)) { std::cerr << "Donor image missing for property " << e.path << "\n"; return false; }
    if(baseIdx!=donorIdx || parts.size()!=baseIdx+2) {
        std::cerr << "Only top-level IMG properties are supported: " << e.path << "\n";
        return false;
    }
    if(!EnsureParsed(baseImage,"base/"+Join(parts,0,baseIdx+1))) return false;
    if(!EnsureParsed(donorImage,"donor/"+Join(parts,0,donorIdx+1))) return false;

    const std::string propName=parts.back();
    auto* source=donorImage->GetFromPath(propName);
    if(!source) { std::cerr << "Donor property missing " << e.path << "\n"; return false; }
    auto* existing=baseImage->GetFromPath(propName);
    if(existing && e.onlyIfMissing) { std::cout << "Property already present, preserved: " << e.path << "\n"; return true; }

    if(existing) {
        auto removed=baseImage->RemoveProperty(existing);
        if(!removed) { std::cerr << "Could not remove existing property " << e.path << ": " << removed.error().message() << "\n"; return false; }
    }
    auto moved=donorImage->RemoveProperty(source);
    if(!moved) { std::cerr << "Could not detach donor property " << e.path << ": " << moved.error().message() << "\n"; return false; }
    auto added=baseImage->AddProperty(std::move(moved.value()));
    if(!added) { std::cerr << "Could not add property " << e.path << ": " << added.error().message() << "\n"; return false; }
    baseImage->SetChanged(true);
    std::cout << (existing?"Replaced property: ":"Added property: ") << e.path << "\n";
    return true;
}

static bool VerifyEntry(wz::WzDirectory* root, const Entry& e) {
    auto parts=Split(e.path);
    if(e.type==EntryType::Image) {
        if(parts.size()<2) return false;
        auto image=parts.back(); parts.pop_back();
        auto* dir=ResolveDir(root,parts,false);
        return dir && dir->GetImageByName(image);
    }
    wz::WzImage* image=nullptr; size_t idx=0;
    if(!ResolveImagePath(root,parts,false,image,idx) || !EnsureParsed(image,"verify/"+e.path)) return false;
    return ResolveProperty(image,parts,idx,parts.size())!=nullptr;
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
    for(const auto& e:entries) {
        const bool ok = e.type==EntryType::Image ? CopyImage(base.GetWzDirectory(),donor.GetWzDirectory(),e)
                                                 : CopyProperty(base.GetWzDirectory(),donor.GetWzDirectory(),e);
        if(!ok) return 6;
    }
    auto saved=base.SaveToDisk(outputPath.string(),false,wz::WzMapleVersion::GMS);
    if(!saved) { std::cerr << "Save failed: " << saved.error().message() << "\n"; return 7; }
    wz::WzFile verify(outputPath.string(),baseVer,wz::WzMapleVersion::GMS);
    if(verify.ParseWzFile()!=wz::WzFileParseStatus::Success) { std::cerr << "Output reparse failed\n"; return 8; }
    for(const auto& e:entries) {
        if(!VerifyEntry(verify.GetWzDirectory(),e)) { std::cerr << "Output missing " << e.path << "\n"; return 9; }
        std::cout << "Verified: " << e.path << "\n";
    }
    return 0;
}
