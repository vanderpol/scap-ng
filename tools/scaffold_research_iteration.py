#!/usr/bin/env python3
"""Create the stable directory skeleton for a new SCAP-NG research iteration."""

from __future__ import annotations

import argparse
from pathlib import Path


DIRECTORIES = (
    "feedback/responses",
    "notes",
    "prototypes/combined-rule/content/windows",
    "prototypes/combined-rule/content/linux",
    "prototypes/combined-rule/results/windows",
    "prototypes/combined-rule/results/linux",
    "prototypes/split-policy-assessment-binding/content/windows/policy",
    "prototypes/split-policy-assessment-binding/content/windows/assessments",
    "prototypes/split-policy-assessment-binding/content/linux/policy",
    "prototypes/split-policy-assessment-binding/content/linux/assessments",
    "prototypes/split-policy-assessment-binding/results/windows",
    "prototypes/split-policy-assessment-binding/results/linux",
    "prototypes/package",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("iteration", help="Iteration number, e.g. 002")
    parser.add_argument(
        "--research-root",
        type=Path,
        default=Path("research/iterations"),
    )
    args = parser.parse_args()

    iteration = args.iteration.zfill(3)
    root = args.research_root / iteration

    for relative in DIRECTORIES:
        (root / relative).mkdir(parents=True, exist_ok=True)

    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# SCAP-NG Research Iteration {iteration}\n\n"
            "**Status:** Preliminary research\n",
            encoding="utf-8",
        )

    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
