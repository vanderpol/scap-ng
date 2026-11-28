#!/usr/bin/env python3
"""Replay the canonical content-package fixture through RI installation."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

from build_content_fixture import build, json_bytes
from runner import CONFORMANCE, load


def replay(binary, revision):
    oracle = load(CONFORMANCE / "content-package/expected.json")
    observed = {}
    package_manifest_digest = None
    for variant, expected in oracle["variants"].items():
        with TemporaryDirectory(prefix="scap-ng-content-replay-") as temp:
            root = Path(temp)
            package = root / "package"
            manifest = build(package)
            manifest_path = package / "manifest.json"
            primary = package / "rules/primary.json"
            if variant == "accepted":
                package_manifest_digest = sha256(manifest_path.read_bytes()).hexdigest()
            elif variant == "changed_bytes":
                primary.write_bytes(primary.read_bytes() + b" ")
            elif variant == "dangling_rule_assessment":
                document = load(primary)
                document["rule"]["assessment_choices"]["standard"]["assessment"] = "missing-assessment"
                raw = json_bytes(document)
                primary.write_bytes(raw)
                manifest["objects"]["rule:primary-rule"].update(sha256=sha256(raw).hexdigest(), size=len(raw))
                manifest_path.write_bytes(json_bytes(manifest))
            elif variant == "unexpected_member":
                (package / "unexpected.json").write_text("{}\n", encoding="utf-8")
            elif variant != "require_signature":
                raise ValueError(f"Unknown variant {variant}")

            command = [str(binary), "install", "--store", str(root / "store"), "--package", str(package)]
            if variant == "require_signature":
                command.append("--require-signature")
            result = subprocess.run(command, capture_output=True, text=True, timeout=15)
            if result.returncode != expected["exit_code"]:
                raise ValueError(f"{variant}: unexpected status {result.returncode}: {result.stderr.strip()}")
            row = {"exit_code": result.returncode}
            if result.returncode:
                row["diagnostic"] = result.stderr.strip()
                if expected["reason"] not in row["diagnostic"]:
                    raise ValueError(f"{variant}: unexpected diagnostic {row['diagnostic']}")
            else:
                installed = json.loads(result.stdout)
                row["benchmark_id"] = installed["benchmark_id"]
                if row["benchmark_id"] != oracle["benchmark_id"]:
                    raise ValueError("Installed Benchmark identity differs from the oracle")
                row["package_digest"] = installed["package_digest"]
            observed[variant] = row

    return {
        "format": "scap-ng-ri-content-admission-receipt-1",
        "ri_revision": revision,
        "schema_pin": oracle["schema_pin"],
        "manifest_sha256": package_manifest_digest,
        "scope": "Content installation and validation. No policy or Assessment evaluation took place.",
        "variants": observed,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ri-content", type=Path, required=True)
    parser.add_argument("--ri-revision", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json_bytes(replay(args.ri_content.resolve(strict=True), args.ri_revision))
    if args.check:
        saved = (CONFORMANCE / "content-package/ri-receipt.json").read_bytes()
        if rendered != saved:
            raise SystemExit("RI content-package receipt differs from the pinned fixture")
    print(rendered.decode(), end="")
