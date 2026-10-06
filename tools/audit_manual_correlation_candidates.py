#!/usr/bin/env python3
"""Heuristically find manual-only XCCDF rules that may need scoped correlation.

Research-only. This is a candidate finder, never an automatic conversion proof.
It deliberately separates strong relational language from broad per-item wording
so corpus counts do not overstate the case for native scoped iteration.
"""
from __future__ import annotations
import argparse, json, re, zipfile
from pathlib import Path
from lxml import etree as ET

HIGH_PATTERNS = [
    ("corresponding_private_key", re.compile(r"\bcorresponding\s+private\s+key\b", re.I)),
    ("certificate_identity_mapping", re.compile(r"\b(certificate|authenticated\s+identity).{0,180}\bcorresponding\s+(user|group|account)\b", re.I|re.S)),
    ("home_owner_primary_group", re.compile(r"\bhome\s+director(?:y|ies).{0,180}\b(owner(?:'s)?\s+primary\s+group|primary\s+group\s+of\s+the\s+user|same\s+as\s+the\s+primary\s+gid\s+of\s+the\s+user)\b", re.I|re.S)),
    ("home_owned_by_assigned_user", re.compile(r"\bhome\s+director(?:y|ies).{0,180}\bowned\s+by\s+the\s+(respective\s+)?user\b.{0,180}\b(/etc/passwd|assigned)\b", re.I|re.S)),
    ("assigned_home_owner_relation", re.compile(r"\bhome\s+director(?:y|ies).{0,180}\b(respective\s+user|user\s+assigned\s+to\s+it)\b", re.I|re.S)),
]

MEDIUM_PATTERNS = [
    ("corresponding_resource", re.compile(r"\bcorresponding\s+(user|account|owner|directory|file|group|device|interface|record|entry)\b", re.I)),
    ("respective_subject", re.compile(r"\b(respective|that|same)\s+(user|account|owner|group|directory|file|device|interface)\b", re.I)),
    ("parent_derived_expectation", re.compile(r"\b(that\s+user(?:'s)?|user(?:'s)?\s+primary|owner(?:'s)?\s+primary|same\s+(?:user|account|owner))\b", re.I)),
    ("home_from_account_must_exist", re.compile(r"\bhome\s+director(?:y|ies)\b.{0,120}\b(defined|assigned|configured)\b.{0,100}\b(/etc/passwd|user|account)\b.{0,120}\bexist", re.I|re.S)),
    ("user_home_path_relation", re.compile(r"\b(user(?:'s)?|users)\s+home\s+director(?:y|ies)\b", re.I)),
    ("initialization_file_user_relation", re.compile(r"\binitialization\s+files?\b.{0,160}\b(home\s+directory\s+user|user(?:'s)?\s+primary\s+group|users?\s+home\s+director)", re.I|re.S)),
    ("assignment_relation", re.compile(r"\b(assigned|associated)\b.{0,100}\b(user|account|home|group|owner|device|interface)\b", re.I|re.S)),
    ("same_as_relation", re.compile(r"\b(same as|match(?:es)?|correspond(?:s|ing)?)\b.{0,100}\b(user|owner|group|account|directory|file|entry|record)\b", re.I|re.S)),
]

BROAD_PATTERNS = [
    ("owner_relation", re.compile(r"\b(owner(?:'s)?|owned by|group-owned by)\b", re.I)),
    ("per_item_relation", re.compile(r"\b(for each|each|all)\b.{0,100}\b(user|account|home director|directory|file|interface|device|certificate|service)\b", re.I|re.S)),
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


def matching(patterns, corpus):
    return [name for name,pat in patterns if pat.search(corpus)]


def confidence(high, medium, broad):
    if high:
        return "high"
    if len(medium)>=2:
        return "high"
    if medium:
        return "medium"
    if broad:
        return "broad"
    return None


def excerpt(corpus, patterns, width=420):
    positions=[]
    for _,pat in patterns:
        m=pat.search(corpus)
        if m:
            positions.append(m.start())
    if not positions:
        return None
    start=max(0,min(positions)-100)
    return corpus[start:start+width]


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

            # Manual prose is often carried by check/check-content rather than
            # Rule description, so include it in the candidate evidence.
            check_text=" ".join(text(chk) for chk in checks)
            corpus=" ".join(x for x in [title,desc,check_text] if x)
            high=matching(HIGH_PATTERNS,corpus)
            medium=matching(MEDIUM_PATTERNS,corpus)
            broad=matching(BROAD_PATTERNS,corpus)
            conf=confidence(high,medium,broad)
            if conf is None:
                continue

            version=next((text(x) for x in rule if lname(x)=="version"),None)
            all_signals=high+medium+broad
            rows.append({
                "rule_id":rid,
                "version":version,
                "title":title,
                "component":component,
                "confidence":conf,
                "signals":{
                    "high":high,
                    "medium":medium,
                    "broad":broad,
                },
                "evidence_excerpt":excerpt(corpus,HIGH_PATTERNS+MEDIUM_PATTERNS+BROAD_PATTERNS),
                "classification":"manual_correlation_candidate",
                "disposition":"review_for_native_scoped_automation",
            })

    # Deduplicate rules repeated in multiple embedded components.
    rank={"broad":0,"medium":1,"high":2}
    by={}
    for row in rows:
        key=(row["rule_id"],row["title"])
        prev=by.get(key)
        if prev is None or rank[row["confidence"]]>rank[prev["confidence"]]:
            by[key]=row
    out_rows=sorted(by.values(),key=lambda x:(x["rule_id"],x["title"]))
    counts={k:sum(1 for r in out_rows if r["confidence"]==k) for k in ("high","medium","broad")}
    report={
        "label":args.label,
        "manual_correlation_candidates":len(out_rows),
        "confidence_counts":counts,
        "confirmed_candidates":0,
        "note":"All rows are heuristic until source-policy semantics are reviewed. High confidence means strong relational language, not proven automability.",
        "candidates":out_rows,
    }
    Path(args.output).write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
        "label":args.label,
        "manual_correlation_candidates":len(out_rows),
        "confidence_counts":counts,
    },indent=2))


if __name__=="__main__": main()
