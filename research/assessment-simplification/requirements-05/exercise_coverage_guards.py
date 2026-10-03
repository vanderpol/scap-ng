#!/usr/bin/env python3
"""Negative controls for coverage evidence, not assessment semantic tests."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import verify_coverage as coverage

HERE = Path(__file__).resolve().parent


def exercise(source_root):
    results = []
    for case in ("omit_rule", "trim_check_text", "change_reference", "change_selector",
                 "change_text_hash", "reading_gap"):
        with tempfile.TemporaryDirectory(prefix="scap-requirements-controls-") as scratch:
            target = Path(scratch)
            shutil.copytree(HERE / "evidence", target / "evidence")
            shutil.copy(HERE / "READING-NOTES.md", target / "READING-NOTES.md")
            path = target / "evidence/rhel_9.json"
            payload = json.loads(path.read_text())
            if case == "omit_rule":
                payload["rules"].pop()
                payload["rule_count"] -= 1
            elif case == "trim_check_text":
                rule = next(r for r in payload["rules"] if r["id"] == "SV-257879")
                check = next(c for c in rule["checks"] if c["content"])
                check["content"][0] = check["content"][0].split("\n\n")[0]
            elif case == "change_reference":
                check = next(c for r in payload["rules"] for c in r["checks"] if c["references"])
                check["references"][0]["name"] = "incorrect-source-definition"
            elif case == "change_selector":
                payload["rules"][0]["checks"][0]["selector"] = "incorrect-selector"
            elif case == "change_text_hash":
                payload["rules"][0]["check_text_sha256"][0] = "0" * 64
            elif case == "reading_gap":
                notes = target / "READING-NOTES.md"
                notes.write_text(notes.read_text().replace("## RHEL 9, 1–50", "## RHEL 9, 2–50"))
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
            # Refresh the extraction hash deliberately: the original-source and
            # reading comparisons, not just a stale file digest, must detect loss.
            manifest_path = target / "evidence/extraction.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["families"]["rhel_9"]["extracted_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            coverage.HERE = target
            try:
                coverage.verify(source_root)
            except ValueError as exc:
                results.append({"case": case, "detected": True, "diagnostic": str(exc)})
            else:
                raise RuntimeError(f"negative control was not detected: {case}")
            finally:
                coverage.HERE = HERE
    report = {"negative_controls": results, "passed": len(results),
              "scope": "Evidence coverage guard sensitivity only; not evaluator/scanner semantics."}
    (HERE / "evidence/coverage-controls.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(exercise(args.source_root), indent=2))
