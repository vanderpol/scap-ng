#!/usr/bin/env python3
"""Heuristically find manual-only XCCDF rules that look relational/correlated.

Research-only. This is a candidate finder, never an automatic conversion proof.
"""
from __future__ import annotations
import argparse, json, re, zipfile
from pathlib import Path
from lxml import etree as ET

REL_PATTERNS = [
    ("possessive_same_subject", re.compile(r"\b(that|same|corresponding|respective)\s+(user|account|owner|directory|file|group|device|interface)", re.I)),
    ("owner_relation", re.compile(r"\b(owner(?:'s)?|owned by|group-owned by)\b", re.I)),
    ("per_item_relation", re.compile(r"\b(for each|each|all)\b.{0,100}\b(user|account|home director|directory|file|interface|device|certificate|service)\b", re.I|re.S)),
    ("same_as_relation", re.compile(r"\b(same as|match(?:es)?|correspond(?:s|ing)?)\b.{0,100}\b(user|owner|group|account|directory|file|entry|record)\b", re.I|re.S)),
    ("assignment_relation", re.compile(r"\b(assigned|associated)\b.{0,100}\b(user|account|home|group|owner|device|interface)\b", re.I|re.S)),
]

def lname(el):
    try: return ET.QName(el).localname
    except Exception: return ""

def text(el):
    return " ".join(" ".join(el.itertext()).split()) if el is not None else ""

def parse_zip(path: Path):
    docs=[]
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if not name.lower().endswith(".xml"):
                continue
            try:
                root=ET.fromstring(z.read(name))
            except Exception:
                continue
            if any(lname(x)=="Rule" for x in root.iter()):
                docs.append((name,root))
    return docs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_zip")
    ap.add_argument("--label",default="benchmark")
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    rows=[]
    for component,root in parse_zip(Path(args.source_zip)):
        for rule in root.iter():
            if lname(rule)!="Rule": continue
            rid=rule.get("id") or ""
            title_el=next((x for x in rule if lname(x)=="title"),None)
            desc_el=next((x for x in rule if lname(x)=="description"),None)
            title=text(title_el)
            desc=text(desc_el)
            checks=[x for x in rule if lname(x)=="check"]
            oval_checks=[]
            for chk in checks:
                system=(chk.get("system") or "").lower()
                if "oval" in system:
                    oval_checks.append(chk)
            if oval_checks:
                continue
            corpus=" ".join([title,desc])
            hits=[name for name,pat in REL_PATTERNS if pat.search(corpus)]
            if not hits:
                continue
            version=next((text(x) for x in rule if lname(x)=="version"),None)
            rows.append({
                "rule_id":rid,
                "version":version,
                "title":title,
                "component":component,
                "signals":hits,
                "classification":"manual_correlation_candidate",
                "disposition":"review_for_native_for_each_automation",
            })
    # Deduplicate rules repeated in multiple embedded components.
    by={}
    for row in rows:
        key=(row["rule_id"],row["title"])
        if key not in by or len(row["signals"])>len(by[key]["signals"]):
            by[key]=row
    out_rows=sorted(by.values(),key=lambda x:(x["rule_id"],x["title"]))
    report={"label":args.label,"manual_correlation_candidates":len(out_rows),"candidates":out_rows}
    Path(args.output).write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"label":args.label,"manual_correlation_candidates":len(out_rows)},indent=2))

if __name__=="__main__": main()
