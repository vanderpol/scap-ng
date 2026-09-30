#!/usr/bin/env python3
"""Audit explicit runtime defaults in generated native v003 assessments.

This tests source readability and selected OVAL-derived invariants. It does
not prove complete execution parity and deliberately distinguishes Object
entities, State entities, and record fields from variable expressions.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import yaml


def has_variable(value):
    return isinstance(value, dict) and set(value) == {"variable"}


def audit_doc(document, source="<memory>"):
    errors = []
    totals = Counter()
    assessment = document.get("assessment", {})
    if assessment.get("mode") != "automated":
        return [], totals
    totals["automated_assessments"] += 1

    def issue(code, location):
        errors.append({"code": code, "source": source, "location": location})

    def common_entity(item, path, *, variable_id_selector=False):
        totals["entities"] += 1
        if not isinstance(item, dict) or "value" not in item:
            issue("UNNORMALIZED_ENTITY", path)
            return
        for field in ("operation", "datatype", "mask"):
            if field not in item:
                issue("HIDDEN_ENTITY_DEFAULT_"+field.upper(), path)
        if has_variable(item.get("value")):
            totals["variable_references"] += 1
            if variable_id_selector:
                totals["independent_variable_id_selectors"] += 1
            elif "variable_check" not in item:
                issue("HIDDEN_VARIABLE_CHECK", path)

    def inspect(value, path):
        if isinstance(value, list):
            for i, child in enumerate(value):
                inspect(child, f"{path}[{i}]")
            return
        if not isinstance(value, dict):
            return
        # Collection Object entities are under select, including collects
        # nested inside set expressions and variable object_values.
        if isinstance(value.get("select"), dict):
            for key, ent in value["select"].items():
                is_id = value.get("capability") == "independent.variable" and key == "var_ref"
                common_entity(ent, f"{path}.select.{key}", variable_id_selector=is_id)
        # State predicates are distinguished by having BOTH field and value.
        if "field" in value and "value" in value:
            totals["state_entities"] += 1
            common_entity(value, path)
            for field in ("entity_existence", "entity_check"):
                if field not in value:
                    issue("HIDDEN_STATE_DEFAULT_"+field.upper(), path)
        # OVAL record-field definitions use name+value but not field+value.
        if "name" in value and "value" in value:
            totals["record_fields"] += 1
            common_entity(value, path)
            if "entity_check" not in value:
                issue("HIDDEN_RECORD_FIELD_ENTITY_CHECK", path)
        for name, child in value.items():
            inspect(child, f"{path}.{name}")

    for key, chk in (assessment.get("checks") or {}).items():
        totals["checks"] += 1
        assertion = chk.get("assert", {})
        if isinstance(assertion, dict):
            for field in ("existence", "check"):
                if field not in assertion:
                    issue("HIDDEN_TEST_DEFAULT_"+field.upper(), f"checks.{key}.assert")
        inspect(chk.get("collect"), f"checks.{key}.collect")
        inspect(assertion.get("state"), f"checks.{key}.assert.state")
        inspect(assertion.get("states"), f"checks.{key}.assert.states")
    for key, variable in (assessment.get("variables") or {}).items():
        totals["variables"] += 1
        if "datatype" not in variable:
            issue("MISSING_VARIABLE_DATATYPE", f"variables.{key}")
        inspect(variable.get("expression"), f"variables.{key}.expression")
    return errors, totals


def audit_tree(root):
    combined = Counter()
    errors = []
    files = sorted(root.rglob("*.assessment.yaml"))
    if not files:
        return {"assessment_files": 0, "totals": {},
                "errors": [{"code": "NO_ASSESSMENT_FILES", "source": str(root)}]}
    for path in files:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        issues, counts = audit_doc(document, path.relative_to(root).as_posix())
        errors.extend(issues)
        combined.update(counts)
    return {"assessment_files": len(files),
            "totals": dict(sorted(combined.items())),
            "issue_count": len(errors),
            "errors": errors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    result = audit_tree(args.root)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n",
                           encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "errors"}, indent=2))
    if result.get("issue_count", 0) or result.get("errors"):
        print(json.dumps(result["errors"][:25], indent=2))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
