#!/usr/bin/env python3
"""#237: real Windows DNS RRL source and shell output Item multiplicity pilot."""
from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0,str(Path(__file__).resolve().parent))
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN,ERROR,NOT_APPLICABLE
from research_b_source_shell_lowering import lower_source_shell_assessment
from research_b_source_shell_snapshot import normalize,PROVIDER
from research_b_compiled_ir import encode,decode,evaluate_json

ROOT=(Path(__file__).resolve().parents[1]/
      "research/requirements-first-language/contract-candidate/corpus/"
      "source-specimens")
DNS=ROOT/"independent-shellcommand-dns-small-db533570bbca.source.yaml"
RHEL=ROOT/"independent-shellcommand-0-365f46522e9e.source.yaml"
APACHE=ROOT/"independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml"


class SourceShellTests(unittest.TestCase):
    def setUp(self):
        self.doc=yaml.safe_load(DNS.read_text())
        self.ast=lower_source_shell_assessment(self.doc)
        self.payload=encode(self.doc["assessment"]["id"],self.ast)

    def observation(self,lines=None,status="complete",using=None,stderr=None,exit_status=0):
        query=self.ast["using"] if using is None else using
        records=[] if lines is None else [{
            "stdout_line":lines,
            "stderr_line":[] if stderr is None else stderr,
            "exit_status":exit_status}]
        return normalize({"query":query,"status":status,"records":records},
                         **self.ast["using"])

    def verdict(self,obs):
        return evaluate_json(self.payload,{PROVIDER:obs}).result

    def test_direct_real_dns_source_retains_literal_command_identity(self):
        self.assertEqual(self.doc["assessment"]["id"],"SV-259417.automated")
        self.assertEqual(self.ast["source_test_id"],
                         "windows-dns-response-rate-limiting-rrl-enabled-test")
        self.assertEqual(self.ast["using"]["shell"],"powershell")
        self.assertIn("Get-DnsServerResponseRateLimiting",self.ast["using"]["command"])
        ir=decode(self.payload)
        self.assertEqual(ir["source_kind"],"compiler-compatibility")
        self.assertEqual(ir["root"]["state"]["expected"],"Enable")

    def test_dns_enable_proven_only_with_exact_single_item_stdout_entity(self):
        self.assertEqual(self.verdict(self.observation(["Enable"])),TRUE)
        self.assertEqual(self.verdict(self.observation(["Disable"])),FALSE)
        self.assertEqual(self.verdict(self.observation([])),FALSE)
        self.assertEqual(self.verdict(self.observation(None)),FALSE)
        self.assertEqual(self.verdict(self.observation(["Enable","Disable"])),FALSE)
        self.assertEqual(self.verdict(self.observation(["Enable","Enable"])),TRUE)

    def test_incomplete_collection_and_terminal_errors_cannot_claim_false_pass(self):
        self.assertEqual(self.verdict(self.observation(["Enable"],"incomplete")),UNKNOWN)
        self.assertEqual(self.verdict(self.observation(["Disable"],"incomplete")),FALSE)
        self.assertEqual(self.verdict(self.observation(None,"incomplete")),UNKNOWN)
        for flag,expected in [("error",ERROR),("not collected",UNKNOWN),
                              ("not applicable",NOT_APPLICABLE)]:
            with self.subTest(flag=flag):
                self.assertEqual(self.verdict(self.observation(None,flag)),expected)
        self.assertEqual(evaluate_json(self.payload,{}).result,UNKNOWN)

    def test_wrong_command_or_malformed_line_array_is_not_accepted(self):
        other=dict(self.ast["using"],command="Get-DnsServer")
        self.assertEqual(self.verdict(self.observation(["Enable"],using=other)),ERROR)
        bad=self.observation(["Enable"])
        bad["items"][0]["fields"]["stdout_line"]="Enable"
        self.assertEqual(self.verdict(bad),ERROR)
        bad=self.observation(["Enable"])
        bad["items"].append(copy.deepcopy(bad["items"][0]))
        self.assertEqual(self.verdict(bad),ERROR)

    def test_multivalued_stdout_does_not_become_several_source_items(self):
        e=self.observation(["Enable","Enable"])
        self.assertEqual(len(e["items"]),1)
        self.assertEqual(e["items"][0]["fields"]["stdout_line"],["Enable","Enable"])
        self.assertEqual(self.verdict(e),TRUE)

    def test_source_literal_stdout_empty_is_not_absence_of_stdout(self):
        rhel=yaml.safe_load(RHEL.read_text())
        node=lower_source_shell_assessment(rhel)
        payload=encode(rhel["assessment"]["id"],node)
        using=node["using"]
        def result(lines):
            snapshot={"query":using,"status":"complete",
                      "records":[{"stdout_line":lines,"stderr_line":[],"exit_status":0}]}
            e=normalize(snapshot,**using)
            return evaluate_json(payload,{PROVIDER:e}).result
        self.assertEqual(result([""]),TRUE)
        self.assertEqual(result([]),FALSE)

    def test_dynamic_apache_command_cannot_be_guessed(self):
        apache=yaml.safe_load(APACHE.read_text())
        with self.assertRaisesRegex(ValueError,"Variables/inputs"):
            lower_source_shell_assessment(apache)

    def test_source_change_to_unsupported_shell_or_regex_fails_closed(self):
        modifications=[
            lambda t:t["states"][0].update(operation="pattern_match"),
            lambda t:t["object"]["collect"].update(pattern="Enable"),
            lambda t:t["object"]["collect"].update(command={"variable":"x"}),
            lambda t:t["object"]["collect"].update(shell="cmd"),
            lambda t:t["states"].append(dict(t["states"][0])),
        ]
        for m in modifications:
            with self.subTest(m=m):
                doc=copy.deepcopy(self.doc)
                m(next(iter(doc["assessment"]["tests"].values())))
                with self.assertRaises((ValueError,TypeError)):
                    lower_source_shell_assessment(doc)

    def test_snapshot_source_flags_must_be_honored_when_true(self):
        using=dict(self.ast["using"],error_if_exit_status_not_0=True)
        raw={"query":using,"status":"complete",
             "records":[{"stdout_line":["Enable"],"stderr_line":[],"exit_status":1}]}
        normalized=normalize(raw,**using)
        self.assertEqual(normalized["status"],"error")
        self.assertEqual(normalized["items"],[])


if __name__=="__main__":
    unittest.main()
