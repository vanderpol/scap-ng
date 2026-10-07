#!/usr/bin/env python3
"""Measure cloning of shared OVAL Objects/Variables into per-Rule split closures.

Research-only. Same source OVAL identity + same canonical payload across multiple
Rule singles is strong evidence that rule splitting cloned a genuinely shared
source node.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from lxml import etree


def local(tag: str) -> str:
    return etree.QName(tag).localname


def canonical_hash(node) -> str:
    data=etree.tostring(node,method="c14n",with_comments=False)
    return hashlib.sha256(data).hexdigest()


def node_summary(node) -> dict[str, Any]:
    def attrs(e):
        return {
            local(k):v
            for k,v in sorted(e.attrib.items(),key=lambda kv:local(kv[0]))
            if local(k)!="id"
        }
    children=[]
    for child in list(node)[:12]:
        text=" ".join("".join(child.itertext()).split())
        children.append({
            "element":local(child.tag),
            "attributes":attrs(child),
            "text":text[:240] if text else None,
        })
    return {
        "element":local(node.tag),
        "comment":node.get("comment"),
        "attributes":attrs(node),
        "children":children,
    }


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("split_root",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--top",type=int,default=50)
    args=ap.parse_args()

    manifest=json.loads((args.split_root/"manifest.json").read_text(encoding="utf-8"))
    valid={
        row["path"]:row
        for row in manifest.get("rules",[])
        if row.get("status")=="split_valid" and row.get("path")
    }

    by_kind_id: dict[str, dict[str, dict[str, Any]]]={
        "objects":{},
        "variables":{},
    }
    payload_groups: dict[str, dict[str, list[dict[str, Any]]]]={
        "objects":defaultdict(list),
        "variables":defaultdict(list),
    }

    for rel,row in sorted(valid.items()):
        path=args.split_root/rel
        root=etree.parse(str(path)).getroot()
        rule_id=row.get("rule_id")
        for section in root:
            kind=local(section.tag)
            if kind not in by_kind_id:
                continue
            for node in section:
                oid=node.get("id")
                if not oid:
                    continue
                digest=canonical_hash(node)
                rec=by_kind_id[kind].setdefault(
                    oid,
                    {
                        "id":oid,
                        "payload_hashes":set(),
                        "rules":set(),
                        "occurrences":0,
                        "node_summary":node_summary(node),
                    },
                )
                rec["payload_hashes"].add(digest)
                rec["rules"].add(rule_id)
                rec["occurrences"]+=1
                payload_groups[kind][digest].append(
                    {"id":oid,"rule_id":rule_id}
                )

    report={
        "format":"scap-ng-split-source-fanout-0.1",
        "status":"research_only_not_accepted_design",
        "source":manifest.get("source"),
        "benchmark_key":manifest.get("benchmark_key"),
        "split_valid_rules":len(valid),
        "kinds":{},
    }

    for kind,records in by_kind_id.items():
        rows=[]
        shared_occurrences=0
        shared_ids=0
        max_fanout=0
        fanout_hist=Counter()
        conflicts=[]
        for oid,rec in records.items():
            fanout=len(rec["rules"])
            fanout_hist[fanout]+=1
            max_fanout=max(max_fanout,fanout)
            if len(rec["payload_hashes"])!=1:
                conflicts.append({
                    "id":oid,
                    "payload_hashes":sorted(rec["payload_hashes"]),
                    "rules":sorted(rec["rules"]),
                })
            if fanout>=2:
                shared_ids+=1
                shared_occurrences+=rec["occurrences"]
                rows.append({
                    "id":oid,
                    "rule_fanout":fanout,
                    "occurrences":rec["occurrences"],
                    "rules":sorted(rec["rules"]),
                    "payload_hash":next(iter(rec["payload_hashes"])) if len(rec["payload_hashes"])==1 else None,
                    "node_summary":rec["node_summary"],
                })
        rows.sort(key=lambda x:(-x["rule_fanout"],x["id"]))

        identical_payload_different_ids=[]
        for digest,members in payload_groups[kind].items():
            ids=sorted({x["id"] for x in members})
            rules=sorted({x["rule_id"] for x in members})
            if len(ids)>=2:
                identical_payload_different_ids.append({
                    "payload_hash":digest,
                    "source_ids":ids,
                    "source_id_count":len(ids),
                    "rule_count":len(rules),
                    "occurrences":len(members),
                })
        identical_payload_different_ids.sort(
            key=lambda x:(-x["occurrences"],-x["source_id_count"],x["payload_hash"])
        )

        total_occurrences=sum(x["occurrences"] for x in records.values())
        report["kinds"][kind]={
            "unique_source_ids":len(records),
            "split_occurrences":total_occurrences,
            "same_source_ids_shared_across_rules":shared_ids,
            "occurrences_from_shared_source_ids":shared_occurrences,
            "duplicate_occurrences_from_rule_splitting":sum(
                max(0,x["occurrences"]-1) for x in records.values()
            ),
            "max_rule_fanout":max_fanout,
            "fanout_histogram":{str(k):v for k,v in sorted(fanout_hist.items())},
            "source_id_payload_conflicts":conflicts,
            "top_shared_source_ids":rows[:args.top],
            "identical_payload_groups_with_different_source_ids":identical_payload_different_ids[:args.top],
        }

    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "benchmark_key":report["benchmark_key"],
        "split_valid_rules":report["split_valid_rules"],
        "objects":{k:v for k,v in report["kinds"]["objects"].items() if k not in {"top_shared_source_ids","identical_payload_groups_with_different_source_ids","source_id_payload_conflicts"}},
        "variables":{k:v for k,v in report["kinds"]["variables"].items() if k not in {"top_shared_source_ids","identical_payload_groups_with_different_source_ids","source_id_payload_conflicts"}},
    },indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
