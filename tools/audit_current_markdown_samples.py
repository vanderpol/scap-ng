#!/usr/bin/env python3
"""Reject stale sample recommendations and require the current 0.4 download index.

Historical 0.3 schemas, synthetic results, research, issue records and archive
files are intentionally not rewritten. This checks the current reader-facing
entry points, not semantic acceptance or scanner execution.
"""
from pathlib import Path
import re
import sys

CURRENT = (
    "README.md", "ROADMAP.md", "specification/README.md",
    "specification/examples/README.md", "specification/examples/assessments.md",
    "review/current/README.md", "review/current/REVIEW-GUIDE.md",
    "review/current/examples/rhel9-full.md",
    "review/current/examples/windows11-full.md",
    "schema/README.md", "schema/v0.4.0/README.md",
    "docs/public-authoring/README.md",
    "docs/public-authoring/VERSION-AND-SOURCES.md",
)
CURRENT_INDEX = "0.4.0-downloads-and-samples.md"
REQUIRED_INDEX_MARKERS = (
    "v04-normalized-library-review-20261030-ff69d46b3",
    "v04-revised-all65-draft-files-20261030-a08c9beb9",
    "v04-toolchain-rc-20261030-a5db02e1b",
    "0.4.0-six-stig-authoring.md",
    "UNVERIFIED",
)
STALE = (
    re.compile(r"https://github\.com/vanderpol/scap-ng/releases/(?:tag|download)/v0\.3\.0-",re.I),
    re.compile(r"0\.3(?:\.0)?\s+(?:is|remains)\s+(?:the\s+)?(?:current|active)\b",re.I),
    re.compile(r"^#\s+SCAP-NG\s+0\.3\s+examples\b",re.I|re.M),
)
# The pages actively recommending 0.4 native source must link the maintained
# download/index landing page, not an obsolete six-STIG sample tag.
NEEDS_CURRENT_INDEX = (
    "README.md", "ROADMAP.md",
    "specification/examples/README.md","specification/examples/assessments.md",
    "review/current/README.md","review/current/REVIEW-GUIDE.md",
    "review/current/examples/rhel9-full.md",
    "review/current/examples/windows11-full.md",
    "schema/v0.4.0/README.md",
    "docs/public-authoring/README.md",
    "docs/public-authoring/VERSION-AND-SOURCES.md",
)

def check(root: Path):
    problems=[]
    count=0
    for relative in CURRENT:
        path=root/relative
        if not path.is_file():
            problems.append(f"missing current Markdown entry: {relative}")
            continue
        count+=1
        text=path.read_text(encoding="utf-8")
        if relative in NEEDS_CURRENT_INDEX and CURRENT_INDEX not in text:
            problems.append(f"{relative}: current 0.4 downloads index missing")
        for pattern in STALE:
            for m in pattern.finditer(text):
                line=text.count("\n",0,m.start())+1
                problems.append(f"{relative}:{line}: stale 0.3 source/current status: {m.group(0)}")
    index=root/"docs/releases"/CURRENT_INDEX
    if not index.is_file():
        problems.append(f"missing current 0.4 downloads index: {index.relative_to(root)}")
    else:
        contents=index.read_text(encoding="utf-8")
        for marker in REQUIRED_INDEX_MARKERS:
            if marker not in contents:
                problems.append(f"current 0.4 downloads index missing pinned marker: {marker}")
        if "no final" not in contents.lower():
            problems.append("current 0.4 downloads index must state that no final release exists")
    archive=root/"archive/0.3.0/README.md"
    if not archive.is_file() or "v0.3.0-six-stig-typed-operators" not in archive.read_text(encoding="utf-8"):
        problems.append("missing preserved historic 0.3 samples and release link")
    return count,problems


def main():
    root=Path(__file__).resolve().parents[1]
    checked,problems=check(root)
    for error in problems: print("FAIL",error,file=sys.stderr)
    if problems: raise SystemExit(1)
    print(f"PASS {checked} current Markdown entry points use the pinned 0.4 downloads index; historic 0.3 archived")


if __name__=="__main__":
    main()
