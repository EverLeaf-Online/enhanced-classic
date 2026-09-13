from pathlib import Path

TARGET = Path("client/native/core/MainMain.cpp")


def replace_once(text: str, old: str, new: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"Missing expected client source marker:\n{old}")
    if count != 1:
        raise SystemExit(f"Expected one source marker, found {count}:\n{old}")
    return text.replace(old, new, 1)


text = TARGET.read_text(encoding="utf-8")

text = replace_once(text, 'bool MainMain::ownCashShopFrame = false;', 'bool MainMain::ownCashShopFrame = true;')

anchor = '\tif (!std::filesystem::exists(BfilePath) && !std::filesystem::exists(BfilePath2)) {'
inserted = '\tconst bool preferCommunityUi = reader.GetBoolean("general", "PreferCommunityUI", true);\n' + anchor
text = replace_once(text, anchor, inserted)

text = replace_once(
    text,
    '\t\tMainMain::EverLeafUiResourcesIncluded = true; MainMain::CustomLoginFrame = true; MainMain::usingEverLeafUiWz = true; }',
    '\t\tMainMain::EverLeafUiResourcesIncluded = true; MainMain::CustomLoginFrame = !preferCommunityUi; MainMain::usingEverLeafUiWz = true; }',
)
text = replace_once(
    text,
    '\telse if(std::filesystem::exists(EfilePath2)){ MainMain::EverLeafUiResourcesIncluded = true; MainMain::CustomLoginFrame = true; }',
    '\telse if(std::filesystem::exists(EfilePath2)){ MainMain::EverLeafUiResourcesIncluded = true; MainMain::CustomLoginFrame = !preferCommunityUi; }',
)
text = replace_once(
    text,
    '\t\t\tMainMain::EverLeafUiResourcesIncluded = true; MainMain::CustomLoginFrame = true; MainMain::usingEverLeafUiWz = true;',
    '\t\t\tMainMain::EverLeafUiResourcesIncluded = true; MainMain::CustomLoginFrame = !preferCommunityUi; MainMain::usingEverLeafUiWz = true;',
)
text = replace_once(
    text,
    '\t\t\tMainMain::EverLeafUiResourcesIncluded = true; MainMain::CustomLoginFrame = true;\n\t\t}',
    '\t\t\tMainMain::EverLeafUiResourcesIncluded = true; MainMain::CustomLoginFrame = !preferCommunityUi;\n\t\t}',
)

resolution_anchor = '\t//Memory::UseVirtuProtect = reader.GetBoolean("general", "UseVirtuProtect", true);'
community_block = (
    '\tif (preferCommunityUi) {\n'
    '\t\t// Keep the compatibility UI package on disk, but do not advertise the\n'
    '\t\t// historical custom frame asset set to the StringPool replacement hook.\n'
    '\t\tMainMain::EverLeafUiResourcesIncluded = false;\n'
    '\t\tMainMain::usingEverLeafUiWz = false;\n'
    '\t\tMainMain::CustomLoginFrame = false;\n'
    '\t\tMainMain::ownLoginFrame = false;\n'
    '\t\tMainMain::bigLoginFrame = false;\n'
    '\t\tMainMain::ownCashShopFrame = true;\n'
    '\t}\n'
    + resolution_anchor
)
text = replace_once(text, resolution_anchor, community_block)

text = replace_once(text, '\tMainMain::ownCashShopFrame = false;', '\tMainMain::ownCashShopFrame = preferCommunityUi;')

TARGET.write_text(text, encoding="utf-8", newline="\n")
print("Community UI preference transform applied")
