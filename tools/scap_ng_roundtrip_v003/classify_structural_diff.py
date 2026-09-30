#!/usr/bin/env python3
"""Classify structural differences in an OVAL round trip.

This does not replace semantic comparison. It documents the XML-level changes
that remain after semantic equality is established and highlights anything not
covered by an intentional normalization category.
"""
from __future__ import annotations
import argparse, collections, json
from pathlib import Path
import xml.etree.ElementTree as ET

OD="http://oval.mitre.org/XMLSchema/oval-definitions-5"

def q(name):
    return f"{{{OD}}}{name}"

def local(tag):
    return tag.rsplit("}",1)[-1]

def section_counts(root):
    result={}
    for section in ("definitions","tests","objects","states","variables"):
        node=root.find(q(section))
        result[section]=0 if node is None else len(list(node))
    return result

def count_local(root,name):
    return sum(1 for n in root.iter() if local(n.tag)==name)

def ids(root):
    return {
        n.get("id")
        for n in root.iter()
        if n.get("id")
    }

def definition_metadata_profile(root):
    counts=collections.Counter()
    for definition in root.findall(f".//{q('definition')}"):
        md=definition.find(q("metadata"))
        if md is None:
            continue
        for child in list(md):
            counts[local(child.tag)]+=1
    return dict(sorted(counts.items()))

def comments(root):
    return sum(1 for n in root.iter() if n.get("comment") is not None)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--regenerated",type=Path,required=True)
    ap.add_argument("--semantic-report",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    s=ET.parse(args.source).getroot()
    r=ET.parse(args.regenerated).getroot()
    semantic=json.loads(args.semantic_report.read_text(encoding="utf-8"))

    sc=section_counts(s)
    rc=section_counts(r)
    source_ids=ids(s)
    regen_ids=ids(r)
    shared_ids=source_ids & regen_ids

    source_extend=count_local(s,"extend_definition")
    regen_extend=count_local(r,"extend_definition")
    source_generator=count_local(s,"generator")
    regen_generator=count_local(r,"generator")

    categories=[]

    if source_ids != regen_ids:
        categories.append({
            "category":"generated_ids",
            "status":"intentional",
            "source_ids":len(source_ids),
            "regenerated_ids":len(regen_ids),
            "shared_ids":len(shared_ids),
            "reason":"OVAL identifiers are regenerated; semantic comparison is ID-independent.",
        })

    if source_extend != regen_extend:
        categories.append({
            "category":"extend_definition_dereference",
            "status":"intentional",
            "source_count":source_extend,
            "regenerated_count":regen_extend,
            "reason":"SCAP-NG dereferences extend_definition and preserves the referenced criteria semantics.",
        })

    source_md=definition_metadata_profile(s)
    regen_md=definition_metadata_profile(r)
    if source_md != regen_md:
        categories.append({
            "category":"definition_metadata_reconstruction",
            "status":"intentional-provenance-separation",
            "source_profile":source_md,
            "regenerated_profile":regen_md,
            "reason":"Legacy descriptive/provenance metadata is not part of native assessment truth semantics; root class/version/deprecation and assessment title are preserved separately.",
        })

    if sc != rc:
        categories.append({
            "category":"aggregate_dependency_duplication",
            "status":"harness-normalization",
            "source_counts":sc,
            "regenerated_counts":rc,
            "reason":"The first aggregate gate merges independent split-assessment dependency closures without cross-assessment semantic deduplication. A separate dedup gate follows.",
        })

    if source_generator or regen_generator:
        categories.append({
            "category":"generator_metadata",
            "status":"intentional",
            "source_generator_elements":source_generator,
            "regenerated_generator_elements":regen_generator,
            "reason":"Generator product/timestamp metadata is regenerated.",
        })

    source_comments=comments(s)
    regen_comments=comments(r)
    if source_comments != regen_comments:
        categories.append({
            "category":"comment_normalization",
            "status":"intentional-provenance-separation",
            "source_comments":source_comments,
            "regenerated_comments":regen_comments,
            "reason":"OVAL comments are descriptive metadata; native assessment fields preserve useful titles while legacy comments/provenance are not serialization constraints.",
        })

    unexplained=[]
    if semantic.get("failures",0):
        unexplained.append({
            "category":"semantic_differences",
            "count":semantic.get("failures"),
            "details":semantic.get("failures_by_stage",{}),
        })

    report={
        "source_counts":sc,
        "regenerated_counts":rc,
        "semantic_failures":semantic.get("failures"),
        "classified_differences":categories,
        "unexplained_differences":unexplained,
        "unexplained_count":len(unexplained),
    }
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 1 if unexplained else 0

if __name__=="__main__":
    raise SystemExit(main())
