#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate


ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/file.hash.json"


class FileHashCapabilitySchemaTests(unittest.TestCase):
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

    def entity(self,value,operation="equal",datatype="string"):
        return {
            "value":value,
            "operation":operation,
            "datatype":datatype,
            "mask":False,
        }

    def test_reuses_shared_file_and_set_primitives(self):
        encoded=json.dumps(self.schema)
        self.assertIn("capability-common.schema.json#/$defs/object_entity_base",encoded)
        self.assertIn("capability-common.schema.json#/$defs/file_traversal",encoded)
        self.assertIn("capability-common.schema.json#/$defs/set_expression",encoded)

    def test_algorithm_is_collection_parameter_not_entity(self):
        obj=self.schema["$defs"]["object"]
        collect=obj["properties"]["collect"]
        self.assertEqual(
            collect["properties"]["algorithm"]["enum"],
            ["md5","sha1","sha224","sha256","sha384","sha512"],
        )
        self.assertEqual(collect["required"],["algorithm"])
        encoded=json.dumps(collect)
        self.assertNotIn('"operation"',encoded)
        self.assertNotIn('"datatype"',encoded)
        self.assertNotIn('"mask"',encoded)

    def test_valid_full_path_hash_collection(self):
        self.validate_def("object",{
            "object_title":"passwd digest",
            "capability":"file.hash",
            "select":{
                "full_path":self.entity("/etc/passwd"),
            },
            "collect":{"algorithm":"sha256"},
        })

    def test_valid_directory_hash_collection_with_traversal(self):
        self.validate_def("object",{
            "object_title":"config digests",
            "capability":"file.hash",
            "select":{
                "directory":self.entity("/etc"),
                "name":self.entity(".*\\.conf$",operation="match"),
            },
            "traversal":{
                "max_depth":1,
                "follow_links":False,
                "filesystem":"local",
            },
            "collect":{"algorithm":"sha512"},
        })

    def test_collect_block_is_required(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object",{
                "object_title":"missing collect",
                "capability":"file.hash",
                "select":{"full_path":self.entity("/etc/passwd")},
            })

    def test_hash_algorithm_is_required(self):
        with self.assertRaises(jsonschema.ValidationError):
            self.validate_def("object",{
                "object_title":"missing algorithm",
                "capability":"file.hash",
                "select":{"full_path":self.entity("/etc/passwd")},
                "collect":{},
            })

    def test_legacy_algorithm_spellings_are_not_native(self):
        for value in ("SHA-256","SHA-1",""):
            with self.subTest(value=value):
                with self.assertRaises(jsonschema.ValidationError):
                    self.validate_def("object",{
                        "object_title":None,
                        "capability":"file.hash",
                        "select":{"full_path":self.entity("/etc/passwd")},
                        "collect":{"algorithm":value},
                    })

    def test_state_uses_native_algorithm_and_digest_fields(self):
        self.validate_def("state",{
            "state_title":"expected sha256",
            "capability":"file.hash",
            "state":{
                "field":"algorithm",
                "value":"sha256",
                "operation":"equal",
                "datatype":"string",
                "mask":False,
                "match":"all",
                "existence":"some",
            },
        })
        self.validate_def("state",{
            "state_title":"expected digest",
            "capability":"file.hash",
            "state":{
                "field":"digest",
                "value":"abcdef",
                "operation":"equal",
                "datatype":"string",
                "mask":False,
                "match":"all",
                "existence":"some",
            },
        })

    def test_windows_view_is_not_native(self):
        encoded=json.dumps(self.schema)
        self.assertNotIn("windows_view",encoded)


if __name__=="__main__":
    unittest.main()
