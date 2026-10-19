#!/usr/bin/env python3
"""#245 Run the exact C focused test list locally; no git clone or CI queue.

Run from any path within a checked-out vanderpol/scap-ng repository:
    python tools/run_research_c_locally.py --quick
    python tools/run_research_c_locally.py --all
    python tools/run_research_c_locally.py --list

Only a test harness; not an OVAL oracle, scanner or proof of source parity.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

QUICK = (
    "tools/test_research_c_require_language.py",
    "tools/test_research_c_one_frontend.py",
    "tools/test_research_c_unified_compiler.py",
    "tools/test_research_c_objectless.py",
    "tools/test_research_c_unified_complex_windows.py",
    "tools/test_research_c_rhel_account_observations.py",
)
RUN_RE = re.compile(r"^\s*run: python -m unittest -v (tools/test_research_c_[^\r\n]+)\s*$", re.MULTILINE)


def selected_test_paths(repo: Path, mode: str) -> list[str]:
    workflow = (repo / ".github/workflows/research-c-shared-engine.yml").read_text(encoding="utf-8")
    matches = RUN_RE.findall(workflow)
    if len(matches) != 1:
        raise ValueError("expected exactly one pinned C unittest command in workflow")
    entries = matches[0].split()
    if len(entries) != len(set(entries)) or not entries:
        raise ValueError("duplicate or empty C test list")
    if any(not re.fullmatch(r"tools/test_research_c_[a-z0-9_]+\.py", t) for t in entries):
        raise ValueError("unexpected filename in workflow test command")
    selected = list(QUICK) if mode == "quick" else entries
    if mode == "quick" and not set(QUICK) <= set(entries):
        raise ValueError("quick tests differ from canonical CI command")
    for path in selected:
        if not (repo / path).is_file():
            raise ValueError(f"C test source missing: {path}")
    return selected


def main(argv=None):
    parser = argparse.ArgumentParser(description="C research tests using local checkout; no network")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="small compilation/compatibility gate")
    group.add_argument("--all", action="store_true", help="same test file list as CI")
    group.add_argument("--list", action="store_true", help="print the pinned CI test paths")
    args = parser.parse_args(argv)
    repo = Path(__file__).resolve().parents[1]
    selected = selected_test_paths(repo, "quick" if args.quick else "all")
    if args.list:
        print("\n".join(selected))
        return 0
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo,
                         capture_output=True, text=True, check=False)
    print(f"C local test checkout: {repo}; revision: {git.stdout.strip() or 'unavailable'}", flush=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo/"tools") + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.call([sys.executable,"-m","unittest","-v",*selected],cwd=repo,env=env)

if __name__=="__main__":
    sys.exit(main())
