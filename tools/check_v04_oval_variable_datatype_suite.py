#!/usr/bin/env python3
"""Original source -> 0.4 native -> independent OVAL 5.12.3 datatype proof.

All seven source-pinned datatype suites must pass schema, XSD, original-root
semantic graph and adversarial literal/criteria mutations. No scanner parity.
Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path

import yaml

from convert_v04_oval_variable_datatype_suite import CASES, PIN, convert
from export_v04_oval_variable_datatype_suite import emit
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_flat_object_authoring import dump_hybrid
from validate_v04_oval_5123 import check


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

    tampered = raw.replace(b'check="at least one"', b'check="all"', 1)
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

    changed = deepcopy(native)
    firstvar = changed["assessment"]["variables"]["source-1-variable"]
    firstvar["expression"]["literal"][0] += "-altered"
    xml, altered_id = emit(changed)
    altered = target / "mutated-variable.xml"
    xml.write(altered, encoding="utf-8", xml_declaration=True)
    must(not compare(source, altered, source_root=CASES[filename][0],
                     regenerated_root=altered_id, root_only=True)["equal"],
         "modified Variable literal must change original meaning")

    changed = deepcopy(native)
    changed["assessment"]["evaluate"] = invert_first_leaf(
        changed["assessment"]["evaluate"])
    xml, altered_id = emit(changed)
    altered = target / "mutated-criterion.xml"
    xml.write(altered, encoding="utf-8", xml_declaration=True)
    must(not compare(source, altered, source_root=CASES[filename][0],
                     regenerated_root=altered_id, root_only=True)["equal"],
         "modified Criterion negation must change original meaning")
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
    must(len(reports) == 7 and sum(r["native_test_count"] for r in reports) == 122,
         "7 original datatype Definitions and 122 original Tests")
    summary = {
        "status": "SEVEN_ORIGINAL_OVAL_DATATYPE_DEFINITIONS_NATIVE_SCHEMA_XSD_GRAPH_PASS",
        "source_revision": PIN,
        "definition_count": 7, "test_count": 122,
        "original_ids": [r["original_definition_id"] for r in reports],
        "scanner_result_parity_proven": 0,
        "cumulative_167_promotion": "PENDING_INDEPENDENT_LEDGER_GATE",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
