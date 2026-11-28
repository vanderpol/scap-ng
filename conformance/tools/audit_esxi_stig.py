#!/usr/bin/env python3
"""Account for the pinned DISA ESXi manual checks against OVAL 6.0 families."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from qualify_merge_fixture import require_equal
from runner import CONFORMANCE, ROOT, load

FIXTURE = CONFORMANCE / "experimental/esxi/stig"
XCCDF = "{http://checklists.nist.gov/xccdf/1.1}"
ADVANCED_SETTING = re.compile(r'Get-AdvancedSetting\s+-Name\s+["\']?([A-Za-z][A-Za-z0-9_.]+)', re.I)


def check_projection(capabilities, domains, oval_tests):
    result = {}
    for name, fields in capabilities.items():
        valid = {row["name"] for row in domains[name]["item_fields"]}
        if not fields or not set(fields) <= valid:
            raise ValueError(f"Invalid OVAL 6.0 evidence fields for {name}: {fields}")
        qname, status = oval_tests[name]
        result[name] = {"oval_6_test": qname, "adoption": status, "fields": fields}
    return result


def audit(archive):
    pins = load(FIXTURE / "source.json")
    review = load(FIXTURE / "review.json")
    fixture = load(FIXTURE / "expected.json")
    require_equal(fixture["source_release"], pins["release"], "native fixture source version")
    fixture_cases = {case["stig_id"]: (name, case["check_marker"]) for name, case in fixture["tests"].items()}

    require_equal(sha256(archive.read_bytes()).hexdigest(), pins["archive_sha256"], "DISA archive bytes")
    with ZipFile(archive) as package:
        raw = package.read(pins["member"])
    require_equal(sha256(raw).hexdigest(), pins["member_sha256"], "ESXi XCCDF bytes")
    benchmark = ET.fromstring(raw)
    require_equal((benchmark.tag, benchmark.attrib["id"]), (XCCDF + "Benchmark", pins["benchmark"]), "XCCDF")
    require_equal(benchmark.findtext(XCCDF + "version"), pins["release"].split(".")[0], "Benchmark version")
    release = benchmark.find(f'{XCCDF}plain-text[@id="release-info"]').text
    require_equal(release, "Release: 5 Benchmark Date: 30 Sep 2026", "release marker")

    oval = load(CONFORMANCE / "oval-source-coverage.json")
    mapping = load(ROOT / "proposed/issue86-esx-oval6/capability-crosswalk.json")
    require_equal(mapping["source"]["commit"], oval["pins"]["oval_6_0"], "OVAL source commit")
    domains = {row["capability"]: row for row in mapping["families"]}
    oval_tests = {row["capability"]: (qname, row["status"]) for qname, row in oval["oval_6_0_esxi_tests"].items()}
    require_equal(set(domains), set(oval_tests), "OVAL Test families")

    rows = {}
    reviewed = set()
    for group in benchmark.iter(XCCDF + "Group"):
        for rule in group.findall(XCCDF + "Rule"):
            stig_id = rule.findtext(XCCDF + "version")
            if stig_id in rows:
                raise ValueError(f"Duplicate STIG Rule {stig_id}")
            check, = rule.findall(XCCDF + "check")
            ref, = check.findall(XCCDF + "check-content-ref")
            require_equal(ref.get("name"), "M", stig_id)
            content = " ".join(check.findtext(XCCDF + "check-content").split())
            row = {"group_id": group.attrib["id"], "rule_id": rule.attrib["id"], "severity": rule.attrib["severity"],
                   "source_check_sha256": sha256(content.encode()).hexdigest(), "check_kind": "manual",
                   "disposition": "unreviewed", "projections": {}}
            settings = sorted(set(ADVANCED_SETTING.findall(content)))
            if settings:
                row.update(
                    disposition="candidate-projection", selectors=settings,
                    projections=check_projection({"esx.host_advancedsetting": ["advanced_setting_name",
                                                                                "advanced_setting_value"]}, domains, oval_tests),
                    qualification_gap="The projected setting needs independently reviewed conditional, value and acquisition semantics.",
                )
            if stig_id in review["explicit_projections"]:
                approved = review["explicit_projections"][stig_id]
                if approved["marker"].casefold() not in content.casefold():
                    raise ValueError(f"{stig_id}: reviewed source marker is absent")
                row.update(disposition="candidate-projection",
                           projections=check_projection(approved["capabilities"], domains, oval_tests),
                           qualification_gap=approved["qualification_gap"])
                selectors = approved.get("selectors", [])
                if selectors:
                    if any(selector not in content for selector in selectors):
                        raise ValueError(f"{stig_id}: projected setting is absent from the check")
                    row["selectors"] = selectors
                reviewed.add(stig_id)
            if stig_id in review["source_holds"]:
                hold = review["source_holds"][stig_id]
                if any(marker.casefold() not in content.casefold() for marker in hold["markers"]):
                    raise ValueError(f"{stig_id}: held source marker is absent")
                row.update(disposition="held", qualification_gap=hold["reason"])
                reviewed.add(stig_id)
            if stig_id in fixture_cases:
                name, marker = fixture_cases[stig_id]
                if marker.casefold() not in content.casefold() or row["disposition"] != "candidate-projection":
                    raise ValueError(f"{stig_id}: cannot verify the authored case against its source")
                row["experimental_test"] = name
            rows[stig_id] = row
    require_equal(reviewed, set(review["source_holds"]) | set(review["explicit_projections"]), "reviewed source IDs")
    require_equal(len(rows), pins["rule_count"], "manual Rule census")
    require_equal([key for key, row in rows.items() if row["disposition"] == "unreviewed"], [], "unreviewed Rules")
    require_equal(set(fixture_cases), {key for key, row in rows.items() if "experimental_test" in row}, "experimental cases")

    families = {name: {"oval_6_test": qname, "adoption": status, "projected_rule_ids": []}
                for name, (qname, status) in oval_tests.items()}
    for stig_id, row in sorted(rows.items()):
        if row["disposition"] == "candidate-projection":
            for capability in row["projections"]:
                families[capability]["projected_rule_ids"].append(stig_id)
    return {
        "format": "scap-ng-esxi-stig-oval6-audit-1", "source": pins, "oval_6_pin": oval["pins"]["oval_6_0"],
        "dispositions": dict(Counter(row["disposition"] for row in rows.values())),
        "qualification": "Experimental and proposed evidence crosswalk. All source checks are manual. "
                         "No full Rule, converter parity, hardware or runtime qualification is asserted.",
        "families": families, "rules": rows,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = json.dumps(audit(args.archive), indent=2, sort_keys=True) + "\n"
    receipt = FIXTURE / "coverage.json"
    if args.check and receipt.read_text(encoding="utf-8") != output:
        raise SystemExit("ESXi STIG receipt differs from the pinned audit")
    print(output, end="")
