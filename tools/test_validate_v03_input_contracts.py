import copy
import unittest
from validate_v03_input_contracts import validate_input_contracts


def fixtures():
    benchmark={"id":"bench","parameters":[{
        "id":"approved_fs","datatype":"string","cardinality":"one_or_more",
        "resolution":"organization","required":True}]}
    assessment={"id":"home-check","inputs":{"approved-types-input":{
        "datatype":"string","cardinality":"one_or_more","required":True}},
        "states":{},"tests":{"home-type-test":{"states":[{
            "capability":"linux.partition",
            "state":{"field":"fs_type","value":{"input":"approved-types-input"},
                     "operation":"equals","datatype":"string","value_match":"one_or_more",
                     "match":"all","existence":"one_or_more"}
        }]}}}
    rule={"assessment_choices":{"automated":{"assessment":"home-check",
        "inputs":{"approved-types-input":{"parameter":"approved_fs"}}}},
        "organizational_input_requirements":{"automated":[{
            "input":"approved_fs","required":True,"uses":[{
                "test":"home-type-test","state":"home-type-test.states[0]",
                "state_slot":"fs_type"}]}]}}
    return benchmark,{"R1":rule},{"home-check":assessment}


class InputContractTests(unittest.TestCase):
    def test_complete_binding(self):
        validate_input_contracts(*fixtures())

    def test_all_missing_and_misaligned_paths_are_blocked(self):
        edits=[
            lambda b,r,a:r["R1"]["assessment_choices"]["automated"]["inputs"].clear(),
            lambda b,r,a:r["R1"]["assessment_choices"]["automated"]["inputs"].update(
                {"approved-types-input":{"parameter":"missing"}}),
            lambda b,r,a:b["parameters"][0].update({"datatype":"integer"}),
            lambda b,r,a:b["parameters"][0].update({"cardinality":"one"}),
            lambda b,r,a:a["home-check"]["inputs"].clear(),
            lambda b,r,a:r["R1"]["organizational_input_requirements"].clear(),
            lambda b,r,a:r["R1"]["organizational_input_requirements"]["automated"][0]["uses"][0].update(
                {"state_slot":"mount_point"}),
            lambda b,r,a:a["home-check"]["tests"]["home-type-test"]["states"][0]["state"]["value"].update(
                {"input":"unknown-input"}),
        ]
        for n,edit in enumerate(edits):
            data=copy.deepcopy(fixtures())
            edit(*data)
            with self.subTest(case=n),self.assertRaises(ValueError):
                validate_input_contracts(*data)

    def test_multiple_consumers_require_multiple_discovery_locations(self):
        benchmark,rules,assessments=fixtures()
        test=assessments["home-check"]["tests"]["home-type-test"]
        other=copy.deepcopy(test["states"][0])
        other["state"]["field"]="mount_options"
        test["states"].append(other)
        with self.assertRaisesRegex(ValueError,"discovery locations"):
            validate_input_contracts(benchmark,rules,assessments)
        rules["R1"]["organizational_input_requirements"]["automated"][0]["uses"].append({
            "test":"home-type-test","state":"home-type-test.states[1]",
            "state_slot":"mount_options"})
        validate_input_contracts(benchmark,rules,assessments)

    def test_publisher_parameter_does_not_claim_org_discoverability(self):
        benchmark,rules,assessments=fixtures()
        benchmark["parameters"][0]["resolution"]="publisher"
        rules["R1"]["organizational_input_requirements"]={}
        validate_input_contracts(benchmark,rules,assessments)


if __name__=="__main__":
    unittest.main()
