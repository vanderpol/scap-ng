#!/usr/bin/env python3
import json
from pathlib import Path
import unittest

import jsonschema
from referencing import Registry, Resource

from generate_capability_schema import generate
from validate_generated_capability_semantics import validate_assessment_capability_semantics


ROOT=Path(__file__).resolve().parents[1]
V03=ROOT/"schema/v0.3.0"
V02=ROOT/"schema/v0.2.0"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ForeachV03Integration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_mapping=load(V03/"capability-mappings/supported/unix.file.json")
        cls.file_schema=generate(cls.file_mapping,ROOT)
        common=load(V03/"capability-common.schema.json")
        collected=load(V03/"collected-item.schema.json")
        result_types=load(V03/"result-types.schema.json")
        cls.registry=(Registry()
            .with_resource(common["$id"],Resource.from_contents(common))
            .with_resource(collected["$id"],Resource.from_contents(collected))
            .with_resource(result_types["$id"],Resource.from_contents(result_types)))

    def validate_file_object(self,value):
        jsonschema.Draft202012Validator(
            self.file_schema["$defs"]["object"],
            registry=self.registry,
        ).validate(value)

    def base_assessment(self):
        return {
            "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.3.0"},
            "shared_objects":{
                "users-object":{
                    "object_title":"selected users",
                    "capability":"unix.password",
                    "select":{
                        "username":{
                            "value":".+",
                            "operation":"pattern_match",
                            "datatype":"string",
                        }
                    },
                },
                "files-object":{
                    "object_title":"files in selected homes",
                    "capability":"unix.file",
                    "for_each":{"item":"user","in":"users-object"},
                    "select":{
                        "directory":{"from":"user.home_dir"},
                        "name":{
                            "value":"^\\.[^\\s\\.]+",
                            "operation":"pattern_match",
                            "datatype":"string",
                        },
                    },
                    "filesystem":"all",
                },
            },
            "states":{},
            "variables":{},
            "tests":{
                "file-test":{
                    "capability":"unix.file",
                    "object":"files-object",
                    "states":[],
                }
            },
        }

    def test_generated_03_schema_accepts_simple_binding(self):
        self.validate_file_object(self.base_assessment()["shared_objects"]["files"])

    def test_generated_02_schema_rejects_foreach(self):
        mapping=load(V02/"capability-mappings/supported/unix.file.json")
        schema=generate(mapping,ROOT)
        common=load(V02/"capability-common.schema.json")
        collected=load(V02/"collected-item.schema.json")
        result_types=load(V02/"result-types.schema.json")
        registry=(Registry()
            .with_resource(common["$id"],Resource.from_contents(common))
            .with_resource(collected["$id"],Resource.from_contents(collected))
            .with_resource(result_types["$id"],Resource.from_contents(result_types)))
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.Draft202012Validator(
                schema["$defs"]["object"],registry=registry
            ).validate(self.base_assessment()["shared_objects"]["files"])

    def test_semantics_accept_home_dir_to_directory(self):
        rows=validate_assessment_capability_semantics(self.base_assessment())
        self.assertFalse([r for r in rows if str(r.get("code","")).startswith("foreach.")],rows)

    def test_semantics_reject_wrong_alias(self):
        doc=self.base_assessment()
        doc["shared_objects"]["files"]["select"]["directory"]["from"]="account.home_dir"
        codes={r["code"] for r in validate_assessment_capability_semantics(doc)}
        self.assertIn("foreach.binding_alias",codes)

    def test_semantics_reject_incompatible_datatype(self):
        doc=self.base_assessment()
        doc["shared_objects"]["files"]["select"]["directory"]["from"]="user.last_login"
        codes={r["code"] for r in validate_assessment_capability_semantics(doc)}
        self.assertIn("foreach.datatype_compatibility",codes)

    def test_semantics_reject_unknown_source(self):
        doc=self.base_assessment()
        doc["shared_objects"]["files"]["for_each"]["in"]="missing-users-object"
        codes={r["code"] for r in validate_assessment_capability_semantics(doc)}
        self.assertIn("foreach.source_missing",codes)

    def test_semantics_reject_helper_target(self):
        doc=self.base_assessment()
        doc["tests"]={}
        codes={r["code"] for r in validate_assessment_capability_semantics(doc)}
        self.assertIn("foreach.target_not_consumed",codes)

    def test_semantics_accept_correlated_nested_chain(self):
        doc=self.base_assessment()
        doc["shared_objects"]["directories-object"]={
            "object_title":"selected directories",
            "capability":"unix.file",
            "for_each":{"item":"file","in":"files-object"},
            "select":{
                "full_path":{"from":"file.full_path"},
            },
        }
        doc["tests"]["directory-test"]={
            "capability":"unix.file",
            "object":"directories-object",
            "states":[],
        }
        rows=validate_assessment_capability_semantics(doc)
        self.assertFalse(
            [r for r in rows if str(r.get("code","")).startswith("foreach.")],
            rows,
        )

    def test_semantics_reject_foreach_cycle(self):
        doc=self.base_assessment()
        doc["shared_objects"]["users-object"]["for_each"]={
            "item":"loop",
            "in":"files-object",
        }
        doc["shared_objects"]["users-object"]["select"]["username"]={
            "from":"loop.name",
        }
        codes={r["code"] for r in validate_assessment_capability_semantics(doc)}
        self.assertIn("foreach.dependency_cycle",codes)

    def test_semantics_reject_nested_alias_shadow(self):
        doc=self.base_assessment()
        doc["shared_objects"]["directories-object"]={
            "object_title":"selected directories",
            "capability":"unix.file",
            "for_each":{"item":"user","in":"files-object"},
            "select":{
                "full_path":{"from":"user.full_path"},
            },
        }
        doc["tests"]["directory-test"]={
            "capability":"unix.file",
            "object":"directories-object",
            "states":[],
        }
        codes={r["code"] for r in validate_assessment_capability_semantics(doc)}
        self.assertIn("foreach.alias_shadow",codes)

    def test_semantics_reject_from_without_foreach(self):
        doc=self.base_assessment()
        del doc["shared_objects"]["files"]["for_each"]
        codes={r["code"] for r in validate_assessment_capability_semantics(doc)}
        self.assertIn("foreach.from_without_for_each",codes)


if __name__=="__main__":
    unittest.main()
