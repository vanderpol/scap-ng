#!/usr/bin/env python3
"""#245 Group only proven pure source values; preserve commands and all nodes."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from tempfile import TemporaryDirectory
import yaml

from generate_c_apache_full_hybrid import export_review

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_apache_grouped_values import (
    present_grouped_apache,compile_grouped_apache,prove_grouped_apache)
from research_c_apache_hybrid_authoring import present_c_apache_hybrid

SOURCE=(Path(__file__).resolve().parents[1]/
    "research/requirements-first-language/contract-candidate/corpus/"
    "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")

def source():
    return yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["assessment"]

class GroupedApacheC(unittest.TestCase):
    def test_exact_original_19_variables_with_15_visible_4_nested_values(self):
        original=source()
        snapshot=deepcopy(original)
        grouped=present_grouped_apache(original)
        self.assertEqual(original,snapshot)
        self.assertEqual(grouped["source_total_derived_value_count"],19)
        self.assertEqual(grouped["grouped_presentation_count"],4)
        self.assertEqual(len(grouped["derived_values"]),15)
        self.assertEqual(len(grouped["checks"]),5)
        compiled=compile_grouped_apache(grouped)
        self.assertEqual(compiled,original)
        proof=prove_grouped_apache(original,grouped)
        self.assertEqual(proof["native_A_variables_rehydrated"],19)
        self.assertEqual(proof["author_visible_derived_value_steps"],15)
        self.assertEqual(proof["nested_pure_value_steps"],4)
        self.assertFalse(proof["scanner_runtime_parity_proven"])

    def test_five_dynamic_commands_remain_named_explicit_dependencies(self):
        orig=source()
        grouped=present_grouped_apache(orig)
        values={x["name"] for x in grouped["derived_values"]}
        for chk in grouped["checks"].values():
            cmd=chk["from"]["independent.shellcommand"]["collect"]["command"]
            self.assertEqual(set(cmd),{"use"})
            self.assertIn(cmd["use"],values)
        self.assertEqual(compile_grouped_apache(grouped)["tests"],orig["tests"])

    def test_presented_safe_grouping_preserves_all_original_test_descriptions(self):
        original=source()
        grouped=present_grouped_apache(original)
        test_ids={x["source_id"] for x in grouped["checks"].values()}
        self.assertEqual(test_ids,set(original["tests"]))
        for chk in grouped["checks"].values():
            self.assertTrue(chk["description"].strip())
            self.assertIn(chk["must"]["items_match"],("every","some","one","none"))

    def test_visible_to_nested_regression_no_source_step_loss(self):
        grouped=present_grouped_apache(source())
        grouped["derived_values"].pop()
        with self.assertRaises(ValueError):
            compile_grouped_apache(grouped)
        grouped=present_grouped_apache(source())
        grouped["grouped_presentation_count"]=5
        with self.assertRaisesRegex(ValueError,"inventory"):
            compile_grouped_apache(grouped)

    def test_cannot_move_pure_value_into_command_collector(self):
        original=source()
        grouped=present_grouped_apache(original)
        visible=grouped["derived_values"][0]
        # Insert illicit inline node in a check command: must fail before
        # it could be interpreted as an arbitrary Test acquisition.
        k=next(iter(grouped["checks"]))
        grouped["checks"][k]["from"]["independent.shellcommand"][
            "collect"]["command"]={"inline_derived_value":deepcopy(visible)}
        with self.assertRaises(ValueError):
            compile_grouped_apache(grouped)

    def test_nested_source_identity_and_value_mutations_fail_source_claim(self):
        orig=source()
        authored=present_grouped_apache(orig)
        authored["derived_values"][0]["title"]="Original title changed"
        with self.assertRaises(ValueError):
            prove_grouped_apache(orig,authored)
        authored=present_grouped_apache(orig)
        authored["checks"][next(iter(authored["checks"]))]["must"][
            "items_exist"]="optional"
        with self.assertRaises(ValueError):
            prove_grouped_apache(orig,authored)

    def test_raw_yaml_measurement_keeps_unproven_readability_claims_out(self):
        with TemporaryDirectory() as folder:
            report=export_review(SOURCE,folder)
            a=report["presentation_comparison"]["full"]
            b=report["presentation_comparison"]["grouped"]
            self.assertEqual(a["visible_derived_value_declarations"],19)
            self.assertEqual(b["visible_derived_value_declarations"],15)
            self.assertEqual(a["lines"],b["lines"])
            self.assertGreaterEqual(b["bytes"],a["bytes"])
            self.assertTrue(report["presentation_comparison"]["source_graph_equal_in_both"])
            self.assertFalse(report["presentation_comparison"]["automatic_grouping_promoted"])
            self.assertFalse(report["presentation_comparison"][
                "authoring_comprehension_test_completed"])

    def test_not_every_single_consumer_may_be_folded(self):
        orig=source()
        doc=present_c_apache_hybrid(orig)
        grouped=present_grouped_apache(orig)
        visible={v["name"] for v in grouped["derived_values"]}
        audit_sources={v["name"] for v in doc["derived_values"]}-visible
        self.assertEqual(len(audit_sources),4)
        commands={x["from"]["independent.shellcommand"]["collect"]["command"][
            "use"] for x in grouped["checks"].values()}
        self.assertTrue(commands<=visible)
        self.assertTrue(not audit_sources.intersection(commands))

if __name__=="__main__":
    unittest.main()
