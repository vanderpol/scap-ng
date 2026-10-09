"""End-to-end native 0.3 Rule->Assessment logical-ID compilation and frozen Input binding."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import yaml

from scap_ng_content_compiler import compile_benchmark
from resolve_v03_organizational_input import resolve_input_sets, bind_assessment_inputs


def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(yaml.safe_dump(obj,sort_keys=False),encoding="utf-8")


class V03DirectInputCompilationTests(unittest.TestCase):
    def create(self,root):
        b=root/"sample"
        benchmark={"benchmark":{"id":"sample.benchmark","version":{"value":"V1"},
            "rules":["SV-1"],"profiles":[],
            "parameters":[{"id":"approved_types","datatype":"string",
                 "cardinality":"one_or_more","required":True,
                 "resolution":"organization"}]}}
        assessment={"assessment":{
            "id":"home-approved","version":1,
            "assessment_title":"Home filesystem type is organization approved",
            "mode":"automated","class":"compliance","purpose":"assessment",
            "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.3.0"},
            "inputs":{"approved-types-input":{
                "datatype":"string","cardinality":"one_or_more","required":True}},
            "tests":{"home-type-test":{
                "test_title":"Home filesystem type",
                "capability":"linux.partition",
                "object":{"capability":"linux.partition","select":{
                    "mount_point":{"value":"/home","operation":"equals","datatype":"string"}}},
                "states":[{"field":"fs_type","value":{"input":"approved-types-input"},
                    "operation":"equals","datatype":"string",
                    "value_match":"one_or_more","match":"all","existence":"one_or_more"}],
                "reported_elements":"all","existence":"one_or_more","match":"all"}},
            "evaluate":{"test":"home-type-test"},
        }}
        rule={"rule":{
            "id":"SV-1","assessment_choices":{"automated":{
                "assessment":"home-approved",
                "inputs":{"approved-types-input":{"parameter":"approved_types"}}}},
            "default_assessment_choice":"automated",
            "organizational_input_requirements":{"automated":[{
                "input":"approved_types","required":True,
                "uses":[{"test":"home-type-test","state":"home-type-test.states[0]",
                         "state_slot":"fs_type"}]}]},
        }}
        write(b/"benchmark.yaml",benchmark)
        write(b/"rules/SV-1.rule.yaml",rule)
        write(b/"assessments/home.yaml",assessment)
        return b,benchmark,rule,assessment

    def test_actual_compile_links_logical_ids_and_frozen_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            b,benchmark,rule,assessment=self.create(root)
            _,members,index=compile_benchmark(root,b)
            self.assertIn("home-approved",index)
            out=json.loads(members[index["SV-1"]["path"]])["rule"]
            self.assertEqual(
                out["assessment_choices"]["automated"]["assessment"],"home-approved")
            frozen=resolve_input_sets(benchmark["benchmark"],[{
                "organizational_input":{"id":"site","version":1,
                    "benchmark":{"id":"sample.benchmark","version":"V1"},
                    "values":{"approved_types":["ext4","xfs"]},
                    "provenance":{"authorization_status":"approved"}}}],
                run_start="2026-10-08T15:00:00-04:00")
            projected=bind_assessment_inputs(out,"automated",assessment["assessment"],frozen)
            self.assertEqual(projected["outcome"],"ready")
            self.assertEqual(projected["bindings"]["approved-types-input"],["ext4","xfs"])

    def test_compiler_catches_unbound_input_and_wrong_discovery_field(self):
        for variant in ("missing_binding","wrong_discovery","type_mismatch"):
            with tempfile.TemporaryDirectory() as temp:
                root=Path(temp)
                b,benchmark,rule,assessment=self.create(root)
                if variant=="missing_binding":
                    rule["rule"]["assessment_choices"]["automated"].pop("inputs")
                elif variant=="wrong_discovery":
                    req=rule["rule"]["organizational_input_requirements"]["automated"][0]
                    req["uses"][0]["state_slot"]="mount_options"
                else:
                    benchmark["benchmark"]["parameters"][0]["datatype"]="integer"
                write(b/"rules/SV-1.rule.yaml",rule)
                write(b/"benchmark.yaml",benchmark)
                with self.subTest(variant=variant),self.assertRaises(ValueError):
                    compile_benchmark(root,b)


if __name__=="__main__":
    unittest.main()
