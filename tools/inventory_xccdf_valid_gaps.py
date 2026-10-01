#!/usr/bin/env python3
"""Inventory XCCDF Value/Profile-value and direct CPE platform usage in SCAP ZIPs."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

XCCDF="http://checklists.nist.gov/xccdf/1.2"
NS={"x":XCCDF}

def local(tag):
    return tag.rsplit("}",1)[-1]

def text(node):
    if node is None:
        return None
    return " ".join("".join(node.itertext()).split())

def benchmark_from_zip(path):
    found=[]
    with zipfile.ZipFile(path) as z:
        for name in sorted(z.namelist()):
            if not name.lower().endswith(".xml"):
                continue
            try:
                root=ET.fromstring(z.read(name))
            except ET.ParseError:
                continue
            for node in root.iter():
                if local(node.tag)=="Benchmark":
                    found.append(node)
    if len(found)!=1:
        raise ValueError(f"{path}: expected one Benchmark, found {len(found)}")
    return found[0]

def selected_rows(parent, name):
    out=[]
    for node in parent.findall(f"x:{name}",NS):
        row={"text":text(node)}
        row.update({k:v for k,v in node.attrib.items()})
        out.append(row)
    return out

def inspect(path):
    root=benchmark_from_zip(path)
    values=[]
    for node in root.findall(".//x:Value",NS):
        values.append({
            "id":node.get("id"),
            "type":node.get("type") or "string",
            "operator":node.get("operator") or "equals",
            "interactive":node.get("interactive"),
            "prohibitChanges":node.get("prohibitChanges"),
            "abstract":node.get("abstract"),
            "title":[text(x) for x in node.findall("x:title",NS)],
            "description":[text(x) for x in node.findall("x:description",NS)],
            "values":selected_rows(node,"value"),
            "complex_values":[
                {"selector":x.get("selector"),"xml":ET.tostring(x,encoding="unicode")}
                for x in node.findall("x:complex-value",NS)
            ],
            "defaults":selected_rows(node,"default"),
            "complex_defaults":[
                {"selector":x.get("selector"),"xml":ET.tostring(x,encoding="unicode")}
                for x in node.findall("x:complex-default",NS)
            ],
            "matches":selected_rows(node,"match"),
            "lower_bounds":selected_rows(node,"lower-bound"),
            "upper_bounds":selected_rows(node,"upper-bound"),
            "choices":[
                {"selector":x.get("selector"),"mustMatch":x.get("mustMatch"),
                 "values":[text(v) for v in x.findall("x:choice",NS)]}
                for x in node.findall("x:choices",NS)
            ],
            "sources":[text(x) for x in node.findall("x:source",NS)],
        })
    profiles=[]
    for profile in root.findall("x:Profile",NS):
        actions=[]
        for child in profile:
            kind=local(child.tag)
            if kind in ("set-value","set-complex-value","refine-value"):
                actions.append({
                    "kind":kind,
                    "idref":child.get("idref"),
                    "selector":child.get("selector"),
                    "operator":child.get("operator"),
                    "text":text(child),
                    "xml":ET.tostring(child,encoding="unicode"),
                })
        if actions:
            profiles.append({
                "id":profile.get("id"),
                "extends":profile.get("extends"),
                "actions":actions,
            })
    benchmark_platforms=[x.get("idref") for x in root.findall("x:platform",NS)]
    rule_platforms=[]
    for rule in root.findall(".//x:Rule",NS):
        refs=[x.get("idref") for x in rule.findall("x:platform",NS)]
        if refs:
            rule_platforms.append({"rule_id":rule.get("id"),"platforms":refs})
    direct_cpe=sorted({
        ref for ref in benchmark_platforms+
        [ref for row in rule_platforms for ref in row["platforms"]]
        if isinstance(ref,str) and ref.startswith("cpe:")
    })
    return {
        "artifact":path.name,
        "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "benchmark_id":root.get("id"),
        "value_count":len(values),
        "values":values,
        "profile_value_action_count":sum(len(x["actions"]) for x in profiles),
        "profiles_with_value_actions":profiles,
        "benchmark_platforms":benchmark_platforms,
        "rule_platform_reference_count":sum(len(x["platforms"]) for x in rule_platforms),
        "direct_cpe_platforms":direct_cpe,
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    files=sorted(args.source.glob("*SCAP_1-4_Benchmark*.zip")) if args.source.is_dir() else [args.source]
    rows=[inspect(p) for p in files]
    interesting=[r for r in rows if r["value_count"] or r["direct_cpe_platforms"]]
    summary={
        "packages_scanned":len(rows),
        "packages_with_values":sum(bool(r["value_count"]) for r in rows),
        "total_values":sum(r["value_count"] for r in rows),
        "profile_value_actions":sum(r["profile_value_action_count"] for r in rows),
        "packages_with_direct_cpe":sum(bool(r["direct_cpe_platforms"]) for r in rows),
        "value_types":dict(Counter(v["type"] for r in rows for v in r["values"])),
        "value_operators":dict(Counter(v["operator"] for r in rows for v in r["values"])),
    }
    out={"format":"xccdf-valid-gap-inventory-0.1","summary":summary,"packages":interesting}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
