#!/usr/bin/env python3
"""Generate the genuinely manual v180 naming/runtime-review worklist.

Do NOT treat every icon-only missing String.wz ID as needing a human-written name.
EverLeaf already classifies strong system/data families separately in
MISSING_STRING_CLASSIFICATION.json. This tool emits only C_RUNTIME_REVIEW_REQUIRED.
"""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
from classify_missing_strings import load_xml_item_dump, canonical_numeric_id as normalize_id

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target-item",required=True)
    ap.add_argument("--structural-classification",required=True)
    ap.add_argument("--output-csv",required=True)
    ap.add_argument("--ids-file",required=True)
    args=ap.parse_args()

    items=load_xml_item_dump(args.target_item)
    data=json.loads(Path(args.structural_classification).read_text(encoding="utf-8"))
    rows=[]; ids=[]
    for rec in data.get("items",[]):
        if rec.get("tier")!="C_RUNTIME_REVIEW_REQUIRED": continue
        iid=str(rec.get("id")); node=items.get(normalize_id(iid)); ids.append(iid)
        meta=rec.get("metadata",{})
        rows.append({
            "ID":iid,
            "Category":rec.get("category",""),
            "HasIcon":"" if node is None else node.has_icon,
            "HasEmbeddedMetadata":"" if node is None else bool(node.embedded_name or node.embedded_desc),
            "SourceFile":"" if node is None else node.source_file,
            "Reason":rec.get("reason",""),
            "MetadataJson":json.dumps(meta,separators=(",",":"),ensure_ascii=False),
            "SearchQuery":f'"{iid}" MapleStory',
            "Name":"",
            "Desc":"",
            "ReviewStatus":"UNREVIEWED",
        })
    rows.sort(key=lambda r:(r["Category"],int(r["ID"])))
    fields=["ID","Category","HasIcon","HasEmbeddedMetadata","SourceFile","Reason","MetadataJson","SearchQuery","Name","Desc","ReviewStatus"]
    with open(args.output_csv,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    Path(args.ids_file).write_text("\n".join(ids)+("\n" if ids else ""),encoding="utf-8")
    print(json.dumps({"runtimeReviewCount":len(rows),"productionApplyAllowed":False},indent=2))

if __name__=="__main__": main()
