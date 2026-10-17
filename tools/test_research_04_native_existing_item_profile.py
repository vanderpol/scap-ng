#!/usr/bin/env python3
"""Research-only JSON Schema guard for real Items, absent fields and failures.

This is *not* a normative result schema or proof that every OVAL source can
be migrated. It validates a small representation contract before promotion.
"""
import json
from pathlib import Path
import unittest
from copy import deepcopy
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"research/assessment-simplification/english-first-04/native-existing-item.profile.schema.json"

def fixture():
    return {"collection":{"status":"complete","population_complete":True},"items":[]}

def real_item():
    return {"id":"observed-1","capability":"windows.ntuser",
            "identity":{"ntuser_dat":"C:/Users/example/NTUSER.DAT"},
            "status":"exists",
            "fields":{"requested_setting":{"status":"does_not_exist"}}}

class NativeItemProfileResearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=json.loads(SCHEMA.read_text())
        jsonschema.Draft202012Validator.check_schema(cls.schema)
        cls.validator=jsonschema.Draft202012Validator(cls.schema)

    def assert_valid(self,data):
        self.validator.validate(data)

    def assert_invalid(self,data):
        with self.assertRaises(jsonschema.ValidationError):
            self.validator.validate(data)

    def test_no_match_is_zero_items_not_phantom(self):
        self.assert_valid(fixture())

    def test_existing_hive_missing_setting_stays_real_item(self):
        data=fixture()
        data["items"]=[real_item()]
        self.assert_valid(data)

    def test_missing_root_item_disallowed(self):
        for status in ("does_not_exist","error","not_collected"):
            with self.subTest(status=status):
                data=fixture()
                item=real_item()
                item["status"]=status
                data["items"]=[item]
                self.assert_invalid(data)

    def test_root_identity_must_be_nonempty(self):
        data=fixture()
        item=real_item()
        item["identity"]={}
        data["items"]=[item]
        self.assert_invalid(data)

    def test_missing_field_must_not_have_fabricated_value(self):
        data=fixture()
        item=real_item()
        item["fields"]["requested_setting"]["value"]=1
        data["items"]=[item]
        self.assert_invalid(data)

    def test_error_must_not_be_misreported_as_absence(self):
        data=fixture()
        data["collection"]={"status":"error","population_complete":False}
        item=real_item()
        item["fields"]["requested_setting"]={"status":"not_collected"}
        data["items"]=[item]
        self.assert_valid(data)

    def test_actual_value_supported_when_observed(self):
        data=fixture()
        item=real_item()
        item["fields"]["requested_setting"]={"status":"exists","value":1}
        data["items"]=[item]
        self.assert_valid(data)

    def test_incomplete_is_not_definite_absence(self):
        data=fixture()
        data["collection"]={"status":"incomplete","population_complete":False}
        self.assert_valid(data)

    def test_absent_collection_has_no_fabricated_items(self):
        data=fixture()
        data["collection"]={"status":"does_not_exist","population_complete":True}
        self.assert_valid(data)

if __name__=="__main__":
    unittest.main()
