#!/usr/bin/env python3
"""Refs #245: Apache 19-node source census for candidate value grouping."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_variable_folding_safety import candidate_single_use_value_steps

ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/"research/requirements-first-language/contract-candidate/corpus/"
     "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")

def apache():
    return yaml.safe_load(SRC.read_text(encoding="utf-8"))["assessment"]

class ValueGroupingSafetyTests(unittest.TestCase):
    def test_real_apache_19_exposes_only_pure_single_consumer_candidates(self):
        doc=apache(); before=deepcopy(doc)
        result=candidate_single_use_value_steps(doc)
        self.assertEqual(doc,before)
        self.assertEqual(result["named_variable_count"],19)
        self.assertEqual(result["presentation_group_candidates"],4)
        self.assertEqual(result["actual_native_variables_removed"],0)
        self.assertFalse(result["automatic_inline_or_migration_authorized"])
        self.assertFalse(result["oval_runtime_parity_proven"])
        actual={x["source_id"] for x in result["candidates"]
                if x["presentation_grouping_candidate"]}
        self.assertEqual(actual,{
            "all-included-conf-files-from-include-refernces-in-httd-conf-variable",
            "all-loaded-configuration-filepaths-variable",
            "merged-included-conf-files-from-include-refernces-in-httd-conf-variable",
            "relative-server-config-file-variable",
        })

    def test_command_collector_dependencies_are_not_pure_value_transform(self):
        result=candidate_single_use_value_steps(apache())
        by_id={x["source_id"]:x for x in result["candidates"]}
        for name in (
            "httpd-root-apachectl-v-variable",
            "server-config-file-apachectl-v-variable",
            "shell-command-check-all-include-include-optional-files-variable",
            "command-gather-httpd-apache2-list-all-loaded-configuration-files-variable",
        ):
            with self.subTest(name=name):
                self.assertFalse(by_id[name]["presentation_grouping_candidate"])
                self.assertEqual(by_id[name]["reason"],"DYNAMIC_ACQUISITION_CONSUMER")

    def test_reused_or_test_bound_source_must_remain_exposed(self):
        doc=apache()
        result=candidate_single_use_value_steps(doc)
        by_id={x["source_id"]:x for x in result["candidates"]}
        self.assertEqual(by_id["apache-path-httpd-or-apache2-variable"]["reason"],
                         "REUSED_VALUE")
        victim="relative-server-config-file-variable"
        test=next(iter(doc["tests"].values()))
        test["states"].append({"inspect_additional_dependency":{
            "equals":{"variable":victim}}})
        after=candidate_single_use_value_steps(doc)
        by_id={x["source_id"]:x for x in after["candidates"]}
        self.assertEqual(after["presentation_group_candidates"],3)
        self.assertEqual(by_id[victim]["consumer_count"],2)
        self.assertFalse(by_id[victim]["presentation_grouping_candidate"])

    def test_broken_source_dependency_is_rejected_not_grouped(self):
        doc=apache()
        doc["variables"]["relative-server-config-file-variable"][
            "expression"]["regex_capture"]["value"]["values"]["object"][
            "collect"]["command"]={"variable":"missing-upstream-variable"}
        with self.assertRaisesRegex(ValueError,"unresolved"):
            candidate_single_use_value_steps(doc)

if __name__=="__main__":
    unittest.main()
