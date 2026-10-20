#!/usr/bin/env python3
"""Exact-shape OVAL provenance classification fixtures (no semantic rewriting)."""
import unittest
from audit_v04_filtered_union_oval_provenance import source_objects, inspect_candidate

XML=b'''<oval_definitions xmlns:i="http://oval.mitre.org/XMLSchema/oval-definitions-5#independent" xmlns:o="http://oval.mitre.org/XMLSchema/oval-definitions-5">
<objects>
<i:shellcommand_object id="oval:obj:1" comment="Bluetooth command"><i:command>foo</i:command>
<o:filter action="include">oval:ste:1</o:filter></i:shellcommand_object>
<i:shellcommand_object id="oval:obj:2" comment="Real Set"><o:set set_operator="UNION">
<o:object_reference>oval:obj:1</o:object_reference></o:set></i:shellcommand_object>
</objects></oval_definitions>'''

def candidate(title,actions):
    return {"path":"authoring/ms_windows_11/assessments/a.json",
            "assessment":"bluetooth","test_id":"test","capability":"independent.shellcommand",
            "outer_title":title,"filters":actions}

class SourceProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.objects=source_objects(XML)
    def test_real_direct_filter(self):
        actual=inspect_candidate(candidate("Bluetooth command",["include"]),self.objects)
        self.assertEqual(actual["status"],"UNIQUE_DIRECT_OVAL_FILTER_NO_SET")
        self.assertEqual(actual["source_candidates"][0]["id"],"oval:obj:1")
    def test_real_set_does_not_get_flattened(self):
        result=inspect_candidate(candidate("Real Set",[]),self.objects)
        self.assertEqual(result["status"],"SOURCE_REVIEW_REQUIRED")
        self.assertTrue(result["source_candidates"][0]["source_has_set"])
    def test_mismatched_filter_action_and_unknown_title_fail(self):
        for item in (candidate("Bluetooth command",["exclude"]),candidate("Missing",["include"])):
            self.assertEqual(inspect_candidate(item,self.objects)["status"],"SOURCE_REVIEW_REQUIRED")

if __name__=="__main__":
    unittest.main()
