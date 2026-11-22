#!/usr/bin/env python3
"""Validate the bounded Issue #86 proposed design artifacts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    return json.loads(path.read_text()) if path.suffix == ".json" else yaml.safe_load(path.read_text())


def main() -> int:
    inventory = load(ROOT / "schema-inventory.json")
    crosswalk = load(ROOT / "capability-crosswalk.json")
    errors = []
    source = inventory["source"]
    if source["commit"] != "5afcf590fb5d334687bfdc47f98716424cdb7f3d":
        errors.append("unexpected OVAL v6.0 source commit")
    names = {part: {f[part]["name"] for f in inventory["families"]} for part in ("test", "object", "state", "item")}
    if any(len(values) != inventory["counts"][f"{part}_elements"] for part, values in names.items()):
        errors.append("family element counts are not unique")
    if len(crosswalk["families"]) != inventory["counts"]["test_families"]:
        errors.append("crosswalk does not cover every XSD family")
    if {row["source"]["test"] for row in crosswalk["families"]} != names["test"]:
        errors.append("crosswalk has missing or extra Test families")
    for filename, digest in source["schema_files_sha256"].items():
        actual = hashlib.sha256((ROOT / "source" / filename).read_bytes()).hexdigest()
        if actual != digest:
            errors.append(f"source hash mismatch: {filename}")
    for path in sorted((ROOT / "assessments").glob("*.yaml")):
        doc = load(path)
        for test_name, test in doc["assessment"]["tests"].items():
            keys = list(test)
            if "object" in test and "require" in test and keys.index("object") > keys.index("require"):
                errors.append(f"object follows require: {path}:{test_name}")
    for fixture_path in sorted((ROOT / "fixtures").glob("*.json")):
        fixture = load(fixture_path)
        expected = load(ROOT / "expected" / fixture_path.name)
        positive = fixture["variants"]["positive"]["items"]
        negative = fixture["variants"]["negative"]["items"]
        if positive == negative or expected["variants"]["positive"]["assessment_outcome"] == expected["variants"]["negative"]["assessment_outcome"]:
            errors.append(f"non-distinct or contradictory fixture: {fixture_path.name}")
        contract = fixture["semantic_contract"]
        if contract["negative_strategy"] == "field-mismatch":
            for selector in contract["selector_fields"]:
                if positive[0]["fields"].get(selector) != negative[0]["fields"].get(selector):
                    errors.append(f"negative changed selector {selector}: {fixture_path.name}")
            if positive[0]["fields"].get(contract["negative_field"]) == negative[0]["fields"].get(contract["negative_field"]):
                errors.append(f"negative did not change comparison field: {fixture_path.name}")
    if errors:
        for error in errors:
            print("ERROR", error)
        return 1
    print(json.dumps({"families": len(inventory["families"]), "enums": inventory["counts"]["enumerations"], "assessments": len(list((ROOT / "assessments").glob("*.yaml"))), "validated": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
