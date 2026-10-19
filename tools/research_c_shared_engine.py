#!/usr/bin/env python3
"""#245 0.4-C research: C authoring/view to existing A collection + dataflow.

No OS collectors, scanner, or source semantic rewrite. The two bounded bridges
prove only native 0.4-A structural identity and Apache fixture equivalence.
Source fingerprints fail closed; no 0.4-A grammar is modified.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import re

from v04_a_dataflow_index import index_assessment_dataflow

# Human steps are a non-normative *representation* of A's original graph.
# No unknown operation may be dropped, guessed, or silently normalized.
SOURCE_TO_C = {
    "concat": "combine",
    "regex_capture": "extract",
    "merge": "merge_values",
    "unique": "distinct",
    "values": "read_field",
    "literal": "constant",
}
C_TO_SOURCE = {v: k for k, v in SOURCE_TO_C.items()}
FORMAT = "scap-ng-c-shared-a-backend-proof/0.1"
_STEP_ID = re.compile(r"^[a-z][a-z0-9_-]*$")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def fingerprint(obj):
    return sha256(canonical(obj).encode("utf-8")).hexdigest()


def simple_c_home_to_a_test(requirement, reference):
    """Lower one *explicitly bounded* human check to the exact original A Test.

    The C 'all_found_items' and 'field_contains' have distinct aggregation
    scopes. A literal /home equality is NOT converted to the original regex.
    No runtime scanner equivalence is implied by structural identity.
    """
    if not isinstance(requirement, dict) or set(requirement) != {
        "each", "where", "minimum_items", "all_found_items"
    }:
        raise ValueError("unsupported C authoring shape; no guessed defaults")
    if requirement["each"] != "linux.partition" or type(requirement["minimum_items"]) is not int or requirement["minimum_items"] != 1:
        raise ValueError("C acquisition/counted population does not match source")
    condition = requirement["all_found_items"]
    if not isinstance(condition, dict) or set(condition) != {"mount_options"} or (
        not isinstance(condition["mount_options"], dict) or
        set(condition["mount_options"]) != {"contains"} or
        not isinstance(condition["mount_options"]["contains"], str)
    ):
        raise ValueError("C Item predicate/field aggregation unsupported")
    if not isinstance(requirement["where"], dict) or set(requirement["where"]) != {"mount_point"} or (
        not isinstance(requirement["where"]["mount_point"], dict) or
        set(requirement["where"]["mount_point"]) != {"matches_regex"}
    ):
        raise ValueError("preserve source mount regex and selector identity")
    a = reference["assessment"]
    if a["mode"] != "automated" or len(a["tests"]) != 1:
        raise ValueError("reference requires one automated Test")
    test_id, original = next(iter(a["tests"].items()))
    if a.get("evaluate") != {"test": test_id} or (
        original["capability"] != "linux.partition" or
        original["object"]["capability"] != "linux.partition" or
        original["object"].get("select") != requirement["where"] or
        original.get("reported_elements") != "all"
    ):
        raise ValueError("collection identity or evaluation scope differs")
    field = original["states"][0]["mount_options"]
    if original.get("require") != "at_least_one_exists_and_all_match" or (
        field.get("require") != "at_least_one_exists_and_some_match" or
        field.get("equals") != condition["mount_options"]["contains"]
    ):
        raise ValueError("source Item or field existence/matching semantics differ")
    # One canonical compiled descriptor shared by source and C routes; not a
    # new collector API with different options or an assertion of execution.
    return {
        "format": FORMAT,
        "source_test_id": test_id,
        "source_sha256": fingerprint(original),
        "acquisition": deepcopy(original["object"]),
        "field_predicates": deepcopy(original["states"]),
        "item_requirement": original["require"],
        "evaluation": deepcopy(a["evaluate"]),
        "scanner_executed": False,
        "original_source_parity_verified": False,
    }


def source_a_home_descriptor(reference):
    a = reference["assessment"]
    test_id, t = next(iter(a["tests"].items()))
    if a.get("evaluate") != {"test": test_id}:
        raise ValueError("unsupported expression")
    return {
        "format": FORMAT,
        "source_test_id": test_id,
        "source_sha256": fingerprint(t),
        "acquisition": deepcopy(t["object"]),
        "field_predicates": deepcopy(t["states"]),
        "item_requirement": t["require"],
        "evaluation": deepcopy(a["evaluate"]),
        "scanner_executed": False,
        "original_source_parity_verified": False,
    }


def _aliases(source):
    # Deterministic, 1:1 mapping allows readable step names without losing
    # any original source Variable IDs needed for evidence and diagnostics.
    out = {}
    used = set()
    for identity, var in sorted(source.items()):
        if not isinstance(var, dict) or not isinstance(var.get("expression"), dict):
            raise ValueError("unsupported Variable declaration")
        title = str(var.get("title") or identity)
        alias = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:64]
        alias = alias or "derived_value"
        if not _STEP_ID.fullmatch(alias):
            alias = "step_" + re.sub(r"[^a-z0-9]+", "_", identity)[:45]
        candidate, ix = alias, 2
        while candidate in used:
            candidate, ix = f"{alias}_{ix}", ix + 1
        used.add(candidate)
        out[identity] = candidate
    return out


def _convert_expression(obj, aliases, reverse=False):
    """Only rewrite EXACT structural op/ref nodes, not opaque collector data."""
    trans = C_TO_SOURCE if reverse else SOURCE_TO_C
    if isinstance(obj, list):
        return [_convert_expression(v, aliases, reverse) for v in obj]
    if not isinstance(obj, dict):
        return deepcopy(obj)
    if len(obj) == 1:
        key, value = next(iter(obj.items()))
        if not reverse and key == "variable":
            if type(value) is not str or value not in aliases:
                raise ValueError(f"unresolved source Variable {value!r}")
            return {"use": aliases[value]}
        if reverse and key == "use":
            if type(value) is not str or value not in aliases:
                raise ValueError(f"unresolved C Variable alias {value!r}")
            return {"variable": aliases[value]}
        if key in trans:
            return {trans[key]: _convert_expression(value, aliases, reverse)}
        if key in (C_TO_SOURCE if not reverse else SOURCE_TO_C):
            raise ValueError(f"mixed/unrecognized expression spelling {key!r}")
    # Preserve collection descriptors, selector names, sort/order flags and
    # all provenance-bearing metadata, while translating nested expressions.
    return {key: _convert_expression(value, aliases, reverse)
            for key, value in obj.items()}


def present_c_variable_steps(assessment):
    """Read-only human steps over one original A-compatible source graph."""
    source = assessment.get("variables")
    if not isinstance(source, dict) or not source or len(source) > 512:
        raise ValueError("bounded source Variable graph required")
    index = index_assessment_dataflow(assessment)
    aliases = _aliases(source)
    steps = []
    for original_id, alias in aliases.items():
        raw = source[original_id]
        expr = raw["expression"]
        if len(expr) != 1 or next(iter(expr)) not in SOURCE_TO_C:
            raise ValueError("unsupported C display operation; retain A compatibility")
        steps.append({
            "name": alias,
            "source_id": original_id,
            "title": raw.get("title"),
            "kind": raw.get("kind"),
            "datatype": raw.get("datatype"),
            "derive": _convert_expression(expr, aliases),
        })
    return {
        "format": FORMAT,
        "mode": "variable-steps-readonly-compatibility",
        "source_assessment_id": assessment["id"],
        "source_variables_sha256": fingerprint(source),
        "source_dataflow_sha256": fingerprint(index),
        "steps": steps,
        "execution_supported": False,
        "scanner_executed": False,
        "original_source_parity_verified": False,
    }


def compile_c_variable_steps(view, original_assessment):
    """Reconstruct A source from C display and refuse ANY semantic drift."""
    if not isinstance(view, dict) or view.get("format") != FORMAT or (
        view.get("mode") != "variable-steps-readonly-compatibility" or
        view.get("execution_supported") is not False or
        view.get("original_source_parity_verified") is not False or
        view.get("source_assessment_id") != original_assessment.get("id")
    ):
        raise ValueError("invalid/unverified C research representation")
    original = original_assessment["variables"]
    steps = view.get("steps")
    if not isinstance(steps, list) or len(steps) != len(original):
        raise ValueError("loss or duplication of source Variable nodes")
    aliases = {step["name"]: step["source_id"] for step in steps}
    if len(aliases) != len(steps) or set(aliases.values()) != set(original):
        raise ValueError("non-bijective Variable identity mapping")
    new_vars = {}
    for step in steps:
        source_id = step["source_id"]
        if source_id in new_vars or set(step) != {"name", "source_id", "title",
                                                   "kind", "datatype", "derive"}:
            raise ValueError("duplicate or malformed C step")
        new_vars[source_id] = {
            "title": step["title"],
            "kind": step["kind"],
            "datatype": step["datatype"],
            "expression": _convert_expression(step["derive"], aliases, True),
        }
    # Research contract: no accepted semantic rewrites in this first gate.
    if fingerprint(new_vars) != view["source_variables_sha256"] or (
        fingerprint(original) != view["source_variables_sha256"]
    ):
        raise ValueError("Variable transformation differs: cannot claim lossless")
    result = deepcopy(original_assessment)
    result["variables"] = deepcopy(original)
    restored = index_assessment_dataflow(result)
    if fingerprint(restored) != view["source_dataflow_sha256"]:
        raise ValueError("acquisition/Variable dependency graph changed")
    return result
