#!/usr/bin/env python3
"""#237: source Variable DAG census must distinguish refs, cycles and Assessments."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_variable_dag_inventory import (
    analyze_graph,inventory,markdown,variable_references,
)

SOURCE=(Path(__file__).resolve().parents[1]/
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml")


class SourceVariableCensusTests(unittest.TestCase):
    def test_real_apache_chain_is_not_flattened(self):
        assessment=yaml.safe_load(SOURCE.read_text())["assessment"]
        graph=analyze_graph(assessment)
        self.assertEqual(graph["variable_count"],2)
        self.assertEqual(graph["max_variable_depth"],2)
        self.assertEqual(graph["operators"],{"concat":1,"regex_capture":1})
        self.assertEqual(graph["test_variables"],["command-gather-apache-version-variable"])
        self.assertEqual(graph["dependencies"]["command-gather-apache-version-variable"],
                         ["apache-path-httpd-or-apache2-variable"])
        self.assertEqual(graph["cycle_nodes"],[])
        self.assertEqual(graph["unbound_test_variables"],[])

    def test_source_cycle_is_recorded_never_claimed_resolvable(self):
        a={"mode":"automated","id":"bad-cycle","tests":{"x":{
            "object":{"command":{"variable":"first"}}}},
            "variables":{
                "first":{"expression":{"concat":[{"variable":"second"}]}},
                "second":{"expression":{"concat":[{"variable":"first"}]}},
            }}
        g=analyze_graph(a)
        self.assertTrue(g["cycle_nodes"])
        self.assertEqual(g["variable_count"],2)
        self.assertEqual(g["unbound_test_variables"],[])

    def test_unknown_references_are_not_inferred_as_local_defaults(self):
        a={"mode":"automated","id":"unbound",
           "tests":{"check":{"command":{"variable":"absent"}}},
           "variables":{"first":{"expression":{"concat":[{"variable":"different"}]}}}}
        g=analyze_graph(a)
        self.assertEqual(g["unbound_test_variables"],["absent"])
        self.assertEqual(g["external_dependencies"],{"first":["different"]})

    def test_distinct_assessment_denominator_and_source_warning(self):
        real=yaml.safe_load(SOURCE.read_text())["assessment"]
        corpus={
            "apache":{"source_path":"authoring/apache_server_2-4_unix_server/assessments/automated/a.yaml",
                      "source_document":{"assessment":real}},
            "manual":{"source_path":"authoring/shared/assessments/manual/m.yaml",
                      "source_document":{"assessment":{"mode":"manual","variables":{"x":{}}}}},
            "plain":{"source_path":"authoring/rhel_9/assessments/automated/b.yaml",
                     "source_document":{"assessment":{"mode":"automated","variables":{}}}},
        }
        r=inventory(corpus)
        self.assertEqual(r["assessments_with_variables"],1)
        self.assertEqual(r["total_declared_variables"],2)
        self.assertEqual(r["source_operator_counts"],{"concat":1,"regex_capture":1})
        self.assertFalse(r["original_source_parity_verified"])
        self.assertIn("not original SCAP 1.4",markdown(r))

    def test_nested_variable_references_are_collected_without_running_commands(self):
        refs=variable_references({"values":[
            {"variable":"a"},{"expr":{"concat":[{"variable":"b"}]}}]})
        self.assertEqual(refs,{"a","b"})


if __name__=="__main__":
    unittest.main()
