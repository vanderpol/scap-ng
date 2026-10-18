#!/usr/bin/env python3
"""#237 original OVAL vs converted 0.3 source lexical crosswalk regression."""
from __future__ import annotations

import copy
import sys
from pathlib import Path
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_apache_original_oval_crosswalk import crosswalk,XML,YAML
from research_b_variable_value_ops import capture,merge,values


class ApacheOriginalOvalCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.original=XML.read_bytes()
        self.converted=yaml.safe_load(YAML.read_text())

    def test_original_oval_xml_confirms_two_merge_variables_and_first_capture(self):
        report=crosswalk(self.original,self.converted)
        self.assertEqual(report["source_oval_schema"],"5.12.3")
        self.assertEqual(report["source_test_count"],5)
        self.assertEqual(report["source_variable_count"],19)
        self.assertEqual(len(report["merge_rows"]),2)
        self.assertTrue(report["merge_is_native_OVAL_5_12_3"])
        self.assertTrue(report["regex_pattern_preserved"])
        self.assertFalse(report["original_OVAL_result_parity_verified"])
        self.assertFalse(report["source_System_Characteristics_item_order_verified"])
        for row in report["merge_rows"]:
            self.assertEqual(row["attributes"],{"delimiter":" ",
                                                  "sort":"document",
                                                  "order":"ascending"})
        pattern=report["original_regex_capture_pattern"]
        self.assertEqual(capture(values(["/usr/sbin/httpd"]),pattern),
                         values(["/usr/sbin/"]))
        self.assertEqual(capture(values(["/usr/sbin/apache2"]),pattern),
                         values([""]))
        self.assertEqual(merge(values(["/b.conf","/a.conf"]),delimiter=" ",
                               sort="document",order="ascending"),
                         values(["/b.conf /a.conf"]))

    def test_altered_regex_source_can_never_pass_crosswalk(self):
        a=copy.deepcopy(self.converted)
        a["assessment"]["variables"]["apache-base-install-directories-unix-variable"][
            "expression"]["regex_capture"]["pattern"]="/(httpd|apache2)$"
        with self.assertRaisesRegex(ValueError,"regex_capture"):
            crosswalk(self.original,a)

    def test_merge_sort_delimiter_and_source_variable_are_immutable(self):
        for field,value in [("delimiter",","),("sort","lexical"),("order","descending")]:
            with self.subTest(field=field):
                a=copy.deepcopy(self.converted)
                variable=a["assessment"]["variables"][
                    "merged-list-all-loaded-config-files-variable"]["expression"]["merge"]
                variable[field]=value
                with self.assertRaisesRegex(ValueError,"merge attributes"):
                    crosswalk(self.original,a)

    def test_removing_source_test_or_variable_must_be_fatal(self):
        a=copy.deepcopy(self.converted)
        del a["assessment"]["tests"]["apache-session-cookie-module-enabled-test"]
        with self.assertRaisesRegex(ValueError,"5-Test"):
            crosswalk(self.original,a)
        a=copy.deepcopy(self.converted)
        del a["assessment"]["variables"]["apache-base-install-directories-unix-variable"]
        with self.assertRaisesRegex(ValueError,"19-source-Variable"):
            crosswalk(self.original,a)

    def test_original_oval_xml_is_pinned_to_5_12_3(self):
        altered=self.original.replace(b"<oval:schema_version>5.12.3</oval:schema_version>",
                                      b"<oval:schema_version>5.11.2</oval:schema_version>")
        self.assertNotEqual(self.original,altered)
        with self.assertRaisesRegex(ValueError,"5.12.3"):
            crosswalk(altered,self.converted)


if __name__=="__main__":
    unittest.main()
