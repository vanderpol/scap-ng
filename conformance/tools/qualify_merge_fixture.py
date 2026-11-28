#!/usr/bin/env python3
"""Check the pinned OVAL merge Definition and replay its native Test leaves."""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from runner import CONFORMANCE, load, validator

OVAL = "{http://oval.mitre.org/XMLSchema/oval-definitions-5}"
INDEPENDENT = "{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}"
FIXTURE = CONFORMANCE / "variable-merge"


def require_equal(actual, expected, context):
    if actual != expected:
        raise ValueError(f"{context}: observed {actual!r}, expected {expected!r}")


def joined(values, sort, delimiter):
    ordered = sorted(values) if sort == "natural" else values
    return delimiter.join(map(str, ordered))


def verify_oval(raw, oracle):
    root = ET.fromstring(raw)
    nodes = {node.attrib["id"]: node for node in root.iter() if "id" in node.attrib}
    definition = nodes[oracle["definition"]]
    required = [row.get("test_ref") for row in definition.findall(f"{OVAL}criteria/{OVAL}criterion")]
    require_equal(required, list(oracle["tests"]), "source criteria")
    bindings = {}
    for test_id, expected in oracle["tests"].items():
        test = nodes[test_id]
        object_node = nodes[test.find(INDEPENDENT + "object").attrib["object_ref"]]
        state = nodes[test.find(INDEPENDENT + "state").attrib["state_ref"]]
        variable_ref = object_node.findtext(INDEPENDENT + "var_ref")
        merge = nodes[variable_ref].find(OVAL + "merge")
        component, = merge
        require_equal(component.tag, OVAL + "object_component", test_id)
        require_equal(component.attrib["item_field"], "value", test_id)
        value_object = nodes[component.attrib["object_ref"]]
        require_equal(value_object.tag, INDEPENDENT + "variable_object", test_id)
        reference, = value_object
        require_equal(reference.tag, INDEPENDENT + "var_ref", test_id)
        constant = nodes[reference.text]
        require_equal(constant.tag, OVAL + "constant_variable", test_id)
        values = [entry.text for entry in constant.findall(OVAL + "value")]
        if constant.attrib["datatype"] == "int":
            values = [int(value) for value in values]
        sort = merge.get("sort", "document")
        delimiter = merge.get("delimiter", "")
        require_equal((values, sort, delimiter), (expected["values"], expected["sort"], expected["delimiter"]), test_id)
        require_equal(merge.get("order", "ascending"), "ascending", test_id)
        require_equal(joined(values, sort, delimiter), expected["joined"], test_id)
        require_equal(state.findtext(INDEPENDENT + "value"), expected["joined"], test_id)
        bindings[test_id] = (variable_ref, reference.text)
    return bindings


def evaluate(binary, pin, document, test_id):
    request = {"schema_family_sha256": pin, "assessment_document": document, "bindings": {}}
    run = subprocess.run([str(binary), "--test", test_id], input=json.dumps(request),
                         capture_output=True, text=True, timeout=10, check=True)
    return json.loads(run.stdout)


def qualify(oval, converted, binary, revision):
    oracle = load(FIXTURE / "expected.json")
    raw = (oval / oracle["source_path"]).read_bytes()
    digest = sha256(raw).hexdigest()
    require_equal(digest, oracle["source_sha256"], "OVAL source bytes")
    source_bindings = verify_oval(raw, oracle)

    document = load(converted / "assessment.json")
    validator().validate(document)
    trace = load(converted / "source-trace.json")
    require_equal(trace["source_commit"], oracle["source_pin"], "source trace commit")
    require_equal(trace["source_sha256"], digest, "source trace bytes")
    require_equal(trace["definition_id"], oracle["definition"], "converted Definition")
    native_ids = {row["source_id"]: row["native_id"]
                  for row in trace["native_identities"] if row["kind"] == "test"}
    require_equal(set(native_ids), set(oracle["tests"]), "source Test IDs")
    variable_ids = {row["source_id"]: row["native_id"]
                    for row in trace["native_identities"] if row["kind"] == "variable"}
    assessment = document["assessment"]
    pin = trace["assessment_closure_sha256"]
    observed = {}
    literals = {}
    for source_id, expected in oracle["tests"].items():
        test_id = native_ids[source_id]
        test = assessment["tests"][test_id]
        merge = assessment["variables"][test["variable"]]["expression"]["merge"]
        literal_id = merge["values"]["variable"]
        require_equal((test["variable"], literal_id),
                      tuple(variable_ids[ref] for ref in source_bindings[source_id]), source_id)
        literals[source_id] = literal_id
        values = assessment["variables"][literal_id]["expression"]["literal"]["value"]
        require_equal(values, expected["values"], source_id)
        require_equal((merge["delimiter"], merge["sort"], merge["order"]),
                      (expected["delimiter"], expected["sort"], "ascending"), source_id)
        require_equal(test["require"]["fields"]["value"]["equals"], expected["joined"], source_id)
        reply = evaluate(binary, pin, document, test_id)
        require_equal(reply["technical_outcome"], "true", test_id)
        observed[source_id] = {"native_test": test_id, "outcome": reply["technical_outcome"],
                               "explanation": reply["explanation"]}

    mutation = oracle["reordered_integers"]
    changed = deepcopy(document)
    literal_id, = {literals[test] for test in mutation["outcomes"]}
    changed["assessment"]["variables"][literal_id]["expression"]["literal"]["value"] = mutation["values"]
    validator().validate(changed)
    outcomes = {}
    for source_id, expected in mutation["outcomes"].items():
        reply = evaluate(binary, pin, changed, native_ids[source_id])
        require_equal(reply["technical_outcome"], expected, source_id)
        outcomes[source_id] = reply["technical_outcome"]

    return {
        "format": "scap-ng-merge-source-witness-receipt-1",
        "source_sha256": digest,
        "native_assessment_sha256": sha256((converted / "assessment.json").read_bytes()).hexdigest(),
        "converter_revision": trace["converter_commit"],
        "schema_commit": trace["schema_commit"],
        "ri_revision": revision,
        "leaves": observed,
        "reordered_integers": outcomes,
        "scope": "Pinned homogeneous integer and ASCII merge cases. Direct RI Test evaluation only.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-assertion", type=Path, required=True)
    parser.add_argument("--converted", type=Path, required=True)
    parser.add_argument("--ri-evaluate", type=Path, required=True)
    parser.add_argument("--ri-revision", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = qualify(args.self_assertion, args.converted, args.ri_evaluate.resolve(strict=True), args.ri_revision)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check and (FIXTURE / "ri-receipt.json").read_text(encoding="utf-8") != rendered:
        raise SystemExit("merge receipt differs from the replay")
    print(rendered, end="")
