#!/usr/bin/env python3
"""#235: one evaluator dispatches typed native AST and compiler-only OVAL Tests.

This proves a narrow integration architecture is feasible; NO SCAP 1.4
source-to-IR conversion, OVAL Object/State/Variable execution, or full scanner
has been implemented by this test. Tests pin original Apache Test IDs and
existence values while intentionally supplying already-evaluated Item results.
"""
from pathlib import Path
import sys
import tempfile
import unittest
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,ERROR,UNKNOWN,NOT_APPLICABLE
from research_native_contract_candidate import EXAMPLES,read,compile_doc
from research_native_contract_evaluator import evaluate
from research_provider_apache_directives import collect

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/assessment-simplification/english-first-04/canonical-operators/apache.canonical.research.yaml"

def shell_test(check_id,exists,*,flag="complete",results=None):
    return {"kind":"compat_oval_test",
            "source_test_id":check_id,
            "test":{"flag":flag,"existence":"at_least_one_exists",
                    "check":"all","has_state":True,
                    "exists":exists,
                    "item_results":list(results if results is not None else [TRUE]*exists)}}

def legacy_apache(checks,counts,results=None):
    children=[]
    for i,(name,_data) in enumerate(checks):
        curr_results=None if results is None else results[i]
        children.append(shell_test(name,counts[i],results=curr_results))
    return {"kind":"logic","operator":"all","children":children}

class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc=yaml.safe_load(SOURCE.read_text())
        cls.checks=list(doc["checks"].items())
        assert len(cls.checks)==4
        assert all(c["require"]["items"]=="at_least_one" for _,c in cls.checks)

    def test_source_four_tests_positive_items_pass_compiler_owned_node(self):
        root=legacy_apache(self.checks,[1,1,1,1])
        self.assertEqual(evaluate(root,{}).result,TRUE)

    def test_missing_one_original_shell_item_is_false_even_when_native_passes(self):
        root=legacy_apache(self.checks,[1,0,1,1])
        self.assertEqual(evaluate(root,{}).result,FALSE)
        with tempfile.TemporaryDirectory() as temp:
            home=Path(temp)
            (home/"httpd.conf").write_text("KeepAlive On\nMaxKeepAliveRequests 150\n")
            observed=collect(home/"httpd.conf",server_root=home)
            native=read(EXAMPLES/"04-apache-two-settings.yaml")["ast"]
            self.assertEqual(evaluate(native,{"apache.config_directives":observed}).result,TRUE)
            # Matching fluent native requirements cannot replace all four
            # source-required shell Items without proving acquisition mapping.

    def test_compatibility_unknown_partial_does_not_become_false_by_default(self):
        source=shell_test(self.checks[0][0],1,flag="incomplete",results=[TRUE])
        self.assertEqual(evaluate(source,{}).result,UNKNOWN)

    def test_compatibility_incomplete_observed_violation_decisively_fails(self):
        source=shell_test(self.checks[0][0],1,flag="incomplete",results=[FALSE])
        self.assertEqual(evaluate(source,{}).result,FALSE)

    def test_compatibility_error_and_not_applicable_states_preserved(self):
        node=shell_test(self.checks[0][0],0,flag="error",results=[])
        self.assertEqual(evaluate(node,{}).result,ERROR)
        node["test"]["flag"]="not applicable"
        self.assertEqual(evaluate(node,{}).result,NOT_APPLICABLE)

    def test_native_and_compatibility_share_one_boolean_group_evaluator(self):
        native=read(EXAMPLES/"01-required-home.yaml")["ast"]
        source=shell_test(self.checks[0][0],0,flag="error",results=[])
        group={"kind":"logic","operator":"any","children":[native,source]}
        passing_mount={"status":"complete",
                       "items":[{"id":"m","fields":{"mount_point":"/home",
                                                   "mount_options":["nosuid"]}}]}
        self.assertEqual(evaluate(group,{"linux.mounts":passing_mount}).result,TRUE)
        group["operator"]="all"
        self.assertEqual(evaluate(group,{"linux.mounts":passing_mount}).result,ERROR)

    def test_compiler_rejects_compatibility_authoring_node(self):
        forbidden={"id":"x","title":"x","require":{
            "compat_oval_test":{"test":{"flag":"complete","exists":1}}}}
        with self.assertRaisesRegex(ValueError,"exactly one named resource"):
            compile_doc(forbidden)

    def test_missing_or_undocumented_legacy_input_fails_closed(self):
        bad={"kind":"compat_oval_test","source_test_id":self.checks[0][0],
             "test":{"flag":"complete","existence":"at_least_one_exists",
                     "exists":1,"check":"all","invented":True}}
        with self.assertRaisesRegex(ValueError,"unexpected"):
            evaluate(bad,{})
        with self.assertRaisesRegex(ValueError,"requires source_test_id"):
            evaluate({"kind":"compat_oval_test","test":bad["test"]},{})

if __name__=="__main__":unittest.main()
