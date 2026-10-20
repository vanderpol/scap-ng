#!/usr/bin/env python3
"""Small source-triage fixtures for all remaining 0.4.0 singleton Sets (#248)."""
import unittest
import xml.etree.ElementTree as ET

from audit_v04_remaining_singletons_oval import audit, local_set_sites


P="authoring/ms_windows_11/assessments/automated/example.json"


def doc():
    return {P: {"assessment": {
        "id":"example", "mode":"automated",
        "tests":{"check-test":{"capability":"windows.registry",
            "object":{"object_title":"Registry keys",
                "set":{"operator":"union","operands":[
                    {"object":{"object_title":"Registry keys",
                               "capability":"windows.registry",
                               "select":{"key":{"equals":"Example"}}},
                     "filters":[{"include":{"key":{"equals":"Example"}}}]}
                ]}},
            "require":{"items":"one_or_more"}}},
        "evaluate":{"test":"check-test"},
    }}}


def xml(comment, with_set=False):
    child='<set set_operator="UNION"><object_reference>oval:obj:other</object_reference></set>' if with_set else '<filter action="include">oval:state:1</filter>'
    return ET.fromstring(f'<objects><registry_object id="oval:obj:1" comment="{comment}">{child}</registry_object></objects>')[0]


def pins():
    return {"ms_windows_11":"pinned-hash"}


class RemainingSingletonTests(unittest.TestCase):
    def test_source_direct_filter_without_set_is_triage_only(self):
        r=audit(doc(),{"ms_windows_11":[xml("Registry keys")]},pins())
        self.assertEqual(r["singleton_set_occurrences"],1)
        self.assertEqual(r["classifications"],{"UNIQUE_SOURCE_DIRECT_FILTER_NO_SET":1})
        self.assertFalse(r["rewrites_authorized"])
        self.assertFalse(r["scanner_semantics_verified"])

    def test_source_real_set_is_explicitly_preserved(self):
        r=audit(doc(),{"ms_windows_11":[xml("Registry keys",True)]},pins())
        self.assertEqual(r["classifications"],{"SOURCE_CONTAINS_SET":1})

    def test_ambiguous_source_titles_not_guessed(self):
        r=audit(doc(),{"ms_windows_11":[xml("Registry keys"),xml("Registry keys",True)]},pins())
        self.assertEqual(r["classifications"],{"SAME_ID_DIVERGENT_SOURCE_XML":1})
        self.assertEqual(len(r["items"][0]["source_matches"]),2)

    def test_shared_duplicate_source_ids_are_not_false_ambiguity(self):
        d=doc()
        src=xml("Registry keys",True)
        sources={"ms_windows_11":[src,xml("Registry keys",True)]}
        r=audit(d,sources,pins())
        self.assertEqual(r["classifications"],{"REPEATED_IDENTICAL_SOURCE_OBJECT":1})
        self.assertEqual(len(r["items"][0]["source_matches"]),2)

    def test_distinct_source_ids_remain_ambiguous(self):
        one=xml("Registry keys",False)
        two=xml("Registry keys",True)
        two.set("id","oval:obj:another")
        r=audit(doc(),{"ms_windows_11":[one,two]},pins())
        self.assertEqual(r["classifications"],{"MULTIPLE_DISTINCT_SOURCE_OBJECTS":1})

    def test_no_title_is_not_assumed_oval_identity(self):
        d=doc()
        ob=d[P]["assessment"]["tests"]["check-test"]["object"]
        ob.pop("object_title")
        ob["set"]["operands"][0]["object"]["object_title"]=None
        r=audit(d,{"ms_windows_11":[xml("Registry keys")]},pins())
        self.assertEqual(r["classifications"],{"NO_SOURCE_TITLE":1})

    def test_missing_object_title_can_be_traced_to_original_test_ref(self):
        d=doc()
        a=d[P]["assessment"]
        test=a["tests"]["check-test"]
        test["test_title"]="Original registry Test"
        outer=test["object"]
        outer.pop("object_title")
        outer["set"]["operands"][0]["object"]["object_title"]=None
        original_test=ET.fromstring(
            '<registry_test id="oval:test:4" comment="Original registry Test">'
            '<object object_ref="oval:obj:1"/></registry_test>')
        source={"objects":[xml("Registry keys",True)],"tests":[original_test]}
        result=audit(d,{"ms_windows_11":source},pins())
        row=result["items"][0]
        self.assertEqual(row["classification"],"NO_SOURCE_TITLE")
        self.assertEqual(row["source_test_linkage"],"UNIQUE_OVAL_TEST_OBJECT_REF")
        self.assertEqual(row["source_test_object_refs"],["oval:obj:1"])
        self.assertEqual(row["source_test_linked_object_status"],
                         "TEST_REFERENCES_ORIGINAL_SET")

    def test_source_test_object_ref_with_no_set_exposes_remaining_wrappers(self):
        d=doc()
        d[P]["assessment"]["tests"]["check-test"]["test_title"]="Source registry check"
        src=xml("Registry keys",False)
        test=ET.fromstring('<registry_test id="oval:test:4" comment="Source registry check">'
                           '<object object_ref="oval:obj:1"/></registry_test>')
        r=audit(d,{"ms_windows_11":{"objects":[src],"tests":[test]}},pins())
        self.assertEqual(r["source_test_linked_object_shapes"],
                         {"TEST_REFERENCES_ORIGINAL_DIRECT_FILTER":1})

    def test_mixed_test_and_variable_sites_preserve_provenance_path(self):
        d=doc()
        a=d[P]["assessment"]
        a["variables"]={"value-variable":{"expression":{"values":{
            "object":a["tests"]["check-test"]["object"],"field":"value"}}}}
        rows=local_set_sites(d)
        self.assertEqual(len(rows),2)
        self.assertEqual({r["test"] for r in rows},{"check-test",None})
        self.assertTrue(any("variables" in r["site"] for r in rows))


if __name__=="__main__":
    unittest.main()
