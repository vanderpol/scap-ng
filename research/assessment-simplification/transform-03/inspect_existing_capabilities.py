#!/usr/bin/env python3
"""Inventory pinned source versions/Test types; never execute content commands."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
STUDY = ROOT / "research/assessment-simplification"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-cache", type=Path, required=True)
    args = parser.parse_args()
    report = {
        "receiving_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "niwc_revision": "8c8e5dff860af6b1290ee9273a282db24278f8d5",
        "method": "Parse extracted OVAL tests/generator; verify pinned ZIP hashes and read original data-stream scap-version attributes. No content commands execute.",
        "cases": [], "packages": [],
    }
    for path in sorted((STUDY / "evidence").glob("*/*/source-oval.xml")):
        tree = etree.parse(str(path))
        counts = Counter(etree.QName(n).localname for n in tree.getroot().find("{*}tests"))
        report["cases"].append({
            "family": path.parent.parent.name, "rule": path.parent.name,
            "file": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "oval_generator_schema_versions": tree.xpath('//*[local-name()="generator"]/*[local-name()="schema_version"]/text()'),
            "test_types": dict(sorted(counts.items())),
        })
    pins = json.loads((STUDY / "refinement-01/evidence/source-reproduction.json").read_text())["package_hashes"]
    for pin in pins:
        path = args.source_cache / pin["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != pin["sha256"]:
            raise ValueError(f"pinned ZIP hash mismatch: {path}")
        streams = []
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                if not member.lower().endswith(".xml"):
                    continue
                with archive.open(member) as handle:
                    for _, node in etree.iterparse(handle, events=("start",)):
                        if etree.QName(node).localname == "data-stream":
                            streams.append({"member": member, "attributes": dict(node.attrib)})
        report["packages"].append({"family": pin["family"], "path": pin["path"],
                                   "sha256": digest, "data_streams": streams})
    report["limits"] = [
        "Enhanced NIWC sources do not establish what DISA currently publishes for every benchmark.",
        "Shellcommand use and a 1.4 declaration do not prove target support or result equivalence.",
        "Generator version differs from capability use and datastream version.",
    ]
    (STUDY / "transform-03/evidence/existing-capabilities-inventory.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"cases": len(report["cases"]),
                      "cases_using_shellcommand": sum("shellcommand_test" in r["test_types"] for r in report["cases"]),
                      "package_scap_versions": [s["attributes"].get("scap-version")
                                                for r in report["packages"] for s in r["data_streams"]]}, indent=2))


if __name__ == "__main__":
    main()
