// Reuse the existing validated WZ traversal and canvas replacement helpers.
#define main legacy_patcher_main
#include "main.cpp"
#undef main
#include "wz/Properties/WzVectorProperty.h"
static bool Export(wz::WzImageProperty* p,const std::string& path){
 if(!p)return false;
 if(p->PropertyType()==wz::WzPropertyType::Canvas)
  return bool(static_cast<wz::WzCanvasProperty*>(p)->PngProperty()->SaveToFile(path));
 if(p->PropertyType()==wz::WzPropertyType::SubProperty){
  for(auto*c:*static_cast<wz::WzSubProperty*>(p)->WzProperties())if(Export(c,path))return true;
 }
 if(p->PropertyType()==wz::WzPropertyType::UOL)return Export(ResolveUolProperty(static_cast<wz::WzUOLProperty*>(p)),path);
 return false;
}
int main(int argc,char**argv){
 if(argc!=5)return 2; // mode (map/ui/verify-map/verify-ui), input, art/export directory, output
 std::string mode=argv[1];fs::path art=argv[3];
 wz::WzFile f(argv[2],83,wz::WzMapleVersion::GMS);
 if(f.ParseWzFile()!=wz::WzFileParseStatus::Success)return 3;
 if(mode=="map"||mode=="verify-map"){
  auto*b=FindLoginImage(FindDirectory(f.GetWzDirectory(),"back","Back"));
  auto*o=FindLoginImage(FindDirectory(f.GetWzDirectory(),"obj","Obj"));
  if(!b||!o||!b->ParseImage()||!o->ParseImage())return 4;
  auto*p=b->GetFromPath("back/11");
  if(!p||p->PropertyType()!=wz::WzPropertyType::Canvas)return 5;
  auto*c=static_cast<wz::WzCanvasProperty*>(p);
  auto*v=c->GetFromPath("origin");
  if(!v||v->PropertyType()!=wz::WzPropertyType::Vector)return 6;
  auto*origin=static_cast<wz::WzVectorProperty*>(v);
  if(mode=="verify-map"){
   std::cout<<c->PngProperty()->Width()<<"x"<<c->PngProperty()->Height()<<" origin "<<origin->X->Value()<<","<<origin->Y->Value()<<std::endl;
   if(c->PngProperty()->Width()!=1400||c->PngProperty()->Height()!=3240||origin->X->Value()!=636||origin->Y->Value()!=2880)return 7;
   return Export(o->GetFromPath("Title/signboard"),(art/"signboard-roundtrip.png").string())&&Export(o->GetFromPath("Title/logo"),(art/"logo-roundtrip.png").string())?0:8;
  }
  if(!PatchRequiredPath(b,"back/11",art/"background.png")||!PatchRequiredPath(o,"Title/logo",art/"logo.png")||!PatchRequiredPath(o,"Title/signboard",art/"signboard.png"))return 9;
  origin->X->SetValue(636); // Add 40px coverage on each side, retaining scene center.
 }else{
  auto*i=FindRootImage(f.GetWzDirectory(),"login.img","Login.img");
  if(!i||!i->ParseImage())return 10;
  const std::vector<std::pair<std::string,std::string>> controls={{"BtLogin","login"},{"BtLoginIDSave","save-id"},{"BtLoginIDLost","find-id"},{"BtPasswdLost","reset-password"},{"BtNew","register"},{"BtHomePage","homepage"},{"BtQuit","quit"}};
  for(const auto&[node,asset]:controls)for(const auto&state:{"normal","mouseOver","pressed","disabled"}){
   std::string path="Title/"+node+"/"+state;
   if(mode=="verify-ui"){
    if(!Export(i->GetFromPath(path),(art/(asset+"-"+state+"-roundtrip.png")).string()))return 11;
   }else if(!PatchRequiredPath(i,path,art/(asset+"-"+state+".png")))return 12;
  }
  if(mode=="verify-ui")return 0;
 }
 auto r=f.SaveToDisk(argv[4],false,wz::WzMapleVersion::GMS);
 if(!r){std::cerr<<r.error().message()<<std::endl;return 13;}
 return 0;
}
