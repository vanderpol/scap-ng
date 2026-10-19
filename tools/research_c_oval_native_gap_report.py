#!/usr/bin/env python3
"""Refs #245: source-accounted native 0.4-C conversion gap report.

Summarizes actual pinned original Self-Assertion native C conversion.
Research triage, not a conversion, compatibility claim, or scanner result.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
import argparse
import json
import re

ORIGINAL="https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/"
CODE="https://github.com/vanderpol/scap-ng/blob/main/tools/research_c_original_oval_to_authored_c.py"
SOURCE_PATH=re.compile(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+\.xml$")
REASON=re.compile(r"^[A-Z][A-Z0-9_]*")

def gap_report(manifest, *, min_expected_total=None):
    if not isinstance(manifest,dict) or manifest.get("stage")!=(
        "SOURCE_BACKED_NATIVE_C_SUBSET_NOT_SCANNER_PARITY"
    ):
        raise ValueError("untrusted native C source manifest")
    converted=manifest.get("native_C_converted")
    unsupported=manifest.get("unsupported")
    if not isinstance(converted,list) or not isinstance(unsupported,list):
        raise ValueError("every original Definition requires explicit disposition")
    source_total=manifest.get("A_compatible_Definitions_seen")
    if (type(source_total) is not int or source_total<1 or
        len(converted)!=manifest.get("native_C_Definitions") or
        len(unsupported)!=manifest.get("source_compatible_not_yet_native_C") or
        source_total!=len(converted)+len(unsupported)):
        raise ValueError("source Definition coverage mismatch")
    if min_expected_total is not None and source_total!=min_expected_total:
        raise ValueError("source corpus total differs from pinned baseline")
    seen=set()
    by_reason=defaultdict(list)
    for status,rows in (("converted",converted),("unsupported",unsupported)):
        for entry in rows:
            if not isinstance(entry,dict):
                raise ValueError("malformed original source disposition")
            path=entry.get("file")
            did=entry.get("definition_id")
            if (type(path) is not str or not SOURCE_PATH.fullmatch(path)
                or type(did) is not str or not did.startswith("oval:")):
                raise ValueError("unverifiable source Definition or XML path")
            identity=(path,did)
            if identity in seen:
                raise ValueError("one source Definition counted more than once")
            seen.add(identity)
            if status=="unsupported":
                reason=entry.get("reason")
                if type(reason) is not str or not reason.strip():
                    raise ValueError("unsupported Definition without explicit reason")
                group=REASON.match(reason)
                if not group:
                    raise ValueError("unsupported reason lacks machine-readable category")
                by_reason[group.group(0)].append(entry)
    lines=[
        "# Original OVAL Self-Assertion: 0.4-C native-conversion blockers",
        "",
        "**Generated from the checked, version-pinned source manifest.**",
        "This is not proof of OVAL scanner runtime parity.",
        "",
        f"- Pinned source-compatible Definitions accounted for: **{source_total}**",
        f"- Native 0.4-C authoring conversions in research subset: **{len(converted)}**",
        f"- Source-compatible but not natively compiled: **{len(unsupported)}**",
        "- Five source-invalid/deprecated original OVAL Definitions excluded from this 162-Definition baseline.",
        "",
        "## Leading fail-closed reasons",
        "",
        "| Unsupported category | Definitions | Pinned original OVAL examples |",
        "| --- | ---: | --- |",
    ]
    for reason,items in sorted(by_reason.items(),key=lambda kv:(-len(kv[1]),kv[0])):
        links=[]
        for item in sorted(items,key=lambda x:(x["file"],x["definition_id"]))[:3]:
            label=item["file"]
            links.append(f"[{label}]({ORIGINAL}{label})")
        lines.append(f"| {chr(96)}{reason}{chr(96)} | {len(items)} | {', '.join(links)} |")
    lines += [
        "",
        "## Limits of this histogram",
        "",
        "Each category is the **first rejected construct** encountered by the "
        "bounded native authoring compiler. A Definition may contain additional "
        "unsupported features behind the first reason. This is NOT an exhaustive "
        "OVAL feature-frequency audit.",
        "",
        f"Compiler: [native C conversion adapter]({CODE}). "
        "The 0.3 source round-trip is tracked separately. Counts exclude "
        "the Set/Filter/Variable and Apache hybrid research adapters until "
        "one unified C grammar passes its full source and runtime gates.",
        "",
    ]
    return {"total":source_total,"converted":len(converted),
            "unsupported":len(unsupported),
            "categories":{k:len(v) for k,v in sorted(by_reason.items())},
            "markdown":"\n".join(lines)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--expected-total",type=int)
    args=ap.parse_args()
    report=gap_report(json.loads(args.manifest.read_text(encoding="utf-8")),
                      min_expected_total=args.expected_total)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(report["markdown"],encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="markdown"},
                     indent=2,sort_keys=True))
if __name__=="__main__":
    main()
