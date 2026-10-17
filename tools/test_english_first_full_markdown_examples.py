#!/usr/bin/env python3
"""Guard all five full Markdown before/after reviews against State-first regressions.

Ensures complete experimental YAML has the source selector before requirements
and fully reconstructs the original pinned 0.4 Assessment. No scanner parity
claim. Research issues #227, #235.
"""
import re
from pathlib import Path
import yaml
from research_english_first_04_complex import to_native
from research_english_first_04_compact_layout import (
    expand, require_acquisition_before_criteria
)

ROOT = Path("research/assessment-simplification/english-first-04")
PAGES = (
    "FULL-01-linux-home.md",
    "FULL-02-linux-files.md",
    "FULL-03-win11-rights.md",
    "FULL-04-dns.md",
    "FULL-05-apache.md",
)

def yaml_under_heading(md, heading):
    start = md.find("## " + heading)
    if start == -1:
        raise AssertionError("Missing " + heading)
    other = md.find("\n## ", start + 3)
    section = md[start:other] if other >= 0 else md[start:]
    fence = chr(96) * 3
    pattern = "(?m)^" + fence + "yaml" + chr(10) + "(.*?)" + chr(10) + fence
    match = re.search(pattern, section, re.DOTALL)
    if match is None:
        raise AssertionError("No complete YAML in " + heading)
    return yaml.safe_load(match.group(1))

def test_page(name):
    content = (ROOT / name).read_text(encoding="utf-8")
    before_head = next((line[3:] for line in content.splitlines()
                        if line.startswith("## Before")), None)
    after_head = next((line[3:] for line in content.splitlines()
                       if line.startswith("## After")), None)
    if not before_head or not after_head:
        raise AssertionError(name + ": missing section headings")
    source = yaml_under_heading(content, before_head)["assessment"]
    candidate = yaml_under_heading(content, after_head)
    if set(candidate) != {"metadata", "sources", "checks", "evaluate"}:
        raise AssertionError(name + ": incomplete research Assessment")
    if not candidate["checks"]:
        raise AssertionError(name + ": empty checks")
    for test_id, check in candidate["checks"].items():
        try:
            require_acquisition_before_criteria(check)
        except AssertionError as error:
            raise AssertionError(f"{name}: {test_id}: {error}") from error
    reconstructed = to_native(expand(candidate))
    if reconstructed != source:
        raise AssertionError(name + ": After YAML does not reverse to exact Before YAML")
    return len(candidate["checks"])

if __name__ == "__main__":
    total = 0
    for page in PAGES:
        count = test_page(page)
        total += count
        print(f"PASS: {page}: {count} named Tests; Object before State; exact source")
    print(f"PASS: {len(PAGES)} full before/after reviews, {total} Tests")
