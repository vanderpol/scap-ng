#!/usr/bin/env python3
"""#240/#232: ONE COMMAND: frozen YAML + JSON -> verified A research IR.

Run the two parsers and full independent base/0.4 Test validation, insist on
identical unsigned authoring research archive bytes, then independently build
and decode the same normalized typed source IR from both staged input graphs.
No source rewrites, approved migration, scanner or signed bundle is claimed.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from v04_a_authoring_graph_index import canonical_json, read_authoring_archive
from v04_a_end_to_end_base_authoring import stage_and_package, _extract_docs
from v04_a_lossless_ir import IR_FORMAT, IR_STATUS, normalize_documents, decode_and_verify


def compile_pair(json_archive, yaml_archive, *, validate_base=True):
    """Return checked IR source bytes, unsigned research ZIP, report.

    validate_base=False is exclusively for synthetic unit-test fixtures.
    There is deliberately no CLI switch to skip source validation.
    """
    jsource = read_authoring_archive(json_archive, "json")
    ysource = read_authoring_archive(yaml_archive, "yaml")
    jzip, jreport = stage_and_package(jsource, validate_base=validate_base)
    yzip, yreport = stage_and_package(ysource, validate_base=validate_base)
    if jzip != yzip or jreport != yreport:
        raise ValueError("independently parsed YAML/JSON base research packages differ")
    jdocs, jm = _extract_docs(jzip)
    ydocs, ym = _extract_docs(yzip)
    j_ir = normalize_documents(jdocs)
    y_ir = normalize_documents(ydocs)
    if canonical_json(j_ir) != canonical_json(y_ir):
        raise ValueError("YAML/JSON independently normalized typed IR differs")
    if decode_and_verify(j_ir) != jdocs or decode_and_verify(y_ir) != ydocs:
        raise ValueError("independent source AST decode differs from base input")
    from jsonschema import Draft202012Validator
    root = Path(__file__).resolve().parents[1]
    schema_path = (root / "research/assessment-simplification/"
                   "compact-authoring-04/lossless-ir-envelope.schema.json")
    research_schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(research_schema)
    Draft202012Validator(research_schema).validate(j_ir)
    ir_data = canonical_json(j_ir) + b"\n"
    result = {
        "status": "DUAL_FORMAT_VERIFIED_IR_RESEARCH_NOT_EXECUTABLE",
        "ir_format": IR_FORMAT,
        "ir_stage": IR_STATUS,
        "source_documents": len(jdocs),
        "automated_assessments": j_ir["automated_assessment_count"],
        "automated_tests": j_ir["automated_test_count"],
        "rule_choice_links": j_ir["rule_choice_link_count"],
        "source_graph_sha256": j_ir["source_graph_sha256"],
        "ir_sha256": sha256(ir_data).hexdigest(),
        "unsigned_base_archive_sha256": sha256(jzip).hexdigest(),
        "full_source_preservation": "PASS",
        "base_schema": jreport["base_schema"],
        "native_capability_test_nodes_validated": jreport[
            "native_capability_proof"]["native_test_nodes_validated"],
        "yaml_json_base_byte_parity": "PASS",
        "yaml_json_ir_byte_parity": "PASS",
        "research_ir_schema": "PASS",
        "version_policy_approved": False,
        "native_executable_compiler_completed": False,
        "signed_bundle": False,
        "scanner_executed": False,
    }
    return ir_data, jzip, result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", type=Path, required=True)
    p.add_argument("--yaml-archive", type=Path, required=True)
    p.add_argument("--out-ir", type=Path, required=True)
    p.add_argument("--out-base-zip", type=Path,
                   help="optional unsigned research artifact, never a scannable .scapng")
    p.add_argument("--report-json", type=Path)
    p.add_argument("--assert-six", action="store_true")
    args = p.parse_args(argv)
    ir, research_zip, report = compile_pair(args.json_archive, args.yaml_archive)
    if args.assert_six:
        if (report["source_documents"], report["automated_assessments"],
            report["automated_tests"], report["rule_choice_links"]) != (
                4001, 872, 1375, 2958):
            raise ValueError("pinned six-STIG typed IR counts differ")
        if report["native_capability_test_nodes_validated"] != 1375:
            raise ValueError("0.4 capability-specific native Test gate incomplete")
        if report["base_schema"] != "ALL_AUTOMATED_ASSESSMENTS_VALIDATED":
            raise ValueError("0.4 base Assessment schema gate incomplete")
    args.out_ir.parent.mkdir(parents=True, exist_ok=True)
    args.out_ir.write_bytes(ir)
    if args.out_base_zip:
        args.out_base_zip.parent.mkdir(parents=True, exist_ok=True)
        args.out_base_zip.write_bytes(research_zip)
    rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
    print(rendered, end="")
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
