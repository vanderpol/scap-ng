#!/usr/bin/env python3
"""Reject stale 0.3 authoring-sample recommendations in CURRENT Markdown entry points.

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
RELEASE = "v0.4.0-six-stig-authoring-approved-20261020"
STALE = (
    re.compile(r"https://github\\.com/vanderpol/scap-ng/releases/(?:tag|download)/v0\\.3\\.0-",re.I),
    re.compile(r"0\\.3(?:\\.0)?\\s+(?:is|remains)\\s+(?:the\\s+)?(?:current|active)\\b",re.I),
    re.compile(r"^#\\s+SCAP-NG\\s+0\\.3\\s+examples\\b",re.I|re.M),
)
# The pages actively recommending a source download must link the exact
# approved source release. Informative version lists can use nearby docs links.
NEEDS_CURRENT_RELEASE = (
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
        if relative in NEEDS_CURRENT_RELEASE and RELEASE not in text:
            problems.append(f"{relative}: approved 0.4 sample release missing")
        for pattern in STALE:
            for m in pattern.finditer(text):
                line=text.count("\\n",0,m.start())+1
                problems.append(f"{relative}:{line}: stale 0.3 source/current status: {m.group(0)}")
    archive=root/"archive/0.3.0/README.md"
    if not archive.is_file() or "v0.3.0-six-stig-typed-operators" not in archive.read_text(encoding="utf-8"):
        problems.append("missing preserved historic 0.3 samples and release link")
    return count,problems


def main():
    root=Path(__file__).resolve().parents[1]
    checked,problems=check(root)
    for error in problems: print("FAIL",error,file=sys.stderr)
    if problems: raise SystemExit(1)
    print(f"PASS {checked} current Markdown entry points use 0.4.0; historic 0.3 archived")


if __name__=="__main__":
    main()
