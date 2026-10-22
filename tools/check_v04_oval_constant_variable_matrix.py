#!/usr/bin/env python3
"""Two pinned original OVAL constant Variable -> 0.4 -> OVAL proof gates.

Validates the current native Assessment/capability schemas, YAML/JSON
equivalence, independent original-root semantic graph, OVAL 5.12.3 XSD and
adversarial meaning changes. Does not execute a scanner. Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

import yaml

from convert_v04_oval_constant_variable_matrix import CASES, convert
from export_v04_oval_constant_variable_matrix import emit
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_flat_object_authoring import dump_hybrid
from validate_v04_oval_5123 import check


def must(ok, label):
    if not ok:
        raise AssertionError(label)


def prove(original, schema_root, xsd_root, output, validators, capability_schema):
    raw = original.read_bytes()
    name = original.name
    native, proof = convert(raw, name)
    target = output / name.removesuffix(".xml")
    target.mkdir(parents=True, exist_ok=True)
    (target / "original.xml").write_bytes(raw)
    native_path = target / "native-040.assessment.json"
    native_path.write_text(json.dumps(native, indent=2) + "\n")
    yaml_text = dump_hybrid(native)
    (target / "native-040.assessment.yaml").write_text(yaml_text)
    must(yaml.safe_load(yaml_text) == native, "YAML/JSON native divergence")
    validate_docs({"authoring/" + name + ".assessment.json": native}, validators)
    for test in native["assessment"]["tests"].values():
        errors = validate(capability_schema, "test", test)
        must(not errors, "native variable.value Test schema: " +
             "; ".join(str(e) for e in errors[:3]))

    tree, new_id = emit(native)
    exported = target / "roundtrip-oval.xml"
    tree.write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "independent")
    (target / "roundtrip-xsd.json").write_text(
        json.dumps(xsd, indent=2) + "\n")
    must(xsd["status"] == "PASS", "OVAL 5.12.3 XSD: " + str(xsd["diagnostics"]))
    comparison = compare(original, exported, source_root=CASES[name][0],
                         regenerated_root=new_id, root_only=True)
    (target / "roundtrip-semantics.json").write_text(
        json.dumps(comparison, indent=2, default=str) + "\n")
    must(comparison["equal"], "original-versus-native OVAL semantic graph")

    # The conversion must never 'repair' changed pinned original OVAL source.
    tampered = raw.replace(b'check="all"', b'check="at least one"', 1)
    must(tampered != raw, "original Test source mutation not constructed")
    try:
        convert(tampered, name)
    except ValueError as exc:
        must("source SHA" in str(exc), "source hash guard")
    else:
        raise AssertionError("modified original OVAL Test was accepted")

    def reject_native(mutator, label):
        changed = deepcopy(native)
        mutator(changed["assessment"])
        try:
            emit(changed)
        except ValueError:
            return label
        raise AssertionError("unreviewed native change accepted: " + label)

    rejected = [
        reject_native(lambda a: a["tests"]["source-1-test"].__setitem__(
            "require", "none_exist"), "Test_check"),
        reject_native(lambda a: a["tests"].pop("source-1-test"),
                      "missing_Test"),
    ]
    first = native["assessment"]["tests"]["source-1-test"]["states"][0]["value"]
    if "value_match" in first:
        rejected.append(reject_native(lambda a: a["tests"]["source-1-test"][
            "states"][0]["value"].__setitem__("value_match", "unrecognized"),
            "var_check_enum"))
    else:
        rejected.append(reject_native(lambda a: a["tests"]["source-1-test"][
            "states"][0]["value"].__setitem__("value_match", "all"),
            "scalar_var_check"))

    mutated = deepcopy(native)
    values = mutated["assessment"]["variables"]["source-1-variable"][
        "expression"]["literal"]
    values[0] += 100
    tree, mutated_id = emit(mutated)
    mutated_file = target / "mutated-value-oval.xml"
    tree.write(mutated_file, encoding="utf-8", xml_declaration=True)
    comparison_bad = compare(original, mutated_file, source_root=CASES[name][0],
                             regenerated_root=mutated_id, root_only=True)
    must(not comparison_bad["equal"], "changed Variable was not detected")

    mutated = deepcopy(native)
    first_criterion = mutated["assessment"]["evaluate"]["and"][0]
    mutated["assessment"]["evaluate"]["and"][0] = (
        {"not": first_criterion} if "test" in first_criterion
        else first_criterion["not"])
    tree, mutated_id = emit(mutated)
    mutated_file = target / "mutated-negation-oval.xml"
    tree.write(mutated_file, encoding="utf-8", xml_declaration=True)
    comparison_bad = compare(original, mutated_file, source_root=CASES[name][0],
                             regenerated_root=mutated_id, root_only=True)
    must(not comparison_bad["equal"], "changed Criterion negation not detected")

    proof.update({
        "native_assessment_schema": "PASS",
        "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS",
        "oval_5123_xsd": "PASS",
        "original_root_semantic_graph": "PASS",
        "source_sha_mutation": "REJECTED",
        "native_structural_mutations": rejected,
        "independent_semantic_mutations": ["Variable_value", "Criterion_negation"],
    })
    (target / "source-and-mapping-proof.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n")
    return proof


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root", required=True, type=Path)
    parser.add_argument("--schema-root", required=True, type=Path)
    parser.add_argument("--xsd-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    validators = _schema_validators(args.schema_root)
    capability_schema = materialize("variable.value")
    proofs = []
    for name in CASES:
        path = args.original_root / "agnostic" / name
        must(path.is_file(), "missing pinned Self-Assertion case " + name)
        proofs.append(prove(path, args.schema_root, args.xsd_root, args.output,
                            validators, capability_schema))
    must(len(proofs) == 2 and sum(x["native_test_count"] for x in proofs) == 12,
         "two Definition / 12 Test source matrix")
    summary = {
        "status": "TWO_ORIGINAL_OVAL_DEFINITIONS_NATIVE_SCHEMA_XSD_GRAPH_PASS",
        "source_revision": "e3538595c5083b9c34d937a81d319234df9bbfaa",
        "definition_count": 2, "test_count": 12,
        "original_ids": [x["original_definition_id"] for x in proofs],
        "scanner_result_parity_proven": 0,
        "cumulative_167_promotion": "PENDING_INDEPENDENT_LEDGER_GATE",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
