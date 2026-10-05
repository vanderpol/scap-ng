#!/usr/bin/env python3
"""Inventory a pinned Git tree and verify the current/archive boundary.

Static imports and literal workflow paths are evidence of use, not a proof that
an unreferenced file is dispensable. Never deletes or moves repository content.
"""
import argparse
import ast
from collections import Counter
import csv
import gzip
import io
import json
from pathlib import Path
import re
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def tracked_tree(ref):
    rows = {}
    for line in git("ls-tree", "-rz", "--full-tree", ref).split(b"\0"):
        if not line:
            continue
        meta, path = line.split(b"\t", 1)
        mode, kind, blob = meta.decode().split()
        rows[path.decode()] = {"mode": mode, "type": kind, "git_blob": blob}
    return rows


def workflow_role(name, policy):
    for key, role in (("historical_manual_workflows", "historical-reproduction"),
                      ("held_workflows", "historical-held"),
                      ("publication_workflows", "board-publication"),
                      ("legacy_regression_workflows", "legacy-semantic-regression"),
                      ("current_workflows", "current-ci")):
        if name in policy[key]:
            return role
    return "needs-review"


def import_graph():
    modules = {str(p.relative_to(ROOT / "tools")).removesuffix(".py").replace("/", "."): str(p.relative_to(ROOT))
               for p in (ROOT / "tools").rglob("*.py")}
    edges = {p: set() for p in modules.values()}
    for module, path in modules.items():
        tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = node.module or ""
                if node.level:
                    prefix = ".".join(module.split(".")[:-node.level] + ([node.module] if node.module else []))
                names = [prefix] + [prefix + "." + a.name for a in node.names]
            for name in names:
                if name in modules:
                    edges[path].add(modules[name])
    return edges


def dependencies(policy):
    graph = import_graph()
    roots = set(policy["current_entrypoints"])
    workflows = []
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        doc = yaml.safe_load(path.read_text())
        role = workflow_role(path.name, policy)
        scripts = set()
        for match in re.findall(r"(?:scap-ng/)?(?:research/iterations/00[123]/)?tools/[\w/.-]+\.py", path.read_text()):
            candidate = match.removeprefix("scap-ng/")
            if (ROOT / candidate).is_file():
                scripts.add(candidate)
        workflows.append({"path": str(path.relative_to(ROOT)), "name": doc["name"], "role": role,
                          "direct_script_paths": sorted(scripts),
                          "triggers": sorted(str(k) for k in doc.get("on", doc.get(True, {}))),
                          "job_conditions": {k: v.get("if") for k, v in doc["jobs"].items()}})
        if role == "current-ci":
            roots.update(scripts)
    seen = set()
    todo = list(roots)
    while todo:
        path = todo.pop()
        if path in seen:
            continue
        seen.add(path)
        todo.extend(graph.get(path, set()))
    return {"scope": "Static Python imports and existing literal workflow script paths; dynamic calls, external execution and data paths require explicit review.",
            "current_roots": sorted(roots), "current_import_closure": sorted(seen),
            "imports": {p: sorted(v) for p, v in sorted(graph.items())}, "workflows": workflows}


def classify(path, policy, closure):
    if path in policy["historical_input_exceptions"]:
        return "current-support-at-historical-path", policy["historical_input_exceptions"][path]
    if path.startswith(".github/workflows/"):
        return workflow_role(Path(path).name, policy), "Explicit workflow policy"
    if path in closure:
        return "current-tool-or-regression", "Current entry point, CI script, or static import dependency"
    if path.startswith("tools/") and path.endswith("README.md"):
        return "research-navigation", "Tool navigation"
    if path.startswith("tools/"):
        if Path(path).name in policy["historical_root_tools"] or path in policy["historical_v003_tools"]:
            return "historical-tool", "Superseded renderer/runner; preserve for reproduction"
        return "support-tool-review", "Retained helper, test, or experiment; no static-current-use claim"
    if path.startswith(("research/datastream/", "research/vulnerability/")):
        return "research-topic-evidence", "Exploratory topic; retained for review, not current implementation proof"
    if path == "research/README.md" or (path.startswith("tools/") and path.endswith("README.md")):
        return "research-navigation", "Navigation; current/archive directions require review"
    if path.startswith("research/iterations/001/") or path.startswith("research/iterations/002/"):
        parts = path.split("/")
        if parts[3] in {"generated", "demonstrations", "prototypes", "showcases"} or (parts[2] == "002" and parts[3] == "examples"):
            return "historical-artifact", "Archived iteration output/fixture; not current authoring guidance"
        if parts[3] == "tools":
            return "historical-tool", "Iteration-local experiment (exceptions classified first)"
        return "historical-decision-evidence", "Retained reasoning, lessons, questions or source records; reconcile before reuse"
    if path.startswith("research/iterations/003/"):
        area = path.split("/")[3]
        if area in {"source", "packages"}:
            return "historical-artifact", "Superseded v003 generation snapshot; current review lives under review/"
        if area == "design":
            return "current-design-record", "Working design; older paragraphs require current-design precedence"
        if area == "board-review":
            return "board-question-evidence", "Unratified discussion; consult reconciled Board index"
        if area == "evidence":
            return "dated-validation-evidence", "Evidence only for its pinned inputs/commit"
        if area == "review":
            if "/rhel9-current-full/" in path or "/windows11-current-full/" in path or "/full-current-native-normalized/" in path:
                return "current-generated-review", "Source/design review candidate; not finalized grammar or runtime conformance"
            return "prior-review-evidence", "Earlier focused slice; do not infer latest-grammar compliance"
        if area in {"examples", "results"}:
            return "working-example-review", "Focused experiment; validate individual syntax/status before reuse"
        return "research-navigation", "Navigation or tooling notes"
    if path.startswith("specification/"):
        return "current-draft-specification", "Pre-alpha draft; Board ratification and current-decision conflicts remain explicit"
    if path.startswith("schema/"):
        return "current-schema-or-mapping", "Pre-alpha structural schemas and reviewed mapping inputs"
    if path.startswith("third_party/"):
        return "pinned-third-party", "Upstream validation inputs; retain licenses/hashes/provenance"
    if path.startswith("board/"):
        return "board-governance", "Discussion or test proposal; no official vote implied"
    if path.startswith("transition/"):
        return "continuity-record", "Handoff evidence and retrieval limits"
    if path.startswith(("docs/", "archive/")) or path in {"AGENTS.md", "README.md", "ROADMAP.md", "START-HERE.md"}:
        return "navigation-and-governance", "Repository navigation/instructions/audit"
    return "needs-review", "No deletion inference permitted"


