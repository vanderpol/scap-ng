#!/usr/bin/env python3
"""Publish research JSON and readable summaries as files hosted on github.com.

Research issue #235. GitHub Actions artifacts remain supplemental.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess

BASE = "research/assessment-simplification/english-first-04/reports"
REPORTS = {
    "english-first-04-reference-graph-report.json": "Named source and variable reference graph",
    "english-first-04-compact-layout-report.json": "Compact authoring layout",
    "english-first-04-auditor-candidate.json": "Auditor-first requirement language candidate",
    "english-first-04-full-assessment-census.json": "Full Assessment source inversion",
    "english-first-04-six-state-cardinality.json": "Six-state cardinality comparison",
    "english-first-04-none-exist-state-boundary.json": "Unresolved none_exist State boundary",
    "english-first-04-variable-record-set-boundaries.json": "Variable, record and Set boundary guards",
    "english-first-04-six-stig-census.json": "Six-STIG Test census",
    "english-first-04-shape-census.json": "Assessment source-shape census",
    "english-first-04-state-free-presence.json": "State-free presence checks",
    "english-first-04-objectless.json": "Built-in Objectless collectors",
    "english-first-04-generic-scalar.json": "Typed common scalar checks",
}
EXAMPLES_DIR = "research/assessment-simplification/english-first-04/comparisons"
EXAMPLE_LABELS = {
    "linux-initialization": "RHEL9 initialization-file Set and foreach",
    "win11-role-rights": "Windows 11 domain-role and Remote Desktop rights",
    "dns-zone-signing": "Windows Server DNS zone-signing commands",
    "apache-keepalive": "Apache include-file and directive discovery",
}
# GitHub's online file viewer works best for smaller files.
MAX_JSON_BYTES = 700000


def git_api(repo, path, content, run):
    """Write to main with issue-linked commits via GitHub's Contents API."""
    old = subprocess.run(["gh", "api", f"repos/{repo}/contents/{path}",
                          "--jq", ".sha"], text=True, capture_output=True)
    if old.returncode not in (0, 1):
        raise RuntimeError("Unable to resolve existing GitHub path " + path)
    body = {
        "message": f"docs(#235): publish online six-STIG report from run {run}",
        "branch": "main",
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }
    if old.returncode == 0:
        body["sha"] = old.stdout.strip()
    result = subprocess.run(["gh", "api", "--method", "PUT",
                             f"repos/{repo}/contents/{path}", "--input", "-"],
                            input=json.dumps(body), text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("Cannot publish " + path + ": " + result.stderr[-600:])


def markdown(name, data, run, repo):
    lines = [
        "# " + name,
        "",
        "**Experimental research. Not an approved SCAP-NG syntax or scanner proof.**",
        "",
        f"Generated in GitHub Actions run {run}:",
        f"https://github.com/{repo}/actions/runs/{run}",
        "",
        "This page is a stable GitHub-hosted rendering of the result.",
        "Structural source inversion does not establish original OVAL runtime/evidence parity.",
        "",
    ]
    for key, value in data.items():
        if key in ("counts", "status", "source_sha256", "negative_acquisition_guards",
                   "source_char_reduction_percent", "source_chars_before",
                   "source_chars_after"):
            lines.extend(["## " + key.replace("_", " ").title(), "", ""])
            if isinstance(value, dict):
                lines.extend(["| Measure | Value |", "| --- | ---: |"])
                for k, v in sorted(value.items()):
                    if isinstance(v, (str, int, bool, float)) or v is None:
                        lines.append("| " + str(k) + " | " +
                                     str(v).replace("|", "\\|").replace("\n", " ") + " |")
            else:
                lines.append(str(value))
            lines.append("")
    for key in ("findings", "deepest_dependency_examples",
                "unsupported_examples", "rejected_examples", "exact_samples"):
        if isinstance(data.get(key), list):
            items = data[key]
            lines.extend(["## " + key.replace("_", " ").title() +
                          " (" + str(len(items)) + " entries)", ""])
            for entry in items[:20]:
                snippet = json.dumps(entry, ensure_ascii=False, sort_keys=True)
                if len(snippet) > 1100:
                    snippet = snippet[:1097] + "..."
                lines.append("- " + snippet.replace("\n", " "))
            if len(items) > 20:
                lines.append("- Additional findings are in the detailed JSON.")
            lines.append("")
    return "\n".join(lines) + "\n"


def publish():
    repo = os.environ["GITHUB_REPOSITORY"]
    run = os.environ["GITHUB_RUN_ID"]
    if repo != "vanderpol/scap-ng":
        raise RuntimeError("Unexpected repository")
    # Reject stale runs so they cannot overwrite reports from a newer commit.
    main = subprocess.run(["gh", "api", f"repos/{repo}/commits/main",
                           "--jq", ".sha"], capture_output=True, text=True, check=True)
    if main.stdout.strip() != os.environ["GITHUB_SHA"]:
        print("Stale run: skip repository publication")
        return
    rows = []
    for filename, title in REPORTS.items():
        path = Path(filename)
        if not path.is_file():
            raise FileNotFoundError(filename)
        raw = path.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        md_name = filename[:-5] + ".md"
        git_api(repo, BASE + "/" + md_name, markdown(title, parsed, run, repo), run)
        if len(raw.encode("utf-8")) <= MAX_JSON_BYTES:
            git_api(repo, BASE + "/" + filename, raw.rstrip() + "\n", run)
            json_link = "[Read JSON](" + filename + ")"
        else:
            json_link = "Over online size threshold; summary available"
        rows.append((title, md_name, json_link))
    # Publish the four COMPLETE, source-exact experimental Assessments directly
    # to github.com. A full-source round-trip is proved in the earlier CI step;
    # these are not a new normative 0.4 dialect or a runtime parity claim.
    for label in EXAMPLE_LABELS:
        source = Path("english-first-04-compact-layout-examples") / (label + ".research.yaml")
        if not source.is_file():
            raise FileNotFoundError("Missing generated full comparison: " + str(source))
        value = source.read_text(encoding="utf-8")
        if not value.startswith("# EXPERIMENT ONLY; reconstructs the pinned Assessment exactly."):
            raise ValueError("Unexpected generated sample format: " + str(source))
        git_api(repo, EXAMPLES_DIR + "/" + label + ".research.yaml", value, run)
    print("Published four full proposed versions on github.com")
    # Publish FIVE complete full source Assessments in the verified
    # auditor-first candidate. This is the same executable research grammar,
    # not a prose facade or a claimed scanner-conformance result.
    candidate_examples = Path("english-first-04-auditor-examples")
    candidate_folder = "research/assessment-simplification/english-first-04/auditor-candidate"
    for label in ("linux-home", "linux-files", "windows-wmi-rights", "dns", "apache"):
        source = candidate_examples / (label + ".auditor.research.yaml")
        if not source.is_file():
            raise FileNotFoundError("Missing auditor candidate " + str(source))
        candidate = source.read_text(encoding="utf-8")
        if not candidate.startswith("# Research-only candidate:"):
            raise ValueError("Incorrectly labeled auditor file " + label)
        git_api(repo, candidate_folder + "/" + label + ".auditor.research.yaml",
                candidate, run)
    print("Published five complete auditor-first candidate Assessments on github.com")



    index = [
        "# Six-STIG research reports (accessible through github.com)",
        "",
        "**Research only, not adopted SCAP-NG syntax or scanner validation.**",
        "",
        "Published from workflow run " + run + ":",
        "https://github.com/" + repo + "/actions/runs/" + run,
        "",
        "Read these pages directly in GitHub; no Actions artifact ZIP is needed.",
        "",
        "[Earlier verified checkpoint](2026-10-16-verified-checkpoint.md)",
        "(from run 38922336217; before the new reference-graph audit).",
        "",
        "| Report | Markdown report | Source JSON |",
        "| --- | --- | --- |",
    ]
    for title, md, json_link in rows:
        index.append("| " + title + " | [Read online](" + md + ") | " + json_link + " |")
    index.extend(["", "The pinned six-STIG source-inversion and six-state",
                  "reference checks are not independent OVAL scanner/evidence proof.",
                  "Unresolved edge cases must remain visible.", ""])
    git_api(repo, BASE + "/README.md", "\n".join(index), run)
    print("Published " + str(len(rows)) + " research reports via GitHub Contents API")


if __name__ == "__main__":
    argparse.ArgumentParser().parse_args()
    publish()
