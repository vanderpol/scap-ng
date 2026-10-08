"""Strict 0.3 file.hash OVAL filehash58 mapping positive and negative fixtures."""
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from generate_capability_schema import generate
from validate_native_json_schemas import schema_store

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.3.0/capability-mappings/supported/file.hash.json"


class V03FileHashSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mapping=json.loads(MAPPING.read_text(encoding="utf-8"))
        cls.schema=generate(mapping,ROOT,schema_version="0.3.0")
        cls.registry=Registry().with_resources(
            (uri,Resource.from_contents(body))
            for uri,body in schema_store(ROOT/"schema/v0.3.0").items()
        )

    def errors(self,kind,doc):
        validator=Draft202012Validator(self.schema["$defs"][kind],
                                      registry=self.registry)
        return [str(e) for e in validator.iter_errors(doc)]

    @staticmethod
    def expected_object():
        return {
            "capability":"file.hash",
            "select":{"full_path":{"value":"/etc/passwd",
                                   "operation":"equals","datatype":"string"}},
            "collect":{"algorithm":"sha256"},
            "filesystem":"all",
        }

    def test_canonical_sha256_full_path_object_accepted(self):
        obj=self.expected_object()
        self.assertEqual([],self.errors("object",obj))

    def test_canonical_digest_state_accepted(self):
        state={
            "state_title":None,"capability":"file.hash",
            "state":{"field":"digest","value":"abcdef",
                     "operation":"equals","datatype":"string",
                     "match":"all","existence":"one_or_more"},
        }
        self.assertEqual([],self.errors("state",state))

    def test_missing_collection_algorithm_rejected(self):
        obj=self.expected_object()
        del obj["collect"]["algorithm"]
        self.assertTrue(self.errors("object",obj))

    def test_legacy_noncanonical_algorithm_rejected(self):
        obj=self.expected_object()
        obj["collect"]["algorithm"]="SHA-256"
        self.assertTrue(self.errors("object",obj))

    def test_deprecated_windows_view_rejected(self):
        obj=self.expected_object()
        obj["collect"]["windows_view"]="64_bit"
        self.assertTrue(self.errors("object",obj))


if __name__=="__main__":
    unittest.main()
