#!/usr/bin/env python3
"""Refs #245: source-backed observation identity and adversarial sharing boundaries."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from research_c_shared_observations import index_shared_observations

SOURCE = Path(__file__).resolve().parents[1] / (
    "research/requirements-first-language/contract-candidate/corpus/"
    "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml"
)

def simple():
    return {"id":"synthetic-observation",
            "tests":{
                "a":{"object":{"capability":"independent.shellcommand",
                    "collect":{"shell":"bash","command":"echo alpha","pattern":"a"},
                    "object_title":"first description"}},
                "b":{"object":{"capability":"independent.shellcommand",
                    "collect":{"shell":"bash","command":"echo alpha","pattern":"a"},
                    "object_title":"other description"}}}}

class SharedObservationGate(unittest.TestCase):
    def test_real_apache_graph_reuse_is_measured_not_guessed(self):
        original = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]
        before = deepcopy(original)
        result = index_shared_observations(original)
        self.assertEqual(original, before)
        self.assertEqual(result["test_count"],5)
        self.assertEqual(result["variable_count"],19)
        self.assertEqual(result["acquisition_site_count"],10)
        self.assertEqual(result["distinct_acquisition_contracts"],10)
        self.assertEqual(len(result["shared_object_references"]),2)
        self.assertEqual(len(result["multi_consumer_variables"]),6)
        self.assertFalse(result["source_runtime_parity_verified"])
        self.assertFalse(result["scanner_executed"])
        self.assertFalse(result["can_replace_distinct_commands_with_one_observation"])

    def test_same_contract_different_titles_share_one_observation_identity(self):
        result = index_shared_observations(simple())
        self.assertEqual(result["acquisition_site_count"],2)
        self.assertEqual(result["distinct_acquisition_contracts"],1)
        self.assertEqual(len(result["acquisitions"][0]["source_sites"]),2)
        self.assertFalse(result["can_assume_one_runtime_collection_per_contract"])

    def test_distinct_filters_and_command_parameters_never_collapse(self):
        initial=simple()
        for change in (
            lambda obj:obj["collect"].update(pattern="b"),
            lambda obj:obj["collect"].update(command="echo beta"),
            lambda obj:obj["collect"].update(shell="powershell"),
            lambda obj:obj.update(filters=[{"exclude":{"state":"example"}}]),
            lambda obj:obj.update(for_each={"item":"parent","in":"files"}),
            lambda obj:obj["collect"].update(error_if_exit_status_not_0=True),
            lambda obj:obj["collect"].update(command={"variable":"dynamic-cmd"}),
        ):
            doc=deepcopy(initial)
            obj=doc["tests"]["b"]["object"]
            change(obj)
            if isinstance(obj["collect"]["command"],dict):
                doc["variables"]={"dynamic-cmd":{"datatype":"string","expression":{"literal":"echo beta"}}}
            with self.subTest(changed=obj):
                res=index_shared_observations(doc)
                self.assertEqual(res["distinct_acquisition_contracts"],2)

    def test_unknown_shared_object_and_variables_fail_closed(self):
        doc=simple()
        doc["tests"]["a"]["object"]="unavailable-original-object"
        with self.assertRaisesRegex(ValueError,"unresolved shared Object"):
            index_shared_observations(doc)
        doc=simple()
        doc["tests"]["a"]["object"]["collect"]["command"]={"variable":"unknown"}
        with self.assertRaisesRegex(ValueError,"unresolved source Variable"):
            index_shared_observations(doc)

    def test_shared_source_reference_preserves_use_sites(self):
        doc={"id":"shared-case",
             "shared_objects":{"shared":{"capability":"independent.shellcommand",
                                        "collect":{"command":"echo one","shell":"bash"}}},
             "variables":{"v1":{"expression":{"values":{"field":"stdout_line","object":"shared"}}},
                          "v2":{"expression":{"values":{"field":"stdout_line","object":"shared"}}}},
             "tests":{}}
        res=index_shared_observations(doc)
        self.assertEqual(len(res["shared_object_references"]),2)
        self.assertEqual(res["distinct_acquisition_contracts"],1)
        self.assertEqual(res["acquisition_site_count"],1)

if __name__=="__main__":
    unittest.main()
