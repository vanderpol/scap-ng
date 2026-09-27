#!/usr/bin/env python3
"""Compare normalized semantic fingerprints for published cross-platform rules."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("left",type=Path)
    ap.add_argument("right",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    left=json.loads(args.left.read_text())
    right=json.loads(args.right.read_text())
    same=left["semantic_fingerprint_sha256"]==right["semantic_fingerprint_sha256"]
    report={
      "format":"scap-ng-native-reuse-comparison-0.1",
      "left":{"rule":left["source"]["rule_id"],"fingerprint":left["semantic_fingerprint_sha256"]},
      "right":{"rule":right["source"]["rule_id"],"fingerprint":right["semantic_fingerprint_sha256"]},
      "same_normalized_semantics":same,
      "reuse_status":"candidate_exact_reuse" if same else "not_identical",
      "qualification":"requires differential equivalence testing before automated reuse approval",
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
