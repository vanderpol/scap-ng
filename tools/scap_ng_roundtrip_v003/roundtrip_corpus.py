#!/usr/bin/env python3
"""Run OVAL -> NG fixture -> OVAL semantic round trips across a corpus."""
from __future__ import annotations
import argparse, json, sys, traceback
from pathlib import Path
from lxml import etree as E

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from oval_to_fixture import Converter
from ng_to_oval import build as build_oval
from compare_oval_semantics import compare
from diff_oval_roundtrip import parse as diff_parse, canonical_lines, strip_noise, pretty_lines, write_diff

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--glob",default="**/oval.xml")
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--strict",action="store_true")
    a=ap.parse_args()

    a.out.mkdir(parents=True,exist_ok=True)
    fixtures_dir=a.out/"fixtures"; regen_dir=a.out/"regenerated"
    fixtures_dir.mkdir(exist_ok=True); regen_dir.mkdir(exist_ok=True)

    rows=[]
    files=sorted(a.root.glob(a.glob))
    for idx,source in enumerate(files,1):
        rel=source.relative_to(a.root).as_posix()
        stem=f"{idx:04d}-{source.parent.name}"
        row={"source":rel,"status":"unknown"}
        try:
            data=Converter(source).convert()
            fixture=fixtures_dir/(stem+".json")
            fixture.write_text(json.dumps(data,indent=2)+chr(10),encoding="utf-8")
            row["fixture"]=fixture.relative_to(a.out).as_posix()
        except Exception as exc:
            row.update(status="forward_error",error=f"{type(exc).__name__}: {exc}")
            rows.append(row); print(f"FORWARD_ERROR {rel}: {exc}"); continue

        try:
            tree=build_oval(data)
            regen=regen_dir/(stem+".xml")
            tree.write(regen,encoding="utf-8",xml_declaration=True)
            row["regenerated"]=regen.relative_to(a.out).as_posix()
        except Exception as exc:
            row.update(status="reverse_error",error=f"{type(exc).__name__}: {exc}")
            rows.append(row); print(f"REVERSE_ERROR {rel}: {exc}"); continue

        try:
            diff_dir=a.out/"diffs"/stem
            diff_dir.mkdir(parents=True,exist_ok=True)
            source_tree=diff_parse(source)
            regen_tree=diff_parse(regen)
            raw=write_diff(
                canonical_lines(source_tree),canonical_lines(regen_tree),
                rel,row["regenerated"],diff_dir/"raw-c14n.diff"
            )
            source_norm=strip_noise(diff_parse(source))
            regen_norm=strip_noise(diff_parse(regen))
            normalized=write_diff(
                pretty_lines(source_norm),pretty_lines(regen_norm),
                "source-normalized.xml","regenerated-normalized.xml",
                diff_dir/"normalized-structural.diff"
            )
            (diff_dir/"source-normalized.xml").write_text(
                E.tostring(source_norm,pretty_print=True,encoding="unicode"),
                encoding="utf-8"
            )
            (diff_dir/"regenerated-normalized.xml").write_text(
                E.tostring(regen_norm,pretty_print=True,encoding="unicode"),
                encoding="utf-8"
            )
            row["raw_diff_lines"]=len(raw.splitlines())
            row["normalized_diff_lines"]=len(normalized.splitlines())
            row["diff_dir"]=diff_dir.relative_to(a.out).as_posix()

            source_roots=data["source"].get("root_definition")
            if source_roots is None:
                source_roots=data["source"].get("root_definitions")
            result=compare(source,regen,source_roots,None)
            if result["equal"]:
                row["status"]="pass"
                print(f"PASS {rel}")
            else:
                row["status"]="semantic_mismatch"
                row["comparison"]=result
                print(f"MISMATCH {rel}")
        except Exception as exc:
            row.update(status="compare_error",error=f"{type(exc).__name__}: {exc}")
            print(f"COMPARE_ERROR {rel}: {exc}")
        rows.append(row)

    counts={}
    error_signatures={}
    for row in rows:
        counts[row["status"]]=counts.get(row["status"],0)+1
        if row["status"]!="pass":
            sig=row.get("error") or row["status"]
            # Normalize volatile IDs and numeric suffixes so repeated semantic
            # blockers group together across rule-specific OVAL closures.
            import re
            sig=re.sub(r"oval:[A-Za-z0-9_.-]+:(?:def|tst|obj|ste|var):[A-Za-z0-9_.-]+","<oval-id>",sig)
            sig=re.sub(r"\b\d{4,}\b","<n>",sig)
            key=f"{row['status']}: {sig}"
            error_signatures[key]=error_signatures.get(key,0)+1
    summary={
        "format":"oval-ng-roundtrip-corpus-summary-0.1",
        "source_file_count":len(files),
        "counts":dict(sorted(counts.items())),
        "error_signatures":dict(sorted(error_signatures.items(), key=lambda kv:(-kv[1],kv[0]))),
        "all_pass":counts.get("pass",0)==len(files),
        "xml_diff_summary":{
            "raw_diff_files":sum(1 for x in rows if x.get("raw_diff_lines",0)>0),
            "normalized_diff_files":sum(1 for x in rows if x.get("normalized_diff_lines",0)>0),
            "raw_diff_lines":sum(x.get("raw_diff_lines",0) for x in rows),
            "normalized_diff_lines":sum(x.get("normalized_diff_lines",0) for x in rows),
        },
        "rows":rows,
    }
    (a.out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+chr(10),encoding="utf-8")
    print(json.dumps({
        "source_file_count":len(files),
        "counts":summary["counts"],
        "all_pass":summary["all_pass"],
        "xml_diff_summary":summary["xml_diff_summary"],
    },indent=2))
    if a.strict and not summary["all_pass"]:
        raise SystemExit(1)

if __name__=="__main__": main()
