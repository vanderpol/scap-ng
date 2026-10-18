#!/usr/bin/env python3
"""#237 identify actual source first-group risks without converting assessments."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_regex_capture_source_audit import audit,capture_expressions,markdown

SOURCE=(Path(__file__).resolve().parents[1]/
        "research/requirements-first-language/contract-candidate/corpus/source-specimens")
SIMPLE=SOURCE/"independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml"
COMPLEX=SOURCE/"independent-shellcommand-1-3d964d126ca8.source.yaml"


def capsule(source):
    d=yaml.safe_load(source.read_text())
    return {"source_document":d,"source_path":source.name}


class RegexAuditTests(unittest.TestCase):
    def test_real_apache_alternation_has_two_captures_and_source_needs_first(self):
        result=audit({"apache":capsule(COMPLEX)})
        self.assertGreaterEqual(result["expressions"],4)
        case=next(x for x in result["cases"]
                  if x["source_variable"]=="apache-base-install-directories-unix-variable")
        self.assertEqual(case["capture_groups_python_re"],2)
        self.assertEqual(case["classification"],"multiple_capture_groups")
        self.assertFalse(case["original_OVAL_first_capture_parity_verified"])
        self.assertIn("first capture",markdown(result))

    def test_simple_apache_single_capture_and_nested_expression_counts(self):
        result=audit({"simple":capsule(SIMPLE)})
        self.assertEqual(result["distinct_assessments"],1)
        self.assertEqual(result["expressions"],1)
        self.assertEqual(result["group_count_summary"],{"first_capture_only":1})

    def test_missing_or_invalid_patterns_stay_explicit_in_source_census(self):
        source={"assessment":{"mode":"automated","variables":{
            "a":{"expression":{"regex_capture":{"pattern":"(","value":{"variable":"v"}}}},
            "b":{"expression":{"regex_capture":{"pattern":"no-group","value":"x"}}},
            "c":{"expression":{"concat":[{"regex_capture":{
                "pattern":{"variable":"dynamic"},"value":"something"}}]}},
        }}}
        c={"source_document":source,"source_path":"x.yaml"}
        r=audit({"x":c})
        self.assertEqual(r["expressions"],3)
        self.assertEqual(r["group_count_summary"]["unsupported_Python_regex"],1)
        self.assertEqual(r["group_count_summary"]["no_capture_groups"],1)
        self.assertEqual(r["group_count_summary"]["dynamic_or_missing"],1)
        self.assertFalse(r["parity_verified"])

    def test_nonregex_variable_objects_not_falsely_counted(self):
        self.assertEqual(capture_expressions({
            "concat":[{"variable":"a"},{"literal":{"value":"hi"}}]}),[])


if __name__=="__main__":
    unittest.main()
