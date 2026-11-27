#!/usr/bin/env python3
"""Check a pinned OVAL external-variable Definition and its independent bindings."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from struct import pack, unpack
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from qualify_merge_fixture import INDEPENDENT, OVAL, require_equal
from runner import CONFORMANCE, load, validator

FIXTURE = CONFORMANCE / "variable-external-input"
OVAL_VARIABLES = "{http://oval.mitre.org/XMLSchema/oval-variables-5}"
NATIVE_TYPES = {"binary": "binary", "boolean": "boolean", "evr_string": "rpm_evr",
                "float": "float", "int": "integer", "string": "string", "version": "version"}
EQUALS = {"binary": "binary_equals", "evr_string": "rpm_evr_equals", "float": "float_equals"}


def literal(datatype, text):
    if datatype == "boolean":
        return {"true": True, "false": False, "1": True, "0": False}[text]
    if datatype == "int":
        return int(text)
    if datatype == "float":
        return unpack("!f", pack("!f", float(text)))[0]
    return text


def elements_by_id(root):
    return {node.attrib["id"]: node for node in root.iter() if "id" in node.attrib}


def source_constraints(variable, datatype, values):
    allowed = [literal(datatype, row.text) for row in variable.findall(OVAL + "possible_value")]
    patterns = []
    for node in variable.findall(OVAL + "possible_restriction"):
        restriction, = node
        require_equal(restriction.tag, OVAL + "restriction", "source possible restriction")
        require_equal(restriction.attrib["operation"], "pattern match", "source restriction operation")
        patterns.append(restriction.text)
    if allowed or patterns:
        require_equal(all(value in allowed or any(re.search(pattern, value) for pattern in patterns)
                          for value in values), True, variable.attrib["id"])
    constraints = {}
    if allowed:
        constraints["allowed"] = allowed
    if patterns:
        predicates = [{"matches_regex": pattern} for pattern in patterns]
        constraints["predicate"] = predicates[0] if len(predicates) == 1 else {"or": predicates}
    return constraints


def expected_predicate(nodes, state, values, source_id):
    operation = state.get("operation", "equals")
    datatype = state.get("datatype", "string")
    if operation == "pattern match":
        require_equal(all(re.search(state.text, value) is not None for value in values), True, source_id)
        return {"matches_regex": state.text}

    require_equal(operation, "equals", source_id)
    if "var_ref" not in state.attrib:
        wanted = literal(datatype, state.text)
        require_equal(all(value == wanted for value in values), True, source_id)
        return {EQUALS.get(datatype, "equals"): wanted}

    require_equal(state.attrib["var_check"], "at least one", source_id)
    wanted_var = nodes[state.attrib["var_ref"]]
    require_equal(wanted_var.tag, OVAL + "constant_variable", source_id)
    require_equal(wanted_var.attrib["datatype"], datatype, source_id)
    wanted = [literal(datatype, row.text) for row in wanted_var.findall(OVAL + "value")]
    require_equal(all(value in wanted for value in values), True, source_id)
    operator = "version_equals" if datatype == "version" else EQUALS.get(datatype, "equals")
    return {operator: wanted, "value_match": "one_or_more", "datatype": NATIVE_TYPES[datatype]}


def cases_from_source(source, bindings, expected, assessment, trace):
    nodes = elements_by_id(ET.fromstring(source))
    supplied = elements_by_id(ET.fromstring(bindings))
    criteria = nodes[expected["definition"]].find(OVAL + "criteria")
    test_sources = [node.attrib["test_ref"] for node in criteria.iter(OVAL + "criterion")]
    test_ids = {row["source_id"]: row["native_id"]
                for row in trace["native_identities"] if row["kind"] == "test"}
    variable_ids = {row["source_id"]: row["native_id"]
                    for row in trace["native_identities"] if row["kind"] == "variable"}
    require_equal(sorted(test_sources), sorted(test_ids), "source Test IDs")
    require_equal(len(test_sources), expected["positive"]["test_count"], "source Test count")

    cases = []
    case_metadata = {}
    for source_id in test_sources:
        test = nodes[source_id]
        require_equal(test.tag, INDEPENDENT + "variable_test", source_id)
        require_equal((test.get("check_existence"), test.get("check")), ("at_least_one_exists", "all"), source_id)
        obj = nodes[test.find(INDEPENDENT + "object").attrib["object_ref"]]
        state = nodes[test.find(INDEPENDENT + "state").attrib["state_ref"]]
        source_variable_id = obj.findtext(INDEPENDENT + "var_ref")
        source_variable = nodes[source_variable_id]
        source_binding = supplied[source_variable_id]
        datatype = source_variable.attrib["datatype"]
        require_equal(source_variable.tag, OVAL + "external_variable", source_id)
        require_equal(source_binding.tag, OVAL_VARIABLES + "variable", source_id)
        require_equal(source_binding.attrib["datatype"], datatype, source_id)
        values = [literal(datatype, row.text) for row in source_binding.findall(OVAL_VARIABLES + "value")]
        predicate = expected_predicate(nodes, state.find(INDEPENDENT + "value"), values, source_id)
        constraints = source_constraints(source_variable, datatype, values)

        native_id = test_ids[source_id]
        native = assessment["tests"][native_id]
        require_equal((native["capability"], native["variable"]), ("variable.value", variable_ids[source_variable_id]), source_id)
        require_equal(native["require"], {
            "item_requirement": {"items_found": "one_or_more", "items_satisfying": "every"},
            "fields": {"value": predicate},
            "field_requirement": {"values_found": "one_or_more", "values_matching": "every"},
        }, source_id)
        variable = assessment["variables"][native["variable"]]
        require_equal(variable["kind"], "local", source_id)
        input_id = variable["expression"]["input"]
        require_equal(variable["expression"], {"input": input_id}, source_id)
        declaration = assessment["inputs"][input_id]
        require_equal({key: value for key, value in declaration.items() if key != "description"},
                      {"datatype": NATIVE_TYPES[datatype], "cardinality": "one_or_more",
                       "required": True, "constraints": constraints}, source_id)
        case_metadata[source_id] = {"native_test": native_id, "native_input": input_id,
                                    "datatype": NATIVE_TYPES[datatype], "values": len(values),
                                    "restricted": bool(constraints)}
        cases.append({"name": source_id, "test": native_id, "values": {input_id: values}})

    require_equal(set(supplied), {obj.findtext(INDEPENDENT + "var_ref") for obj in nodes.values()
                                 if obj.tag == INDEPENDENT + "variable_object"}, "source supplied bindings")
    require_equal({row["native_input"] for row in case_metadata.values()}, set(assessment["inputs"]),
                  "converted Input declarations")
    counts = Counter(row["values"] for row in case_metadata.values())
    require_equal(dict(counts), {1: expected["positive"]["single_value"], 4: expected["positive"]["four_values"]},
                  "source binding multiplicities")
    require_equal(sum(row["restricted"] for row in case_metadata.values()),
                  expected["positive"]["restricted_inputs"], "constrained Inputs")
    control = case_metadata[expected["control_test"]]
    for name, variant in expected["controls"].items():
        values = {control["native_input"]: variant["values"]} if "values" in variant else {}
        cases.append({"name": name, "test": control["native_test"], "values": values})
    return cases, case_metadata


def qualify(self_assertion, converted, ri, go):
    expected = load(FIXTURE / "expected.json")
    archive = self_assertion / expected["source_archive"]
    require_equal(sha256(archive.read_bytes()).hexdigest(), expected["source_archive_sha256"], "source ZIP")
    with ZipFile(archive) as source_zip:
        source = source_zip.read(expected["definition_member"])
        bindings = source_zip.read(expected["bindings_member"])
    source_digest = sha256(source).hexdigest()
    bindings_digest = sha256(bindings).hexdigest()
    require_equal(source_digest, expected["definition_sha256"], "source Definition XML")
    require_equal(bindings_digest, expected["bindings_sha256"], "source bindings XML")

    trace = load(converted / "source-trace.json")
    require_equal(trace["source_commit"], expected["source_pin"], "source trace commit")
    require_equal(trace["source_sha256"], source_digest, "source trace XML")
    require_equal(trace["definition_id"], expected["definition"], "source trace Definition")
    document = load(converted / "assessment.json")
    validator().validate(document)
    assessment = document["assessment"]
    cases, metadata = cases_from_source(source, bindings, expected, assessment, trace)
    request = {"schema_family_sha256": trace["assessment_closure_sha256"],
               "assessment_document": document, "bindings": {}}
    run = subprocess.run([go, "run", str(FIXTURE / "ri-replay.go")], cwd=ri,
                         input=json.dumps({"request": request, "definitions": assessment["inputs"], "cases": cases}),
                         capture_output=True, text=True, timeout=120)
    if run.returncode != 0:
        raise ValueError(f"RI replay failed: {run.stderr}")

    replies = json.loads(run.stdout)
    require_equal(set(replies), {case["name"] for case in cases}, "RI replay cases")
    observations = {}
    for name, observation in replies.items():
        decision = observation["decision"]
        if diagnostic := observation.get("diagnostic"):
            require_equal(decision["technical_outcome"], "", name)
            observations[name] = {"diagnostic": diagnostic["code"]}
            continue
        count = decision["cardinality"]
        observations[name] = {"outcome": decision["technical_outcome"], "values_found": count["values_found"],
                              "values_matching": count.get("values_matching", 0)}
    leaves = {}
    for name, details in metadata.items():
        count = details["values"]
        observed = observations.pop(name)
        require_equal(observed, {"outcome": expected["positive"]["outcome"], "values_found": count,
                                 "values_matching": count}, name)
        leaves[name] = {**details, **observed}
    for name, control in expected["controls"].items():
        require_equal(observations[name], {key: value for key, value in control.items() if key != "values"}, name)
    return {
        "format": "scap-ng-external-variable-ri-leaf-receipt-1",
        "source_sha256": source_digest,
        "source_bindings_sha256": bindings_digest,
        "native_assessment_sha256": sha256((converted / "assessment.json").read_bytes()).hexdigest(),
        "converter_revision": trace["converter_commit"],
        "schema_commit": trace["schema_commit"],
        "ri_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ri, text=True).strip(),
        "leaves": leaves,
        "controls": observations,
        "scope": "Direct RI Test evaluation with caller-supplied Inputs. Benchmark policy enforcement and rollup remain separate.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-assertion", type=Path, required=True)
    parser.add_argument("--converted", type=Path, required=True)
    parser.add_argument("--ri", type=Path, required=True)
    parser.add_argument("--go", default="go")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = qualify(args.self_assertion, args.converted, args.ri, args.go)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check and (FIXTURE / "ri-receipt.json").read_text(encoding="utf-8") != rendered:
        raise SystemExit("external-variable receipt differs from the replay")
    print(rendered, end="")
