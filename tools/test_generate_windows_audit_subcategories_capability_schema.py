#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/windows.auditeventpolicysubcategories.json"


class WindowsAuditSubcategoriesCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(cls.mapping,ROOT)
        common=json.loads(
            (ROOT/"schema/v0.1.0/capability-common.schema.json").read_text(encoding="utf-8")
        )
        cls.registry=Registry().with_resource(
            common["$id"],Resource.from_contents(common)
        )

    def validate_def(self,name,value):
        jsonschema.Draft202012Validator(
            self.schema["$defs"][name],
            registry=self.registry,
        ).validate(value)

    def test_singleton_capability_has_no_object_schema(self):
        self.assertNotIn("object",self.schema["$defs"])
        self.validate_def("test",{
            "test_title":"Credential validation auditing",
            "capability":"windows.auditeventpolicysubcategories",
            "existence":"all",
            "match":"all",
            "states":["credential-validation"],
        })

    def test_test_rejects_fake_object_reference(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("test",{
                "test_title":None,
                "capability":"windows.auditeventpolicysubcategories",
                "object":"system",
                "existence":"all",
                "match":"all",
            })

    def test_supported_audit_value_is_preserved(self):
        self.validate_def("state",{
            "state_title":None,
            "capability":"windows.auditeventpolicysubcategories",
            "state":{
                "field":"credential_validation",
                "value":"AUDIT_SUCCESS_FAILURE",
                "operation":"equal",
                "datatype":"string",
                "mask":False,
                "match":"all",
                "existence":"some",
            },
        })

    def test_deprecated_kerberos_ticket_events_is_not_native(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("state",{
                "state_title":None,
                "capability":"windows.auditeventpolicysubcategories",
                "state":{
                    "field":"kerberos_ticket_events",
                    "value":"AUDIT_SUCCESS",
                    "operation":"equal",
                    "datatype":"string",
                    "mask":False,
                    "match":"all",
                    "existence":"some",
                },
            })

    def test_oval_audit_constants_not_renamed(self):
        encoded=json.dumps(self.schema)
        for value in ("AUDIT_FAILURE","AUDIT_NONE","AUDIT_SUCCESS","AUDIT_SUCCESS_FAILURE"):
            self.assertIn(value,encoded)

    def test_semantic_rules_preserved(self):
        ids={row["id"] for row in self.schema["x-semantic-validator-rules"]}
        self.assertIn("windows.auditeventpolicysubcategories.singleton_source",ids)


if __name__=="__main__":
    unittest.main()
