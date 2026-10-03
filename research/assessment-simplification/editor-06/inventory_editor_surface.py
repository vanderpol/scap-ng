#!/usr/bin/env python3
"""Snapshot editor obligations from current mappings/contracts; no editor coverage claim."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SCHEMA = ROOT / "schema/v0.1.0"
XSD = "{http://www.w3.org/2001/XMLSchema}"


def pin(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def inventory():
    rows = []
    for path in sorted((SCHEMA / "capability-mappings").glob("*.json")):
        mapping = json.loads(path.read_text())
        native = mapping["native"]
        rows.append({"capability": mapping["capability"], "mapping": pin(path),
                     "source_test": mapping["source"].get("test"),
                     "native_contract": native,
                     "semantic_obligations": mapping.get("semantic_validator_rules", []),
                     "editor_coverage": {k: "not_implemented" for k in
                                         ("read_preserve", "inspect", "create_edit", "graph_refactor", "validation", "guided_view")},
                     "editor_fixture_evidence": []})
    require_unique = {row["capability"] for row in rows}
    if len(require_unique) != len(rows):
        raise ValueError("duplicate native capability identity")
    common_path = SCHEMA / "capability-common.schema.json"
    definitions = json.loads(common_path.read_text())["$defs"]
    oval_path = ROOT / "third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd"
    oval = ET.parse(oval_path).getroot()
    groups = {}
    for name in ("ComponentGroup", "FunctionGroup"):
        group = oval.find(f"{XSD}group[@name='{name}']")
        groups[name] = [element.get("name") for element in group.findall(f"{XSD}choice/{XSD}element")]
    contract_paths = [ROOT / "research/iterations/003/design/oval-variable-coverage.md",
                      ROOT / "research/iterations/003/design/assessment-evaluation-semantics.md",
                      ROOT / "specification/migration/legacy-feature-disposition.md",
                      ROOT / "specification/migration/oval-test-support-overrides.json"]
    authoring_names = ("benchmark", "rule", "assessment", "applicability", "manual-assessment", "tailoring", "organizational-input")
    report = {"format": "editor-authoring-obligations-research-0.1",
              "receiving_commit": "9e5540507a2a8698257437922e630677b14c363a",
              "scope": "Current reviewed mapping/shared-structure obligations; not full language inventory, editor implementation or runtime equivalence.",
              "summary": {"mapping_count": len(rows),
                          "families": dict(sorted(Counter(row["capability"].split('.')[0] for row in rows).items())),
                          "shared_definitions": len(definitions), "legacy_function_members": len(groups["FunctionGroup"]),
                          "editor_implemented_capabilities": 0},
              "authoring_schemas": [pin(SCHEMA / f"{name}.schema.json") for name in authoring_names],
              "shared_schema": pin(common_path), "shared_definitions": definitions,
              "legacy_variable_schema": pin(oval_path), "legacy_variable_components": groups,
              "semantics_and_disposition_pins": [pin(path) for path in contract_paths],
              "capabilities": rows,
              "outstanding": ["Reconcile unmapped/schema-only candidates and governance dispositions without rarity-based removal.",
                              "Reconcile complete native Variable/function grammar and graph/reference contracts; schemas alone are insufficient.",
                              "Add production and conformance fixtures, independent edit expectations and compositional/generative evidence.",
                              "Implement and verify editor create/edit/inspect behavior; preserving raw content alone is insufficient."]}
    (HERE / "authoring-obligations.json").write_text(json.dumps(report, indent=2) + "\n")
    return report["summary"]


if __name__ == "__main__":
    print(json.dumps(inventory(), indent=2))
