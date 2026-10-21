#!/usr/bin/env python3
"""Fail-closed original OVAL Self-Assertion release-readiness inventory.

Consumes a completed, source-pinned independent OVAL->0.3->OVAL compatibility
review and an older experimental 0.4-C subset manifest. This is NOT a 0.4.0
converter or native 0.4.0 round-trip proof. Refs #248 #245 #229 #232.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from hashlib import sha256
import json
from pathlib import Path

PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
EXPECTED = {"files": 144, "definitions": 167, "declared_tests": 785,
            "source_compatible": 162, "source_blocked": 5,
            "experimental_c": 36, "not_c": 126}
TOP = {"VARIABLE_SOURCE_GRAPH_NEEDS_COMPATIBILITY": 68, "MULTI_TEST": 44}
FIELDS = ["source_file","definition_id","source_status","source_test_count",
          "native_test_count","native_capabilities","experimental_c_status",
          "experimental_c_reason","original_source_file_sha256",
          "current_040_native_schema","current_040_oval_xml_roundtrip",
          "scanner_six_state_parity"]


def build(root: Path):
    root = Path(root)
    review = json.loads((root/"c-review/manifest.json").read_text())
    c = json.loads((root/"c-native/conversion-manifest.json").read_text())
    if review["source_revision"] != PIN:
        raise ValueError("Unpinned OVAL Test Content source revision")
    expected_keys = {"source_file_count":"files","source_definition_count":"definitions",
                     "source_test_count":"declared_tests",
                     "A_source_parity_review_definitions":"source_compatible",
                     "failed_A_roundtrip_or_unsupported_definitions":"source_blocked"}
    for key, metric in expected_keys.items():
        if review[key] != EXPECTED[metric]:
            raise ValueError(f"Original source census changed: {key}")
    if c["A_compatible_Definitions_seen"] != EXPECTED["source_compatible"]:
        raise ValueError("Experimental converter source universe changed")
    if c["native_C_Definitions"] != EXPECTED["experimental_c"] or c[
            "source_compatible_not_yet_native_C"] != EXPECTED["not_c"]:
        raise ValueError("Experimental converter subset changed")
    source = {(x["file"], x["definition_id"]): x
              for x in review["exported_views"]}
    blocked = {(x["file"], x["definition_id"]): x
               for x in review["blocked_definitions"]}
    converted = {(x["file"], x["definition_id"]): x
                 for x in c["native_C_converted"]}
    unsupported = {(x["file"], x["definition_id"]): x
                   for x in c["unsupported"]}
    if any(len(m) != len(rows) for m,rows in (
            (source,review["exported_views"]),
            (blocked,review["blocked_definitions"]),
            (converted,c["native_C_converted"]),
            (unsupported,c["unsupported"]))):
        raise ValueError("Duplicate original OVAL Definition identifier")
    if source.keys() & blocked.keys() or converted.keys() & unsupported.keys():
        raise ValueError("Overlap in distinct release dispositions")
    if (converted.keys() | unsupported.keys()) != source.keys():
        raise ValueError("Experimental 0.4 subset does not account for 162 source-compatible Definitions")
    if len(source | blocked) != EXPECTED["definitions"]:
        raise ValueError("Original Definition closure incomplete")
    reasons=Counter(x["reason"].split(":",1)[0] for x in unsupported.values())
    if any(reasons[x] != n for x,n in TOP.items()):
        raise ValueError("Regression in the two leading unsupported reasons")
    rows=[]
    for identity in sorted(source.keys() | blocked.keys()):
        file, did=identity
        if identity in blocked:
            entry=blocked[identity]
            reason=";".join(str(x.get("feature"))
                             for x in entry.get("unsupported_features",[]))
            rows.append(dict(zip(FIELDS,[
                file,did,"OVAL_SOURCE_INVALID_OR_DEPRECATED",0,0,"",
                "NOT_CONVERTIBLE_SOURCE",reason,"","NOT_TESTED","NOT_TESTED","NOT_TESTED"])))
            continue
        r=source[identity]
        path=root/"c-review"/r["review_file"]
        document=json.loads(path.read_text())
        src=document["source"]
        native=document["A_source_compatibility_fallback"]
        if src["file"]!=file or src["definition_id"]!=did or src[
                "source_file_sha256"] in ("",None):
            raise ValueError("Source identity/provenance mismatch: "+file)
        if src["source_file_sha256"] != document["source"]["source_file_sha256"]:
            raise ValueError("Source digest changed")
        original_tests=src["original_test_documentation"]
        if len(original_tests)!=r["original_tests"] or len(native["tests"])!=r["native_tests"]:
            raise ValueError("OVAL Test closure differs from source-compatibility record")
        if not all(test.get("id") and test.get("kind") for test in original_tests):
            raise ValueError("Original OVAL Test identity undocumented")
        if identity in converted:
            status="EARLIER_EXPERIMENTAL_C_PROVED_A_PROJECTION_ONLY"
            reason=""
            record=converted[identity]
            if not record.get("native_C_compilation_passed") or not record.get(
                    "A_projection_equivalence_checked"):
                raise ValueError("Experimental C was counted without source-compatible proof")
        else:
            status="SOURCE_COMPATIBLE_NOT_EXPERIMENTAL_C"
            reason=unsupported[identity]["reason"]
        caps=";".join(sorted({t["capability"] for t in native["tests"].values()}))
        rows.append(dict(zip(FIELDS,[
            file,did,"OVAL_003_SOURCE_COMPATIBLE",
            len(original_tests),len(native["tests"]),caps,status,reason,
            src["source_file_sha256"],"NOT_TESTED","NOT_TESTED","NOT_TESTED"])))
    if len(rows)!=167:
        raise ValueError("Manifest does not close 167 source Definitions")
    classifications=Counter(x["experimental_c_status"] for x in rows)
    return rows,{
        "status":"SOURCE_PINNED_RELEASE_GAP_AUDIT_NOT_CURRENT_040_VALIDATION",
        "source_repository":"OVAL-Community/SCAP-Self-Assertion",
        "source_revision":PIN,"declared_oval_tests":785,
        "source_xml_files":144,"definitions":167,
        "dispositions":dict(sorted(classifications.items())),
        "recorded_first_blocking_reasons":dict(sorted(reasons.items())),
        "current_040_validated_definitions_in_this_corpus":0,
        "current_040_schema_gate":"NOT_TESTED_FOR_THIS_CORPUS",
        "original_oval_xml_roundtrip_gate":"NOT_TESTED_FOR_THIS_CORPUS",
        "scanner_six_state_parity_gate":"NOT_TESTED",
        "evidence_scope":"historical pinned source OVAL->v003 OVAL compatibility plus experimental C-to-A subset only",
    }


def publish(rows,report,out):
    out=Path(out);out.mkdir(exist_ok=True,parents=True)
    with (out/"original-oval-definition-release-gaps.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
    (out/"release-readiness.json").write_text(
        json.dumps({"summary":report,"definitions":rows},indent=2,ensure_ascii=False)+"\n")
    lines=[
      "# SCAP-NG 0.4.0 — original OVAL Test Content release-readiness inventory","",
      "**This is a gap report, NOT a validated 0.4.0 OVAL Test Content conversion.**","",
      "Pinned source: `OVAL-Community/SCAP-Self-Assertion@"+PIN+"`.","",
      "- Declared source: **144 XML files, 167 Definitions, 785 Tests**.",
      "- **162** Definitions had source-compatible v003 XML round-trip evidence.",
      "- **36** of those previously reached an experimental C→A source-equivalent subset.",
      "- **126** source-compatible Definitions remained outside that experimental converter.",
      "- **5** had documented invalid/deprecated original source content.",
      "- **0 of 167** have established *full-corpus* current 0.4.0 native-schema / original-XML semantic round-trip / scanner parity proof in this inventory.",
      "",
      "## Dominant first unsupported reason (per Definition)","",
    ]
    for reason,count in sorted(report["recorded_first_blocking_reasons"].items(),key=lambda kv:(-kv[1],kv[0])):
        lines.append(f"- {reason}: {count}")
    lines+=["","## Priorities","",
      "1. Preserve and modernize source Variable graphs before extending C syntax; account for 68 immediately blocked Definitions.",
      "2. Lower multi-Test Definitions with explicit AND/OR/ONE/XOR and original check/existence scope; 44 immediately blocked Definitions.",
      "3. Address remaining specialized cardinality, capability and nil/type cases individually.",
      "4. Validate every Definition against the *current* 0.4.0 native grammar, export supported graphs independently to OVAL 5.12.3 and compare source semantics. Never promote source-inverse parity as scanner runtime parity.",
      "",
      "See `original-oval-definition-release-gaps.csv` for every original source path/ID and its first recorded blocking reason.",
      ""]
    (out/"START-HERE.md").write_text("\n".join(lines))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",type=Path,required=True,
                   help="Extracted historical source-backed review artifact root")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    rows,report=build(args.input)
    publish(rows,report,args.output)
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    main()