def check(policy):
    failures = []
    for name in policy["historical_manual_workflows"]:
        doc = yaml.safe_load((ROOT / ".github/workflows" / name).read_text())
        events = doc.get("on", doc.get(True, {}))
        if set(events) != {"workflow_dispatch"}:
            failures.append(name + ": historical workflow has automatic triggers")
        if events.get("workflow_dispatch", {}).get("inputs", {}).get("allow_historical", {}).get("default") is not False:
            failures.append(name + ": explicit opt-in must default false")
        for job, config in doc["jobs"].items():
            if "inputs.allow_historical" not in str(config.get("if", "")):
                failures.append(name + ": ungated historical job " + job)
    for path in policy["current_entrypoints"] + [policy["current_design"]]:
        if not (ROOT / path).is_file():
            failures.append("Missing current path: " + path)
    for name in policy["held_workflows"]:
        doc = yaml.safe_load((ROOT / ".github/workflows" / name).read_text())
        if any(str(v.get("if", "")).strip() != "${{ false }}" for v in doc["jobs"].values()):
            failures.append(name + ": held workflow was reenabled")
    for path in dependencies(policy)["current_import_closure"]:
        if path.startswith(("research/iterations/001/", "research/iterations/002/")):
            failures.append("Current CI executes archived iteration code: " + path)
    baseline = tracked_tree(policy["baseline_commit"])

    removed_roots = policy.get("removed_trees", {})
    allowed_missing = set()

    for path, record in policy.get("removed_files", {}).items():
        if path not in baseline:
            failures.append("Removed historical file not present in baseline: " + path)
            continue
        if not record.get("recovery_tag"):
            failures.append("Removed historical file missing recovery tag: " + path)
        if not record.get("deletion_commit"):
            failures.append("Removed historical file missing deletion commit: " + path)
        allowed_missing.add(path)
    for root, record in removed_roots.items():
        expected = {p for p in baseline if p == root or p.startswith(root + "/")}
        if not expected:
            failures.append("Removed historical tree not present in baseline: " + root)
            continue
        actual_tree = git("rev-parse", f'{policy["baseline_commit"]}:{root}').decode().strip()
        if actual_tree != record.get("tree_sha"):
            failures.append(
                f"Removed historical tree SHA mismatch for {root}: "
                f"policy={record.get('tree_sha')} baseline={actual_tree}"
            )
        if not record.get("recovery_tag"):
            failures.append("Removed historical tree missing recovery tag: " + root)
        allowed_missing.update(expected)

    missing = [p for p in baseline if not (ROOT / p).exists() and p not in allowed_missing]
    failures.extend("Lost unaccounted baseline path: " + p for p in missing)

    historical = [
        p for p in baseline
        if p.startswith(("research/iterations/001/", "research/iterations/002/"))
        and (ROOT / p).exists()
    ]
    if historical:
        process = subprocess.run(
            ["git", "hash-object", "--stdin-paths"],
            input="\n".join(historical) + "\n",
            text=True,
            capture_output=True,
            check=True,
            cwd=ROOT,
        )
        for p, actual in zip(historical, process.stdout.splitlines()):
            if actual != baseline[p]["git_blob"]:
                failures.append("Historical payload changed: " + p)

    for path in policy.get("current_data_inputs", []):
        if not (ROOT / path).is_file():
            failures.append("Missing promoted current data input: " + path)
    return failures


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--output", type=Path, default=ROOT / "docs/audit")
    args = ap.parse_args()
    policy = json.loads((ROOT / "docs/repository-policy.json").read_text())
    failures = check(policy)
    if args.check:
        print(json.dumps({"baseline_paths": len(tracked_tree(policy["baseline_commit"])), "failures": failures}, indent=2))
        return bool(failures)
    deps = dependencies(policy)
    tree = tracked_tree(policy["baseline_commit"])
    counts = Counter()
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter="\t", lineterminator="\n")
    writer.writerow(["path", "git_blob", "mode", "role", "basis"])
    for path, meta in sorted(tree.items()):
        role, basis = classify(path, policy, deps["current_import_closure"])
        counts[role] += 1
        writer.writerow([path, meta["git_blob"], meta["mode"], role, basis])
    args.output.mkdir(parents=True, exist_ok=True)
    raw = buf.getvalue().encode()
    (args.output / "repository-inventory.tsv.gz").write_bytes(gzip.compress(raw, mtime=0))
    (args.output / "dependencies.json").write_text(json.dumps(deps, indent=2) + "\n")
    summary = {"baseline_commit": policy["baseline_commit"], "tracked_files": len(tree), "roles": dict(sorted(counts.items())),
               "scope": "Every tracked path classified; generated files classified by provenance/location, not individually accepted as correct. Static dependency discovery is conservative and does not prove disuse.",
               "preservation_check_failures": failures}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
