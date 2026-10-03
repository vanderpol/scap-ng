#!/usr/bin/env python3
"""Extract complete pinned check requirements; never run content commands."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))
import scap14_rule_splitter as split

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
FAMILIES = ("rhel_9", "ms_windows_server_2025")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def value(node, field):
    child = next((c for c in node if split.local(c.tag) == field), None)
    return "" if child is None else "".join(child.itertext())


def extract(source_root):
    destination = HERE / "evidence"
    destination.mkdir(exist_ok=True)
    summary = {"source_revision": "8c8e5dff860af6b1290ee9273a282db24278f8d5", "families": {},
               "limits": "Original check requirements and reference inventory; not interpretation or scanner equivalence."}
    for family in FAMILIES:
        pin = json.loads((STUDY / "samples" / family / "source-generation.json").read_text())
        path = source_root / pin["source_zip"]
        digest = sha(path.read_bytes())
        if digest != pin["source_sha256"]:
            raise ValueError(f"source ZIP hash mismatch: {path}")
        member, data, ds = split.find_datastream(path)
        components, refs = split.embedded_components(ds)
        benchmarks = [v for v in components.values() if split.component_kind(v) == "xccdf"]
        if len(benchmarks) != 1:
            raise ValueError("expected one source Benchmark")
        benchmark = benchmarks[0]
        rules = []
        for raw in benchmark.iter():
            if split.local(raw.tag) != "Rule":
                continue
            identifier = re.search(r"SV-\d+", raw.get("id", ""))
            if identifier is None:
                raise ValueError(f"unrecognized source Rule identity: {raw.get('id')}")
            checks = []
            for check in raw:
                if split.local(check.tag) != "check":
                    continue
                checks.append({"system": check.get("system"), "selector": check.get("selector"),
                               "content": ["".join(c.itertext()) for c in check
                                           if split.local(c.tag) == "check-content"],
                               "references": [dict(c.attrib) for c in check
                                              if split.local(c.tag) == "check-content-ref"]})
            texts = [t for c in checks for t in c["content"] if t.strip()]
            if not texts:
                raise ValueError(f"no check requirement for {identifier.group()}")
            rules.append({"ordinal": len(rules) + 1, "id": identifier.group(), "source_id": raw.get("id"),
                          "version": value(raw, "version"), "title": value(raw, "title"),
                          "severity": raw.get("severity"), "checks": checks,
                          "rule_xml_sha256": sha(etree.tostring(raw)),
                          "check_text_sha256": [sha(t.encode()) for t in texts]})
        if len({r["id"] for r in rules}) != len(rules):
            raise ValueError("duplicate Rule identity")
        payload = {"source": pin, "datastream_member": member, "datastream_sha256": sha(data),
                   "benchmark_id": benchmark.get("id"), "benchmark_version": value(benchmark, "version"),
                   "rule_count": len(rules), "rules": rules}
        output = destination / f"{family}.json"
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        summary["families"][family] = {"rules": len(rules), "with_check_text": len(rules),
                                       "version": payload["benchmark_version"], "zip_sha256": digest,
                                       "datastream_sha256": sha(data), "extracted_sha256": sha(output.read_bytes()),
                                       "severity": dict(Counter(r["severity"] for r in rules)),
                                       "check_characters": sum(len(t) for r in rules for c in r["checks"] for t in c["content"])}
    (destination / "extraction.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_root", type=Path)
    args = parser.parse_args()
    print(json.dumps(extract(args.source_root), indent=2))
