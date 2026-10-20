#!/usr/bin/env python3
"""OVAL XML -> *actual* SCAP-NG 0.4.0 -> regenerated OVAL XML differential.

The input manifest MUST come from an actual v0.4.0 converter and exporter run.
This tool does not regenerate XML from original source/provenance, and does not
use the old v003 exporter. It checks the resulting independent output, and is
fail-closed for missing artifacts, non-v0.4 Assessment syntax, semantic changes,
and (optionally) incompletely covered corpora.

Root Definition semantics are compared ID-independently via the maintained
OVAL 5.12.3 graph comparator; a secondary canonical XML diff is diagnostic,
not the pass criterion. Do not confuse an authoring exact inverse with this
independent export, or a semantic XML comparison with scanner execution.

Refs #248, #229.
"""
from __future__ import annotations

import argparse
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from scap_ng_roundtrip_v003.compare_oval_semantics import compare as compare_oval

FORMAT = "scap-ng-v04-oval-xml-roundtrip-1"
OVAL_NS = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
MAX_DIFF_LINES = 100


def read_doc(path):
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    if path.suffix in (".yaml", ".yml"):
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    raise ValueError("Assessment authoring must be JSON or YAML")


def safe_file(root, rel):
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise ValueError("File path must be relative to audit root")
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError("Missing/out-of-root roundtrip artifact: " + repr(rel))
    return target


def checked_hash(path, expected):
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError("A SHA-256 is mandatory for every roundtrip artifact")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError("Input artifact SHA-256 changed: " + path.name)
    return actual


def xml_root(path):
    node = ET.parse(path).getroot()
    if node.tag != "{" + OVAL_NS + "}oval_definitions":
        raise ValueError("Expected original OVAL Definitions XML, not ARF/XCCDF or a result document")
    return node


def xml_diagnostic(source, output):
    source_text = ET.canonicalize(source.read_text(encoding="utf-8")).splitlines()
    output_text = ET.canonicalize(output.read_text(encoding="utf-8")).splitlines()
    return list(difflib.unified_diff(source_text, output_text,
                 fromfile=source.name, tofile=output.name,
                 lineterm=""))[:MAX_DIFF_LINES]


def check_case(row, root, *, compare_fn=compare_oval):
    ident = row["case_id"]
    if not isinstance(ident, str) or not ident:
        raise ValueError("Case ID required")
    stage = row["status"]
    if stage == "blocked":
        if row.get("original") is None or row.get("blocker") is None:
            raise ValueError(ident + ": blocked source requires explicit artifact and blocker reason")
        source = safe_file(root, row["original"])
        checked_hash(source, row.get("original_sha256"))
        xml_root(source)
        return {"case_id": ident, "status": "BLOCKED",
                "blocker": row["blocker"], "source_sha256": row["original_sha256"]}
    if stage != "converted":
        raise ValueError(ident + ": unrecognized coverage status")
    if row.get("forward_profile") != "0.4.0" or row.get("reverse_profile") != "0.4.0":
        raise ValueError(ident + ": converter AND exporter must be active 0.4.0")
    files = {}
    for key in ("original", "native_assessment", "regenerated"):
        files[key] = safe_file(root, row[key])
        checked_hash(files[key], row.get(key + "_sha256"))
    if files["original"] == files["regenerated"]:
        raise ValueError(ident + ": exporter cannot return original source path")
    xml_root(files["original"])
    xml_root(files["regenerated"])
    native = read_doc(files["native_assessment"])
    assessment = native.get("assessment") if isinstance(native, dict) else None
    spec = assessment.get("specification") if isinstance(assessment, dict) else None
    if (not isinstance(spec, dict) or spec.get("version") != "0.4.0"
            or assessment.get("mode") != "automated"
            or not isinstance(assessment.get("tests"), dict)
            or not assessment["tests"]):
        raise ValueError(ident + ": no real 0.4.0 automated Assessment in conversion output")
    source_id = row.get("source_definition")
    target_id = row.get("regenerated_definition")
    if not source_id or not target_id:
        raise ValueError(ident + ": original and exported Definition IDs are required")
    comparison = compare_fn(
        files["original"], files["regenerated"],
        source_root=source_id, regenerated_root=target_id,
        root_only=True,
    )
    result = {"case_id":ident, "status":"EQUAL" if comparison["equal"] else "DIFFERENT",
              "source_definition":source_id,
              "regenerated_definition":target_id,
              "source_sha256":row["original_sha256"],
              "native_sha256":row["native_assessment_sha256"],
              "regenerated_sha256":row["regenerated_sha256"],
              "semantic_equal":comparison["equal"],
              "schema_validated":False, "scanner_executed":False}
    if not comparison["equal"]:
        # Include the first canonicalized XML delta and both graph signatures
        # to explain discrepancies in original OVAL vocabulary.
        result["semantic_diff"] = {
            "source_graph":str(comparison.get("source_definition",""))[:12000],
            "regenerated_graph":str(comparison.get("regenerated_definition",""))[:12000],
        }
        result["xml_diff"] = xml_diagnostic(files["original"], files["regenerated"])
    return result


def audit(manifest, root, *, compare_fn=compare_oval, expected=None):
    if manifest.get("format") != FORMAT or manifest.get("profile") != "0.4.0":
        raise ValueError("Not a 0.4.0 roundtrip input manifest")
    cases=manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("Roundtrip manifest must enumerate source Definition cases")
    if expected is not None and len(cases) != expected:
        raise ValueError("Missing OVAL test-content cases: expected %d, got %d" %
                         (expected,len(cases)))
    seen=set()
    outcomes=[]
    for row in cases:
        if not isinstance(row, dict) or row.get("case_id") in seen:
            raise ValueError("Invalid or duplicate OVAL Definition coverage record")
        seen.add(row["case_id"])
        # Do not stop at first failure; preserve source-specific diagnostics.
        try:
            outcomes.append(check_case(row, root, compare_fn=compare_fn))
        except Exception as exc:
            outcomes.append({"case_id":row["case_id"],"status":"ERROR",
                             "reason":str(exc)})
    counts=Counter(item["status"] for item in outcomes)
    status="PASS" if len(outcomes)==len(cases) and counts == {"EQUAL":len(cases)} else "FAIL"
    return {"format":"scap-ng-v04-oval-xml-roundtrip-report-1",
            "status":status, "source_case_count":len(cases),
            "outcome_counts":dict(sorted(counts.items())),
            "cases":outcomes, "xsd_validation":"NOT_RUN",
            "schematron_validation":"NOT_RUN",
            "scanner_execution":"NOT_RUN"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--expected-cases",type=int,default=None)
    args=p.parse_args()
    report=audit(json.loads(args.manifest.read_text()),args.root,expected=args.expected_cases)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="cases"},indent=2))
    raise SystemExit(0 if report["status"]=="PASS" else 1)

if __name__=="__main__":
    main()
