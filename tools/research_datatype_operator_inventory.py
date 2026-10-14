#!/usr/bin/env python3
"""Research-only inventory of SCAP-NG datatype authoring redundancy (#200).

Does NOT change published source, schemas, or package semantics.
The reversible in-memory trial proves only structural representability;
it does NOT establish scanner runtime or OVAL 5.12.3 conformance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import zipfile

import yaml


OPERATIONS = {
    "equals", "not_equal", "greater_than", "greater_than_or_equal",
    "less_than", "less_than_or_equal",
}


def analyze(archive_path: Path) -> dict:
    datatype_counts = Counter()
    operation_counts = Counter()
    classifications = Counter()
    source_categories = Counter()
    tricky_lexical_strings = 0
    total_yaml_bytes = 0
    datatype_line_bytes = 0
    structural_mismatches = []
    assessment_count = 0

    with zipfile.ZipFile(archive_path) as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            raise ValueError(f"Corrupt ZIP member: {bad_member}")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP member paths")
        for name in names:
            if not name.endswith(".yaml"):
                continue
            raw = archive.read(name)
            total_yaml_bytes += len(raw)
            datatype_line_bytes += sum(
                len(line) for line in raw.splitlines(keepends=True)
                if re.match(rb"^[ \t]*datatype:[ \t]*", line)
            )
            original = yaml.safe_load(raw)
            if not isinstance(original, dict) or len(original) != 1:
                raise ValueError(f"Invalid YAML document root: {name}")
            source_categories[next(iter(original))] += 1
            if "assessment" not in original:
                continue
            assessment_count += 1
            modified = deepcopy(original)
            deleted: dict[int, tuple[str, str | None]] = {}

            def forward(node):
                nonlocal tricky_lexical_strings
                if isinstance(node, dict):
                    if "datatype" in node:
                        datatype = node["datatype"]
                        op = node.get("operation")
                        datatype_counts[datatype] += 1
                        operation_counts[(datatype, op or "(none)")] += 1
                        value = node.get("value")
                        if "value" not in node:
                            classifications["typed_variable_or_expression"] += 1
                        elif isinstance(value, dict):
                            classifications["referenced_or_computed_value"] += 1
                        elif isinstance(value, list):
                            classifications["literal_collection"] += 1
                        elif datatype == "version" and type(value) is str and op in OPERATIONS:
                            node.pop("datatype")
                            node["operation"] = "version_" + op
                            deleted[id(node)] = (datatype, op)
                            classifications["candidate_specialized_operator"] += 1
                        elif (
                            (datatype == "string" and type(value) is str)
                            or (datatype == "integer" and type(value) is int)
                            or (datatype == "boolean" and type(value) is bool)
                        ):
                            if (datatype == "string"
                                    and (value.isdecimal()
                                         or value.lower() in {"true", "false"})):
                                tricky_lexical_strings += 1
                            node.pop("datatype")
                            deleted[id(node)] = (datatype, op)
                            classifications["candidate_native_scalar"] += 1
                        else:
                            classifications["needs_individual_review"] += 1
                    for child in node.values():
                        forward(child)
                elif isinstance(node, list):
                    for child in node:
                        forward(child)

            def reconstruct(node):
                if isinstance(node, dict):
                    if id(node) in deleted:
                        datatype, operation = deleted[id(node)]
                        node["datatype"] = datatype
                        if datatype == "version":
                            node["operation"] = operation
                    for child in node.values():
                        reconstruct(child)
                elif isinstance(node, list):
                    for child in node:
                        reconstruct(child)

            forward(modified)
            reconstruct(modified)
            if modified != original:
                structural_mismatches.append(name)

    if structural_mismatches:
        raise ValueError("Structural trial did not roundtrip: " +
                         ", ".join(structural_mismatches[:10]))
    return {
        "source_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        "assessment_count": assessment_count,
        "documents_by_kind": dict(sorted(source_categories.items())),
        "datatype_occurrences": dict(sorted(datatype_counts.items())),
        "total_datatype_occurrences": sum(datatype_counts.values()),
        "operation_datatype_pairs": {
            f"{datatype} | {operation}": amount
            for (datatype, operation), amount in sorted(operation_counts.items())
        },
        "classifications": dict(sorted(classifications.items())),
        "native_scalar_candidate_count": classifications["candidate_native_scalar"],
        "typed_version_operator_candidate_count":
            classifications["candidate_specialized_operator"],
        "potentially_removable_authored_fields":
            classifications["candidate_native_scalar"] +
            classifications["candidate_specialized_operator"],
        "not_yet_proven_safe_to_remove":
            classifications["typed_variable_or_expression"] +
            classifications["referenced_or_computed_value"] +
            classifications["literal_collection"] +
            classifications["needs_individual_review"],
        "numeric_or_boolean_looking_string_literals": tricky_lexical_strings,
        "yaml_bytes_uncompressed": total_yaml_bytes,
        "datatype_lines_bytes_uncompressed": datatype_line_bytes,
        "structural_trial_mismatches": len(structural_mismatches),
        "proof_limit": "In-memory original-AST recovery only. No schema, runtime, "
                       "migrated OVAL item comparison, or SCAP conformance proof.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("authoring_zip", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = analyze(args.authoring_zip)
    output = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
