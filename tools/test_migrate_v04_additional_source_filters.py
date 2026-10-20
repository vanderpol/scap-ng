#!/usr/bin/env python3
"""0.4.0 original-OVAL Test-Object Filter migration positive/negative fixtures."""
from copy import deepcopy
import unittest

from migrate_v04_additional_source_filters import (
    STATUS, index_source_proof, migrate, recover_migration,
)

PATH = "authoring/ms_windows_11/assessments/automated/example.json"
TEST = "bluetooth-installation-test"
CAP = "independent.shellcommand"


def doc(filters=None):
    if filters is None:
        filters = [{"include":{"stdout_line":{"case_insensitive_equals":"Bluetooth"}}}]
    obj = {"object_title":"Bluetooth devices",
           "set":{"operator":"union","operands":[{
               "object":{"object_title":"Bluetooth devices","capability":CAP,
                         "collect":{"command":"Get-PnpDevice -class bluetooth"}},
               "filters":deepcopy(filters)}]}}
    return {"assessment":{"id":"bluetooth-assessment", "mode":"automated",
            "tests":{TEST:{"test_title":"Original Bluetooth installed","capability":CAP,
                           "object":obj,"require":{"items":"one_or_more"}}},
            "evaluate":{"test":TEST}}}


def row():
    return {"path":PATH,"assessment":"bluetooth-assessment","test":TEST,
            "test_title":"Original Bluetooth installed","test_capability":CAP,
            "site":["assessment","tests",TEST,"object","set"],
            "operator":"union","filter_actions":["include"],
            "leaf_capability":CAP,"source_test_linkage":"UNIQUE_OVAL_TEST_OBJECT_REF",
            "source_test_object_refs":["oval:source:obj:101"],
            "source_test_linked_object_status":STATUS,
            "source_test_linked_object_candidates":[{
                "source_id":"oval:source:obj:101",
                "source_has_set":False,"source_direct_filter_actions":["include"],
                "source_structure_sha256":"fa6e86bc",
            }]}


def report():
    source=row()
    return {"status":"SOURCE_COMMENT_TRIAGE_NOT_SOURCE_IDENTITY_OR_SCANNER_PARITY",
            "rewrites_authorized":False,"scanner_semantics_verified":False,
            "singleton_set_occurrences":50,
            "original_oval_source_zip_sha256":{str(i):str(i) for i in range(6)},
            "items":[source]}


class OriginalOVALFilterMigrationTests(unittest.TestCase):
    def test_verified_test_local_leaf_roundtrips_without_losing_filter(self):
        src=doc()
        indexed=index_source_proof(report())
        out,counts=migrate(src,PATH,indexed)
        self.assertEqual(counts["source_linked_additional_direct_filters"],1)
        obj=out["assessment"]["tests"][TEST]["object"]
        self.assertNotIn("set",obj)
        self.assertNotIn("capability",obj)
        self.assertEqual(obj["filters"],
                         src["assessment"]["tests"][TEST]["object"]["set"]["operands"][0]["filters"])
        self.assertEqual(src,doc())
        self.assertTrue(recover_migration(out,src,PATH,indexed))

    def test_include_exclude_sequence_and_negative_mutations(self):
        filters=[{"include":{"a":{"equals":1}}},{"exclude":{"b":{"equals":2}}}]
        src=doc(filters)
        evidence=report()
        evidence["items"][0]["filter_actions"]=["include","exclude"]
        evidence["items"][0]["source_test_linked_object_candidates"][0][
            "source_direct_filter_actions"]=["include","exclude"]
        proof=index_source_proof(evidence)
        candidate,_=migrate(src,PATH,proof)
        self.assertEqual(len(candidate["assessment"]["tests"][TEST]["object"]["filters"]),2)
        candidate["assessment"]["tests"][TEST]["object"]["filters"].reverse()
        with self.assertRaisesRegex(ValueError,"inverse mismatched"):
            recover_migration(candidate,src,PATH,proof)

    def test_genuine_original_set_never_auto_converted(self):
        evidence=report()
        evidence["items"][0]["source_test_linked_object_status"]="TEST_REFERENCES_ORIGINAL_SET"
        evidence["items"][0]["source_test_linked_object_candidates"][0]["source_has_set"]=True
        out,counts=migrate(doc(),PATH,index_source_proof(evidence))
        self.assertEqual(out,doc())
        self.assertEqual(counts,{})

    def test_title_capability_set_and_ambiguous_source_fail_closed(self):
        proof=index_source_proof(report())
        for mutate in (
            lambda d: d["assessment"]["tests"][TEST]["object"].update(object_title="changed"),
            lambda d: d["assessment"]["tests"][TEST]["object"]["set"].update(operator="difference"),
            lambda d: d["assessment"]["tests"][TEST]["object"]["set"]["operands"][0]["object"].update(capability="windows.registry"),
            lambda d: d["assessment"]["tests"][TEST]["object"]["set"]["operands"].append(
                deepcopy(d["assessment"]["tests"][TEST]["object"]["set"]["operands"][0])),
        ):
            d=doc();mutate(d)
            with self.subTest(d=d), self.assertRaises(ValueError):
                migrate(d,PATH,proof)
        for mutate in (
            lambda e: e["items"][0]["source_test_object_refs"].append("different"),
            lambda e: e["items"][0]["source_test_linked_object_candidates"][0].update(source_has_set=True),
            lambda e: e["items"][0]["source_test_linked_object_candidates"][0].update(source_direct_filter_actions=["exclude"]),
            lambda e: e["original_oval_source_zip_sha256"].pop("0"),
        ):
            e=report();mutate(e)
            with self.subTest(e=e),self.assertRaises(ValueError):
                index_source_proof(e)

    def test_variable_shared_object_location_cannot_be_authorized(self):
        evidence=report()
        evidence["items"][0]["site"]=[
            "assessment","variables","value-variable","expression","object","set"]
        with self.assertRaisesRegex(ValueError,"Test-local"):
            index_source_proof(evidence)

    def test_pinned_original_corpus_must_contain_all_50(self):
        with self.assertRaisesRegex(ValueError,"baseline changed"):
            index_source_proof(report(), assert_six=True)


if __name__=="__main__":
    unittest.main()
