#!/usr/bin/env python3
"""Refs #245 original Apache 19-value, five-Test source exact authoring."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_apache_hybrid_authoring import (
    present_c_apache_hybrid,compile_c_apache_hybrid,prove_c_apache_hybrid)
from v04_a_dataflow_index import index_assessment_dataflow

ROOT=Path(__file__).resolve().parents[1]
APACHE=(ROOT/"research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml")

def original():
    return yaml.safe_load(APACHE.read_text(encoding="utf-8"))["assessment"]

class FullApacheCHybridTests(unittest.TestCase):
    def test_19_real_derived_values_and_five_source_tests_exactly_recompile(self):
        native=original()
        before=deepcopy(native)
        authored=present_c_apache_hybrid(native)
        self.assertEqual(native,before)
        self.assertEqual(authored["stage"],
             "C_RESEARCH_COMPLETE_APACHE_DERIVED_VALUES_AND_MUST_TO_0_3_IR")
        self.assertEqual(len(authored["derived_values"]),19)
        self.assertEqual(len(authored["observations"]),1)
        self.assertEqual(len(authored["checks"]),5)
        self.assertEqual(len(authored["require"]["and"]),5)
        self.assertTrue(all("from" in c and "must" in c and "description" in c
                            for c in authored["checks"].values()))
        self.assertTrue(all("object" not in c for c in authored["checks"].values()))
        self.assertEqual(compile_c_apache_hybrid(authored),native)
        proof=prove_c_apache_hybrid(native,authored)
        self.assertEqual(proof["source_test_count"],5)
        self.assertEqual(proof["source_variable_count"],19)
        self.assertEqual(proof["source_shared_acquisition_count"],1)
        self.assertFalse(proof["original_scanner_execution_proven"])
        self.assertFalse(proof["six_state_runtime_parity_proven"])
        self.assertEqual(index_assessment_dataflow(
                         compile_c_apache_hybrid(authored)),index_assessment_dataflow(native))

    def test_dynamic_shell_commands_use_human_value_aliases_not_oval_variable_ids(self):
        native=original();doc=present_c_apache_hybrid(native)
        variable_aliases={x["source_id"]:x["name"] for x in doc["derived_values"]}
        for check in doc["checks"].values():
            cmd=check["from"]["independent.shellcommand"]["collect"]["command"]
            self.assertEqual(set(cmd),{"use"})
            self.assertIn(cmd["use"],variable_aliases.values())
            self.assertNotIn("variable",cmd)
        self.assertEqual(compile_c_apache_hybrid(doc)["tests"],native["tests"])

    def test_real_apache_preserves_optional_fields_and_composed_match(self):
        native=original();doc=present_c_apache_hybrid(native)
        cid="if-sessioncookiename-directive-exists-in-other-loaded-configuration-files-verify"
        check=doc["checks"][cid]
        self.assertEqual(check["must"]["fields_join"],"and")
        self.assertEqual(len(check["must"]["fields"]),2)
        self.assertEqual([x["matches_regex"] for x in check["must"]["fields"]],
                         [r"(?i)HttpOnly",r"(?i)Secure"])
        self.assertEqual([x["exists"] for x in check["must"]["fields"]],
                         ["optional","optional"])
        result=compile_c_apache_hybrid(doc)
        self.assertEqual(result["tests"][cid+"-test"]["states_match"],"all")

    def test_changed_shell_command_or_selectors_cannot_claim_source_parity(self):
        native=original();doc=present_c_apache_hybrid(native)
        k=next(iter(doc["checks"]))
        doc["checks"][k]["from"]["independent.shellcommand"]["collect"]["pattern"]="new"
        with self.assertRaisesRegex(ValueError,"graph differs"):
            prove_c_apache_hybrid(native,doc)
        doc=present_c_apache_hybrid(native)
        doc["derived_values"][0]["derive"]={"use":"does_not_exist"}
        with self.assertRaises(ValueError):
            compile_c_apache_hybrid(doc)

    def test_missing_test_check_and_altered_existence_fail_closed(self):
        native=original();doc=present_c_apache_hybrid(native)
        doc["require"]["and"].pop()
        with self.assertRaisesRegex(ValueError,"coverage incomplete"):
            compile_c_apache_hybrid(doc)
        doc=present_c_apache_hybrid(native)
        k=next(iter(doc["checks"]))
        doc["checks"][k]["must"]["items_exist"]="optional"
        with self.assertRaisesRegex(ValueError,"graph differs"):
            prove_c_apache_hybrid(native,doc)
        doc=present_c_apache_hybrid(native)
        doc["checks"][k]["description"]=""
        with self.assertRaisesRegex(ValueError,"description"):
            compile_c_apache_hybrid(doc)

    def test_shared_observation_is_pinned_and_identity_not_duplicated(self):
        native=original();doc=present_c_apache_hybrid(native)
        k=next(iter(doc["observations"]))
        doc["observations"][k]["from"]["independent.shellcommand"]["collect"][
            "pattern"]="unexpected"
        with self.assertRaisesRegex(ValueError,"pinned source"):
            compile_c_apache_hybrid(doc)

    def test_variable_dependency_cycle_and_unknown_field_semantics_are_errors(self):
        native=original();doc=present_c_apache_hybrid(native)
        first=next(iter(doc["checks"]))
        doc["checks"][first]["must"]["fields"][0]["unapproved_check"]=True
        with self.assertRaisesRegex(ValueError,"typed C Item"):
            compile_c_apache_hybrid(doc)
        doc=present_c_apache_hybrid(native)
        alias=doc["derived_values"][0]["name"]
        doc["derived_values"][0]["derive"]={"use":alias}
        with self.assertRaises(ValueError):
            compile_c_apache_hybrid(doc)

if __name__=="__main__":
    unittest.main()
