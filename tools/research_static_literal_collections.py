#!/usr/bin/env python3
"""Research proof for replacing static constant Variables with native literals.

Accepted SCAP-NG 0.3 transform proof. This utility does not modify source files.
It proves that the bounded static-literal transform can inline constant Variable
values and structurally re-expand the original document.
"""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path

import yaml


def walk_variable_refs(value, variable_id, path=()):
    if isinstance(value, dict):
        if value == {"variable": variable_id}:
            yield path
        for key, child in value.items():
            yield from walk_variable_refs(child, variable_id, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_variable_refs(child, variable_id, path + (index,))


def path_parent(root, path):
    node = root
    for step in path[:-1]:
        node = node[step]
    return node, path[-1]


def native_literal(value, datatype):
    """Normalize constant lexical values to the native JSON representation."""
    if isinstance(value,list):
        if not value:
            raise ValueError("constant literal collection must not be empty")
        return [native_literal(item,datatype) for item in value]
    if datatype=="integer":
        if isinstance(value,int) and not isinstance(value,bool):
            return value
        if isinstance(value,str):
            return int(value,10)
        raise ValueError(f"invalid integer constant literal: {value!r}")
    if datatype=="float":
        if isinstance(value,bool):
            raise ValueError(f"invalid float constant literal: {value!r}")
        if isinstance(value,(int,float)):
            return float(value)
        if isinstance(value,str):
            return float(value)
        raise ValueError(f"invalid float constant literal: {value!r}")
    if datatype=="boolean":
        if isinstance(value,bool):
            return value
        if isinstance(value,str):
            normalized=value.strip().lower()
            if normalized in {"true","1"}:
                return True
            if normalized in {"false","0"}:
                return False
        raise ValueError(f"invalid boolean constant literal: {value!r}")
    return copy.deepcopy(value)


def constant_literal(payload):
    if not isinstance(payload, dict) or payload.get("kind") != "constant":
        return None, False
    expression = payload.get("expression")
    if not isinstance(expression, dict) or set(expression) != {"literal"}:
        return None, False
    try:
        return native_literal(expression["literal"],payload.get("datatype")), True
    except (TypeError,ValueError):
        # Fail closed at the transform boundary: malformed/non-native constants
        # remain named for ordinary validation instead of being partially folded.
        return None, False


def classify_collection_path(path):
    text = "/".join(str(part) for part in path)
    if "/states/" in f"/{text}/":
        return "state_collection_ref"
    if "/object/" in f"/{text}/" or "/objects/" in f"/{text}/":
        return "object_collection_ref"
    return "other_collection_ref"


def inline_constants(document):
    rendered = copy.deepcopy(document)
    assessment = rendered.get("assessment")
    if not isinstance(assessment, dict):
        return rendered, []

    variables = assessment.get("variables")
    if not isinstance(variables, dict):
        return rendered, []

    proof = []
    for variable_id, payload in list(variables.items()):
        literal, supported = constant_literal(payload)
        if not supported:
            continue

        refs = list(walk_variable_refs(assessment, variable_id))
        if not refs:
            continue

        # Automatic folding is atomic per Variable. If any reference is not in
        # the proven literal-replacement class, leave the Variable and every
        # reference unchanged rather than partially rewriting or failing the
        # containing Assessment/package.
        planned = []
        supported = True
        for path in refs:
            parent, last = path_parent(assessment, path)
            if parent[last] != {"variable": variable_id}:
                supported = False
                break

            if isinstance(literal, list):
                if not path or path[-1] != "value":
                    supported = False
                    break
                replacement = copy.deepcopy(literal)
                mode = classify_collection_path(path)
            elif path and path[-1] == "value":
                replacement = copy.deepcopy(literal)
                mode = "direct_scalar_ref"
            else:
                replacement = {"literal": copy.deepcopy(literal)}
                mode = "expression_scalar_ref"
            planned.append((path, replacement, mode))

        if not supported:
            continue

        for path, replacement, mode in planned:
            parent, last = path_parent(assessment, path)
            parent[last] = copy.deepcopy(replacement)
            proof.append(
                {
                    "variable": variable_id,
                    "path": list(path),
                    "literal": copy.deepcopy(literal),
                    "mode": mode,
                    "payload": copy.deepcopy(payload),
                }
            )

        variables.pop(variable_id)

    if not variables:
        assessment.pop("variables", None)

    return rendered, proof


def reexpand_constants(document, proof):
    restored = copy.deepcopy(document)
    if not proof:
        return restored
    assessment = restored["assessment"]
    variables = assessment.setdefault("variables", {})

    payloads = {}
    for row in proof:
        path = tuple(row["path"])
        parent, last = path_parent(assessment, path)
        expected = (
            {"literal": row["literal"]}
            if row["mode"] == "expression_scalar_ref"
            else row["literal"]
        )
        if parent[last] != expected:
            raise ValueError(
                f"inline payload changed for {row['variable']!r} at {path!r}"
            )
        parent[last] = {"variable": row["variable"]}
        payloads[row["variable"]] = copy.deepcopy(row["payload"])

    for variable_id, payload in payloads.items():
        variables[variable_id] = payload

    return restored


def yaml_metrics(document):
    text = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
    return len(text.splitlines()), len(text.encode("utf-8"))


def build_report(root: Path):
    counts = Counter()
    mismatches = []
    changed_files = []

    for path in sorted(root.rglob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict) or not isinstance(
            document.get("assessment"), dict
        ):
            continue

        rendered, proof = inline_constants(document)
        if not proof:
            continue

        restored = reexpand_constants(rendered, proof)
        if restored != document:
            mismatches.append(str(path.relative_to(root)))
            continue

        before_lines, before_bytes = yaml_metrics(document)
        after_lines, after_bytes = yaml_metrics(rendered)

        variables = {row["variable"] for row in proof}
        counts["files_changed"] += 1
        counts["constant_variables_removed"] += len(variables)
        counts["references_replaced"] += len(proof)
        counts["before_lines"] += before_lines
        counts["after_lines"] += after_lines
        counts["before_bytes"] += before_bytes
        counts["after_bytes"] += after_bytes
        counts.update(row["mode"] for row in proof)

        changed_files.append(
            {
                "path": str(path.relative_to(root)),
                "constant_variables_removed": len(variables),
                "references_replaced": len(proof),
            }
        )

    report = {
        "format": "scap-ng-static-literal-collection-proof-0.1",
        "status": "accepted_0_3_transform_proof",
        "root": str(root),
        "summary": dict(counts),
        "round_trip_mismatches": mismatches,
        "changed_files": changed_files,
    }

    if counts["before_lines"]:
        report["summary"]["line_change_percent"] = round(
            100.0
            * (counts["after_lines"] - counts["before_lines"])
            / counts["before_lines"],
            2,
        )
    if counts["before_bytes"]:
        report["summary"]["byte_change_percent"] = round(
            100.0
            * (counts["after_bytes"] - counts["before_bytes"])
            / counts["before_bytes"],
            2,
        )

    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_report(args.root)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")

    if report["round_trip_mismatches"]:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
