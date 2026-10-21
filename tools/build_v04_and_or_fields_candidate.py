#!/usr/bin/env python3
"""Build a reversible six-STIG 0.4-C logical AND/OR + fields naming preview.

This is NOT approved v0.4 syntax. It first uses the source-conservative
Test.state_operator whole-condition transformation and then rewrites only
structurally safe within-State AND lists with unique entity names.

- Whole-State AND (from a migrated states_match: all) stays AND.
- Group-scoped state_fields_require becomes a local require BEFORE fields.
- Test-inherited state_fields_require is retained if still in scope.
- Field-specific require overrides and the source-order ledger are retained.
- Repeated field names, record predicates and other unproven shapes stay old.

All transformed Tests are exactly inverted. The source archive is pinned by
the invoking workflow; semantic scanner parity and schema approval remain OPEN.
Refs #248 #239.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

from migrate_v04_states_match_to_logic import (
    migrate as migrate_state_alternatives,
    restore as restore_state_alternatives,
)

RESERVED = {"and", "or", "one", "xor", "all", "any", "odd",
            "fields", "fields_operator", "require"}
LIST = "all_items_must"


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
         separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def read_path(root, path):
    current = root
    for part in path:
        current = current[part]
    return current


def replace_path(root, path, value):
    parent = read_path(root, path[:-1])
    parent[path[-1]] = value


def simple_and_group(node):
    if not isinstance(node, dict) or "and" not in node:
        return None
    if set(node) - {"and", "state_fields_require"}:
        return None
    entries = node["and"]
    if not isinstance(entries, list) or len(entries) < 2:
        return None
    fields = []
    for entry in entries:
        if not isinstance(entry, dict) or len(entry) != 1:
            return None
        name, predicate = next(iter(entry.items()))
        if (not isinstance(name, str) or name in RESERVED or
            not isinstance(predicate, dict) or not predicate or
            "record" in predicate):
            return None
        fields.append((name, predicate))
    if len(set(name for name, _ in fields)) != len(fields):
        return None
    return fields


def transform_test(test, whole_state_and=False):
    result = deepcopy(test)
    edits = []
    test_scope = test.get("state_fields_require")

    def visit(node, path):
        if not isinstance(node, dict):
            return
        outer = (whole_state_and and path ==
                 ["require", LIST, 0])
        fields = simple_and_group(node) if not outer else None
        if fields is not None:
            scope = node.get("state_fields_require", test_scope)
            if (scope is not None or
                all(isinstance(predicate.get("require"), str)
                    for _, predicate in fields)):
                previous = deepcopy(node)
                rewritten = {}
                if "state_fields_require" in node:
                    rewritten["require"] = deepcopy(node["state_fields_require"])
                rewritten["fields"] = {name: deepcopy(predicate)
                                       for name, predicate in fields}
                replace_path(result, path, rewritten)
                edits.append({"path": deepcopy(path),
                              "source_sha256": fingerprint(previous),
                              "candidate_sha256": fingerprint(rewritten),
                              "source_field_names": [name for name, _ in fields],
                              "source_local_field_requirement":
                                  deepcopy(node.get("state_fields_require")),
                              "source_has_local_field_requirement":
                                  "state_fields_require" in node,
                              "uses_test_field_requirement":
                                  "state_fields_require" not in node and
                                  test_scope is not None})
                return
        for operator in ("and", "or", "one", "xor", "all", "any", "odd"):
            children = node.get(operator)
            if isinstance(children, list):
                for i, child in enumerate(children):
                    visit(child, path + [operator, i])

    req = result.get("require")
    if isinstance(req, dict) and isinstance(req.get(LIST), list):
        for index, clause in enumerate(req[LIST]):
            visit(clause, ["require", LIST, index])
    return result, edits


def invert_test(test, edits, original_test_sha):
    recovered = deepcopy(test)
    for edit in reversed(edits):
        path = edit["path"]
        current = read_path(recovered, path)
        if fingerprint(current) != edit["candidate_sha256"]:
            raise ValueError("Field candidate changed before inversion: " + str(path))
        expected = ({"require", "fields"} if
                    edit["source_has_local_field_requirement"] else {"fields"})
        if set(current) != expected:
            raise ValueError("Unexpected field group scope: " + str(path))
        entries = current["fields"]
        if (not isinstance(entries, dict) or
            list(entries) != edit["source_field_names"]):
            raise ValueError("Entity ordering/repetition not retained")
        old = {}
        if edit["source_has_local_field_requirement"]:
            if current["require"] != edit["source_local_field_requirement"]:
                raise ValueError("Local field cardinality changed")
            old["state_fields_require"] = deepcopy(current["require"])
        old["and"] = [{name: deepcopy(pred)}
                      for name, pred in entries.items()]
        if fingerprint(old) != edit["source_sha256"]:
            raise ValueError("Not an exact original field group")
        replace_path(recovered, path, old)
    if fingerprint(recovered) != original_test_sha:
        raise ValueError("Not an exact original Test after field inverse")
    return recovered


def project_document(original):
    stage1, states_ledger = migrate_state_alternatives(original)
    result = deepcopy(stage1)
    fields_ledger = []
    assessment = result.get("assessment") if isinstance(result, dict) else None
    if isinstance(assessment, dict) and assessment.get("mode") == "automated":
        whole_and_tests = {row["test_id"] for row in states_ledger
                           if row["source_state_operator"] == "all"}
        for test_id, test in list(assessment.get("tests", {}).items()):
            updated, changes = transform_test(
                test, whole_state_and=test_id in whole_and_tests)
            if changes:
                assessment["tests"][test_id] = updated
                fields_ledger.append({
                    "test_id": test_id,
                    "stage1_test_sha256": fingerprint(test),
                    "candidate_test_sha256": fingerprint(updated),
                    "changed_field_groups": changes})
    ledger = {"source_sha256": fingerprint(original),
              "stage1_sha256": fingerprint(stage1),
              "candidate_sha256": fingerprint(result),
              "states": states_ledger,
              "fields": fields_ledger}
    if restore_document(result, ledger) != original:
        raise ValueError("Source exact inverse failed")
    return result, ledger


def restore_document(candidate, ledger):
    if fingerprint(candidate) != ledger["candidate_sha256"]:
        raise ValueError("Candidate document changed")
    result = deepcopy(candidate)
    a = result.get("assessment") if isinstance(result, dict) else None
    for entry in ledger["fields"]:
        test_id = entry["test_id"]
        test = a["tests"][test_id]
        if fingerprint(test) != entry["candidate_test_sha256"]:
            raise ValueError("Field Test was edited after proof")
        a["tests"][test_id] = invert_test(
            test, entry["changed_field_groups"], entry["stage1_test_sha256"])
    if fingerprint(result) != ledger["stage1_sha256"]:
        raise ValueError("Field stage source graph not recovered")
    source = restore_state_alternatives(result, ledger["states"])
    if fingerprint(source) != ledger["source_sha256"]:
        raise ValueError("Whole-State source graph not recovered")
    return source


def archive_preview(source_zip, output_json, output_yaml, output_ledger,
                    *, expected_documents=4001, expected_states=123,
                    expected_fields=231):
    import yaml
    totals = Counter()
    samples = []
    proof = []
    with zipfile.ZipFile(source_zip) as original, \
            zipfile.ZipFile(output_json, "w", zipfile.ZIP_DEFLATED) as jzip, \
            zipfile.ZipFile(output_yaml, "w", zipfile.ZIP_DEFLATED) as yzip:
        for name in original.namelist():
            if not name.endswith(".json"):
                continue
            source = json.loads(original.read(name))
            candidate, ledger = project_document(source)
            jzip.writestr(name, json.dumps(candidate, ensure_ascii=False,
                                          indent=2) + "\n")
            as_yaml = yaml.safe_dump(candidate, sort_keys=False,
                                     allow_unicode=True)
            parsed_yaml = yaml.safe_load(as_yaml)
            if parsed_yaml != candidate:
                raise ValueError("YAML roundtrip changed candidate: " + name)
            yzip.writestr(name[:-5] + ".yaml", as_yaml)
            totals["documents"] += 1
            totals["whole_state_tests"] += len(ledger["states"])
            totals["field_groups"] += sum(len(row["changed_field_groups"])
                                           for row in ledger["fields"])
            if ledger["states"] or ledger["fields"]:
                totals["affected_documents"] += 1
                proof.append({"path": name,
                              "source_sha256": ledger["source_sha256"],
                              "candidate_sha256": ledger["candidate_sha256"],
                              "whole_state_changes": len(ledger["states"]),
                              "field_changes": len(ledger["fields"])})
                if len(samples) < 16:
                    samples.append({"path": name,
                                    "field_group_sites": [
                                      {"test_id": entry["test_id"],
                                       "paths": [e["path"] for e in
                                                 entry["changed_field_groups"]]}
                                      for entry in ledger["fields"]]})
    for key, expected in (("documents", expected_documents),
                          ("whole_state_tests", expected_states),
                          ("field_groups", expected_fields)):
        if totals[key] != expected:
            raise ValueError(f"Source corpus drift: {key} got {totals[key]}, "
                             f"expected {expected}")
    report = {"status": "PREVIEW_ONLY_EXACT_SOURCE_GRAPH_INVERSE_NO_RUNTIME_PARITY",
              "counts": dict(totals), "original_archive_sha256":
                  hashlib.sha256(source_zip.read_bytes()).hexdigest(),
              "json_archive_sha256":
                  hashlib.sha256(output_json.read_bytes()).hexdigest(),
              "yaml_archive_sha256":
                  hashlib.sha256(output_yaml.read_bytes()).hexdigest(),
              "original_oval_xml_roundtrip": False,
              "schema_promoted": False, "scanner_parity_proven": False,
              "changed_documents": proof,
              "sample_changed_sites": samples}
    output_ledger.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--canonical-zip", type=Path, required=True)
    p.add_argument("--json-zip", type=Path, required=True)
    p.add_argument("--yaml-zip", type=Path, required=True)
    p.add_argument("--ledger", type=Path, required=True)
    a = p.parse_args()
    for target in (a.json_zip, a.yaml_zip, a.ledger):
        target.parent.mkdir(parents=True, exist_ok=True)
    report = archive_preview(a.canonical_zip, a.json_zip, a.yaml_zip, a.ledger)
    print(json.dumps(report["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
