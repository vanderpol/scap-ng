#!/usr/bin/env python3
"""Reversible research-only OVAL State -> author-facing field-group projection.

Two different operators MUST stay at two different levels:
* OVAL Test.state_operator combines whole States, on the SAME Item.
* OVAL State.operator combines its field/entity predicate outcomes.

A unique-name AND State can be written as one compact `fields:` mapping.
Non-AND States and repeated field names use `fields_operator` plus an
ordered `fields:` sequence. This avoids silent duplicate YAML key loss.

Only source graph structural reversibility is established here. Original
Test.check and check_existence strings are deliberately carried unchanged;
no scanner, schema promotion, XML serializer or default field existence
policy is claimed. The source XML fixture was separately XSD-validated.
Refs #248 #239.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"
OPERATORS = {"AND": "and", "OR": "or", "ONE": "one", "XOR": "xor"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                           separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def source_graph(path):
    """Preserve original OVAL State identity, ordered entities and Test scope."""
    root = ET.parse(path).getroot()
    tests = []
    for test in root.findall("./{" + OD + "}tests/{" + IND + "}shellcommand_test"):
        refs = [node.attrib["state_ref"]
                for node in test.findall("{" + IND + "}state")]
        if not refs:
            raise ValueError("This pilot expects Tests with States")
        op = test.get("state_operator", "AND")
        if op not in OPERATORS:
            raise ValueError("Invalid original Test State operator: " + op)
        tests.append({"id": test.attrib["id"],
                      "attributes": dict(test.attrib),
                      "state_refs": refs})
    states = {}
    for state in root.findall("./{" + OD + "}states/{" + IND + "}shellcommand_state"):
        op = state.get("operator", "AND")
        if op not in OPERATORS:
            raise ValueError("Invalid original State field operator: " + op)
        fields = []
        for field in state:
            if not field.tag.startswith("{" + IND + "}"):
                raise ValueError("Non-independent field outside pilot")
            fields.append({"name": field.tag.split("}", 1)[1],
                           "attributes": dict(field.attrib),
                           "text": field.text or ""})
        if not fields:
            raise ValueError("Empty State fields are unsupported by this pilot")
        if state.attrib["id"] in states:
            raise ValueError("Repeated OVAL State ID")
        states[state.attrib["id"]] = {
            "attributes": dict(state.attrib),
            "fields": fields}
    if not tests:
        raise ValueError("No independent.shellcommand original Tests")
    for test in tests:
        for ref in test["state_refs"]:
            if ref not in states:
                raise ValueError("Missing original State " + ref)
    return {"tests": tests, "states": states}


def field_group(state):
    """Make the ONE-OVAL-State boundary visible; never flatten across States."""
    source = state["fields"]
    if not isinstance(source, list) or not source:
        raise ValueError("Original OVAL State must have ordered field entries")
    op = state["attributes"].get("operator", "AND")
    if op not in OPERATORS:
        raise ValueError("Unsupported source operator")
    names = [field["name"] for field in source]
    if any(not name for name in names):
        raise ValueError("Unnamed field")
    entries = [{field["name"]: {"attributes": deepcopy(field["attributes"]),
                                "text": field["text"]}} for field in source]
    if op == "AND" and len(set(names)) == len(names):
        # A fields mapping is, by definition, conjunction within one State.
        return {"fields": {name: entry[name] for name, entry in zip(names, entries)}}
    return {"fields_operator": OPERATORS[op], "fields": entries}


def inverse_field_group(group, original_attributes):
    if not isinstance(group, dict) or "fields" not in group:
        raise ValueError("Missing expected field group")
    shape = set(group)
    fields = group["fields"]
    if shape == {"fields"} and isinstance(fields, dict) and fields:
        operator = "AND"
        entries = [{name: value} for name, value in fields.items()]
    elif (shape == {"fields_operator", "fields"} and
          group["fields_operator"] in OPERATORS.values() and
          isinstance(fields, list) and fields):
        operator = {value: key for key, value in OPERATORS.items()}[
            group["fields_operator"]]
        entries = fields
    else:
        raise ValueError("Malformed or ambiguously scoped fields group")
    restored = []
    for entry in entries:
        if not isinstance(entry, dict) or len(entry) != 1:
            raise ValueError("A field entry must carry exactly one name")
        name, value = next(iter(entry.items()))
        if (not isinstance(value, dict) or
            set(value) != {"attributes", "text"} or
            not isinstance(value["attributes"], dict) or
            not isinstance(value["text"], str)):
            raise ValueError("Field value/provenance changed")
        restored.append({"name": name,
                         "attributes": deepcopy(value["attributes"]),
                         "text": value["text"]})
    if original_attributes.get("operator", "AND") != operator:
        raise ValueError("Changed source OVAL State field operator")
    return {"attributes": deepcopy(original_attributes), "fields": restored}


def project(graph):
    """Return candidate Test-local syntax plus migration source-identity ledger."""
    tests = []
    ledger = []
    for test in graph["tests"]:
        original = test["attributes"]
        op = original.get("state_operator", "AND")
        if op not in OPERATORS:
            raise ValueError("Unknown Test state_operator")
        refs = test["state_refs"]
        branches = [field_group(graph["states"][ref]) for ref in refs]
        if len(refs) > 1:
            condition = {OPERATORS[op]: branches}
        else:
            condition = branches[0]
        # This intentionally retains source Test check and existence values,
        # rather than guessing NG matching/existence names in a naming pilot.
        tests.append({"id": test["id"],
                      "item_existence_oval": original.get("check_existence",
                                                         "at_least_one_exists"),
                      "item_matching_oval": original.get("check", "all"),
                      "item_condition": condition})
        ledger.append({"id": test["id"], "test_attributes": deepcopy(original),
                       "state_refs": deepcopy(refs),
                       "state_attributes": [deepcopy(graph["states"][ref]["attributes"])
                                            for ref in refs]})
    candidate = {"tests": tests}
    proof = {"source_graph_sha256": digest(graph),
             "candidate_sha256": digest(candidate), "tests": ledger}
    return candidate, proof


def restore(candidate, proof):
    """Reconstruct the precise original semantic Test/State graph, not XML."""
    if digest(candidate) != proof["candidate_sha256"]:
        raise ValueError("Candidate drifted since reversible source proof")
    if len(candidate["tests"]) != len(proof["tests"]):
        raise ValueError("Test count changed")
    restored_tests = []
    restored_states = {}
    for view, entry in zip(candidate["tests"], proof["tests"]):
        attrs = entry["test_attributes"]
        if (view["id"] != entry["id"] or
            view["item_existence_oval"] !=
                attrs.get("check_existence", "at_least_one_exists") or
            view["item_matching_oval"] != attrs.get("check", "all")):
            raise ValueError("Source Test scope or identity altered")
        refs = entry["state_refs"]
        test_op = attrs.get("state_operator", "AND")
        condition = view["item_condition"]
        if len(refs) > 1:
            if (not isinstance(condition, dict) or
                set(condition) != {OPERATORS[test_op]} or
                not isinstance(condition[OPERATORS[test_op]], list) or
                len(condition[OPERATORS[test_op]]) != len(refs)):
                raise ValueError("Whole-State operator or identity lost")
            groups = condition[OPERATORS[test_op]]
        else:
            groups = [condition]
        for ref, group, state_attrs in zip(refs, groups,
                                           entry["state_attributes"]):
            state = inverse_field_group(group, state_attrs)
            if ref in restored_states and restored_states[ref] != state:
                raise ValueError("Shared source State has divergent consumers")
            restored_states[ref] = state
        restored_tests.append({"id": entry["id"],
                               "attributes": deepcopy(attrs),
                               "state_refs": deepcopy(refs)})
    graph = {"tests": restored_tests, "states": restored_states}
    if digest(graph) != proof["source_graph_sha256"]:
        raise ValueError("Original OVAL Test/State semantic graph not recovered")
    return graph


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--oval-xml", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--ledger", type=Path, required=True)
    a = p.parse_args()
    graph = source_graph(a.oval_xml)
    candidate, proof = project(graph)
    if restore(candidate, proof) != graph:
        raise ValueError("Failed exact structural roundtrip")
    for path, value in ((a.candidate, candidate), (a.ledger, proof)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    print(f"PASS: {len(graph['tests'])} OVAL Tests; "
          f"{len(graph['states'])} States; exact Test/State graph inverse; "
          "schema/scanner parity NOT established")


if __name__ == "__main__":
    main()
