#!/usr/bin/env python3
"""Refs #245: one static frontend grammar covers all tested direct/shared C."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_one_frontend import normalize_c_frontend
from research_c_require_language import parse_c_yaml

BASE=Path(__file__).resolve().parents[1]/(
    "research/assessment-simplification/compact-authoring-04")

def sample(name):
    return parse_c_yaml((BASE/name).read_text(encoding="utf-8"))

class OneCFrontendShape(unittest.TestCase):
    def test_simple_linux_and_windows_dns_are_one_check_same_contract(self):
        for name in ("c-short-linux-home.research.yaml",
                     "c-short-windows-dns-rrl.research.yaml",
                     "c-short-windows-wdigest.research.yaml"):
            with self.subTest(sample=name):
                parsed=sample(name)
                result=normalize_c_frontend(parsed)
                self.assertEqual(result["assessment_id"],None)
                self.assertTrue(result["generated_internal_single_check_alias"])
                self.assertEqual(len(result["checks"]),1)
                self.assertEqual(len(result["observations"]),0)
                self.assertEqual(result["require"],{"op":"check","id":"single_check"})
                self.assertEqual(result["checks"][0]["must"],parsed["must"])

    def test_two_windows_named_inline_checks_use_same_frontend(self):
        c=sample("c-two-windows-checks.research.yaml")
        result=normalize_c_frontend(c)
        self.assertEqual(result["assessment_id"],c["id"])
        self.assertEqual(len(result["checks"]),2)
        self.assertEqual(len(result["observations"]),0)
        self.assertEqual(result["require"]["op"],"every")
        self.assertEqual([x["id"] for x in result["checks"]],
                         ["wdigest","non_ntfs_local_volumes"])
        self.assertTrue(all(x["observation"] is None for x in result["checks"]))

    def test_complex_windows_named_shared_observations_use_same_frontend(self):
        c=sample("c-source-exact-windows-rdp-rights.research.yaml")
        result=normalize_c_frontend(c)
        self.assertEqual(result["assessment_id"],None)
        self.assertFalse(result["generated_internal_single_check_alias"])
        self.assertEqual(len(result["observations"]),2)
        self.assertEqual(len(result["checks"]),7)
        self.assertEqual(result["require"]["op"],"one_of")
        self.assertEqual(result["check_references_in_order"].count("deny_guests"),2)
        self.assertEqual(set(result["observations"]),
                         {"system_role","denied_remote_logon_trustees"})
        self.assertEqual(result["checks"][0]["observation"],"system_role")
        self.assertEqual(result["checks"][0]["from"]["capability"],
                         "windows.wmi.query")
        self.assertFalse(result["source_semantics_validated"])
        self.assertFalse(result["scanner_executed"])

    def test_mixed_direct_and_shared_check_do_not_create_second_language(self):
        c=sample("c-source-exact-windows-rdp-rights.research.yaml")
        extra=sample("c-short-windows-wdigest.research.yaml")
        c["checks"]["wdigest"]={"from":extra["from"],"must":extra["must"]}
        c["require"]["one_of"].append({"check":"wdigest"})
        result=normalize_c_frontend(c)
        self.assertEqual(len(result["checks"]),8)
        self.assertEqual(len(result["observations"]),2)
        self.assertEqual(result["checks"][-1]["from"]["capability"],
                         "windows.registry")
        self.assertIsNone(result["checks"][-1]["observation"])
        self.assertEqual(result["require"]["children"][-1],
                         {"op":"check","id":"wdigest"})

    def test_source_is_unchanged_including_regex_and_collectors(self):
        c=sample("c-source-exact-windows-rdp-rights.research.yaml")
        old=deepcopy(c)
        result=normalize_c_frontend(c)
        self.assertEqual(c,old)
        self.assertEqual(result["checks"][2]["must"],old["checks"]["deny_local_accounts"]["must"])
        self.assertEqual(result["observations"]["system_role"]["from"]["arguments"],
                         old["observations"]["system_role"]["from"]["windows.wmi.query"])

    def test_two_sources_on_one_check_is_not_accepted(self):
        c=sample("c-source-exact-windows-rdp-rights.research.yaml")
        c["checks"]["standalone"]["from"]={
            "windows.registry":{"name":"Example"}}
        with self.assertRaisesRegex(ValueError,"two acquisition routes"):
            normalize_c_frontend(c)

    def test_unresolved_and_orphan_shared_observation_fail_closed(self):
        c=sample("c-source-exact-windows-rdp-rights.research.yaml")
        c["checks"]["standalone"]["observation"]="nonexistent"
        with self.assertRaisesRegex(ValueError,"unresolved"):
            normalize_c_frontend(c)
        c=sample("c-source-exact-windows-rdp-rights.research.yaml")
        c["observations"]["unused"]={"from":{"linux.partition":{"mount_point":"/home"}}}
        with self.assertRaisesRegex(ValueError,"unused shared"):
            normalize_c_frontend(c)

    def test_missing_or_unknown_checks_cannot_disappear(self):
        c=sample("c-two-windows-checks.research.yaml")
        c["require"]["every"].pop()
        with self.assertRaisesRegex(ValueError,"all authored checks"):
            normalize_c_frontend(c)
        c=sample("c-two-windows-checks.research.yaml")
        c["require"]["every"][0]["check"]="unregistered"
        with self.assertRaisesRegex(ValueError,"unknown named"):
            normalize_c_frontend(c)

    def test_boolean_ambiguity_is_parse_error_not_a_second_check(self):
        for ambiguous in ("on: subject\n", "yes: subject\n"):
            with self.assertRaisesRegex(ValueError,"mapping key must be a string"):
                parse_c_yaml(ambiguous)

    def test_only_checked_explicit_ids_in_authored_names(self):
        c=sample("c-two-windows-checks.research.yaml")
        c["checks"]["Bad ID"]=c["checks"].pop("wdigest")
        with self.assertRaisesRegex(ValueError,"stable lowercase"):
            normalize_c_frontend(c)

if __name__=="__main__":
    unittest.main()
