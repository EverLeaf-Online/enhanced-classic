from pathlib import Path

TARGET = Path("client/ezorsia/ezorsia/MainMain.cpp")


def replace_once(text: str, old: str, new: str) -> str:
    # Safe for repeated CI/package application. Several replacements keep the
    # old marker inside the new text, so prefer the complete replacement check.
    if new in text:
        return text
    count = text.count(old)
    if count == 0:
        raise SystemExit(f"Missing expected client source marker:\n{old}")
    if count != 1:
        raise SystemExit(f"Expected one source marker, found {count}:\n{old}")
    return text.replace(old, new, 1)


text = TARGET.read_text(encoding="utf-8")

text = replace_once(
    text,
    'bool MainMain::ownCashShopFrame = false;',
    'bool MainMain::ownCashShopFrame = true;',
)

anchor = '\tif (!std::filesystem::exists(BfilePath) && !std::filesystem::exists(BfilePath2)) {'
inserted = (
    '\tconst bool preferCommunityUi = reader.GetBoolean("general", "PreferCommunityUI", true);\n'
    + anchor
)
text = replace_once(text, anchor, inserted)

text = replace_once(
    text,
    '\t\tMainMain::EzorsiaV2WzIncluded = true; MainMain::CustomLoginFrame = true; MainMain::usingEzorsiaV2Wz = true; }',
    '\t\tMainMain::EzorsiaV2WzIncluded = true; MainMain::CustomLoginFrame = !preferCommunityUi; MainMain::usingEzorsiaV2Wz = true; }',
)
text = replace_once(
    text,
    '\telse if(std::filesystem::exists(EfilePath2)){ MainMain::EzorsiaV2WzIncluded = true; MainMain::CustomLoginFrame = true; }',
    '\telse if(std::filesystem::exists(EfilePath2)){ MainMain::EzorsiaV2WzIncluded = true; MainMain::CustomLoginFrame = !preferCommunityUi; }',
)
text = replace_once(
    text,
    '\t\t\tMainMain::EzorsiaV2WzIncluded = true; MainMain::CustomLoginFrame = true; MainMain::usingEzorsiaV2Wz = true;',
    '\t\t\tMainMain::EzorsiaV2WzIncluded = true; MainMain::CustomLoginFrame = !preferCommunityUi; MainMain::usingEzorsiaV2Wz = true;',
)
text = replace_once(
    text,
    '\t\t\tMainMain::EzorsiaV2WzIncluded = true; MainMain::CustomLoginFrame = true;\n\t\t}',
    '\t\t\tMainMain::EzorsiaV2WzIncluded = true; MainMain::CustomLoginFrame = !preferCommunityUi;\n\t\t}',
)

resolution_anchor = '\t//Memory::UseVirtuProtect = reader.GetBoolean("general", "UseVirtuProtect", true);'
community_block = (
    '\tif (preferCommunityUi) {\n'
    '\t\t// Keep EverLeaf_UI.wz on disk for compatibility, but do not advertise the\n'
    '\t\t// legacy Ezorsia asset set to the StringPool replacement hook. That hook\n'
    '\t\t// remaps UI/Login.img/Common/frame to the old book-frame canvases whenever\n'
    '\t\t// EzorsiaV2WzIncluded is true, even when CustomLoginFrame is false.\n'
    '\t\tMainMain::EzorsiaV2WzIncluded = false;\n'
    '\t\tMainMain::usingEzorsiaV2Wz = false;\n'
    '\t\tMainMain::CustomLoginFrame = false;\n'
    '\t\tMainMain::ownLoginFrame = false;\n'
    '\t\tMainMain::bigLoginFrame = false;\n'
    '\t\tMainMain::ownCashShopFrame = true;\n'
    '\t}\n'
    + resolution_anchor
)
text = replace_once(text, resolution_anchor, community_block)

text = replace_once(
    text,
    '\tMainMain::ownCashShopFrame = false;',
    '\tMainMain::ownCashShopFrame = preferCommunityUi;',
)

TARGET.write_text(text, encoding="utf-8", newline="\n")
print("Community UI preference transform applied")
