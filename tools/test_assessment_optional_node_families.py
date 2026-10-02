#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=json.loads(
    (ROOT/"schema/v0.1.0/assessment.schema.json").read_text(encoding="utf-8")
)
VALIDATOR=jsonschema.Draft202012Validator(SCHEMA)


class AssessmentOptionalNodeFamiliesTests(unittest.TestCase):
    def test_automated_variable_only_assessment_needs_no_objects_or_states(self):
        value={
            "assessment":{
                "id":"example.variable",
                "version":1,
                "assessment_title":"Variable check",
                "mode":"automated",
                "class":"compliance",
                "purpose":"assessment",
                "specification":{
                    "id":"scap-ng.pre-alpha.assessment",
                    "version":"0.1.0",
                },
                "variables":{
                    "threshold":{
                        "kind":"constant",
                        "datatype":"integer",
                        "value":5,
                    }
                },
                "tests":{
                    "t":{
                        "test_title":"Check variable",
                        "capability":"variable.value",
                        "variable":"threshold",
                    }
                },
                "evaluate":{"test":"t"},
            }
        }
        VALIDATOR.validate(value)
        self.assertNotIn("objects",value["assessment"])
        self.assertNotIn("states",value["assessment"])

    def test_automated_assessment_still_requires_tests_and_evaluate(self):
        value={
            "assessment":{
                "id":"example.empty",
                "version":1,
                "assessment_title":None,
                "mode":"automated",
                "class":"compliance",
                "purpose":"assessment",
                "specification":{
                    "id":"scap-ng.pre-alpha.assessment",
                    "version":"0.1.0",
                },
            }
        }
        with self.assertRaises(jsonschema.ValidationError):
            VALIDATOR.validate(value)


if __name__=="__main__":
    unittest.main()
