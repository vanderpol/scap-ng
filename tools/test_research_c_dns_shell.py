#!/usr/bin/env python3
"""#245 Source-backed DNS PowerShell evidence without implementing collectors.

Real Windows Server DNS SV-259417.automated converted 0.3 fixture.
The C Test-pieces lower to A's supported independent.shellcommand contract.
No PowerShell execution, original OVAL parity or complete 0.4 authoring.
"""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_require_language import (
    compile_c_requirement,evaluate_compiled_c_supplied_items,parse_c_yaml)

ROOT=Path(__file__).resolve().parents[1]
C=ROOT/("research/assessment-simplification/compact-authoring-04/"
        "c-short-windows-dns-rrl.research.yaml")
SOURCE=ROOT/("research/requirements-first-language/contract-candidate/corpus/"
             "source-specimens/independent-shellcommand-dns-small-db533570bbca.source.yaml")

class WindowsDnsCollectorBridge(unittest.TestCase):
    def setUp(self):
        self.c=parse_c_yaml(C.read_text())
        self.src=yaml.safe_load(SOURCE.read_text())["assessment"]
        self.original=next(iter(self.src["tests"].values()))
        self.cplan=compile_c_requirement(self.c)

    def test_real_source_command_and_error_flags_are_exact(self):
        a=self.cplan["test"]
        self.assertEqual(a["capability"],"independent.shellcommand")
        self.assertEqual(a["object"]["collect"],self.original["object"]["collect"])
        self.assertEqual(a["require"],"at_least_one_exists_and_all_match")
        self.assertEqual(a["states"],[{
            "stdout_line":{"require":"at_least_one_exists_and_all_match",
                           "equals":"Enable"}
        }])
        self.assertEqual(self.original["states"][0]["existence"],"one_or_more")
        self.assertEqual(self.original["states"][0]["match"],"all")
        self.assertFalse(self.cplan["source_parity_verified"])

    def test_one_good_two_mixed_missing_incomplete_and_error(self):
        for items,status,expected in (
            (["true"],"complete","true"),
            (["false"],"complete","false"),
            (["true","false"],"complete","false"),
            ([],"complete","false"),
            ([],"incomplete","unknown"),
            (["true"],"incomplete","unknown"),
            (["false"],"incomplete","false"),
            ([],"error","error"),
            ([],"not_collected","unknown"),
        ):
            with self.subTest(items=items,status=status):
                blob={"capability":"independent.shellcommand","status":status,
                      "items":[{"id":f"shell-item-{i}","outcome":v}
                               for i,v in enumerate(items)],
                      "does_not_exist":0,"error":0,"not_collected":0}
                self.assertEqual(evaluate_compiled_c_supplied_items(
                    self.cplan,blob)["outcome"],expected)

    def test_no_hidden_interpreter_or_exit_status_defaults(self):
        for mutation in (
            lambda d:d["from"]["independent.shellcommand"].pop("shell"),
            lambda d:d["from"]["independent.shellcommand"].pop("error_if_exit_status_not_0"),
            lambda d:d["from"]["independent.shellcommand"].update(shell="python"),
            lambda d:d["from"]["independent.shellcommand"].update(
                error_if_exit_status_not_0="false"),
            lambda d:d["from"]["independent.shellcommand"].update(
                extra_untracked_option=True),
        ):
            d=deepcopy(self.c)
            mutation(d)
            with self.subTest(d=d):
                with self.assertRaises(ValueError):
                    compile_c_requirement(d)
        alternative=deepcopy(self.c)
        alternative["from"]["independent.shellcommand"]["command"]="Write-Output Enable"
        changed=compile_c_requirement(alternative)
        self.assertNotEqual(changed["test"]["object"]["collect"],
                            self.cplan["test"]["object"]["collect"])
        # A command change is a NEW policy, never claimed as a source conversion.

if __name__=="__main__":
    unittest.main()
