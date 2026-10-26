#!/usr/bin/env python3
"""Reproduce published Windows 11 Bluetooth direct-Filter 0.4.0 evidence.

Historical consumer: run with the pinned schema/tool snapshot in
v04-bluetooth-archive.yml. Current acceptance uses
prove_v04_current_bluetooth_source.py and original SCAP instead of this archive.

Reads the immutable published six-STIG source-preview ZIP, checks its manifest
and exact Assessment digest, validates native generic/capability schemas,
then exports this Assessment alone to OVAL 5.12.3 and checks the independent
OVAL XSD. This is not a scanner execution or a complete converter proof.
Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from zipfile import ZipFile

from export_v04_oval_shellcommand_pilot import emit, IND, OD
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs
from validate_v04_oval_5123 import check


RELEASE_TAG = "v0.4.0-six-stig-canonical-flat-authoring-20261021"
ASSET = "ms_windows_11.source-preview.zip"
PACKAGE_SHA = "7a053e0aeaa866a3a019d76b6d35e441a4cdfc4c22fd0405c8b4dd29be645170"
ASSESSMENT_ID = "condition.bluetooth-installation.assessment"
ASSESSMENT_SHA = "e096d70827b032ea0029e43c252bc4a439a7e386b2e6717e333da6f974347b1b"
TEST_ID = "report-true-if-bluetooth-installed-test"
COMMAND = "(Get-PnpDevice -class bluetooth -status OK).class"


def require(ok, message):
    if not ok:
        raise ValueError("published Bluetooth 0.4.0 source proof: " + message)


def verify_document(doc):
    require(set(doc) == {"assessment"}, "only Assessment root")
    a = doc["assessment"]
    require(a.get("id") == ASSESSMENT_ID and a.get("version") == 18 and
            a.get("mode") == "automated" and a.get("class") == "inventory" and
            a.get("purpose") == "applicability" and
            a.get("specification") == {
                "id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
            "release Assessment identity and version")
    require(a.get("evaluate") == {"test": TEST_ID} and
            set(a.get("tests", {})) == {TEST_ID},
            "single source-linked Bluetooth Test")
    t = a["tests"][TEST_ID]
    require(t.get("capability") == "independent.shellcommand" and
            t.get("reported_elements") == "all" and
            t.get("require") == {"items": "one_or_more"} and
            "states" not in t,
            "original State-free existence requirement")
    obj = t.get("object")
    require(isinstance(obj, dict) and "set" not in obj and
            "collect" not in obj and "select" not in obj and
            obj.get("shell") == "powershell" and
            obj.get("command") == COMMAND and
            obj.get("error_if_exit_status_not_0") is False and
            obj.get("error_if_stderr_exists") is False,
            "no synthetic Set/Union or generic Object wrappers")
    require(obj.get("filters") == [{"include": {"stdout_line": {
        "case_insensitive_equals": "Bluetooth",
        "require": "at_least_one_exists_and_all_match",
    }}}], "one direct original include Filter over collected stdout_line")
    return t


def prove(source_package, schema_root, xsd_root, output):
    raw_zip = Path(source_package).read_bytes()
    require(sha256(raw_zip).hexdigest() == PACKAGE_SHA,
            "published release ZIP checksum changed")
    with ZipFile(source_package) as package:
        names = set(package.namelist())
        require("META-INF/manifest.json" in names, "missing package manifest")
        manifest = json.loads(package.read("META-INF/manifest.json"))
        record = manifest["objects"]["assessment:" + ASSESSMENT_ID]
        path = record["path"]
        require(path in names and path.startswith("documents/assessment/") and
                path.endswith(".json"), "release manifest Assessment reference")
        source = package.read(path)
        require(sha256(source).hexdigest() == ASSESSMENT_SHA and
                record["sha256"] == ASSESSMENT_SHA and
                record["size"] == len(source),
                "manifest-assessment content digest and size mismatch")
        provenance = manifest.get("build_provenance", {})
        require(provenance.get("executable_compiler_complete") is False and
                provenance.get("scanner_evaluation_verified") is False and
                provenance.get("publisher_signature_verified") is False,
                "source-only preview cannot claim scanner/package signing")
    doc = json.loads(source)
    t = verify_document(doc)
    validate_docs({"authoring/" + ASSESSMENT_ID + ".json": doc},
                  _schema_validators(schema_root))
    errors = validate(materialize("independent.shellcommand"), "test", t)
    require(not errors, "generated shellcommand native Test schema " +
            str(errors[:2]))
    tree, definition_id = emit(doc)
    root = tree.getroot()
    require(not list(root.iter("{" + OD + "}set")) and
            len(list(root.iter("{" + OD + "}filter"))) == 1 and
            len(list(root.iter("{" + IND + "}shellcommand_test"))) == 1 and
            len(list(root.iter("{" + IND + "}shellcommand_state"))) == 1,
            "regenerated original Object direct Filter and State-free Test")
    for bad_mutation in ("replace_with_set", "remove_filter", "change_case"):
        wrong = deepcopy(doc)
        obj = wrong["assessment"]["tests"][TEST_ID]["object"]
        if bad_mutation == "replace_with_set":
            obj["set"] = {"operator": "union", "operands": []}
        elif bad_mutation == "remove_filter":
            del obj["filters"]
        else:
            obj["filters"][0]["include"]["stdout_line"][
                "case_insensitive_equals"] = "WiFi"
        try:
            verify_document(wrong)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted published Bluetooth mutation: " +
                                 bad_mutation)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "native-040-published.json").write_bytes(source)
    oval_path = out / "native-040-exported-oval.xml"
    tree.write(oval_path, encoding="utf-8", xml_declaration=True)
    xsd = check(Path(xsd_root), oval_path, "independent")
    require(xsd["status"] == "PASS", "independent OVAL 5.12.3 XSD " +
            str(xsd["diagnostics"][:3]))
    (out / "exported-oval-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    report = {
        "status": "PASS", "release_tag": RELEASE_TAG, "release_asset": ASSET,
        "release_zip_sha256": PACKAGE_SHA, "assessment_sha256": ASSESSMENT_SHA,
        "assessment_id": ASSESSMENT_ID, "exported_definition_id": definition_id,
        "published_no_synthetic_union": True, "published_direct_include_filter": True,
        "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
        "exported_oval_5123_independent_xsd": "PASS",
        "source_mutations_rejected": 3,
        "scanner_parity": False, "publisher_signature_verified": False,
        "full_source_definition_roundtrip_certified": False,
    }
    (out / "release-content-proof.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-package", required=True, type=Path)
    p.add_argument("--schema-root", required=True, type=Path)
    p.add_argument("--xsd-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(prove(a.source_package, a.schema_root, a.xsd_root, a.output),
                     sort_keys=True))
