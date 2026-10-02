#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from generate_capability_schema import generate

ROOT=Path(__file__).resolve().parents[1]
MAPPING=ROOT/"schema/v0.1.0/capability-mappings/independent.unknown.json"

class UnknownCapabilitySchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping=json.loads(MAPPING.read_text())
        cls.schema=generate(cls.mapping,ROOT)

    def validate(self,value):
        jsonschema.Draft202012Validator(self.schema["$defs"]["test"]).validate(value)

    def test_authored_test_has_no_runtime_result_or_controls(self):
        self.validate({"test_title":"unknown implementation","capability":"independent.unknown"})
        self.assertEqual(self.schema["x-fixed-result"],"unknown")
        for extra in ("result","object","states","existence","match"):
            with self.subTest(extra=extra):
                bad={"test_title":"x","capability":"independent.unknown",extra:"x"}
                with self.assertRaises(jsonschema.ValidationError):
                    self.validate(bad)

if __name__=="__main__":
    unittest.main()
