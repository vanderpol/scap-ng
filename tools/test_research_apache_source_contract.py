#!/usr/bin/env python3
"""Pin the original four Apache shellcommand contracts against simplification.

Do NOT model this as a normative OVAL runtime, Apache effective config or full
six-state evaluator. Full source requirement and collect flags are explicitly
retained, including four separate minimum-item requirements.
"""
from pathlib import Path
import re
import sys
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/assessment-simplification/english-first-04/canonical-operators/apache.canonical.research.yaml"
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_provider_apache_directives import collect
import tempfile

class ApacheSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=yaml.safe_load(SOURCE.read_text())
        cls.tests=list(cls.doc["checks"].values())

    def test_original_four_checks_and_eighteen_variables(self):
        self.assertEqual(len(self.doc["checks"]),4)
        self.assertEqual(len(self.doc["metadata"]["variables"]),18)
        self.assertEqual(len(self.doc["evaluate"]["and"]),4)
        for reference in self.doc["evaluate"]["and"]:
            self.assertIn(reference["test"],self.doc["checks"])

    def test_each_four_probes_requires_at_least_one_item(self):
        for check in self.tests:
            with self.subTest(check=check["check"]):
                self.assertEqual(check["require"]["items"],"at_least_one")
                self.assertEqual(check["require"]["match"],"all")
        # Despite English descriptions beginning "If ... defined", the
        # other-loaded-file probes STILL require >=1 shellcommand Item.
        self.assertIn("If ",self.tests[1]["check"])
        self.assertIn("If ",self.tests[3]["check"])

    def test_optional_entity_is_not_optional_object_item(self):
        self.assertEqual(self.tests[0]["require"]["stdout_line"],{
            "matches_regex":r"\s*KeepAlive On"})
        self.assertEqual(self.tests[1]["require"]["stdout_line"],{
            "when_present_matches_regex":r"\s*KeepAlive On"})
        self.assertEqual(self.tests[2]["require"]["subexpression"],{
            "greater_than_or_equal":100})
        self.assertEqual(self.tests[3]["require"]["subexpression"],{
            "when_present_greater_than_or_equal":100})

    def test_command_exit_and_stderr_are_explicitly_not_error_flags(self):
        for check in self.tests:
            for key in ("error_if_exit_status_not_0","error_if_stderr_exists"):
                self.assertIs(check["collect"][key],False)
        inner_shellcommands=[]
        def find(value):
            if isinstance(value,dict):
                if value.get("capability")=="independent.shellcommand":
                    inner_shellcommands.append(value)
                for x in value.values():find(x)
            elif isinstance(value,list):
                for x in value:find(x)
        find(self.doc["metadata"]["variables"])
        self.assertGreaterEqual(len(inner_shellcommands),1)
        for cmd in inner_shellcommands:
            self.assertIs(cmd["collect"]["error_if_exit_status_not_0"],False)
            self.assertIs(cmd["collect"]["error_if_stderr_exists"],False)

    def test_original_keepalive_grep_is_not_strict_directive_token(self):
        text="KeepAliveTimeout 15"
        # Source variable uses grep -iHn '^\\s*KeepAlive' -- this matches
        # KeepAliveTimeout before the State can examine captured output.
        assert re.search(r"^\s*KeepAlive",text,re.I)
        # A native provider matching exact directive names would skip it.
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            conf=root/"httpd.conf"
            conf.write_text(text+"\n")
            result=collect(conf,server_root=root)
            self.assertEqual(result["status"],"complete")
            self.assertEqual(result["items"],[])
        # Not a proof of different end-result: merely different evidence sets.

    def test_four_probe_structure_cannot_be_inverted_from_two_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"httpd.conf").write_text("KeepAlive On\nMaxKeepAliveRequests 150\n")
            native=collect(root/"httpd.conf",server_root=root)
            self.assertEqual(native["status"],"complete")
            self.assertEqual(len(native["items"]),2)
        # Construct two possible original four-probe collection reports
        # with the EXACT SAME two flattened native configuration values.
        # Scenario A: every shell probe discovers one Item. Scenario B:
        # the second shellcommand returns ZERO Items despite source's
        # at_least_one requirement. B cannot pass the 4-check original.
        original_a=[1,1,1,1]
        original_b=[1,0,1,1]
        self.assertTrue(all(n>=1 for n in original_a))
        self.assertFalse(all(n>=1 for n in original_b))
        self.assertEqual(len(native["items"]),2)

    def test_nested_grep_and_loaded_include_collections_differ(self):
        variables=self.doc["metadata"]["variables"]
        names=list(variables)
        self.assertIn("shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable",names)
        self.assertIn("shell-command-check-keepalive-in-all-loaded-conf-files-variable",names)
        self.assertIn("all-loaded-configuration-filepaths-variable",names)
        self.assertIn("merged-included-conf-files-from-include-refernces-in-httd-conf-variable",names)
        # These paths originate from DIFFERENT sources (grep direct Includes
        # versus Apache -t -D DUMP_INCLUDES output); converting to only one
        # effective config tree drops that distinction.

if __name__=="__main__":unittest.main()
