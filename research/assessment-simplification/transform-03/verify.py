#!/usr/bin/env python3
"""Reproduce this bounded experiment and retain actual commands/results."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from compile_requirements import ROOT, compile_author, load_author
import yaml

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
OUTPUT = HERE / "compiled"


def main():
    EVIDENCE.mkdir(exist_ok=True)
    OUTPUT.mkdir(exist_ok=True)
    author_path = HERE / "examples/initialization-files.author.yaml"
    native, source_map = compile_author(load_author(author_path))
    native_path = OUTPUT / "initialization-files.assessment.yaml"
    native_path.write_text("# EXPERIMENTAL compiled authoring; unchanged native target.\n" +
                           yaml.safe_dump(native, sort_keys=False))
    (EVIDENCE / "source-map.json").write_text(json.dumps(source_map, indent=2) + "\n")
    commands = [
        ("transform-tests", ["-m", "unittest", "discover", "-s", str(HERE.relative_to(ROOT)), "-p", "test_transform.py", "-v"]),
        ("native-schema", ["tools/validate_native_json_schemas.py", str(OUTPUT.relative_to(ROOT)), "--schema-dir", "schema/v0.1.0"]),
        ("authoring-contract", ["tools/check_current_authoring_contract.py", str(OUTPUT.relative_to(ROOT))]),
        ("diagnostic-demo", [str((HERE / "demo.py").relative_to(ROOT))]),
        ("six-state-regressions", ["-m", "unittest", "discover", "-s", "tools", "-p", "test_oval_result_truth_tables*.py", "-v"]),
    ]
    checks = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for label, args in commands:
        command = [sys.executable, *args]
        run = subprocess.run(command, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (EVIDENCE / f"{label}.txt").write_text(run.stdout)
        checks.append({"label": label, "command": command, "exit_code": run.returncode, "log": f"{label}.txt"})
        print(f"{label}: exit {run.returncode}")
    paths = [author_path, native_path,
             HERE.parent / "evidence/rhel_9/SV-257889/source-oval.xml",
             ROOT / "schema/v0.1.0/assessment.schema.json",
             ROOT / "schema/v0.1.0/capability-common.schema.json",
             ROOT / "schema/v0.1.0/capability-mappings/unix.file.json",
             ROOT / "tools/generate_capability_schema.py",
             ROOT / "tools/oval_result_truth_tables.py"]
    nodes = native["assessment"]
    report = {
        "status": "bounded_lowering_passed_not_scanner_equivalence" if all(c["exit_code"] == 0 for c in checks) else "failed",
        "receiving_commit": "acdfa66b77d531a37e8fd36ad199c94883d3a7a5", "branch": "main", "checks": checks,
        "semantic_cases": {"source_permission_modes": 4096, "nontrivial_allowances": 4095,
                           "mode_checks_per_allowance": 4, "eight_comparison_outcomes": 65536,
                           "two_comparison_six_state_combinations": 36},
        "size": {"author_lines_including_comments": len(author_path.read_text().splitlines()),
                 "compiled_lines_including_comments": len(native_path.read_text().splitlines()),
                 "objects": len(nodes["objects"]), "states": len(nodes["states"]), "tests": len(nodes["tests"])},
        "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "limits": ["No target scan, account discovery, native traversal or new collector execution.",
                   "Permission predicate compared with pinned source XML; complete source scope not compiled.",
                   "Test status control flow reuses pinned repository helpers, not an independent scanner oracle.",
                   "Deep capability schemas generated from reviewed mapping and validated inside transform tests.",
                   "No fresh upstream Self-Assertion corpus or author usability trial."]}
    (EVIDENCE / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if all(c["exit_code"] == 0 for c in checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
