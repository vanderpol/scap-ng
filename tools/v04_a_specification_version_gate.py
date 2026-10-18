#!/usr/bin/env python3
"""#232/#239: inspect explicit 0.4-A assessment specification compatibility.

NO source rewriting, inferred migration, schema approval or runnable bundle.
This gate deliberately distinguishes 'static declarations line up' from
'conversion is actually proved'. A non-empty mismatch BLOCKS native bundling.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json

from v04_a_authoring_graph_index import read_authoring_archive

SPEC = "scap-ng.pre-alpha.assessment"


def _identity(value, where):
    if not isinstance(value, dict):
        raise ValueError(f"{where}: specification must be a mapping")
    if not isinstance(value.get("id"), str) or not value["id"]:
        raise ValueError(f"{where}: missing specification id")
    if not isinstance(value.get("version"), str) or not value["version"]:
        raise ValueError(f"{where}: missing specification version")
    if set(value) != {"id", "version"}:
        raise ValueError(f"{where}: ambiguous specification fields {sorted(value)}")
    return (value["id"], value["version"])


def inspect(documents):
    benchmarks, assessment_versions, manual_assessments, errors = {}, Counter(), 0, []
    for path, doc in sorted(documents.items()):
        if not isinstance(doc, dict) or len(doc) != 1:
            raise ValueError(f"{path}: expected exactly one root")
        kind, payload = next(iter(doc.items()))
        if not isinstance(payload, dict):
            raise ValueError(f"{path}: invalid root value")
        if kind == "benchmark":
            ident = payload.get("id")
            if not isinstance(ident, str) or not ident:
                raise ValueError(f"{path}: missing Benchmark id")
            declared = payload.get("assessment_specifications")
            if not isinstance(declared, list) or not declared:
                raise ValueError(f"{path}: missing explicit assessment_specifications list")
            keys = [_identity(x, path + ".assessment_specifications")
                    for x in declared]
            if len(set(keys)) != len(keys):
                raise ValueError(f"{path}: duplicate Benchmark specification declaration")
            if ident in benchmarks:
                raise ValueError(f"{path}: duplicate Benchmark id")
            benchmarks[ident] = sorted(keys)
        elif kind == "assessment":
            mode = payload.get("mode")
            if mode == "manual":
                manual_assessments += 1
                continue
            if mode != "automated":
                # Applicability Assessments must be explicit too, but do not
                # silently classify unknown modes as executable.
                errors.append({"path": path, "reason": "unknown_assessment_mode"})
                continue
            spec = payload.get("specification")
            if spec is None:
                errors.append({"path": path, "reason": "missing_automated_specification"})
                continue
            assessment_versions[_identity(spec, path + ".specification")] += 1
    if not benchmarks:
        raise ValueError("no Benchmarks to establish a declared Assessment specification contract")
    declared_set = set().union(*(set(x) for x in benchmarks.values()))
    mismatches = [
        {"specification": {"id": sid, "version": version}, "automated_assessments": count}
        for (sid, version), count in sorted(assessment_versions.items())
        if (sid, version) not in declared_set
    ]
    # A global *union* of declared versions is a necessary condition, not
    # sufficient for every Benchmark->Rule->Assessment edge, provenance or
    # 0.4 conversion correctness. Never label this gate "compiled".
    status = "BLOCKED_UNDECLARED_SPECIFICATION" if mismatches or errors else "DECLARATIONS_CONSISTENT_NOT_COMPILED"
    return {
        "status": status,
        "proof_stage": "global_declaration_necessary_condition_only",
        "benchmarks": [{"id": k, "declared_specs": [{"id": sid, "version": version}
                              for sid, version in benchmarks[k]]} for k in sorted(benchmarks)],
        "observed_automated_specs": [
            {"id": sid, "version": version, "assessments": count}
            for (sid, version), count in sorted(assessment_versions.items())
        ],
        "contextual_manual_assessments": manual_assessments,
        "unmatched_automated_specs": mismatches,
        "errors": errors[:20],
        "error_count": len(errors),
        "allowed_to_compile": False,  # Semantic, per-edge and schema gates still unproved.
        "limitations": [
            "a matching global declaration is necessary, not sufficient, for per-Rule compatibility",
            "does not verify Benchmark->Rule context, 0.4 schema semantics, or source provenance",
            "does not rewrite 0.3 to 0.4 or invent an importer waiver",
            "does not produce, sign or scan a .scapng bundle",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-archive", required=True)
    parser.add_argument("--yaml-archive")
    parser.add_argument("--report-json")
    parser.add_argument("--expect-blocked", action="store_true",
                        help="Research regression only; require a mismatch without considering it a build pass")
    args = parser.parse_args(argv)
    report = inspect(read_authoring_archive(args.json_archive, "json"))
    if args.yaml_archive:
        alternate = inspect(read_authoring_archive(args.yaml_archive, "yaml"))
        if alternate != report:
            raise ValueError("YAML and JSON version contract reports differ")
        report["yaml_json_agree"] = True
    result = json.dumps(report, sort_keys=True, indent=2) + "\n"
    print(result, end="")
    if args.report_json:
        from pathlib import Path
        Path(args.report_json).write_text(result, encoding="utf-8")
    is_blocked = report["status"].startswith("BLOCKED")
    if args.expect_blocked:
        return 0 if is_blocked else 2
    return 2 if is_blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
