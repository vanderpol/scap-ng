#!/usr/bin/env python3
"""Independently parse and validate the pinned 0.4 JSON authoring review packet.

Research candidate syntax only. This does not compile a signed .scapng bundle,
execute Assessments, or ratify the scoped requirement syntax.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import unittest
import zipfile

from research_04_scoped_schema import validate
from test_v04_review_reference_graph import scan

EXPECTED_DOCUMENTS = 4001
# Pinned six-STIG preview sums 1,396 per-Benchmark *occurrences*.
# Its shared Assessment deduplication yields only 872 distinct authored
# automated documents. Do not confuse these counts or weaken the gate.
EXPECTED_AUTO_ASSESSMENTS = 872
EXPECTED_NATIVE_TEST_NODES = 1375
EXPECTED_RULES = 1567
EXPECTED_ASSESSMENT_IDS = 2422
EXPECTED_RULE_CHOICE_LINKS = 2958


def documents_from_json_archive(archive_path):
    documents = {}
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupted JSON ZIP member")
        for path in sorted(archive.namelist()):
            if not (path.startswith("authoring/") and path.endswith(".json")):
                continue
            try:
                doc = json.loads(archive.read(path))
            except (UnicodeError, ValueError) as exc:
                raise ValueError(f"{path}: invalid standalone JSON: {exc}") from exc
            if not isinstance(doc, dict) or len(doc) != 1:
                raise ValueError(f"{path}: expected a single-root native document")
            documents[path] = doc
    return documents


def audit_json_authoring(documents, *, validate_native=True, pinned_r3=True):
    """Source-independent JSON validation, without reading the YAML archive."""
    if not documents:
        raise ValueError("Empty JSON authoring archive")
    total = Counter()
    parsed = {}
    cache = {}
    for path,doc in sorted(documents.items()):
        if not path.endswith(".json"):
            raise ValueError(f"{path}: authoring source is not JSON")
        if not isinstance(doc,dict) or len(doc)!=1:
            raise ValueError(f"{path}: expected one native document root")
        root = next(iter(doc))
        if root not in {"assessment","rule","benchmark","applicability"}:
            raise ValueError(f"{path}: unsupported native document root {root!r}")
        total[root]+=1
        if root == "assessment":
            assessment = doc["assessment"]
            if not isinstance(assessment,dict):
                raise ValueError(f"{path}: invalid Assessment")
            if assessment.get("mode") == "automated":
                total["automated_assessments"]+=1
                total["native_test_nodes"]+=len(assessment.get("tests") or {})
                if validate_native:
                    try:
                        validate(doc,cache)
                    except Exception as exc:
                        raise ValueError(f"{path}: independent native JSON schema failure: {exc}") from exc
            else:
                total["contextual_assessments"]+=1
        parsed[path] = doc

    references,errors=scan(parsed)
    if errors:
        raise ValueError("Unresolved JSON authoring references: "+repr(errors[:15]))
    total["documents"]=len(parsed)
    total.update({k:references.get(k,0) for k in
                  ("rule_choice_links","evaluate_test_leaves","variable_references",
                   "shared_object_references","unresolved")})
    if pinned_r3:
        for key,expected in (
            ("documents",EXPECTED_DOCUMENTS),
            ("assessment",EXPECTED_ASSESSMENT_IDS),
            ("rule",EXPECTED_RULES),
            ("rule_choice_links",EXPECTED_RULE_CHOICE_LINKS),
            ("automated_assessments",EXPECTED_AUTO_ASSESSMENTS),
            ("native_test_nodes",EXPECTED_NATIVE_TEST_NODES),
            ("unresolved",0),
        ):
            if total[key] != expected:
                raise ValueError(f"Pinned r3 {key} changed: {total[key]} != {expected}")
    return dict(total)


class JsonOnlyPositiveNegativeTests(unittest.TestCase):
    def basic_docs(self):
        return {
            "authoring/a.json":{"assessment":{"id":"a","mode":"manual"}},
            "authoring/r.json":{"rule":{"id":"r",
                "assessment_choices":{"manual":{"assessment":"a"}},
                "default_assessment_choice":"manual"}},
        }

    def test_independent_json_reference_graph(self):
        result=audit_json_authoring(self.basic_docs(),validate_native=False,pinned_r3=False)
        self.assertEqual(result["rule_choice_links"],1)
        self.assertEqual(result["unresolved"],0)

    def test_dangling_json_reference_fails(self):
        docs=self.basic_docs()
        docs["authoring/r.json"]["rule"]["assessment_choices"]["manual"]["assessment"]="missing"
        with self.assertRaisesRegex(ValueError,"Unresolved JSON"):
            audit_json_authoring(docs,validate_native=False,pinned_r3=False)

    def test_duplicate_assessment_identity_fails(self):
        docs=self.basic_docs()
        docs["authoring/duplicate.json"]={"assessment":{"id":"a","mode":"manual"}}
        with self.assertRaisesRegex(ValueError,"Unresolved JSON"):
            audit_json_authoring(docs,validate_native=False,pinned_r3=False)

    def test_source_file_must_be_json(self):
        docs=self.basic_docs()
        docs["authoring/a.yaml"]=docs.pop("authoring/a.json")
        with self.assertRaisesRegex(ValueError,"not JSON"):
            audit_json_authoring(docs,validate_native=False,pinned_r3=False)

    def test_invalid_document_root_fails(self):
        docs=self.basic_docs()
        docs["authoring/r.json"]={"unknown":{"id":"r"}}
        with self.assertRaisesRegex(ValueError,"unsupported native document root"):
            audit_json_authoring(docs,validate_native=False,pinned_r3=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-archive",type=Path)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(JsonOnlyPositiveNegativeTests)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)
    if args.json_archive:
        stats=audit_json_authoring(documents_from_json_archive(args.json_archive))
        report={"status":"PASS","source":"JSON authoring ZIP only",
                "scope":"Candidate+native Assessment schema and static references; NOT JSON compilation or scanner result",
                "counts":stats}
        print(json.dumps(report,sort_keys=True,indent=2))
        if args.report:
            args.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
