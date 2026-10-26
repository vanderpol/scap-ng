#!/usr/bin/env python3
"""Original source -> 0.4 native -> independent OVAL 5.12.3 datatype proof.

All ten source-pinned datatype suites must pass schema, XSD, original-root
semantic graph and adversarial literal/criteria mutations. No scanner parity.
Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from v04_source_proof_contract import current_document, independent_export_view
from copy import deepcopy
import json
from pathlib import Path

import yaml

from convert_v04_oval_variable_datatype_suite import CASES, ENTITY_CASE, PIN, convert as _source_convert
from export_v04_oval_variable_datatype_suite import emit as _source_emit
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_flat_object_authoring import dump_hybrid
from validate_v04_oval_5123 import check


def convert(*args, **kwargs):
    source, proof = _source_convert(*args, **kwargs)
    return current_document(source), proof


def emit(document):
    return _source_emit(independent_export_view(document))


def must(ok, reason):
    if not ok:
        raise AssertionError("pinned variable datatype suite: " + reason)


def invert_first_leaf(node):
    if "test" in node:
        return {"not": node}
    if "not" in node:
        return node["not"]
    must("and" in node and len(node["and"]) > 0, "first Boolean leaf")
    node["and"][0] = invert_first_leaf(node["and"][0])
    return node


def prove(source, validators, capability_schema, xsd_root, output):
    filename = source.name
    raw = source.read_bytes()
    native, provenance = convert(raw, filename)
    target = output / filename.removesuffix(".xml")
    target.mkdir(parents=True, exist_ok=True)
    (target / "original.xml").write_bytes(raw)
    (target / "native-040.assessment.json").write_text(json.dumps(native, indent=2) + "\n")
    yaml_text = dump_hybrid(native)
    (target / "native-040.assessment.yaml").write_text(yaml_text)
    must(yaml.safe_load(yaml_text) == native, "YAML/JSON identity")
    validate_docs({"authoring/" + filename + ".assessment.json": native}, validators)
    for name, test in native["assessment"]["tests"].items():
        errors = validate(capability_schema, "test", test)
        must(not errors, "variable.value capability schema " + name + ": " +
             "; ".join(str(e) for e in errors[:2]))
    xml, root_id = emit(native)
    exported = target / "roundtrip-oval.xml"
    xml.write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "independent")
    (target / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    must(xsd["status"] == "PASS", "OVAL 5.12.3 XSD " + str(xsd["diagnostics"][:3]))
    sem = compare(source, exported, source_root=CASES[filename][0],
                  regenerated_root=root_id, root_only=True)
    (target / "roundtrip-semantics.json").write_text(
        json.dumps(sem, indent=2, default=str) + "\n")
    must(sem["equal"], "OVAL original-root semantic graph " + filename)

    old_check = (b'check="all"' if provenance["source_datatype"] in
                 {"ipv4_address", "ipv6_address"} or filename == ENTITY_CASE
                 else b'check="at least one"')
    new_check = (b'check="at least one"' if old_check == b'check="all"'
                 else b'check="all"')
    tampered = raw.replace(old_check, new_check, 1)
    must(raw != tampered, "construct source Test adversary")
    try:
        convert(tampered, filename)
    except ValueError as exc:
        must("source SHA" in str(exc), "source SHA pin rejection")
    else:
        raise AssertionError("accepted modified source Test check")

    invalid = deepcopy(native)
    invalid["assessment"]["tests"]["source-1-test"]["require"] = "none_exist"
    try:
        emit(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("unsupported native Test semantics exported")

    changed = independent_export_view(native)
    firstvar = changed["assessment"]["variables"]["source-1-variable"]
    firstvar["expression"]["literal"][0] += "-altered"
    xml, altered_id = emit(current_document(changed))
    altered = target / "mutated-variable.xml"
    xml.write(altered, encoding="utf-8", xml_declaration=True)
    must(not compare(source, altered, source_root=CASES[filename][0],
                     regenerated_root=altered_id, root_only=True)["equal"],
         "modified Variable literal must change original meaning")

    changed = independent_export_view(native)
    changed["assessment"]["evaluate"] = invert_first_leaf(
        changed["assessment"]["evaluate"])
    xml, altered_id = emit(current_document(changed))
    altered = target / "mutated-criterion.xml"
    xml.write(altered, encoding="utf-8", xml_declaration=True)
    must(not compare(source, altered, source_root=CASES[filename][0],
                     regenerated_root=altered_id, root_only=True)["equal"],
         "modified Criterion negation must change original meaning")
    if provenance["source_datatype"] in {"ipv4_address", "ipv6_address"}:
        prefix = "ipv4_" if provenance["source_datatype"] == "ipv4_address" else "ipv6_"
        changed = independent_export_view(native)
        subset = next(t["states"][0]["value"] for t in changed["assessment"]["tests"].values()
                      if prefix + "subset_of" in t["states"][0]["value"])
        subset[prefix + "superset_of"] = subset.pop(prefix + "subset_of")
        xml, altered_id = emit(current_document(changed))
        altered = target / "mutated-ip-subnet-operation.xml"
        xml.write(altered, encoding="utf-8", xml_declaration=True)
        must(not compare(source, altered, source_root=CASES[filename][0],
                         regenerated_root=altered_id, root_only=True)["equal"],
             "IP subset/superset direction must change original meaning")
        changed = independent_export_view(native)
        changed["assessment"]["tests"]["source-1-test"]["require"] = (
            "at_least_one_exists_and_some_match")
        try:
            emit(current_document(changed))
        except ValueError:
            pass
        else:
            raise AssertionError("IP original all-check lowered as some-match")
    if filename == ENTITY_CASE:
        changed = independent_export_view(native)
        first = changed["assessment"]["tests"]["source-1-test"]["states"][0]["value"]
        must(first["require"] == "at_least_one_exists_and_all_match",
             "entity_check first original all")
        first["require"] = "at_least_one_exists_and_some_match"
        xml, altered_id = emit(current_document(changed))
        altered = target / "mutated-entity-check.xml"
        xml.write(altered, encoding="utf-8", xml_declaration=True)
        must(not compare(source, altered, source_root=CASES[filename][0],
                         regenerated_root=altered_id, root_only=True)["equal"],
             "entity_check all-to-at-least-one must change OVAL source meaning")
    provenance.update({
        "native_assessment_schema": "PASS",
        "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS",
        "oval_5123_xsd": "PASS",
        "original_root_semantic_graph": "PASS",
        "source_sha_mutation": "REJECTED",
        "native_test_requirement_mutation": "REJECTED",
        "original_variable_mutation": "DETECTED",
        "original_criterion_mutation": "DETECTED",
        "ip_subset_direction_mutation": (
            "DETECTED" if provenance["source_datatype"] in
            {"ipv4_address", "ipv6_address"} else "NOT_APPLICABLE"),
        "entity_check_mutation": "DETECTED" if filename == ENTITY_CASE
                                 else "NOT_APPLICABLE",
    })
    (target / "source-and-mapping-proof.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    return provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-root", required=True, type=Path)
    parser.add_argument("--schema-root", required=True, type=Path)
    parser.add_argument("--xsd-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    validators = _schema_validators(args.schema_root)
    capability_schema = materialize("variable.value")
    reports = []
    for filename in CASES:
        source = args.original_root / "agnostic" / filename
        must(source.is_file(), "pinned Self-Assertion source " + filename)
        reports.append(prove(source, validators, capability_schema,
                             args.xsd_root, args.output))
    must(len(reports) == 10 and sum(r["native_test_count"] for r in reports) == 158,
         "10 original datatype/field-enumeration Definitions and 158 original Tests")
    summary = {
        "status": "TEN_ORIGINAL_OVAL_DATATYPE_AND_ENTITY_CHECK_DEFINITIONS_PASS",
        "source_revision": PIN,
        "definition_count": 10, "test_count": 158,
        "original_ids": [r["original_definition_id"] for r in reports],
        "scanner_result_parity_proven": 0,
        "cumulative_167_promotion": "PENDING_INDEPENDENT_LEDGER_GATE",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
