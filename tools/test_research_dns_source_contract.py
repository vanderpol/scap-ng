#!/usr/bin/env python3
"""Pin original 5-check Windows DNS source semantics before native simplification.

Tests inspect complete authored source YAML and deliberately demonstrate
information-loss cases. They DO NOT run PowerShell, DNS services, a Windows
collector, a SCAP-NG scanner or the normative OVAL six-state evaluator.
"""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/assessment-simplification/english-first-04/canonical-operators/dns.canonical.research.yaml"

class DnsSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=yaml.safe_load(SOURCE.read_text())
        cls.checks=list(cls.doc["checks"].values())

    def test_exactly_five_source_checks_three_logical_alternatives(self):
        self.assertEqual(len(self.checks),5)
        branches=self.doc["evaluate"]["or"]
        self.assertEqual(len(branches),3)
        self.assertEqual(len(branches[2]["and"]),3)
        ids=set(self.doc["checks"])
        for branch in branches[:2]:
            self.assertIn(branch["test"],ids)
        for branch in branches[2]["and"]:
            self.assertIn(branch["test"],ids)

    def test_every_source_check_requires_shellcommand_item(self):
        for check in self.checks:
            with self.subTest(name=check["check"]):
                self.assertEqual(check["require"]["items"],"at_least_one")
                self.assertEqual(check["require"]["match"],"all")

    def test_empty_zone_alternatives_test_absent_stdout_values_not_zero_items(self):
        for check in self.checks[:2]:
            self.assertEqual(check["require"]["stdout_line"]["no_values_exist"],True)
            self.assertEqual(check["require"]["stdout_line"]["source_comparison"],
                             {"equals":""})
        # A source command Item with no stdout_line values is not the same
        # as the absence of the Item itself, which fails at_least_one.
        self.assertFalse(0>=1)
        self.assertTrue(1>=1)

    def test_signing_boolean_is_exactly_one_string_true(self):
        self.assertEqual(self.checks[2]["require"]["stdout_line"],
                         {"exactly_one_equals":"True"})
        # Not a generic Python bool, nor "some of repeated values == True".

    def test_lower_and_upper_states_separately_preserved_for_both_key_types(self):
        for check in self.checks[3:]:
            self.assertIs(check["all_state_fields_exist"],True)
            requirements=check["require"]["states"]["and"]
            self.assertEqual(len(requirements),2)
            self.assertEqual(requirements[0]["stdout_line"],{"greater_than_or_equal":48})
            self.assertEqual(requirements[1]["stdout_line"],{"less_than_or_equal":168})

    def test_zone_source_filters_are_not_all_dns_zones(self):
        src=self.doc["sources"]["list-all-forward-lookup-zones-object"]["collect"]["command"]
        self.assertIn("Forwarder",src)
        self.assertIn("TrustAnchors",src)
        self.assertIn("IsAutoCreated",src)
        self.assertIn("IsReverseLookupZone",src)
        self.assertIn("ZoneName",src)

    def test_zone_signing_and_key_signing_are_distinct_source_collections(self):
        variables=self.doc["metadata"]["variables"]
        self.assertEqual(len(variables),3)
        z=variables["command-get-list-dns-key-signature-validity-periods-zone-signing-variable"]
        k=variables["command-get-list-dns-key-signature-validity-periods-key-signing-variable"]
        def text(v):
            return "\n".join(str(x) for x in v["expression"]["concat"])
        self.assertIn("ZoneSigningKey",text(z))
        self.assertIn("KeySigningKey",text(k))
        self.assertIn("catch {Write-Output '0'}",text(z))
        self.assertIn("catch {Write-Output '0'}",text(k))
        self.assertIn("DnsKeySignatureValidityPeriod.Days",text(z))
        self.assertIn("DnsKeySignatureValidityPeriod.Hours",text(z))

    def test_failed_commands_do_not_automatically_become_error_by_flags(self):
        for check in self.checks:
            self.assertIs(check["collect"]["error_if_exit_status_not_0"],False)
            self.assertIs(check["collect"]["error_if_stderr_exists"],False)
        source=self.doc["sources"]["list-all-forward-lookup-zones-object"]["collect"]
        self.assertIs(source["error_if_exit_status_not_0"],False)
        self.assertIs(source["error_if_stderr_exists"],False)

    def test_native_none_zones_cannot_preserve_original_shell_item_existence(self):
        # Greenfield caching_only might accept a proven zero-zone collection.
        native_no_zones_is_true=True
        # But original source additionally requires at_least_one shell Item,
        # so zero shell Items is a definite False before inspecting stdout.
        source_empty_shell_item_set_satisfies_existence=(0>=1)
        self.assertTrue(native_no_zones_is_true)
        self.assertFalse(source_empty_shell_item_set_satisfies_existence)
        # This is only a structural counterexample, NOT evidence real
        # PowerShell invokes a zero-Item status in the particular scenario.

    def test_one_of_48_to_168_cannot_assume_numeric_coercion_or_field_cardinality(self):
        # A scalar between shorthand drops the source two distinct
        # whole-State comparisons and repeated stdout entity semantics.
        numeric_string="72"
        self.assertIsInstance(numeric_string,str)
        self.assertNotIsInstance(numeric_string,int)
        self.assertEqual([72,200].count(72),1)
        self.assertEqual(len([72,200]),2)

if __name__=="__main__":unittest.main()
