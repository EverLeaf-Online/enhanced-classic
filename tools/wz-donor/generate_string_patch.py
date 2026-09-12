#!/usr/bin/env python3
"""Generate safe String.wz autofill patches from embedded Item.wz metadata.

EverLeaf-specific guardrails:
- Reads directory-based WzComparerR2 exports through classify_missing_strings.py.
- Only writes into String.wz families that actually exist in the v180 donor.
- DOES NOT invent Special.img: v180 cash-package names/descriptions live canonically
  in Item.wz/Special/0910.img, so those entries are audited, not duplicated.
- Production is never touched; output is an isolated patch directory.
"""
from __future__ import annotations
import argparse, csv, json, sys, xml.etree.ElementTree as ET
from pathlib import Path
from classify_missing_strings import load_xml_item_dump, canonical_numeric_id as normalize_id

STRING_TARGETS = {
    "Cash": ("Cash.img", None),
    "Consume": ("Consume.img", None),
    "Etc": ("Etc.img", "Etc"),
    "Install": ("Ins.img", None),
}

def indent(e, level=0):
    pad = "\n" + "  " * level
    if len(e):
        if not e.text or not e.text.strip(): e.text = pad + "  "
        for c in e: indent(c, level + 1)
        if not c.tail or not c.tail.strip(): c.tail = pad
    if level and (not e.tail or not e.tail.strip()): e.tail = pad

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target-item", required=True)
    ap.add_argument("--classification", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--audit-csv", required=True)
    args=ap.parse_args()

    items=load_xml_item_dump(args.target_item)
    rows=list(csv.DictReader(open(args.classification, newline="", encoding="utf-8")))
    selected=[r for r in rows if r.get("HasEmbeddedMetadata","").strip().lower() in ("true","1","yes")]

    out=Path(args.output_dir); out.mkdir(parents=True, exist_ok=True)
    grouped={}; audit=[]
    for r in selected:
        iid=normalize_id(r["ID"]); node=items.get(iid); cat=r.get("Category") or (node.category if node else "")
        if node is None:
            audit.append((r["ID"],cat,"MISSING_ITEM_NODE","","")); continue
        name=node.embedded_name or ""; desc=node.embedded_desc or ""
        target=STRING_TARGETS.get(cat)
        if cat=="Special":
            audit.append((r["ID"],cat,"KEEP_IN_ITEM_WZ_SPECIAL",name,desc)); continue
        if not target:
            audit.append((r["ID"],cat,"UNSUPPORTED_STRING_FAMILY",name,desc)); continue
        if not (name or desc):
            audit.append((r["ID"],cat,"NO_EXTRACTABLE_TEXT",name,desc)); continue
        grouped.setdefault(cat,[]).append((node.node_id,name,desc))
        audit.append((r["ID"],cat,"PATCH_STRING_WZ",name,desc))

    files=[]
    for cat, entries in grouped.items():
        image_name, wrapper=STRING_TARGETS[cat]
        root=ET.Element("imgdir", {"name": image_name})
        parent=root if wrapper is None else ET.SubElement(root,"imgdir",{"name":wrapper})
        for iid,name,desc in sorted(entries,key=lambda x:int(normalize_id(x[0]))):
            n=ET.SubElement(parent,"imgdir",{"name":normalize_id(iid)})
            if name: ET.SubElement(n,"string",{"name":"name","value":name})
            if desc: ET.SubElement(n,"string",{"name":"desc","value":desc})
        indent(root)
        p=out/(image_name+".xml"); ET.ElementTree(root).write(p,encoding="utf-8",xml_declaration=True); files.append(str(p))

    with open(args.audit_csv,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["ID","Category","Action","EmbeddedName","EmbeddedDesc"]); w.writerows(audit)

    from collections import Counter
    counts=Counter(a[2] for a in audit)
    summary={"inputEmbeddedMetadata":len(selected),"actions":dict(counts),"patchFiles":files,"productionApplyAllowed":False}
    (out/"MANIFEST.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2),file=sys.stderr)

if __name__=="__main__": main()
