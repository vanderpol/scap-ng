#!/usr/bin/env python3
"""Generate one fresh current-design review tree from a pinned NIWC SCAP 1.4 ZIP.

This wrapper intentionally derives all input from the supplied source ZIP and
current converter code.  It does not read any previously generated SCAP-NG
artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def safe(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-").lower() or "benchmark"


def source_identity(path: Path):
    with zipfile.ZipFile(path) as zf:
        for name in sorted(zf.namelist()):
            if not name.lower().endswith(".xml"):
                continue
            try:
                root = ET.fromstring(zf.read(name))
            except ET.ParseError:
                continue
            candidates = [root] if local(root.tag) == "Benchmark" else [
                x for x in root.iter() if local(x.tag) == "Benchmark"
            ]
            if not candidates:
                continue
            benchmark = candidates[0]
            title = next(
                (" ".join((x.text or "").split()) for x in benchmark if local(x.tag) == "title" and (x.text or "").strip()),
                path.stem,
            )
            source_id = benchmark.get("id") or path.stem
            return {
                "source_benchmark_id": source_id,
                "benchmark_id": "niwc." + safe(source_id),
                "platform_id": "source." + safe(source_id),
                "platform_title": title,
                "title": title,
            }
    raise RuntimeError(f"No XCCDF Benchmark found in {path}")


def run(command):
    print("+", " ".join(map(str, command)), flush=True)
    subprocess.run([str(x) for x in command], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_zip", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--split-root", type=Path, required=True)
    ap.add_argument("--source-revision", required=True)
    ap.add_argument("--source-repository-path", required=True)
    ap.add_argument("--schema", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    identity = source_identity(args.source_zip)
    sha256 = hashlib.sha256(args.source_zip.read_bytes()).hexdigest()
    benchmark_key = safe(identity["source_benchmark_id"])

    args.split_root.parent.mkdir(parents=True, exist_ok=True)
    run([
        sys.executable,
        Path(__file__).with_name("scap14_rule_splitter.py"),
        args.source_zip,
        "--output-dir", args.split_root,
        "--schema", args.schema,
        "--source-revision", args.source_revision,
        "--source-repository-path", args.source_repository_path,
        "--benchmark-key", benchmark_key,
        "--fail-on-unresolved",
    ])
    run([
        sys.executable,
        Path(__file__).parent / "scap_upconvert_v003" / "convert_full_review.py",
        "--input", args.source_zip,
        "--sha256", sha256,
        "--benchmark-id", identity["benchmark_id"],
        "--platform-id", identity["platform_id"],
        "--platform-title", identity["platform_title"],
        "--split-root", args.split_root,
        "--output", args.output,
    ])

    summary = {
        **identity,
        "source_zip": args.source_repository_path,
        "source_revision": args.source_revision,
        "source_sha256": sha256,
        "output": args.output.as_posix(),
        "generated_fresh": True,
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
