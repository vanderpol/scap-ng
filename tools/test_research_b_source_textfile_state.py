#!/usr/bin/env python3
"""#237: source-State and Test quantifiers on raw file capture evidence."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN,ERROR,NOT_APPLICABLE
from research_b_source_textfile_state_lowering import lower_single_capture_textfile_assessment
from research_b_compiled_ir import encode,decode,evaluate_json
from research_provider_textfile_matches import collect,PROVIDER

PATTERN=r"^[ \t]*ProcessSizeMax[ \t]*=[ \t]*(\w+)[ \t]*(?:#.*)?$"


def source():
    return {"assessment":{
        "id":"research-core-dump-capture",
        "version":1,
        "assessment_title":"RHEL core dump config value (research)",
        "mode":"automated","purpose":"assessment","class":"compliance",
        "specification":{"id":"scap-ng.pre-alpha.assessment","version":"0.3.0"},
        "tests":{
            "core-dump-process-max":{
                "capability":"independent.textfilecontent54",
                "existence":"one_or_more","match":"all",
                "object":{
                    "capability":"independent.textfilecontent54",
                    "collect":{"ignore_case":False,"item_creation":"all_object_elements_fullfilled",
                               "multiline":True,"singleline":False},
                    "filesystem":"all","object_title":None,
                    "select":{"full_path":{"operation":"equals","value":"/etc/systemd/coredump.conf"},
                              "pattern":{"operation":"pattern_match","value":PATTERN},
                              "instance":{"operation":"greater_than_or_equal","value":1}},
                },
                "reported_elements":"all",
                "states":[{"field":"subexpression","operation":"equals","value":"0",
                           "existence":"one_or_more","match":"all"}],
                "test_title":"Core dump ProcessSizeMax=0",
            }
        },
        "evaluate":{"test":"core-dump-process-max"},
    }}


class CollectedStateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"coredump.conf"
        self.doc=source()
        self.ast=lower_single_capture_textfile_assessment(self.doc)
        self.ast["using"]["path"]=str(self.path)
        self.compiled=encode(self.doc["assessment"]["id"],self.ast)

    def evidence(self,**kwargs):
        return collect(**self.ast["using"],**kwargs)

    def verdict(self,evidence):
        return evaluate_json(self.compiled,{PROVIDER:evidence}).result

    def test_compiler_owned_state_survives_typed_json_roundtrip(self):
        output=decode(self.compiled)
        self.assertEqual(output["source_kind"],"compiler-compatibility")
        self.assertEqual(output["root"]["state"]["field"],"subexpression")
        self.assertEqual(output["root"]["state"]["expected"],"0")
        self.assertEqual(output["root"]["check"],"all")

    def test_source_capture_match_pass_and_fail(self):
        self.path.write_text("ProcessSizeMax=0\n")
        e=self.evidence()
        self.assertEqual(e["items"][0]["fields"]["subexpression"],"0")
        self.assertEqual(self.verdict(e),TRUE)
        self.path.write_text("ProcessSizeMax=1024\n")
        self.assertEqual(self.verdict(self.evidence()),FALSE)

    def test_all_matching_instances_must_pass(self):
        self.path.write_text("ProcessSizeMax=0\nProcessSizeMax=5\n")
        e=self.evidence()
        self.assertEqual(len(e["items"]),2)
        self.assertEqual(self.verdict(e),FALSE)
        changed=copy.deepcopy(self.ast)
        changed["check"]="only one"
        compiled=encode("only-one-quantifier-research",changed)
        self.assertEqual(evaluate_json(compiled,{PROVIDER:e}).result,TRUE)
        self.path.write_text("ProcessSizeMax=0\nProcessSizeMax=0\n")
        self.assertEqual(evaluate_json(compiled,{PROVIDER:self.evidence()}).result,FALSE)

    def test_absent_file_and_nonmatching_file_not_false_pass(self):
        self.assertEqual(self.verdict(self.evidence()),FALSE)
        self.path.write_text("ProcessSizeMax=not-supported trailing stuff\n")
        self.assertEqual(self.verdict(self.evidence()),FALSE)

    def test_incomplete_success_and_failure_preserve_source_state_truth(self):
        self.path.write_text("ProcessSizeMax=0\nProcessSizeMax=5\n")
        e=self.evidence(max_matches=1)
        self.assertEqual(e["status"],"incomplete")
        self.assertEqual(self.verdict(e),UNKNOWN)
        self.path.write_text("ProcessSizeMax=5\nProcessSizeMax=0\n")
        self.assertEqual(self.verdict(self.evidence(max_matches=1)),FALSE)

    def test_missing_and_bad_entity_fields_fail_without_silent_removal(self):
        self.path.write_text("ProcessSizeMax=0\n")
        e=self.evidence()
        del e["items"][0]["fields"]["subexpression"]
        self.assertEqual(self.verdict(e),UNKNOWN)
        e=self.evidence()
        e["items"][0]["fields"]["subexpression"]={"field_status":"absent"}
        self.assertEqual(self.verdict(e),FALSE)
        e=self.evidence()
        e["items"][0]["fields"]["subexpression"]={"field_status":"error"}
        self.assertEqual(self.verdict(e),ERROR)
        e=self.evidence()
        e["items"][0]["fields"]["subexpression"]=0
        self.assertEqual(self.verdict(e),ERROR)

    def test_duplicate_and_wrong_acquisition_rejected(self):
        self.path.write_text("ProcessSizeMax=0\n")
        e=self.evidence()
        e["items"].append(copy.deepcopy(e["items"][0]))
        self.assertEqual(self.verdict(e),ERROR)
        e=self.evidence()
        e["using"]["path"]="/tmp/not-coredump"
        self.assertEqual(self.verdict(e),ERROR)

    def test_terminal_flags_and_missing_source(self):
        for status,expected in (("error",ERROR),("not collected",UNKNOWN),
                                ("not applicable",NOT_APPLICABLE)):
            with self.subTest(status=status):
                e={"status":status,"using":self.ast["using"],"items":[]}
                self.assertEqual(self.verdict(e),expected)
        self.assertEqual(evaluate_json(self.compiled,{}).result,UNKNOWN)

    def test_unsupported_source_shapes_rejected(self):
        mutations=[
            lambda t:t.update(states=[{"field":"value","operation":"equals",
                                        "value":"0","existence":"one_or_more","match":"all"}]),
            lambda t:t["states"].append(dict(t["states"][0])),
            lambda t:t.update(existence="none"),
            lambda t:t["object"]["select"]["pattern"].update(
                value=r"foo(\w+)(\d+)"),
            lambda t:t["states"][0].update(value={"variable":"policy"}),
            lambda t:t.update(states_match="any"),
        ]
        for change in mutations:
            doc=source()
            test=next(iter(doc["assessment"]["tests"].values()))
            change(test)
            with self.subTest(test=test):
                with self.assertRaises(ValueError):
                    lower_single_capture_textfile_assessment(doc)

    def test_source_state_pattern_match_keeps_typed_regex_field_semantics(self):
        doc=source()
        state=next(iter(doc["assessment"]["tests"].values()))["states"][0]
        state["operation"]="pattern_match"
        state["value"]=r"^(?:0|disabled)$"
        ast=lower_single_capture_textfile_assessment(doc)
        ast["using"]["path"]=str(self.path)
        compiled=encode(doc["assessment"]["id"],ast)
        self.path.write_text("ProcessSizeMax=disabled\n")
        self.assertEqual(evaluate_json(
            compiled,{PROVIDER:collect(**ast["using"])}).result,TRUE)
        self.path.write_text("ProcessSizeMax=1000\n")
        self.assertEqual(evaluate_json(
            compiled,{PROVIDER:collect(**ast["using"])}).result,FALSE)
        self.path.write_text("ProcessSizeMax=0\n")
        self.assertEqual(evaluate_json(
            compiled,{PROVIDER:collect(**ast["using"])}).result,TRUE)

    def test_invalid_state_regex_rejected_at_compile_and_ir_decode(self):
        doc=source()
        state=next(iter(doc["assessment"]["tests"].values()))["states"][0]
        state["operation"]="pattern_match"
        state["value"]="["
        with self.assertRaisesRegex(ValueError,"State pattern"):
            lower_single_capture_textfile_assessment(doc)

    def test_typed_integer_bounds_and_canonical_capture_gates(self):
        doc=source()
        state=next(iter(doc["assessment"]["tests"].values()))["states"][0]
        state["operation"]="greater_than_or_equal"
        state["value"]=15
        # Include signs in the *collected* raw field, so invalid integer
        # strings reach the State evaluator rather than disappearing under
        # the collection regex and masquerading as absent Items.
        test=next(iter(doc["assessment"]["tests"].values()))
        test["object"]["select"]["pattern"]["value"]=r"^[ \t]*ProcessSizeMax[ \t]*=[ \t]*([^ \t\r\n#]+)"
        ast=lower_single_capture_textfile_assessment(doc)
        ast["using"]["path"]=str(self.path)
        compiled=encode(doc["assessment"]["id"],ast)
        for captured,expected in [("15",TRUE),("100",TRUE),("14",FALSE),
                                  ("-2",FALSE),("015",ERROR),("+15",ERROR),
                                  ("-0",ERROR),("9223372036854775808",ERROR)]:
            with self.subTest(captured=captured):
                self.path.write_text("ProcessSizeMax="+captured+"\n")
                self.assertEqual(evaluate_json(
                    compiled,{PROVIDER:collect(**ast["using"])}).result,expected)

    def test_less_than_and_less_than_or_equal_keep_exact_comparison(self):
        for op,target,expected in [
            ("less_than",15,FALSE),("less_than_or_equal",15,TRUE),
            ("greater_than",15,FALSE),("greater_than_or_equal",15,TRUE)]:
            with self.subTest(op=op):
                doc=source()
                state=next(iter(doc["assessment"]["tests"].values()))["states"][0]
                state["operation"]=op
                state["value"]=target
                ast=lower_single_capture_textfile_assessment(doc)
                ast["using"]["path"]=str(self.path)
                self.path.write_text("ProcessSizeMax=15\n")
                compiled=encode(doc["assessment"]["id"],ast)
                self.assertEqual(evaluate_json(
                    compiled,{PROVIDER:collect(**ast["using"])}).result,expected)

    def test_boolean_is_not_a_source_integer_literal(self):
        doc=source()
        state=next(iter(doc["assessment"]["tests"].values()))["states"][0]
        state["operation"]="greater_than"
        state["value"]=True
        with self.assertRaisesRegex(ValueError,"signed int64"):
            lower_single_capture_textfile_assessment(doc)

    def test_nonmatching_multiple_capture_groups_are_field_error(self):
        p=str(self.path)
        self.path.write_text("x=123\n")
        e=collect(path=p,pattern=r"x=(\d)(\d+)")
        self.assertEqual(e["items"][0]["fields"]["subexpression"],
                         {"field_status":"error"})

if __name__=="__main__":
    unittest.main()
