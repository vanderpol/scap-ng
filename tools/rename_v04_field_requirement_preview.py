#!/usr/bin/env python3
"""Source-reversible renaming of scalar field requirements in 0.4 research YAML.

This tool does not change the versioned schema, runtime semantics or published
archives. It rewrites only complete, simple fields-only Test conditions for
which a Test-wide field requirement has a provably identical descendant scope.
The enclosing condition logic and source values remain untouched.

Refs #248 #239.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import yaml

OPS = ("and", "or", "one", "xor")
REQUIREMENT = "field_requirement"


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode()).hexdigest()


class UnsafeScope(ValueError):
    """Cannot prove that a key rename has the same field-level scope."""


def migrate_test(test):
    """Return (rewritten Test, invertible ledger), or unchanged Test and None."""
    source = deepcopy(test)
    out = deepcopy(test)
    req = out.get("require")
    if (not isinstance(req, dict)
            or not isinstance(req.get("all_items_must"), list)
            or not req["all_items_must"]
            or "states_match" in out or "states" in out
            or "field_requirement" in req):
        return source, None

    edits = []
    groups = 0
    local = 0
    leaves = 0

    def rename(node, old, path):
        if old in node:
            if REQUIREMENT in node:
                raise UnsafeScope("Two spellings for one requirement")
            value = node.pop(old)
            if not isinstance(value, str):
                raise UnsafeScope("Requirement must be an explicit token")
            node[REQUIREMENT] = value
            edits.append({"path": list(path), "old": old,
                          "value": value})

    def visit(node, path):
        nonlocal groups, local, leaves
        if not isinstance(node, dict) or not node:
            raise UnsafeScope("Empty or nonmapping condition")
        if "fields" in node:
            if set(node) - {"fields", "require"}:
                raise UnsafeScope("Unsupported or mixed fields group")
            fields = node["fields"]
            if (not isinstance(fields, dict) or len(fields) < 2
                    or any(not isinstance(name, str) or not name
                           or not isinstance(value, dict) or not value
                           or "record" in value or REQUIREMENT in value
                           for name, value in fields.items())):
                raise UnsafeScope("Record/repeated/single-field case not proven")
            groups += 1
            if "require" in node:
                rename(node, "require", path)
                local += 1
            for name, value in fields.items():
                if "require" in value:
                    rename(value, "require", path + ("fields", name))
                    leaves += 1
            return
        ops = [key for key in OPS if key in node]
        if len(ops) != 1 or set(node) - {ops[0], "require", "state_fields_require"}:
            raise UnsafeScope("Not solely complete fields and logical groups")
        op = ops[0]
        children = node[op]
        if not isinstance(children, list) or not children:
            raise UnsafeScope("Missing logical operands")
        if "require" in node and "state_fields_require" in node:
            raise UnsafeScope("Conflicting old logical-group requirements")
        for index, child in enumerate(children):
            visit(child, path + (op, index))
        if "require" in node:
            rename(node, "require", path)
        if "state_fields_require" in node:
            rename(node, "state_fields_require", path)

    try:
        for i, clause in enumerate(req["all_items_must"]):
            visit(clause, ("require", "all_items_must", i))
        if not groups:
            return source, None
        # An explicit top-level Test State-field requirement moves to the
        # Test's require mapping, without changing its descendant scope.
    except UnsafeScope:
        return source, None

    # Rename the Test-level source field, independently of condition fields.
    # Keep the original Test requirement untouched except this one added key.
    if "state_fields_require" in out:
        if REQUIREMENT in req:
            return source, None
        value = out.pop("state_fields_require")
        if not isinstance(value, str):
            return source, None
        req[REQUIREMENT] = value
        edits.append({"path": ["require"], "old": "@test.state_fields_require",
                      "value": value})

    if not edits:
        return source, None
    proof = {"before_sha256": fingerprint(source),
             "after_sha256": fingerprint(out), "edits": edits,
             "field_groups": groups, "local_groups": local,
             "field_overrides": leaves}
    if restore_test(out, proof) != source:
        raise ValueError("Renaming failed source inversion")
    return out, proof


def lookup(root, path):
    result = root
    for key in path:
        result = result[key]
    return result


def restore_test(candidate, proof):
    if fingerprint(candidate) != proof["after_sha256"]:
        raise ValueError("Field requirement candidate has been edited")
    restored = deepcopy(candidate)
    for edit in reversed(proof["edits"]):
        node = lookup(restored, edit["path"])
        old = edit["old"]
        if node.get(REQUIREMENT) != edit["value"]:
            raise ValueError("Field requirement or its effective scope changed")
        value = node.pop(REQUIREMENT)
        if old == "@test.state_fields_require":
            if "state_fields_require" in restored:
                raise ValueError("Duplicate restored Test requirement")
            restored["state_fields_require"] = value
        else:
            if old in node:
                raise ValueError("Duplicate restored requirement")
            node[old] = value
    if fingerprint(restored) != proof["before_sha256"]:
        raise ValueError("Renamed Test cannot recover exact source graph")
    return restored


def migrate_document(source):
    result = deepcopy(source)
    a = result.get("assessment") if isinstance(result, dict) else None
    changed = []
    if isinstance(a, dict) and a.get("mode") == "automated":
        for test_id, source_test in list((a.get("tests") or {}).items()):
            converted, proof = migrate_test(source_test)
            if proof:
                a["tests"][test_id] = converted
                changed.append({"test": test_id, **proof})
                if restore_test(converted, proof) != source_test:
                    raise ValueError("Document Test source changed")
    return result, changed


def migrate_archive(original_zip, json_zip, yaml_zip, ledger_path):
    counts = Counter()
    changed = []
    with ZipFile(original_zip) as original, \
         ZipFile(json_zip, "w", ZIP_DEFLATED) as jzip, \
         ZipFile(yaml_zip, "w", ZIP_DEFLATED) as yzip:
        for name in original.namelist():
            if not name.startswith("authoring/") or not name.endswith(".json"):
                raise ValueError("Unexpected input ZIP member: " + name)
            source = json.loads(original.read(name))
            after, proofs = migrate_document(source)
            if proofs:
                counts["affected_documents"] += 1
                for proof in proofs:
                    counts["changed_tests"] += 1
                    counts["field_groups"] += proof["field_groups"]
                    counts["local_groups"] += proof["local_groups"]
                    counts["field_overrides"] += proof["field_overrides"]
                changed.append({"path": name, "before": fingerprint(source),
                                "after": fingerprint(after), "tests": proofs})
            counts["documents"] += 1
            assert fingerprint(after) == fingerprint(json.loads(json.dumps(after)))
            jzip.writestr(name, json.dumps(after, indent=2,
                                          ensure_ascii=False) + "\n")
            rendered = yaml.safe_dump(after, sort_keys=False, allow_unicode=True)
            if yaml.safe_load(rendered) != after:
                raise ValueError("YAML changed requirement scopes")
            yzip.writestr(name.removesuffix(".json") + ".yaml", rendered)
    if counts["documents"] != 4001:
        raise ValueError("Unexpected six-STIG document count")
    result = {"status": "RESEARCH_ONLY_EXACT_TEST_SOURCE_INVERSE",
              "counts": dict(counts), "changed": changed,
              "input_sha256": sha256(original_zip.read_bytes()).hexdigest(),
              "candidate_sha256": sha256(json_zip.read_bytes()).hexdigest(),
              "candidate_yaml_sha256": sha256(yaml_zip.read_bytes()).hexdigest(),
              "native_schema_promoted": False,
              "scanner_semantics_proven": False}
    ledger_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-json", type=Path, required=True)
    parser.add_argument("--candidate-json", type=Path, required=True)
    parser.add_argument("--candidate-yaml", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    args = parser.parse_args()
    for target in (args.candidate_json, args.candidate_yaml, args.proof):
        target.parent.mkdir(parents=True, exist_ok=True)
    result = migrate_archive(args.source_json, args.candidate_json,
                             args.candidate_yaml, args.proof)
    print(json.dumps({k:v for k,v in result.items() if k!="changed"},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
