#!/usr/bin/env python3
"""Independent canonical source-Filter second-pass regression check, v0.4.0.

Compare all 4,001 first-pass canonical authoring documents against final
authoring in YAML/JSON. Require exactly 19 source-verified Test-local
Object.filters rewrites with exact leaf/Filter reverse reconstruction,
otherwise byte/parsed authoring graph unchanged. This is not scanner parity.
Refs #248.
"""
from __future__ import annotations
import argparse
from collections import Counter
from pathlib import Path
import json

from v04_a_authoring_graph_index import read_authoring_archive
from migrate_v04_additional_source_filters import (
    index_source_proof, migrate, recover_migration, EXPECTED_DIRECT_TESTS,
)


def compare(prior, current, proof):
    if set(prior) != set(current):
        raise ValueError("Source and resulting authoring document paths differ")
    counts=Counter()
    changed=[]
    for path in sorted(prior):
        expected,stat=migrate(prior[path],path,proof)
        if expected != current[path]:
            raise ValueError(f"{path}: unrelated source content or unexpected Filter rewrite")
        recover_migration(current[path],prior[path],path,proof)
        if expected != prior[path]:
            changed.append(path)
        counts.update(stat)
    if counts["source_linked_additional_direct_filters"] != EXPECTED_DIRECT_TESTS:
        raise ValueError("Canonical source-linked Filter population changed")
    if not changed:
        raise ValueError("No verified Filter rewrites were made")
    return {
        "status":"PASS",
        "documents":len(prior),
        "source_test_linked_filter_rewrites":counts["source_linked_additional_direct_filters"],
        "changed_documents":len(changed),
        "changed_paths":changed,
        "original_content_roundtrip":"PASS",
        "unaltered_other_documents":"PASS",
        "scanner_runtime_parity":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prior",type=Path,required=True)
    p.add_argument("--current",type=Path,required=True)
    p.add_argument("--source-proof",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    def read(path):
        fmt="yaml" if path.name.endswith(".yaml.zip") else "json"
        return read_authoring_archive(path,fmt)
    proof=index_source_proof(json.loads(args.source_proof.read_text()),assert_six=True)
    report=compare(read(args.prior),read(args.current),proof)
    if report["documents"]!=4001:
        raise ValueError("Incomplete canonical six-STIG source corpus")
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="changed_paths"},indent=2))

if __name__=="__main__":
    main()
