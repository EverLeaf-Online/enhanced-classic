#include <iostream>
#include <memory>
#include "wz/WzFile.h"
#include "wz/WzDirectory.h"
#include "wz/WzImage.h"
#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzPngProperty.h"
#include "wz/Properties/WzVectorProperty.h"
using namespace wz;
int main(int argc,char**argv) {
 if(argc!=2 && argc!=4) return 2;
 WzFile f(argv[1],83,WzMapleVersion::GMS);
 if(f.ParseWzFile()!=WzFileParseStatus::Success) return 3;
 auto* d=f.GetWzDirectory()->GetDirectoryByName("Back");
 if(!d) d=f.GetWzDirectory()->GetDirectoryByName("back");
 auto* i=d?d->GetImageByName("Login.img"):nullptr;
 if(!i && d)i=d->GetImageByName("login.img");
 if(!i || !i->ParseImage()) return 4;
 auto* p=i->GetFromPath("back/11");
 if(!p || p->PropertyType()!=WzPropertyType::Canvas) return 5;
 auto* c=static_cast<WzCanvasProperty*>(p);
 auto* o=c->GetFromPath("origin");
 if(!o || o->PropertyType()!=WzPropertyType::Vector) return 6;
 auto* v=static_cast<WzVectorProperty*>(o);
 std::cout<<"Background "<<c->PngProperty()->Width()<<"x"<<c->PngProperty()->Height()<<" origin "<<v->X->Value()<<","<<v->Y->Value()<<std::endl;
 if(argc==2) return 0;
 auto png=WzPngProperty::FromPngFile(argv[2],WzPngFormat::Format2);
 if(!png || png.value()->Width()!=1320 || png.value()->Height()!=3240) return 7;
 c->SetPngProperty(std::move(png.value()));
 // 40px horizontal overscan: retain the left edge and shift the scene right
 // by 20px relative to a centered crop of the wider artwork.
 // Origin is inspected and preserved; only the backing artwork is replaced.
 i->SetChanged(true);
 auto result=f.SaveToDisk(argv[3],false,WzMapleVersion::GMS);
 if(!result) {std::cerr<<result.error().message()<<std::endl;return 8;}
 std::cout<<"Saved continuous panorama"<<std::endl;
}
