#!/usr/bin/env python3
"""#237: six-stream B executable-coverage compiler gate (RESEARCH ONLY).

Compiles only source patterns the current B prototype can lower and decode.
Every other referenced Assessment is accounted for explicitly. A preserved
0.3 source capsule is NOT executable compatibility code; manual checks are
not counted as executable. Do not publish a partial research ZIP as a scanner
package. Original raw SCAP 1.4/OVAL semantic parity is not established.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import io
import json
from pathlib import Path
import zipfile

from research_b_full_corpus_import import read_source, import_corpus
from research_b_source_textfile_lowering import lower_state_free_textfile_assessment
from research_b_source_partition_lowering import lower_state_free_partition_assessment
from research_b_source_textfile_state_lowering import lower_single_capture_textfile_assessment
from research_b_source_boolean_lowering import lower_source_boolean_assessment
from research_b_source_wmi_lowering import lower_state_free_wmi_assessment
from research_b_source_registry_lowering import lower_source_registry_assessment
from research_b_source_shell_lowering import lower_source_shell_assessment
from research_b_manual_lowering import lower_manual_assessment
from research_b_compiled_ir import encode, decode

FORMAT = "scap-ng-b-six-stream-research-coverage/0.1"
STATUS = "partial-research-not-a-scanner-bundle"
READY_STATUS = "fixture_ir_compiled_source_parity_unverified"


def _ir_filename(assessment_id):
    """Independent of source filename, collision-resistant and zip-safe."""
    return "fixture-ir/" + sha256(assessment_id.encode("utf-8")).hexdigest() + ".json"


_SOURCE_LEAF_LOWERERS=(
    lower_state_free_textfile_assessment,
    lower_state_free_partition_assessment,
    lower_single_capture_textfile_assessment,
    lower_state_free_wmi_assessment,
    lower_source_registry_assessment,
    lower_source_shell_assessment,
)


def _recompile_source_leaf(capsule, test_id):
    """Regenerate a Test leaf independently from its pinned source mapping.

    The compiler uses this only to verify that the final source-provenance
    contract matches the actual converted 0.3 Test, not an invented leaf
    sharing the same ID. This still does not verify original SCAP 1.4 XML.
    """
    a=capsule["source_document"]["assessment"]
    tests=a["tests"]
    single={k:v for k,v in a.items() if k not in ("tests","evaluate")}
    single["tests"]={test_id:tests[test_id]}
    single["evaluate"]={"test":test_id}
    document={"assessment":single}
    candidates=[]
    for lowerer in _SOURCE_LEAF_LOWERERS:
        try:
            candidates.append(lowerer(document))
        except (ValueError,KeyError,TypeError):
            pass
    if not candidates:
        raise ValueError("no independent verified lowering for source Test "+test_id)
    if len(candidates)>1 and any(candidate != candidates[0] for candidate in candidates[1:]):
        raise ValueError("ambiguous source Test lowerings "+test_id)
    return candidates[0]


def _assert_complete_source_provenance(root, capsule):
    """Require every referenced source Test to survive nested Boolean IR.

    A composite AND/OR root carries no Test ID itself. The lowering is valid
    only when ALL source Test definitions have matching, compiler-owned
    leaves. No source branch may be silently omitted or substituted.
    """
    a = capsule["source_document"]["assessment"]
    declared = a.get("tests")
    if not isinstance(declared, dict) or not declared:
        raise ValueError("automated source has no Test table")
    seen = set()

    def visit(node, depth=0):
        if depth > 64 or not isinstance(node, dict):
            raise ValueError("malformed or overdeep compiled source expression")
        if node.get("kind") == "logic":
            if node.get("operator") not in {"all", "any"}:
                raise ValueError("unexpected compiler Boolean operator")
            children = node.get("children")
            if not isinstance(children, list) or len(children) < 2:
                raise ValueError("missing compiler Boolean branch")
            for child in children:
                visit(child, depth + 1)
            return
        if node.get("kind") not in {
            "compat_oval_provider_existence", "compat_oval_provider_state",
            "compat_oval_registry_view_invariant", "compat_oval_shellcommand_state"
        }:
            raise ValueError("unsupported or native-authored source Test leaf")
        if node.get("source_assessment_id") != capsule["id"]:
            raise ValueError("compiled source Assessment identity changed")
        tid = node.get("source_test_id")
        if not isinstance(tid, str) or tid not in declared:
            raise ValueError("compiled source Test reference is not declared")
        expected=_recompile_source_leaf(capsule, tid)
        if node != expected:
            raise ValueError("compiled source Test semantics/selection diverge: "+tid)
        seen.add(tid)

    visit(root)
    if seen != set(declared):
        raise ValueError("compiled source omitted Test definitions: " +
                         repr(sorted(set(declared) - seen)))


def _lower_assessment(capsule):
    doc = capsule["source_document"]
    a = doc.get("assessment")
    if not isinstance(a, dict):
        return "unsupported_source_assessment", "missing Assessment envelope", None
    mode = a.get("mode")
    if mode == "manual":
        try:
            ast=lower_manual_assessment(doc)
            encoded=encode(capsule["id"],ast)
            if decode(encoded)["source_kind"]!="manual":
                raise ValueError("unexpected nonmanual compiled source kind")
            return ("manual_procedure_ir_compiled",
                    "publisher procedure preserved; human attestation required",encoded)
        except (ValueError,KeyError,TypeError) as exc:
            return ("manual_contract_unimplemented",
                    "unsupported manual contract: "+str(exc)[:440],None)
    if mode != "automated":
        return "unsupported_source_assessment", "unrecognized Assessment mode", None
    rejections=[]
    families=[
        ("independent.textfilecontent54/state_free_existence",lower_state_free_textfile_assessment),
        ("linux.partition/state_free_existence",lower_state_free_partition_assessment),
        ("independent.textfilecontent54/single_capture_state",lower_single_capture_textfile_assessment),
        ("windows.wmi.query/state_free_existence",lower_state_free_wmi_assessment),
        ("windows.registry/single_literal_state_unresolved_view",lower_source_registry_assessment),
        ("independent.shellcommand/static_stdout_equality",lower_source_shell_assessment),
        ("supported_Test_Boolean_AND_OR",lower_source_boolean_assessment),
    ]
    for family,lowerer in families:
        try:
            ast = lowerer(doc)
            encoded = encode(capsule["id"], ast)
            decoded = decode(encoded)
            if decoded["source_kind"] != "compiler-compatibility":
                raise ValueError("lowered source must retain compiler-only compatibility scope")
            _assert_complete_source_provenance(decoded["root"], capsule)
            return READY_STATUS, family+"; original XML/runtime parity OPEN", encoded
        except (ValueError, KeyError, TypeError) as exc:
            rejections.append(family+": "+str(exc)[:220])
    return "unsupported_source_semantics", "; ".join(rejections)[:500], None

def build_six_stream_report(corpus, capsules):
    """Pure deterministic per-assessment/per-stream accounting.

    All source reference closure comes from import_corpus. No mutation of its
    nonexecutable source capsule is allowed; these statuses are a separate
    conversion attempt.
    """
    if corpus.get("status") != "structural_only_not_executable":
        raise ValueError("expected validated, nonexecuting source accounting")
    names = corpus.get("source_benchmark_names")
    if not isinstance(names,list) or not names:
        raise ValueError("missing source stream names")
    by_assessment = defaultdict(set)
    for rule in corpus["rules"]:
        if rule["benchmark"] not in names:
            raise ValueError("Rule references an unknown stream")
        for choice in rule["choices"]:
            by_assessment[choice["assessment_id"]].add(rule["benchmark"])
    if set(by_assessment) != set(capsules):
        raise ValueError("source Assessment-reference closure violated")

    entries = []
    compiled = {}
    global_status = Counter()
    per_stream = {stream:Counter() for stream in names}
    by_kind = Counter()
    for aid in sorted(capsules):
        capsule = capsules[aid]
        if capsule.get("id") != aid or capsule.get("migration_status") != "compatibility_execution_pending":
            raise ValueError("source capsule not a verified nonexecutable baseline: " + aid)
        state, reason, payload = _lower_assessment(capsule)
        streams = sorted(by_assessment[aid])
        global_status[state] += 1
        for stream in streams:
            per_stream[stream][state] += 1
            per_stream[stream]["referenced_assessments"] += 1
        source_mode = capsule["source_document"]["assessment"].get("mode")
        by_kind[str(source_mode)] += 1
        row = {
            "assessment_id": aid,
            "benchmark_streams": streams,
            "source_mode": source_mode,
            "source_path": capsule["source_path"],
            "source_raw_sha256": capsule["source_raw_sha256"],
            "source_parsed_sha256": capsule["source_parsed_sha256"],
            "conversion_status": state,
            "reason": reason,
            "source_parity_verified": False,
            "scanner_runtime_verified": False,
        }
        if payload is not None:
            path = _ir_filename(aid)
            if path in compiled:
                raise ValueError("compiled IR member collision")
            compiled[path] = payload
            row["research_fixture_ir_member"] = path
            row["research_fixture_ir_sha256"] = sha256(payload).hexdigest()
        entries.append(row)
    if len(entries) != corpus["summary"]["unique_referenced_assessments"]:
        raise ValueError("all source Assessments must be counted")
    if len(corpus["rules"]) != corpus["summary"]["rules"]:
        raise ValueError("all Rule selections must be accounted for")
    summary = {
        "benchmarks": len(names),
        "rules": len(corpus["rules"]),
        "assessment_choice_bindings": corpus["summary"]["assessment_choice_bindings"],
        "referenced_assessments": len(entries),
        "fixture_ir_compiled": len(compiled),
        "manual_procedure_ir_compiled": global_status.get("manual_procedure_ir_compiled",0),
        "automated_fixture_ir_compiled": global_status.get(READY_STATUS,0),
        "fully_executable_assessments": 0,
        "source_parity_verified_assessments": 0,
        "scanner_verified_assessments": 0,
        "status_counts": dict(sorted(global_status.items())),
        "mode_counts": dict(sorted(by_kind.items())),
    }
    report = {
        "format": FORMAT,
        "status": STATUS,
        "source_tag": corpus["source_tag"],
        "full_six_stream_conversion_complete": False,
        "scanner_package": False,
        "raw_scap_1_4_xml_imported": False,
        "original_oval_semantic_parity_verified": False,
        "summary": summary,
        "by_stream": {
            s:dict(sorted(per_stream[s].items()))
            for s in sorted(names)
        },
        "assessments": entries,
        "rule_choice_index": corpus["rules"],
    }
    return report,compiled


def render_markdown(report):
    summary = report["summary"]
    lines = [
        "# 0.4-B six-STIG executable conversion progress",
        "",
        "**Research only. THIS IS NOT a completed conversion or scanner package.**",
        "Source is the immutable published SCAP-NG 0.3 six-STIG authoring ZIP,",
        "not original SCAP 1.4 XML. A valid JSON fixture IR is not source parity.",
        "",
        "| Verified corpus dimension | Count |",
        "| --- | ---: |",
        f"| STIG streams | {summary['benchmarks']} |",
        f"| Rules | {summary['rules']} |",
        f"| Assessment-choice links | {summary['assessment_choice_bindings']} |",
        f"| Distinct referenced Assessments | {summary['referenced_assessments']} |",
        f"| Strictly lowered automated fixture IR (not scanner-verified) | {summary['automated_fixture_ir_compiled']} |",
        f"| Manual procedures compiled (human result still required) | {summary['manual_procedure_ir_compiled']} |",
        f"| **Verified executable source-equivalent Assessments** | **{summary['source_parity_verified_assessments']}** |",
        "",
        "## Per-stream conversion status",
        "",
        "| Stream | References | Automated fixture IR | Manual procedure IR | Remaining |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name, counts in sorted(report["by_stream"].items()):
        total = counts["referenced_assessments"]
        compiled = counts.get(READY_STATUS,0)
        manual = counts.get("manual_procedure_ir_compiled",0)
        lines.append(f"| {name} | {total} | {compiled} | {manual} | {total-compiled-manual} |")
    lines += ["", "## Classification", "",
              "| Status | Distinct Assessments |",
              "| --- | ---: |"]
    for status,count in sorted(summary["status_counts"].items()):
        lines.append(f"| {status} | {count} |")
    lines += ["",
              "Every referenced Assessment is in [the machine-readable conversion ledger](conversion-progress.json).",
              "The research ZIP contains **only** validated fixture IR, manual procedures and metadata; it is",
              "**not** a partial scanner content release. Unsupported content",
              "is never copied into executable IR or silently discarded. Manual procedures remain unevaluated until a human responds.",
              "",
              "Remaining release gates: complete original SCAP 1.4 import; implement",
              "OVAL Object/State/Variable/Set and source-specific collection behavior;",
              "six-state runtime/evidence; manual, org-input, applicability, results;",
              "full six-stream executable conversion and differential semantic proof.",
              "No A/B bake-off until those comparable-capability gates pass.",
              "",
              "Tracking: [#237](https://github.com/vanderpol/scap-ng/issues/237)",
              " and [#235](https://github.com/vanderpol/scap-ng/issues/235).",
              ""]
    return "\n".join(lines)


def _member(z, name, blob):
    info = zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info,blob)


def write_research_zip(path, report, compiled):
    """Deterministic research ZIP: deliberately NOT a signed .scapng package."""
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,"w") as z:
        _member(z,"RESEARCH-ONLY.txt",(
            "SCAP-NG B PARTIAL FIXTURE RESEARCH; NOT EXECUTABLE SIX-STIG CONTENT.\n"
            "Not a scanner package, not source-equivalent, not signed.\n").encode())
        _member(z,"conversion-progress.json",
                (json.dumps(report,sort_keys=True,ensure_ascii=False,
                            separators=(",",":"))+"\n").encode())
        for name,payload in sorted(compiled.items()):
            _member(z,name,payload)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path)
    p.add_argument("--research-zip",type=Path)
    p.add_argument("--require-six-ready",action="store_true",
                   help="fail closed unless all six streams are fully executable and source-verified")
    args=p.parse_args()
    source,raw_hashes=read_source(args.authoring_zip)
    corpus,capsules=import_corpus(source,raw_hashes,expected_benchmarks=6)
    report,compiled=build_six_stream_report(corpus,capsules)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,
                                      sort_keys=True,indent=2)+"\n")
    if args.markdown:
        args.markdown.parent.mkdir(parents=True,exist_ok=True)
        args.markdown.write_text(render_markdown(report))
    if args.research_zip:
        write_research_zip(args.research_zip,report,compiled)
    print(json.dumps(report["summary"],sort_keys=True,indent=2))
    if args.require_six_ready:
        if (not report["full_six_stream_conversion_complete"] or
            report["summary"]["source_parity_verified_assessments"]!=
                report["summary"]["referenced_assessments"]):
            raise SystemExit("BLOCKED: B six-STIG conversion not yet fully executable and source-equivalent")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
