#!/usr/bin/env python3
"""Reproduce collected-field review evidence from all current capability mappings."""
import argparse
import hashlib
import gzip
import json
from pathlib import Path

from generate_capability_schema import generate


def inventory(root):
    rows = []
    for path in sorted((root / "schema/v0.1.0/capability-mappings").glob("*.json")):
        mapping = json.loads(path.read_text())
        if "capability" not in mapping:
            continue
        generated = generate(mapping, root)
        item = generated.get("$defs", {}).get("collected_item")
        fields = {}
        for fragment in (item or {}).get("allOf", []):
            fields.update(fragment.get("properties", {}).get("fields", {}).get("properties", {}))
        rows.append({
            "capability": mapping["capability"],
            "mapping": path.relative_to(root).as_posix(),
            "mapping_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "generated_schema_sha256": hashlib.sha256(
                json.dumps(generated, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest(),
            "has_collected_item": item is not None,
            "fields": fields,
        })
    return {"provenance_category": "Evidence/Audit", "generator": "tools/generate_capability_schema.py",
            "generator_sha256": hashlib.sha256((root / "tools/generate_capability_schema.py").read_bytes()).hexdigest(),
            "mapping_count": len(rows), "collected_item_count": sum(r["has_collected_item"] for r in rows),
            "capabilities": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    data = inventory(args.repo_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    if args.output.suffix == ".gz":
        args.output.write_bytes(gzip.compress(payload, mtime=0))
    else:
        args.output.write_bytes(payload)
    print(json.dumps({k: data[k] for k in ("mapping_count", "collected_item_count")}))


if __name__ == "__main__":
    main()
