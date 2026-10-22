#!/usr/bin/env python3
"""Audit all 29 constant-only independent.variable -> variable.value OVAL sources.

This is an ORIGINAL-XML closure/semantic-shape census, not 29 native
conversions. It fails on source drift and unresolved refs, preserves source
Test/state axes and identifies only an intentionally narrow first candidate
subset. Refs #248 #229 #228.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from audit_v04_oval_variable_migration_queue import PIN

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"
ALIAS = {"independent.variable": "variable.value"}


def loc(tag):
    return tag.rsplit("}", 1)[-1]


def must(condition, reason):
    if not condition:
        raise ValueError("pinned variable.value source closure: " + reason)


def child(parent, name):
    items = [n for n in parent if loc(n.tag) == name]
    must(len(items) == 1, "required single " + name)
    return items[0]


def source_index(root):
    indexed = {}
    for node in root.iter():
        ident = node.get("id")
        if ident:
            must(ident not in indexed, "duplicate original ID " + ident)
            indexed[ident] = node
    return indexed


def referenced_tests(root_definition_id, indexed):
    """Follow extend_definition and nested criteria; retain repeated leaves.

    OVAL Definition composition is not a flat list of Tests. This traversal
    collects closure for the *shape census* while preserving every source
    cross-Definition edge, operator, negation and duplicate Test occurrence.
    It does NOT claim flattening these trees preserves Boolean outcomes.
    """
    seen_edges = []
    def visit(did, active):
        must(did in indexed and indexed[did].tag == "{" + OD + "}definition",
             "referenced OVAL Definition missing " + did)
        must(did not in active, "cyclic extended Definition " + did)
        definition = indexed[did]
        roots = [x for x in definition if loc(x.tag) == "criteria"]
        must(len(roots) == 1, "missing or duplicate Definition criteria " + did)
        refs = []
        def walk(element):
            for element_child in element:
                kind = loc(element_child.tag)
                if kind == "criterion":
                    tid = element_child.get("test_ref")
                    must(tid in indexed, "original Test reference missing " + str(tid))
                    refs.append(tid)
                elif kind == "extend_definition":
                    ref = element_child.get("definition_ref")
                    must(ref, "missing extended Definition reference")
                    seen_edges.append({
                        "from_definition": did, "to_definition": ref,
                        "negate": element_child.get("negate", "false"),
                    })
                    refs.extend(visit(ref, active + (did,)))
                elif kind == "criteria":
                    walk(element_child)
                else:
                    must(False, "unexpected OVAL criteria element " + kind)
        walk(roots[0])
        return refs
    ids = visit(root_definition_id, ())
    return ids, seen_edges


def direct_variable_test(tid, indexed):
    node = indexed[tid]
    if node.tag != "{" + IND + "}variable_test":
        return None
    children = list(node)
    objects = [n for n in children if loc(n.tag) == "object"]
    states = [n for n in children if loc(n.tag) == "state"]
    must(len(objects) == 1 and len(states) >= 0,
         "variable_test Object cardinality " + tid)
    objid = objects[0].get("object_ref")
    must(objid in indexed, "missing variable_test Object " + tid)
    obj = indexed[objid]
    must(obj.tag == "{" + IND + "}variable_object",
         "variable_test references wrong Object kind " + tid)
    objrefs = [n.text for n in obj if loc(n.tag) == "var_ref"]
    # Sets remain visible but outside this direct-value audit subset.
    is_simple_object = len(obj) == 1 and len(objrefs) == 1
    if objrefs:
        for name in objrefs:
            must(name in indexed and loc(indexed[name].tag).endswith("_variable"),
                 "variable_object var_ref unresolved " + tid)
    state_rows = []
    for state_elem in states:
        stateid = state_elem.get("state_ref")
        must(stateid in indexed, "variable_test State unresolved " + tid)
        state = indexed[stateid]
        must(state.tag == "{" + IND + "}variable_state",
             "variable_test references wrong State kind " + tid)
        identity = [n for n in state if loc(n.tag) == "var_ref"]
        values = [n for n in state if loc(n.tag) == "value"]
        for value in values:
            ref = value.get("var_ref")
            if ref is not None:
                must(ref in indexed and loc(indexed[ref].tag).endswith("_variable"),
                     "variable_state value var_ref unresolved " + tid)
        state_rows.append({
            "source_state_id": stateid,
            "state_operator": state.get("operator"),
            "identity_var_ref": [{"text": n.text, "attributes": dict(n.attrib)}
                                 for n in identity],
            "value_fields": [{"text": n.text, "attributes": dict(n.attrib)}
                             for n in values],
            "source_field_count": len(state),
        })
    # Enumerate the exact extra semantics before attempting any further
    # lowering; these are SOURCE features, not speculative native defaults.
    reasons = []
    if not is_simple_object:
        reasons.append("OBJECT_SET_OR_NON_DIRECT_VARIABLE_REF")
    if len(states) != 1:
        reasons.append("ZERO_OR_MULTIPLE_REFERENCED_STATES")
    for state in state_rows:
        if state["source_field_count"] != 1:
            reasons.append("STATE_HAS_MULTIPLE_OR_ZERO_FIELDS")
        if state["identity_var_ref"]:
            reasons.append("STATE_HAS_SEPARATE_VARIABLE_IDENTITY_CHECK")
        if len(state["value_fields"]) != 1:
            reasons.append("STATE_VALUE_FIELD_MISSING_OR_MULTIPLE")
        for value in state["value_fields"]:
            if value["text"] not in (None, ""):
                reasons.append("STATE_VALUE_HAS_LITERAL_TEXT")
            if set(value["attributes"]) != {"var_ref", "var_check"}:
                reasons.append("STATE_VALUE_HAS_ADDITIONAL_OR_DIFFERENT_ATTRIBUTES")
            if value["attributes"].get("var_check") != "at least one":
                reasons.append("STATE_VAR_CHECK_DIFFERS")
        if state["state_operator"] not in (None, "AND"):
            reasons.append("STATE_OPERATOR_DIFFERS")
    if node.get("check") != "at least one":
        reasons.append("TEST_CHECK_DIFFERS")
    if node.get("check_existence") != "at_least_one_exists":
        reasons.append("TEST_EXISTENCE_DIFFERS")
    reasons = sorted(set(reasons))
    direct = not reasons
    return {
        "source_test": tid,
        "source_test_attributes": dict(node.attrib),
        "source_object_id": objid,
        "source_object_attributes": dict(obj.attrib),
        "source_object_var_refs": objrefs,
        "source_object_children": [loc(n.tag) for n in obj],
        "states": state_rows,
        "source_semantic_axes_requiring_review": reasons,
        "direct_value_test_candidate": direct,
        "candidate_status": (
            "NARROW_SOURCE_SHAPE_ONLY_NOT_NATIVE_VALIDATED"
            if direct else "REQUIRES_SEPARATE_OVAL_SEMANTIC_LOWERING"
        ),
    }


def audit(queue, original_dir):
    must(queue.get("pinned_source_revision") == PIN and
         queue.get("counts", {}).get("constant_only_alias_mapped_unvalidated_definitions") == 29,
         "OVAL Variable migration queue identity or denominator")
    records = [
        row for row in queue.get("records", [])
        if row.get("migration_group") == "constant_only"
        and row.get("native_source_capability_aliases", {}) == ALIAS
    ]
    must(len(records) == 29, "29 original constant-only alias Definitions")
    base = Path(original_dir).resolve()
    seen, cache, output, counters = set(), {}, [], Counter()
    for row in sorted(records, key=lambda x: (x["source_file"], x["source_definition_id"])):
        key = (row["source_file"], row["source_definition_id"])
        must(key not in seen, "duplicate selected source Definition")
        seen.add(key)
        source = (base / row["source_file"]).resolve()
        must(source.is_relative_to(base) and source.is_file(),
             "missing or escaping original OVAL source " + str(key))
        raw = source.read_bytes()
        digest = sha256(raw).hexdigest()
        must(digest == row["source_xml_sha256"],
             "original source file digest changed " + str(key))
        if key[0] not in cache:
            root = ET.fromstring(raw)
            must(root.tag == "{" + OD + "}oval_definitions",
                 "source OVAL Definitions namespace")
            cache[key[0]] = source_index(root)
        indexed = cache[key[0]]
        did = row["source_definition_id"]
        must(did in indexed and indexed[did].tag == "{" + OD + "}definition",
             "pinned source Definition id missing " + str(key))
        definition = indexed[did]
        test_ids, extended = referenced_tests(did, indexed)
        must(test_ids, "original Definition has no reachable Test leaves " + str(key))
        detailed = [direct_variable_test(tid, indexed) for tid in test_ids]
        variable_tests = [x for x in detailed if x is not None]
        must(variable_tests, "original Definition has no independent.variable_test " + str(key))
        # A Definition can contain other Test capabilities; these are
        # intentionally not discarded when classifying a possible importer.
        nonvariable = [
            {"test_id": tid, "source_type": loc(indexed[tid].tag)}
            for tid, t in zip(test_ids, detailed) if t is None
        ]
        direct = (not extended and not nonvariable and
                  all(t["direct_value_test_candidate"] for t in variable_tests))
        counters["definitions"] += 1
        counters["original_variable_test_nodes"] += len(variable_tests)
        counters["distinct_original_variable_tests_per_definition_sum"] += len({
            t["source_test"] for t in variable_tests})
        counters["reused_variable_test_leaf_occurrences"] += (
            len(variable_tests) - len({t["source_test"] for t in variable_tests}))
        reasons = sorted({reason for t in variable_tests
                          for reason in t["source_semantic_axes_requiring_review"]})
        if extended:
            reasons.append("DEFINITION_EXTENDS_OTHER_DEFINITIONS")
        if nonvariable:
            reasons.append("DEFINITION_HAS_OTHER_CAPABILITY_TESTS")
        if any(n.get("operator", "AND") != "AND" or
               n.get("negate", "false") != "false"
               for n in definition.iter() if loc(n.tag) == "criteria"):
            reasons.append("DEFINITION_NONTRIVIAL_BOOLEAN_OPERATORS_OR_NEGATION")
        if any(n.get("negate", "false") != "false" for n in definition.iter()
               if loc(n.tag) in ("criterion", "extend_definition")):
            reasons.append("DEFINITION_NEGATED_LEAF_OR_EXTENSION")
        reasons = sorted(set(reasons))
        for reason in reasons:
            counters["definition_reason:" + reason] += 1
        counters["extended_definition_edges"] += len(extended)
        counters["definitions_with_extended_sources"] += bool(extended)
        counters["original_nonvariable_test_nodes"] += len(nonvariable)
        counters["direct_variable_shape_definitions"] += direct
        counters["complex_variable_shape_definitions"] += not direct
        counters["direct_variable_shape_tests"] += sum(
            t["direct_value_test_candidate"] for t in variable_tests)
        counters["complex_variable_shape_tests"] += sum(
            not t["direct_value_test_candidate"] for t in variable_tests)
        output.append({
            "source_file": row["source_file"],
            "source_sha256": digest,
            "original_definition_id": did,
            "original_definition_class": definition.get("class"),
            "source_criterion_operator_nodes": [
                {"operator": n.get("operator"), "child_count": len(n)}
                for n in definition.iter() if loc(n.tag) == "criteria"],
            "extended_definition_edges": extended,
            "variable_tests": variable_tests,
            "other_source_tests": nonvariable,
            "source_semantic_axes_requiring_review": reasons,
            "distinct_variable_test_count": len({t["source_test"] for t in variable_tests}),
            "all_variable_tests_narrow_value_shape": direct,
            "native_040_schema_conversion": "NOT_TESTED",
            "original_oval_semantic_roundtrip": "NOT_TESTED",
            "scanner_parity": False,
        })
    return {
        "status": "PINNED_29_OVAL_VARIABLE_VALUE_ALIAS_SOURCE_SHAPES_NOT_CONVERTED",
        "pinned_revision": PIN,
        "queue_denominator": 29,
        "counts": dict(sorted(counters.items())),
        "review_queue": [
            {
                "source_file": row["source_file"],
                "definition_id": row["original_definition_id"],
                "semantic_axis_count": len(row["source_semantic_axes_requiring_review"]),
                "semantic_axes": row["source_semantic_axes_requiring_review"],
                "distinct_variable_tests": row["distinct_variable_test_count"],
                "native_conversion": "NOT_VALIDATED_BY_THIS_AUDIT",
            }
            for row in sorted(output, key=lambda row: (
                len(row["source_semantic_axes_requiring_review"]),
                row["source_file"], row["original_definition_id"]))
        ],
        "records": output,
        "native_040_conversions_proven_from_this_audit": 0,
        "scanner_parity_proven": False,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--variable-queue", type=Path, required=True)
    cli.add_argument("--source-root", type=Path, required=True)
    cli.add_argument("--report", type=Path, required=True)
    args = cli.parse_args()
    result = audit(json.loads(args.variable_queue.read_text()), args.source_root)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"],
                      "converted": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
