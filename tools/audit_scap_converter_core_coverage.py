#!/usr/bin/env python3
"""Read-only original OVAL coverage accounting for the maintained 0.4 core.

Separate the mature 0.3 source-lowering numerator from independently accepted
native 0.4 output. A successful 0.3 lowering is NOT native 0.4 support;
neither is evidence of scanner six-state parity. Refs #232 #248 #229.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator

from oval_semantic_ir import parse as parse_oval
from scap_converter_core import convert
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.convert_collection_review import postprocess_automated_assessment
from v04_native_bundle_compiler import compile_assessment_program


FORMAT = "scap-ng-maintained-converter-oval-coverage/0.1"
from v04_canonical_source_ir import _schema_validators
SCHEMA = _schema_validators(Path(__file__).resolve().parents[1] / 'schema/v0.4.0')['assessment']


def safe_error(exc):
    # Keep errors actionable but avoid embedding an entire OVAL XML payload or
    # an arbitrary large third-party exception in the published JSON report.
    return f"{type(exc).__name__}: {str(exc)[:450]}"


def source_files(source: Path):
    source = Path(source).resolve()
    if source.is_file():
        return source, [source]
    if not source.is_dir():
        raise ValueError("--source must identify an OVAL XML file or a directory")
    files = sorted(path for path in source.rglob("*.xml") if path.is_file())
    if not files:
        raise ValueError("no OVAL *.xml files found in --source")
    return source, files


def v003_shape(assessment):
    """Summarize *preserved* source semantics without treating them as 0.4."""
    tests = assessment.get("tests") or {}
    objects = assessment.get("objects") or {}
    states = assessment.get("states") or {}
    variables = assessment.get("variables") or {}

    def contains(node, key):
        if isinstance(node, dict):
            return key in node or any(contains(child, key) for child in node.values())
        if isinstance(node, list):
            return any(contains(child, key) for child in node)
        return False

    return {
        "tests": len(tests),
        "objects": len(objects),
        "states": len(states),
        "variables": len(variables),
        "capabilities": sorted({test["capability"] for test in tests.values()
                                if isinstance(test, dict) and isinstance(test.get("capability"), str)}),
        "test_quantifiers": sorted({
            f"{test.get('existence', 'missing')}|{test.get('match', 'missing')}"
            for test in tests.values() if isinstance(test, dict)
        }),
        "evaluate_root": next(iter(assessment.get("evaluate") or {}), "none"),
        "has_sets": contains(objects, "set"),
        "has_filters": contains(objects, "filters"),
    }


def unresolved_shape_summary(rows):
    """Prioritize missing *families* rather than publishing a one-off list."""
    blocked = [r for r in rows if r.get("v003_source_lowering") == "PASS"
               and r.get("maintained_v004_core") == "BLOCKED"]
    caps = Counter()
    patterns = Counter()
    examples = {}
    simple_quantifiers = Counter()
    simple_examples = {}
    for item in blocked:
        shape = item["v003_shape"]
        for capability in shape["capabilities"]:
            caps[capability] += 1
            examples.setdefault(capability, {
                "source_file": item["source_file"],
                "definition_id": item["definition_id"],
                "shape": shape,
            })
        pattern = (f"T{shape['tests']}/O{shape['objects']}/S{shape['states']}"
                   f"/V{shape['variables']}/Set{int(shape['has_sets'])}"
                   f"/Filter{int(shape['has_filters'])}"
                   f"/{shape['evaluate_root']}")
        patterns[pattern] += 1
        if (shape["tests"] == 1 and shape["objects"] == 1
                and shape["states"] == 0 and shape["variables"] == 0
                and not shape["has_sets"] and not shape["has_filters"]):
            quantifier = ",".join(shape["test_quantifiers"])
            simple_quantifiers[quantifier] += 1
            simple_examples.setdefault(quantifier, {
                "source_file": item["source_file"],
                "definition_id": item["definition_id"],
                "capabilities": shape["capabilities"],
            })
    return {
        "blocked_0_3_lowerable_definitions": len(blocked),
        "by_capability": dict(caps.most_common()),
        "by_semantic_shape": dict(patterns.most_common()),
        "first_source_per_capability": examples,
        "simple_object_only_by_test_quantifiers": dict(simple_quantifiers.most_common()),
        "simple_object_only_examples": simple_examples,
    }


def inventory(source: Path):
    root_path, files = source_files(source)
    counts = Counter()
    diagnostics = Counter()
    rows = []
    for path in files:
        counts["xml_files"] += 1
        relative = path.relative_to(root_path).as_posix() if root_path.is_dir() else path.name
        try:
            raw = path.read_bytes()
            root = ET.fromstring(raw)
            graph = parse_oval(path)
        except (OSError, ValueError, ET.ParseError) as exc:
            counts["source_parse_blocked_files"] += 1
            rows.append({"source_file": relative, "source_parse": "BLOCKED",
                         "diagnostic": safe_error(exc)})
            continue
        definitions = graph.get("definitions", [])
        if not definitions:
            counts["xml_without_definitions"] += 1
        for definition in definitions:
            did = definition.get("id")
            counts["definitions"] += 1
            item = {"source_file": relative, "definition_id": did,
                    "source_sha256": sha256(raw).hexdigest(),
                    "v003_source_lowering": "BLOCKED",
                    "maintained_v004_core": "BLOCKED",
                    "scanner_parity": "NOT_PROVEN"}
            if definition.get("deprecated") in ("true", "1"):
                counts["deprecated_definitions"] += 1
                item["v003_diagnostic"] = "deprecated OVAL Definition"
                item["v004_diagnostic"] = "deprecated OVAL Definition"
                rows.append(item)
                continue
            counts["nondeprecated_definitions"] += 1
            ident = "oval-source-" + sha256(did.encode()).hexdigest()[:18]
            try:
                lowered, err = lower_definition(
                    root, did, ident, collection_graph=True, provenance={})
                if err is not None:
                    raise ValueError(str(err))
                aligned, modern = postprocess_automated_assessment(
                    lowered, target_ng_version="0.3.0")
                if aligned.get("assessment", {}).get("specification", {}).get("version") != "0.3.0":
                    raise ValueError("0.3 capability graph not aligned")
                item["v003_source_lowering"] = "PASS"
                counts["v003_source_lowering_pass"] += 1
                item["v003_shape"] = v003_shape(aligned["assessment"])
                if modern is not None:
                    item["v003_modernization_report_present"] = True
            except (TypeError, KeyError, ValueError, IndexError, AttributeError) as exc:
                item["v003_diagnostic"] = safe_error(exc)
            try:
                native, evidence = convert(path, did)
                if native["assessment"]["specification"]["version"] != "0.4.0":
                    raise ValueError("converter did not emit native 0.4")
                error = next(SCHEMA.iter_errors(native), None)
                if error is not None:
                    raise ValueError("native 0.4 schema invalid: " + error.message)
                compile_assessment_program(native["assessment"])
                if evidence.get("full_oval_coverage") is not False:
                    raise ValueError("incorrect native coverage evidence")
                item["maintained_v004_core"] = "SOURCE_PROVEN"
                item["capability"] = evidence["capability"]
                if evidence.get("original_oval_pinned_direct_graph_attested"):
                    item["source_sha256"] = evidence["source_sha256"]
                    item["pinned_direct_lowering_sha256"] = evidence["pinned_direct_lowering_sha256"]
                counts["maintained_v004_core_source_proven"] += 1
            except (TypeError, KeyError, ValueError, IndexError, AttributeError) as exc:
                item["v004_diagnostic"] = safe_error(exc)
                diagnostics[item["v004_diagnostic"].split(":", 1)[0]] += 1
            if item["v003_source_lowering"] == "PASS" and item["maintained_v004_core"] == "BLOCKED":
                counts["v003_lowerable_but_v004_unproved"] += 1
            rows.append(item)
    if not counts["definitions"]:
        raise ValueError("no OVAL Definition found under --source")
    counts["v003_source_lowering_blocked_nondeprecated"] = (
        counts["nondeprecated_definitions"] - counts["v003_source_lowering_pass"])
    counts["maintained_v004_core_blocked_nondeprecated"] = (
        counts["nondeprecated_definitions"] - counts["maintained_v004_core_source_proven"])
    return {
        "format": FORMAT,
        "source": str(root_path),
        "counts": dict(sorted(counts.items())),
        "v004_error_class_counts": dict(sorted(diagnostics.items())),
        "lowerable_but_unproved": unresolved_shape_summary(rows),
        "definitions": sorted(rows, key=lambda row: (
            row["source_file"], row.get("definition_id", ""))),
        "full_oval_coverage": False,
        "scanner_parity": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path,
                   help="Original OVAL XML or directory (recursively enumerate *.xml)")
    p.add_argument("--report", required=True, type=Path)
    args = p.parse_args()
    result = inventory(args.source)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "counts": result["counts"],
        "top_blocked_capabilities": list(
            result["lowerable_but_unproved"]["by_capability"].items())[:25],
        "top_blocked_shapes": list(
            result["lowerable_but_unproved"]["by_semantic_shape"].items())[:15],
        "source_example_per_capability": result["lowerable_but_unproved"]["first_source_per_capability"],
        "simple_object_only": {
            "by_test_quantifier": result["lowerable_but_unproved"]["simple_object_only_by_test_quantifiers"],
            "examples": result["lowerable_but_unproved"]["simple_object_only_examples"],
        },
    }, sort_keys=True))


if __name__ == "__main__":
    main()
