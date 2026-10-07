#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

from generate_capability_schema import generate
from scap_upconvert_v003.native_capability_mapping import apply_capability_mapping

ROOT=Path(__file__).resolve().parents[1]
V03=ROOT/"schema"/"v0.3.0"
MAPPINGS=V03/"capability-mappings"/"supported"


class V03VocabularyContractTests(unittest.TestCase):
    def mapping(self,name):
        return json.loads((MAPPINGS/name).read_text(encoding="utf-8"))

    def test_common_schema_uses_canonical_03_vocabulary(self):
        common=json.loads((V03/"capability-common.schema.json").read_text(encoding="utf-8"))
        defs=common["$defs"]
        self.assertEqual(
            defs["match_quantifier"]["enum"],
            ["all","one_or_more","one","none"],
        )
        self.assertEqual(
            defs["existence_requirement"]["enum"],
            ["all","one_or_more","none","one","optional"],
        )
        self.assertEqual(
            defs["filesystem_scope"]["enum"],
            ["all","local","same"],
        )
        self.assertEqual(
            defs["comparison_operation"]["enum"],
            [
                "equals","not_equal",
                "case_insensitive_equals","case_insensitive_not_equal",
                "greater_than","greater_than_or_equal",
                "less_than","less_than_or_equal",
                "bitwise_and","bitwise_or","pattern_match",
                "subset_of","superset_of",
            ],
        )

    def test_generated_03_test_schema_uses_existence_and_match(self):
        mapping=self.mapping("unix.file.json")
        generated=generate(mapping,ROOT,schema_version="0.3.0")
        test=generated["$defs"]["test"]
        self.assertIn("existence",test["required"])
        self.assertIn("match",test["required"])
        self.assertNotIn("check_existence",test["required"])
        self.assertNotIn("check",test["required"])
        self.assertEqual(
            test["properties"]["existence"]["$ref"],
            "https://scap-ng.dev/schema/v0.3.0/capability-common.schema.json#/$defs/existence_requirement",
        )
        self.assertEqual(
            test["properties"]["match"]["$ref"],
            "https://scap-ng.dev/schema/v0.3.0/capability-common.schema.json#/$defs/match_quantifier",
        )

    def test_03_converter_emits_canonical_fields_and_values(self):
        mapping=self.mapping("windows.wmi.query.json")
        doc={"assessment":{
            "objects":{"query-object":{
                "object_title":"OS query",
                "capability":"windows.wmi57",
                "select":{
                    "namespace":{"value":"root\\cimv2","operation":"equals","datatype":"string"},
                    "wql":{"value":"SELECT Version FROM Win32_OperatingSystem","operation":"equals","datatype":"string"},
                },
            }},
            "states":{"version-state":{
                "state_title":"version",
                "capability":"windows.wmi57",
                "state":{
                    "field":"result",
                    "value":{"record":[{
                        "name":"version",
                        "value":"10.0",
                        "operation":"greater than or equal",
                        "datatype":"version",
                        "entity_check":"at least one",
                    }]},
                    "operation":"equals",
                    "datatype":"record",
                    "entity_check":"all",
                    "entity_existence":"at_least_one_exists",
                },
            }},
            "tests":{"version-test":{
                "test_title":"version",
                "capability":"windows.wmi57",
                "object":"query-object",
                "check_existence":"at_least_one_exists",
                "check":"at least one",
                "states":["version-state"],
            }},
        }}
        out=apply_capability_mapping(doc,mapping)
        test=out["assessment"]["tests"]["version-test"]
        self.assertEqual(test["existence"],"one_or_more")
        self.assertEqual(test["match"],"one_or_more")
        self.assertNotIn("check_existence",test)
        self.assertNotIn("check",test)
        record=out["assessment"]["states"]["version-state"]["state"]["record"]
        self.assertEqual(record["existence"],"one_or_more")
        self.assertEqual(record["fields"]["version"]["match"],"one_or_more")
        self.assertEqual(
            record["fields"]["version"]["operation"],
            "greater_than_or_equal",
        )

    def test_03_file_scope_restores_all(self):
        mapping=self.mapping("independent.textfilecontent54.json")
        doc={"assessment":{
            "objects":{"config-object":{
                "object_title":"config",
                "capability":"independent.textfilecontent54",
                "select":{
                    "filepath":{"value":"/etc/example","operation":"equals","datatype":"string"},
                    "pattern":{"value":"x","operation":"pattern match","datatype":"string"},
                    "instance":{"value":"1","operation":"equals","datatype":"int"},
                },
                "behaviors":{"recurse_file_system":"all"},
            }},
            "states":{},
            "tests":{},
        }}
        out=apply_capability_mapping(doc,mapping)
        obj=out["assessment"]["objects"]["config-object"]
        self.assertEqual(obj["filesystem"],"all")
        self.assertEqual(obj["select"]["full_path"]["operation"],"equals")
        self.assertEqual(obj["select"]["pattern"]["operation"],"pattern_match")


if __name__=="__main__":
    unittest.main()
