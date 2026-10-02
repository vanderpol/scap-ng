#!/usr/bin/env python3
"""Validate the vendored SCAP 1.4 schema bundle is internally usable."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from lxml import etree

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    args=ap.parse_args()
    root=args.root
    manifest=json.loads((root/"bundle-manifest.json").read_text())
    failures=[]
    for rel, expected in manifest["files"].items():
        p=root/rel
        if not p.is_file():
            failures.append(f"missing: {rel}")
            continue
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(f"digest mismatch: {rel}: {actual} != {expected}")
    try:
        doc=etree.parse(str(root/"omni-schema.xsd"))
        etree.XMLSchema(doc)
    except Exception as exc:
        failures.append(f"omni-schema compile failure: {exc}")
    if failures:
        for f in failures:
            print("ERROR:",f)
        return 1
    print(f"OK: {len(manifest['files'])} SCAP 1.4 schema files verified; omni-schema.xsd compiled")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
