#!/usr/bin/env python3
"""Identify OVAL dataflow shapes that may be modernizable as SCAP-NG foreach.

This is a read-only research analyzer. It does not rewrite OVAL or SCAP-NG.
It intentionally fails closed: direct projection candidates remain
"review_required" until a separately reviewed equivalence rule exists.

The modeled proof families are:

    source Object
      -> local_variable(object_component item_field=...)
      -> target Object entity var_ref

and the bounded unary-transform form:

    source Object
      -> object_component
      -> concat(singleton literals + one projected value)
      -> target Object entity var_ref

These shapes can be representation plumbing for collection expansion. General
multi-input concat remains review-required. The analyzer preserves the target
aggregation boundary and does NOT infer per-source-item Test evaluation.

Inputs may be standalone OVAL XML, SCAP datastream XML containing embedded
oval_definitions components, ZIP packages containing XML, or directories.

Usage:
    python tools/analyze_oval_foreach_candidates.py FILE_OR_DIR [...]
    python tools/analyze_oval_foreach_candidates.py ... --output report.json
"""
from __future__ import annotations

import argparse
from collections import Counter
import io
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from foreach_equivalence import (
    direct_foreach_preconditions,
    unary_concat_foreach_preconditions,
)


CROSS_PRODUCT_OR_MULTI_INPUT_OPS = {
    "arithmetic",
    "concat",
    "merge",
    "time_difference",
}


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def iter_inputs(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for path in paths:
        if path.is_dir():
            out.extend(
                sorted(
                    p
                    for p in path.rglob("*")
                    if p.is_file() and p.suffix.lower() in {".xml", ".zip"}
                )
            )
        elif path.is_file():
            out.append(path)
        else:
            raise FileNotFoundError(path)
    seen = set()
    unique = []
    for path in out:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def section_nodes(root: ET.Element, section_name: str) -> list[ET.Element]:
    for child in root:
        if local(child.tag) == section_name:
            return [x for x in child if isinstance(x.tag, str)]
    return []


def expression_shape(variable: ET.Element) -> dict:
    children = [x for x in variable if isinstance(x.tag, str)]
    if len(children) != 1:
        return {
            "kind": "invalid_component_count",
            "count": len(children),
            "automatic_blocker": True,
        }

    expr = children[0]
    op = local(expr.tag)
    if op == "object_component":
        return {
            "kind": "direct_object_projection",
            "op": op,
            "object_ref": expr.get("object_ref"),
            "item_field": expr.get("item_field"),
            "record_field": expr.get("record_field"),
            "automatic_blocker": False,
        }

    # Bounded second proof class: exactly one collection-valued
    # object_component with only singleton string literal operands around it.
    # OVAL concat is Cartesian in the general case, but one dynamic operand
    # degenerates to a one-to-one value map.
    if op == "concat":
        operands = [x for x in expr if isinstance(x.tag, str)]
        object_operands = [x for x in operands if local(x.tag) == "object_component"]
        other_operands = [x for x in operands if local(x.tag) != "object_component"]
        literals_only = bool(other_operands) and all(
            local(x.tag) == "literal_component"
            and (x.get("datatype") in {None, "string"})
            for x in other_operands
        )
        if len(object_operands) == 1 and literals_only:
            projected = object_operands[0]
            object_index = operands.index(projected)
            before = operands[:object_index]
            after = operands[object_index + 1:]
            if all(local(x.tag) == "literal_component" for x in before + after):
                return {
                    "kind": "unary_concat_object_projection",
                    "op": op,
                    "object_ref": projected.get("object_ref"),
                    "item_field": projected.get("item_field"),
                    "record_field": projected.get("record_field"),
                    "prefix": "".join((x.text or "") for x in before),
                    "suffix": "".join((x.text or "") for x in after),
                    "collection_operands": 1,
                    "dynamic_operands": 1,
                    "nested_functions": 0,
                    "source_datatype": variable.get("datatype") or "string",
                    "operations": [
                        local(x.tag)
                        for x in expr.iter()
                        if isinstance(x.tag, str)
                    ],
                    "cross_product_risk": False,
                    "automatic_blocker": False,
                }

    object_components = []
    operations = []
    for node in expr.iter():
        if not isinstance(node.tag, str):
            continue
        name = local(node.tag)
        operations.append(name)
        if name == "object_component":
            object_components.append({
                "object_ref": node.get("object_ref"),
                "item_field": node.get("item_field"),
                "record_field": node.get("record_field"),
            })

    return {
        "kind": "derived_expression",
        "op": op,
        "operations": operations,
        "object_components": object_components,
        "cross_product_risk": any(x in CROSS_PRODUCT_OR_MULTI_INPUT_OPS for x in operations),
        "automatic_blocker": True,
    }


def object_features(obj: ET.Element) -> dict:
    filters = []
    sets = []
    behaviors = []
    entities = []
    for node in obj.iter():
        if node is obj or not isinstance(node.tag, str):
            continue
        name = local(node.tag)
        if name == "filter":
            filters.append({
                "action": node.get("action", "exclude"),
                "state_ref": (node.text or "").strip() or None,
            })
        elif name == "set":
            sets.append({
                "operator": node.get("set_operator", "UNION"),
                "operator_explicit": "set_operator" in node.attrib,
            })
        elif name == "behaviors":
            behaviors.append(dict(sorted(node.attrib.items())))
        elif node.get("var_ref"):
            entities.append({
                "name": name,
                "var_ref": node.get("var_ref"),
                "var_check": node.get("var_check") or "all",
                "var_check_explicit": "var_check" in node.attrib,
                "operation": node.get("operation") or "equals",
                "datatype": node.get("datatype") or "string",
            })
    return {
        "filters": filters,
        "sets": sets,
        "behaviors": behaviors,
        "variable_entities": entities,
    }


def index_document(root: ET.Element) -> dict:
    objects = {x.get("id"): x for x in section_nodes(root, "objects") if x.get("id")}
    variables = {x.get("id"): x for x in section_nodes(root, "variables") if x.get("id")}
    tests = {x.get("id"): x for x in section_nodes(root, "tests") if x.get("id")}

    variable_consumers: dict[str, list[dict]] = {}
    for object_id, obj in objects.items():
        for node in obj.iter():
            if not isinstance(node.tag, str):
                continue
            var_ref = node.get("var_ref")
            if not var_ref:
                continue
            variable_consumers.setdefault(var_ref, []).append({
                "context": "object_selector",
                "object_id": object_id,
                "object_type": local(obj.tag),
                "entity": local(node.tag),
                "operation": node.get("operation") or "equals",
                "datatype": node.get("datatype") or "string",
                "var_check": node.get("var_check") or "all",
                "var_check_explicit": "var_check" in node.attrib,
            })

    target_tests: dict[str, list[dict]] = {}
    for test_id, test in tests.items():
        for child in test:
            if local(child.tag) != "object":
                continue
            object_ref = child.get("object_ref")
            if not object_ref:
                continue
            target_tests.setdefault(object_ref, []).append({
                "test_id": test_id,
                "test_type": local(test.tag),
                "check": test.get("check"),
                "check_existence": test.get("check_existence") or "at_least_one_exists",
                "state_operator": test.get("state_operator") or "AND",
            })

    return {
        "objects": objects,
        "variables": variables,
        "tests": tests,
        "variable_consumers": variable_consumers,
        "target_tests": target_tests,
    }


def classify_candidate(
    variable_id: str,
    variable: ET.Element,
    index: dict,
) -> dict | None:
    consumers = index["variable_consumers"].get(variable_id, [])
    if not consumers:
        return None

    shape = expression_shape(variable)
    base = {
        "variable_id": variable_id,
        "variable_type": local(variable.tag),
        "datatype": variable.get("datatype"),
        "expression": shape,
        "consumers": consumers,
    }

    if local(variable.tag) != "local_variable":
        return {
            **base,
            "classification": "not_applicable",
            "candidate_family": None,
            "reasons": ["selector_variable_is_not_local_variable"],
        }

    if shape["kind"] not in {
        "direct_object_projection",
        "unary_concat_object_projection",
    }:
        reasons = ["variable_expression_is_not_supported_projection_shape"]
        if shape.get("cross_product_risk"):
            reasons.append("multi_input_or_cartesian_semantics_may_be_present")
        return {
            **base,
            "classification": "review_required",
            "candidate_family": "derived_projection",
            "projection_mode": shape.get("kind"),
            "reasons": reasons,
        }

    projection_mode = (
        "direct"
        if shape["kind"] == "direct_object_projection"
        else "unary_literal_concat"
    )
    source_object_id = shape.get("object_ref")
    source_obj = index["objects"].get(source_object_id)
    if source_obj is None:
        return {
            **base,
            "classification": "blocked",
            "candidate_family": "collection_expansion",
            "reasons": ["source_object_unresolved"],
        }

    target_details = []
    for consumer in consumers:
        target_object_id = consumer["object_id"]
        target_obj = index["objects"].get(target_object_id)
        target_details.append({
            **consumer,
            "object_features": object_features(target_obj),
            "tests": index["target_tests"].get(target_object_id, []),
        })

    selector_checks = sorted({consumer["var_check"] for consumer in consumers})
    if selector_checks == ["at least one"]:
        candidate_family = "collection_expansion_at_least_one"
        quantifier_reason = "selector_accepts_at_least_one_projected_value"
    elif selector_checks == ["all"]:
        candidate_family = "quantified_projection_all_values"
        quantifier_reason = "selector_requires_comparison_against_all_projected_values"
    else:
        candidate_family = "mixed_selector_quantification"
        quantifier_reason = "projected_variable_is_shared_across_different_var_check_semantics"

    reasons = [
        (
            "direct_object_component_projection_into_object_selector"
            if projection_mode == "direct"
            else "unary_literal_concat_projection_into_object_selector"
        ),
        quantifier_reason,
        "collection_aggregation_boundary_must_be_preserved",
        "equivalence_fixture_required_before_safe_automatic",
    ]
    if len(consumers) > 1:
        reasons.append("shared_projected_variable_has_multiple_target_consumers")

    result = {
        **base,
        "classification": "review_required",
        "candidate_family": candidate_family,
        "projection_mode": projection_mode,
        "source": {
            "object_id": source_object_id,
            "object_type": local(source_obj.tag),
            "item_field": shape.get("item_field"),
            "record_field": shape.get("record_field"),
            "object_features": object_features(source_obj),
        },
        "targets": target_details,
        "reasons": reasons,
    }
    if projection_mode == "direct":
        proof = direct_foreach_preconditions(result)
        result["first_proof_class"] = proof
    else:
        proof = unary_concat_foreach_preconditions(result)
        result["unary_concat_proof_class"] = proof

        # Full OVAL components often share one local Variable across multiple
        # Tests/Rules. SCAP-NG conversion is Rule/Assessment scoped, so quantify
        # whether each individual target consumer fits the proof class without
        # declaring the shared source graph globally rewriteable.
        scoped = []
        for target in target_details:
            scoped_candidate = {
                **result,
                "targets": [target],
            }
            scoped_proof = unary_concat_foreach_preconditions(scoped_candidate)
            scoped.append({
                "object_id": target["object_id"],
                "entity": target["entity"],
                "test_ids": [x["test_id"] for x in target.get("tests", [])],
                "proof": scoped_proof,
            })
        result["target_scoped_unary_concat_proofs"] = scoped
    return result


def analyze_oval_root(root: ET.Element, source_label: str) -> dict:
    index = index_document(root)
    candidates = []
    for variable_id, variable in sorted(index["variables"].items()):
        candidate = classify_candidate(variable_id, variable, index)
        if candidate is not None:
            candidates.append(candidate)

    counts = Counter(x["classification"] for x in candidates)
    families = Counter(x.get("candidate_family") or "none" for x in candidates)
    return {
        "path": source_label,
        "status": "ok",
        "counts": dict(sorted(counts.items())),
        "families": dict(sorted(families.items())),
        "candidates": candidates,
    }


def oval_roots(root: ET.Element) -> list[ET.Element]:
    if local(root.tag) == "oval_definitions":
        return [root]
    return [
        node
        for node in root.iter()
        if isinstance(node.tag, str) and local(node.tag) == "oval_definitions"
    ]


def analyze_xml_bytes(data: bytes, source_label: str) -> list[dict]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        return [{
            "path": source_label,
            "status": "parse_error",
            "error": str(exc),
            "candidates": [],
        }]

    roots = oval_roots(root)
    if not roots:
        return [{
            "path": source_label,
            "status": "no_oval_definitions",
            "candidates": [],
        }]
    return [
        analyze_oval_root(
            oval_root,
            source_label if len(roots) == 1 else f"{source_label}#oval[{i}]",
        )
        for i, oval_root in enumerate(roots, start=1)
    ]


def analyze_input(path: Path) -> list[dict]:
    if path.suffix.lower() != ".zip":
        return analyze_xml_bytes(path.read_bytes(), str(path))

    rows = []
    try:
        with zipfile.ZipFile(path) as archive:
            members = sorted(
                info
                for info in archive.infolist()
                if not info.is_dir() and info.filename.lower().endswith(".xml")
            )
            if not members:
                return [{
                    "path": str(path),
                    "status": "zip_has_no_xml",
                    "candidates": [],
                }]
            for info in members:
                with archive.open(info) as stream:
                    data = stream.read()
                rows.extend(analyze_xml_bytes(data, f"{path}!{info.filename}"))
    except zipfile.BadZipFile as exc:
        return [{
            "path": str(path),
            "status": "bad_zip",
            "error": str(exc),
            "candidates": [],
        }]
    return rows


def analyze_file(path: Path) -> dict:
    """Compatibility helper for focused tests expecting one standalone OVAL XML."""
    rows = analyze_input(path)
    if len(rows) != 1:
        raise ValueError(f"expected one analyzed document for {path}, got {len(rows)}")
    return rows[0]


def summarize(files: list[dict]) -> dict:
    classifications = Counter()
    families = Counter()
    derived_operations = Counter()
    proof_class = Counter()
    unary_concat_proof_class = Counter()
    target_scoped_unary_concat_proof_class = Counter()
    projection_modes = Counter()
    parse_status = Counter()
    candidate_files = 0
    for row in files:
        parse_status[row["status"]] += 1
        if row.get("candidates"):
            candidate_files += 1
        for candidate in row.get("candidates", []):
            classifications[candidate["classification"]] += 1
            families[candidate.get("candidate_family") or "none"] += 1
            projection_modes[candidate.get("projection_mode") or "none"] += 1
            proof = candidate.get("first_proof_class")
            if proof is not None:
                proof_class["eligible" if proof.get("eligible") else "ineligible"] += 1
            unary_proof = candidate.get("unary_concat_proof_class")
            if unary_proof is not None:
                unary_concat_proof_class[
                    "eligible" if unary_proof.get("eligible") else "ineligible"
                ] += 1
            for scoped in candidate.get(
                "target_scoped_unary_concat_proofs", []
            ):
                scoped_proof = scoped["proof"]
                target_scoped_unary_concat_proof_class[
                    "eligible"
                    if scoped_proof.get("eligible")
                    else "ineligible"
                ] += 1
            if candidate.get("candidate_family") == "derived_projection":
                for op in candidate.get("expression", {}).get("operations", []):
                    derived_operations[op] += 1
    return {
        "files": len(files),
        "files_with_candidates": candidate_files,
        "parse_status": dict(sorted(parse_status.items())),
        "classifications": dict(sorted(classifications.items())),
        "families": dict(sorted(families.items())),
        "projection_modes": dict(sorted(projection_modes.items())),
        "first_proof_class": dict(sorted(proof_class.items())),
        "unary_concat_proof_class": dict(
            sorted(unary_concat_proof_class.items())
        ),
        "target_scoped_unary_concat_proof_class": dict(
            sorted(target_scoped_unary_concat_proof_class.items())
        ),
        "derived_operations": dict(sorted(derived_operations.items())),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    files = []
    for path in iter_inputs(args.inputs):
        files.extend(analyze_input(path))
    report = {
        "format": "scap-ng-foreach-candidate-analysis-0.4",
        "rewrite_performed": False,
        "safe_automatic_enabled": False,
        "summary": summarize(files),
        "files": files,
    }
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
