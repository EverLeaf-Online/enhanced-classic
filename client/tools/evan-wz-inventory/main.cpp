#include <iostream>
#include <string>
#include <vector>
#include "wz/Properties/WzCanvasProperty.h"
#include "wz/Properties/WzSubProperty.h"
#include "wz/WzDirectory.h"
#include "wz/WzFile.h"
#include "wz/WzImage.h"
#include "wz/WzImageProperty.h"

static void PrintRoot(const char* label, wz::WzDirectory* root) {
  std::cout << "### " << label << " root directories\n";
  for (auto* d : root->WzDirectories()) std::cout << "DIR " << d->Name() << "\n";
  std::cout << "### " << label << " root images\n";
  for (auto* i : root->WzImages()) std::cout << "IMG " << i->Name() << "\n";
}

static bool Parse(wz::WzImage* image) {
  if (!image) return false;
  auto r = image->ParseImage();
  return r && r.value();
}

static void PrintChildren(const std::string& label, wz::WzImageProperty* prop) {
  std::cout << "### " << label << "\n";
  if (!prop) { std::cout << "MISSING\n"; return; }
  wz::WzPropertyCollection* children = nullptr;
  if (prop->PropertyType() == wz::WzPropertyType::SubProperty) {
    children = static_cast<wz::WzSubProperty*>(prop)->WzProperties();
  } else if (prop->PropertyType() == wz::WzPropertyType::Canvas) {
    children = static_cast<wz::WzCanvasProperty*>(prop)->WzProperties();
  }
  if (!children) {
    std::cout << "PRESENT type=" << static_cast<int>(prop->PropertyType()) << "\n";
    return;
  }
  for (auto* child : *children) {
    std::cout << "PROP " << child->Name() << " type=" << static_cast<int>(child->PropertyType()) << "\n";
  }
}

static void PrintImageChildren(const std::string& label, wz::WzImage* image) {
  std::cout << "### " << label << "\n";
  if (!image || !Parse(image)) { std::cout << "MISSING_OR_UNPARSEABLE\n"; return; }
  for (auto* child : *image->WzProperties()) {
    std::cout << "PROP " << child->Name() << " type=" << static_cast<int>(child->PropertyType()) << "\n";
  }
}

static void CheckPath(const std::string& label, wz::WzImage* image, const std::string& path) {
  std::cout << "CHECK " << label << " " << (image && image->GetFromPath(path) ? "PRESENT" : "MISSING") << "\n";
}

int main(int argc, char** argv) {
  if (argc != 5) {
    std::cerr << "Usage: everleaf-evan-wz-inventory <Character.wz> <Skill.wz> <String.wz> <UI.wz>\n";
    return 2;
  }
  wz::WzFile character(argv[1], 83, wz::WzMapleVersion::GMS);
  wz::WzFile skill(argv[2], 83, wz::WzMapleVersion::GMS);
  wz::WzFile strings(argv[3], 83, wz::WzMapleVersion::GMS);
  wz::WzFile ui(argv[4], 83, wz::WzMapleVersion::GMS);
  for (auto* f : std::vector<wz::WzFile*>{&character,&skill,&strings,&ui}) {
    if (f->ParseWzFile() != wz::WzFileParseStatus::Success) {
      std::cerr << "WZ parse failed\n"; return 3;
    }
  }
  auto* cr=character.GetWzDirectory(); auto* sr=skill.GetWzDirectory();
  auto* strr=strings.GetWzDirectory(); auto* ur=ui.GetWzDirectory();
  PrintRoot("Character", cr); PrintRoot("Skill", sr); PrintRoot("String", strr); PrintRoot("UI", ur);

  auto* cDragon=cr->GetDirectoryByName("Dragon");
  std::cout << "CHECK Character/Dragon " << (cDragon?"PRESENT":"MISSING") << "\n";
  if (cDragon) for (auto* i:cDragon->WzImages()) std::cout << "DRAGON_CHARACTER_IMG " << i->Name() << "\n";
  auto* sDragon=sr->GetDirectoryByName("Dragon");
  std::cout << "CHECK Skill/Dragon " << (sDragon?"PRESENT":"MISSING") << "\n";
  if (sDragon) for (auto* i:sDragon->WzImages()) std::cout << "DRAGON_SKILL_IMG " << i->Name() << "\n";

  const std::vector<std::string> jobs={"2001.img","2200.img","2210.img","2211.img","2212.img","2213.img","2214.img","2215.img","2216.img","2217.img","2218.img"};
  for (const auto& j:jobs) std::cout << "CHECK Skill/" << j << " " << (sr->GetImageByName(j)?"PRESENT":"MISSING") << "\n";

  auto* body=cr->GetImageByName("00002000.img");
  std::cout << "CHECK Character/00002000.img " << (body?"PRESENT":"MISSING") << "\n";
  if (Parse(body)) {
    const std::vector<std::string> acts={"dragonStrike","dragonSpark","dragonIceBreathe","dragonShield","dragonFury","dragonFly","dragonAura","dragonSkin","dragonThrust","dragonBreathe"};
    for (const auto& a:acts) CheckPath("Character/00002000.img/"+a, body, a);
  }

  auto* skillString=strr->GetImageByName("Skill.img");
  std::cout << "CHECK String/Skill.img " << (skillString?"PRESENT":"MISSING") << "\n";
  if (Parse(skillString)) {
    for (const auto& id: std::vector<std::string>{"22171003","22171005","22000000","22181000"}) CheckPath("String/Skill.img/"+id, skillString, id);
  }

  auto* uiwindow=ur->GetImageByName("UIWindow.img");
  std::cout << "CHECK UI/UIWindow.img " << (uiwindow?"PRESENT":"MISSING") << "\n";
  if (Parse(uiwindow)) {
    CheckPath("UI/UIWindow.img/SkillEx", uiwindow, "SkillEx");
    CheckPath("UI/UIWindow.img/SkillEx/Dragon", uiwindow, "SkillEx/Dragon");
    PrintChildren("UIWindow SkillEx children", uiwindow->GetFromPath("SkillEx"));
  }
  auto* basic=ur->GetImageByName("Basic.img");
  std::cout << "CHECK UI/Basic.img " << (basic?"PRESENT":"MISSING") << "\n";
  PrintImageChildren("UI Basic top-level children", basic);
  return 0;
}
