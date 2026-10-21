#!/usr/bin/env python3
"""#237 original Windows registry Object selection remains case-insensitive."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_windows_registry_original_crosswalk import compare,XML,CONVERTED


class WindowsRegistryOriginalCrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.xml=XML.read_bytes()
        self.source=yaml.safe_load(CONVERTED.read_text())

    def test_real_windows_server_2025_registry_objects_have_source_casefold(self):
        result=compare(self.xml,self.source)
        self.assertEqual(result["source_registries"],3)
        self.assertEqual(result["converted_registries_checked"],3)
        self.assertEqual(
            {x["original_value_name_selector"]["value"] for x in result["registry_objects"]},
            {"Database log files path", "DSA Database file", "DSA Working Directory"},
        )
        self.assertFalse(result["source_registry_view_default_verified"])
        self.assertFalse(result["scanner_execution_verified"])
        for obj in result["registry_objects"]:
            self.assertEqual(obj["original_key_selector"]["operation"],
                             "case insensitive equals")
            self.assertEqual(obj["original_value_name_selector"]["operation"],
                             "case insensitive equals")
            self.assertFalse(obj["view_default_source_parity_verified"])

    def test_changing_to_case_sensitive_must_fail(self):
        a=copy.deepcopy(self.source)
        registry=next(o for o in a["assessment"]["objects"].values()
                      if o.get("capability")=="windows.registry")
        registry["select"]["key"]["operation"]="equals"
        with self.assertRaisesRegex(ValueError,"source registry selector"):
            compare(self.xml,a)

    def test_wrong_value_name_and_uninvented_view_must_fail(self):
        a=copy.deepcopy(self.source)
        registry=next(o for o in a["assessment"]["objects"].values()
                      if o.get("capability")=="windows.registry")
        registry["select"]["name"]["value"]="wrong-value"
        with self.assertRaisesRegex(ValueError,"source registry selector"):
            compare(self.xml,a)
        a=copy.deepcopy(self.source)
        registry=next(o for o in a["assessment"]["objects"].values()
                      if o.get("capability")=="windows.registry")
        registry["select"]["windows_view"]="64_bit"
        with self.assertRaisesRegex(ValueError,"keys or view"):
            compare(self.xml,a)

    def test_duplicate_converted_registry_source_object_cannot_pass(self):
        a=copy.deepcopy(self.source)
        first=next(o for o in a["assessment"]["objects"].values()
                   if o.get("capability")=="windows.registry")
        a["assessment"]["objects"]["duplicate-registry"]=copy.deepcopy(first)
        with self.assertRaisesRegex(ValueError,"uniquely mapped"):
            compare(self.xml,a)


if __name__=="__main__":
    unittest.main()
