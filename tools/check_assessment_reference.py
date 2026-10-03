#!/usr/bin/env python3
"""Check starter-reference links, native field coverage and exact source pins.

This is documentation consistency evidence, not a runtime/conformance oracle.
Git blobs are used for exact source-byte pins on LF and CRLF checkouts.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
from capability_registry import draft_capabilities, load_mapping

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "specification/assessment/reference"


def table_fields(text, heading):
    section = text.split("## " + heading + "\n", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"^\| `([^`]+)` \|", section, re.MULTILINE))


def main():
    errors = []
    ledger = json.loads((REFERENCE / "sources.json").read_text(encoding="utf-8"))
    for source in ledger["sources"]:
        # Pin files from the actual committed tree, independent of checkout EOLs.
        data = subprocess.check_output(
            ["git", "show", "HEAD:" + source["path"]], cwd=ROOT
        )
        if hashlib.sha256(data).hexdigest() != source["sha256"]:
            errors.append("Source changed; review documentation/pin: " + source["path"])
    documents = list(REFERENCE.glob("*.md"))
    for document in documents:
        text = document.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if ":" in link or link.startswith("#"):
                continue
            target = (document.parent / link.split("#", 1)[0]).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():
                errors.append(f"{document.name}: missing/unsafe reference {link}")
        for command in re.findall(r"^python (tools/[^\s]+\.py)", text, re.MULTILINE):
            if not (ROOT / command).is_file():
                errors.append(f"{document.name}: nonexistent documented command {command}")
    capabilities = ["unix.file", "variable.value", *sorted(draft_capabilities())]
    for capability in capabilities:
        mapping = load_mapping(capability)
        text = (REFERENCE / (capability + ".md")).read_text(encoding="utf-8")
        heading = "Comparable and collected fields" if capability == "unix.file" else "State and Item field reference"
        expected = set(mapping["native"]["state_field_map"].values())
        fields = table_fields(text, heading)
        if fields != expected:
            errors.append(f"{capability}: field table differs: {sorted(fields ^ expected)}")
    extensions = json.loads((ROOT / "schema/v0.2.0/result-field-extensions.json")
                            .read_text(encoding="utf-8"))["capabilities"]["unix.file"]
    text = (REFERENCE / "unix.file.md").read_text(encoding="utf-8")
    if table_fields(text, "Draft 0.2.0 result-only fields") != set(extensions):
        errors.append("unix.file: result-only field table differs")
    print(json.dumps({"documents": len(documents), "source_pins": len(ledger["sources"]),
                      "capability_references": len(capabilities), "errors": errors}, indent=2))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
