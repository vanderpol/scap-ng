#!/usr/bin/env python3
"""#237: source Variable operation research refuses silent cardinality changes."""
from __future__ import annotations
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_b_variable_value_ops import (
    values,capture,concat,unique,MAX_VALUES,
)

SOURCE=(Path(__file__).resolve().parents[1]/
        "research/requirements-first-language/contract-candidate/corpus/"
        "source-specimens/independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml")


class VariableValueOpsTests(unittest.TestCase):
    def source(self):
        return yaml.safe_load(SOURCE.read_text())["assessment"]

    def test_actual_apache_regex_capture_and_concat_preserve_source_graph(self):
        a=self.source()
        variables=a["variables"]
        reg=variables["apache-path-httpd-or-apache2-variable"][
            "expression"]["regex_capture"]["pattern"]
        text=values(["/usr/sbin/httpd -DFOREGROUND"])
        binary=capture(text,reg)
        self.assertEqual(binary,values(["/usr/sbin/httpd"]))
        suffix=variables["command-gather-apache-version-variable"][
            "expression"]["concat"][1]["literal"]["value"]
        self.assertEqual(concat([binary,values([suffix])]),
                         values(["/usr/sbin/httpd -V"]))

    def test_two_different_executables_produce_two_query_identities(self):
        a=self.source()
        pat=a["variables"]["apache-path-httpd-or-apache2-variable"][
            "expression"]["regex_capture"]["pattern"]
        found=capture(values(["/usr/sbin/httpd -DFOREGROUND",
                              "/opt/apache/bin/apache2 -DFOREGROUND"]),pat)
        self.assertEqual(found["status"],"values")
        self.assertEqual(len(found["values"]),2)
        commands=concat([found,values([" -V"])])
        self.assertEqual(commands["values"],
                         ["/usr/sbin/httpd -V","/opt/apache/bin/apache2 -V"])
        self.assertEqual(len(commands["values"]),2)

    def test_no_values_not_equivalent_to_false_or_empty_string(self):
        self.assertEqual(capture(values(["unrelated-process"]),r"(httpd)"),
                         values(status="no_values"))
        self.assertEqual(concat([values(status="no_values"),values([" -V"])]),
                         values(status="no_values"))
        self.assertEqual(concat([values([""]),values([" -V"])]),
                         values([" -V"]))

    def test_unknown_and_error_do_not_become_empty_or_success(self):
        for status in ("unknown","error","not_applicable"):
            with self.subTest(status=status):
                self.assertEqual(capture(values(status=status),r"(httpd)"),
                                 values(status=status))
                self.assertEqual(concat([values(status=status),values([" -V"])]),
                                 values(status=status))
        self.assertEqual(concat([values(status="error"),
                                 values(status="unknown")]),values(status="error"))

    def test_cartesian_cardinality_is_capped_not_truncated(self):
        a=values([str(i) for i in range(40)])
        b=values([str(i) for i in range(20)])
        self.assertEqual(concat([a,b]),values(status="error"))
        self.assertEqual(concat([values(["a","b"]),values(["1","2"])]),
                         values(["a1","a2","b1","b2"]))

    def test_unique_explicitly_reduces_duplicates_only_when_requested(self):
        captured=values(["/bin/httpd","/bin/httpd","/opt/apache2"])
        self.assertEqual(concat([captured,values([" -V"])]),
                         values(["/bin/httpd -V","/bin/httpd -V",
                                 "/opt/apache2 -V"]))
        self.assertEqual(unique(captured),
                         values(["/bin/httpd","/opt/apache2"]))

    def test_regex_capture_requires_one_group_and_bounded_strings(self):
        self.assertEqual(capture(values(["a1"]),r"(a)(1)"),
                         values(status="error"))
        self.assertEqual(capture(values(["a1"]),r"["),
                         values(status="error"))
        self.assertEqual(capture(values(["x"]),"(.+)"),
                         values(["x"]))
        self.assertEqual(capture(values(["abc"]),r"(a)?b(c)"),
                         values(status="error"))
        with self.assertRaises(ValueError):
            values(["x"]*(MAX_VALUES+1))
        with self.assertRaises(ValueError):
            values(["x"*4097])

    def test_typed_envelope_cannot_carry_partial_unverified_values(self):
        with self.assertRaises(ValueError):
            values(["result"],status="unknown")
        with self.assertRaises(ValueError):
            values([],status="values")
        with self.assertRaises(ValueError):
            concat([{"status":"values","values":None}])


if __name__=="__main__":
    unittest.main()
