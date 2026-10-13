#!/usr/bin/env python3
"""Issue #214: validate six-STIG grouped shared paths and stage a separate review ZIP.

Reuses a pinned, green representative conversion's source artifacts. It does
not modify source, existing releases, the root README, or scanner semantics.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import yaml


KEYS = {
    "rhel_9", "oracle_linux_9", "ms_windows_11",
    "ms_windows_server_2025", "apache_server_2-4_unix_server",
    "ms_windows_server_dns",
}


def run(*args: str) -> None:
    print("RUN", " ".join(map(str, args)), flush=True)
    subprocess.run([sys.executable, *map(str, args)], check=True)


def yaml_document(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def inspect(root: Path) -> tuple[dict, dict]:
    payloads = defaultdict(list)
    for path in sorted(root.rglob("*.assessment.yaml")):
        doc = yaml_document(path)
        assessment = doc.get("assessment")
        if not isinstance(assessment, dict):
            continue
        encoded = json.dumps(assessment, sort_keys=True, separators=(",", ":"))
        payloads[assessment["id"]].append(hashlib.sha256(encoded.encode()).hexdigest())
    bindings = {}
    for path in sorted(root.rglob("*.rule.yaml")):
        rule = yaml_document(path)["rule"]
        for selector, choice in (rule.get("assessment_choices") or {}).items():
            target = (path.parent / choice["assessment"]).resolve()
            if not target.is_file():
                raise ValueError(f"Unresolved Rule binding: {path} -> {choice['assessment']}")
            bindings[(path.relative_to(root).as_posix(), selector)] = (
                yaml_document(target)["assessment"]["id"]
            )
    for path in sorted(root.rglob("applicability.yaml")):
        doc = yaml_document(path)["applicability"]
        conditions = doc.get("conditions") or {}
        entries = conditions.items() if isinstance(conditions, dict) else enumerate(conditions)
        for key, choice in entries:
            if not isinstance(choice, dict) or not isinstance(choice.get("assessment"), str):
                continue
            target = (path.parent / choice["assessment"]).resolve()
            if not target.is_file():
                raise ValueError(f"Unresolved applicability binding: {path} -> {choice['assessment']}")
            bindings[(path.relative_to(root).as_posix(), str(key))] = (
                yaml_document(target)["assessment"]["id"]
            )
    return {k: sorted(v) for k, v in payloads.items()}, bindings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--downloads", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--source-run-id", required=True)
    parser.add_argument("--niwc-revision", required=True)
    parser.add_argument("--scap-ng-revision", required=True)
    args = parser.parse_args()
    work = args.work
    raw = work / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    statuses = []
    for path in sorted(args.downloads.rglob("status/result.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        statuses.append(row)
        if row.get("status") != "generated":
            raise ValueError(f"Source conversion not green: {row}")
        source = path.parent.parent / "generated" / row["key"]
        shutil.copytree(source, raw / row["key"])
    if {x["key"] for x in statuses} != KEYS or len(statuses) != 6:
        raise ValueError(f"Need six distinct successfully converted STIGs; got {statuses}")

    source = work / "candidate"
    for benchmark in sorted(raw.iterdir()):
        run(
            "tools/render_0_3_human_review_candidate.py", str(benchmark),
            "--output-root", str(source / benchmark.name),
            "--evidence-dir", str(work / "render-evidence" / benchmark.name),
            "--label", benchmark.name,
        )
    run("tools/validate_native_json_schemas.py", str(source),
        "--schema-dir", "schema/v0.3.0", "--report", str(work / "source-schema.json"))

    for layout in ("flat", "os-subject"):
        label = "grouped" if layout == "os-subject" else "flat"
        run(
            "tools/scap_ng_repo_normalizer.py", str(source),
            "--rewrite", "--output-root", str(work / label),
            "--report", str(work / (label + "-normalizer.json")),
            "--advisory", "none", "--shared-layout", layout,
        )
    flat = json.loads((work / "flat-normalizer.json").read_text())
    grouped = json.loads((work / "grouped-normalizer.json").read_text())
    if flat["summary"] != grouped["summary"]:
        raise ValueError("Normalizer counts differ between layouts")
    def fingerprints(report):
        return {
            x["fingerprint"]: sorted(y["source"] for y in x["members"])
            for x in report["exact_groups"]
        }
    if not fingerprints(flat) or fingerprints(flat) != fingerprints(grouped):
        raise ValueError("Exact semantic Assessment sharing differs")
    flat_payloads, flat_bindings = inspect(work / "flat")
    grouped_payloads, grouped_bindings = inspect(work / "grouped")
    if flat_payloads != grouped_payloads:
        raise ValueError("Logical Assessment IDs or content changed")
    if flat_bindings != grouped_bindings:
        raise ValueError("Rule or applicability bindings changed logical targets")

    old_shared = list((work / "flat" / "shared" / "assessments").rglob("*.assessment.yaml"))
    new_shared = list((work / "grouped" / "shared" / "assessments").rglob("*.assessment.yaml"))
    if not old_shared or len(old_shared) != len(new_shared):
        raise ValueError("Number of shared Assessments differs")
    categories = Counter(
        str(p.relative_to(work / "grouped" / "shared" / "assessments").parent)
        for p in new_shared
    )
    if any("/" not in folder for folder in categories):
        raise ValueError("OS-family/subject grouping absent")
    for target, prefix in ((work / "flat", "flat"), (work / "grouped", "grouped")):
        run("tools/validate_native_json_schemas.py", str(target),
            "--schema-dir", "schema/v0.3.0", "--report", str(work / (prefix + "-schema.json")))
        run("tools/validate_native_semantics.py", str(target),
            "--report", str(work / (prefix + "-semantics.json")))
        run("tools/validate_native_package_graph.py", str(target),
            "--report", str(work / (prefix + "-graph.json")))

    run("tools/scap_ng_content_compiler.py", str(work / "grouped"),
        "--output-dir", str(work / "packages"),
        "--metrics", str(work / "compiler.json"),
        "--source-revision", args.niwc_revision,
        "--scap-ng-revision", args.scap_ng_revision)
    from scap_ng_content_compiler import verify_bundle
    packages = sorted((work / "packages").glob("*.scapng"))
    if len(packages) != 6:
        raise ValueError(f"Expected six compiled bundles, got {len(packages)}")
    verified = [verify_bundle(p) for p in packages]
    comparison = {
        "source_conversion_run": args.source_run_id,
        "scap_ng_revision": args.scap_ng_revision,
        "niwc_revision": args.niwc_revision,
        "benchmarks": 6,
        "shared_assessments": len(new_shared),
        "exact_semantic_groups_unchanged": True,
        "assessment_payloads_and_logical_ids_identical": True,
        "rule_and_applicability_logical_bindings_identical": True,
        "flat_mean_basename": round(sum(len(p.name) for p in old_shared) / len(old_shared), 2),
        "grouped_mean_basename": round(sum(len(p.name) for p in new_shared) / len(new_shared), 2),
        "flat_max_basename": max(len(p.name) for p in old_shared),
        "grouped_max_basename": max(len(p.name) for p in new_shared),
        "os_family_subject_counts": dict(sorted(categories.items())),
        "normalizer_summary": grouped["summary"],
        "verified_compiled_bundles": verified,
    }
    print(json.dumps(comparison, indent=2, sort_keys=True))
    review = work / "review"
    shutil.copytree(work / "grouped", review / "authoring")
    (review / "LAYOUT-COMPARISON.json").write_text(
        json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    (review / "README.md").write_text(
        "# SCAP-NG 0.3 shared Assessment layout preview\n\n"
        "Issue #214 implementation review, not a new normative source-layout requirement.\n\n"
        "The authoring directory contains six converted STIGs after exact semantic "
        "normalization, organized by OS family and subject. The comparison JSON "
        "confirms identical Assessment logical IDs and content and matching Rule "
        "and applicability bindings. Six resulting packages passed compiler/"
        "manifest validation. This source preview does not replace or update "
        "the existing 0.3.0 release ZIPs.\n", encoding="utf-8",
    )
    output = work / "scap-ng-0.3-shared-layout-preview.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(x for x in review.rglob("*") if x.is_file()):
            info = zipfile.ZipInfo(
                (Path("shared-layout-preview") / path.relative_to(review)).as_posix(),
                date_time=(1980, 1, 1, 0, 0, 0),
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 & 0xffff) << 16
            zf.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    (work / "SHA256SUMS.txt").write_text(
        f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output.name}\n",
        encoding="utf-8",
    )
    shutil.copy2(review / "LAYOUT-COMPARISON.json", work / "LAYOUT-COMPARISON.json")
    print("LAYOUT_PREVIEW_VALIDATED", output, flush=True)


if __name__ == "__main__":
    main()
