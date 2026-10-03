#!/usr/bin/env python3
"""Independently check original XCCDF coverage and recorded reading ranges."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

from lxml import etree

HERE = Path(__file__).resolve().parent
NS = {"x": "http://checklists.nist.gov/xccdf/1.2"}
FAMILIES = {"rhel_9": ("RHEL 9", 445),
            "ms_windows_server_2025": ("Windows Server 2025", 291)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(source_root):
    notes = (HERE / "READING-NOTES.md").read_text()
    extraction = json.loads((HERE / "evidence/extraction.json").read_text())
    report = {"families": {}, "scope": "Source-text/reference preservation and recorded reading coverage only; no scanner equivalence."}
    for family, (label, expected_count) in FAMILIES.items():
        path = HERE / "evidence" / f"{family}.json"
        payload = json.loads(path.read_text())
        pin = payload["source"]
        require(pin["source_revision"] == extraction["source_revision"], "revision mismatch")
        source = source_root / pin["source_zip"]
        require(sha(source.read_bytes()) == pin["source_sha256"], "source ZIP hash mismatch")
        require(sha(path.read_bytes()) == extraction["families"][family]["extracted_sha256"], "extracted hash mismatch")
        with ZipFile(source) as archive:
            data = archive.read(payload["datastream_member"])
        require(sha(data) == payload["datastream_sha256"], "datastream hash mismatch")
        root = etree.fromstring(data, etree.XMLParser(resolve_entities=False, no_network=True))
        benchmarks = root.xpath(".//x:Benchmark", namespaces=NS)
        require(len(benchmarks) == 1, "benchmark count mismatch")
        benchmark = benchmarks[0]
        require(benchmark.get("id") == payload["benchmark_id"], "benchmark identity mismatch")
        require(benchmark.findtext("x:version", namespaces=NS) == payload["benchmark_version"], "benchmark version mismatch")
        originals = benchmark.xpath(".//x:Rule", namespaces=NS)
        require(len(originals) == len(payload["rules"]) == payload["rule_count"] == expected_count,
                "Rule coverage mismatch")
        originals_by_id = {node.get("id"): node for node in originals}
        require(len(originals_by_id) == expected_count, "duplicate original identity")
        require(len({r["source_id"] for r in payload["rules"]}) == expected_count,
                "duplicate extracted identity")
        checks_verified = 0
        for ordinal, (original, rule) in enumerate(zip(originals, payload["rules"]), 1):
            require(rule["ordinal"] == ordinal, "ordinal gap")
            require(rule["source_id"] == original.get("id"), "source identity/order mismatch")
            require(rule["id"] == re.search(r"SV-\d+", original.get("id")).group(), "SV identity mismatch")
            for field in ("title", "version"):
                element = original.find(f"x:{field}", namespaces=NS)
                require(rule[field] == "".join(element.itertext()), f"{field} mismatch")
            require(rule["severity"] == original.get("severity"), "severity mismatch")
            original_checks = []
            for check in original.findall("x:check", namespaces=NS):
                original_checks.append({"system": check.get("system"), "selector": check.get("selector"),
                                        "content": ["".join(c.itertext()) for c in check.findall("x:check-content", namespaces=NS)],
                                        "references": [dict(c.attrib) for c in check.findall("x:check-content-ref", namespaces=NS)]})
            require(original_checks == rule["checks"], f"check text/reference mismatch: {rule['id']}")
            texts = [t for c in original_checks for t in c["content"] if t.strip()]
            require(bool(texts), f"no Check Text: {rule['id']}")
            require(rule["check_text_sha256"] == [sha(t.encode()) for t in texts], "text hash mismatch")
            checks_verified += len(original_checks)
        ranges = re.findall(r"^#{2,3} " + re.escape(label) + r", (?:ordinals )?(\d+)–(\d+)", notes, re.M)
        counts = Counter(i for start, end in ranges for i in range(int(start), int(end) + 1))
        require(counts == Counter(range(1, expected_count + 1)), "reading log has gaps/overlaps")
        report["families"][family] = {"rules_verified": expected_count, "checks_verified": checks_verified,
                                       "complete_check_text_matches": expected_count,
                                       "recorded_reading_ordinals": len(counts), "batches": len(ranges)}
    report["total_rules_verified"] = sum(v["rules_verified"] for v in report["families"].values())
    (HERE / "evidence/verification.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.source_root), indent=2))
