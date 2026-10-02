#!/usr/bin/env python3
import copy
import json
import unittest
from pathlib import Path

import jsonschema

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads((ROOT/"schema/v0.1.0/package-manifest.schema.json").read_text(encoding="utf-8"))
VALIDATOR=jsonschema.Draft202012Validator(SCHEMA)

BASE={
    "format":"scap-ng-package-manifest",
    "format_version":"0.0.3-experimental",
    "benchmark_id":"example",
    "benchmark_version":{"value":"1"},
    "entrypoint":"example",
    "objects":{
        "example":{
            "type":"benchmark",
            "version":{"value":"1"},
            "path":"o/b.json",
            "sha256":"0"*64,
            "size":2,
        }
    },
    "integrity":{"algorithm":"sha-256","unexpected_members":"reject"},
    "build_provenance":{"generated_fresh_for_this_run":True},
    "signature":{"format":None,"path":None,"certificate_path":None,"trust":None},
}


class PackageManifestSchemaTests(unittest.TestCase):
    def test_current_manifest_shape_is_valid(self):
        VALIDATOR.validate(BASE)

    def test_runtime_object_record_rejects_authoring_source_path(self):
        value=copy.deepcopy(BASE)
        value["objects"]["example"]["source"]="authoring/example/benchmark.yaml"
        with self.assertRaises(jsonschema.ValidationError):
            VALIDATOR.validate(value)

    def test_unsafe_member_path_is_rejected(self):
        value=copy.deepcopy(BASE)
        value["objects"]["example"]["path"]="../benchmark.json"
        with self.assertRaises(jsonschema.ValidationError):
            VALIDATOR.validate(value)


if __name__=="__main__":
    unittest.main()
