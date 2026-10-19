#!/usr/bin/env python3
"""Refs #245: C form shape reduces visible layers without losing record truth."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_require_language import parse_c_yaml
from research_c_guided_observations import project_c_shared_guided

SOURCE=Path(__file__).resolve().parents[1]/(
    "research/assessment-simplification/compact-authoring-04/"
    "c-source-exact-windows-rdp-rights.research.yaml")

class WindowsSharedGuidedView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=parse_c_yaml(SOURCE.read_text(encoding="utf-8"))
        cls.view=project_c_shared_guided(cls.doc)

    def test_no_source_mutation_and_no_authoritative_result(self):
        original=deepcopy(self.doc)
        v=project_c_shared_guided(self.doc)
        self.assertEqual(self.doc,original)
        self.assertFalse(v["source_yaml_mutated"])
        self.assertEqual(v["scanner_verification"],"NOT_SCANNER_VERIFIED")
        self.assertEqual(v["native_specification"],"0.4.0")

    def test_two_sources_one_tree_seven_checks(self):
        v=self.view
        self.assertEqual(v["distinct_observations"],2)
        self.assertEqual(v["distinct_checks"],7)
        self.assertEqual(len(v["requirement_tree"]["children"]),3)
        self.assertEqual(v["requirement_tree"]["kind"],"one_of")
        self.assertEqual([len(x["children"])
                         for x in v["requirement_tree"]["children"][:2]],[5,2])
        self.assertEqual(v["observations"][0]["capability"],"windows.wmi.query")
        self.assertEqual(v["observations"][1]["capability"],"windows.userright")

    def test_all_uses_link_to_shared_observations_without_duplication(self):
        sources={x["id"]:x["used_by"] for x in self.view["observations"]}
        self.assertEqual(len(sources["system_role"]),2)
        self.assertEqual(len(sources["denied_remote_logon_trustees"]),5)
        self.assertEqual(set(x["using_observation"] for x in self.view["checks"]),
                         set(sources))
        guests=[x for x in self.view["checks"] if x["id"]=="deny_guests"]
        self.assertEqual(len(guests),1)
        self.assertEqual(guests[0]["source_test"],
                         "deny-log-on-through-remote-desktop-services-guests-test")
        self.assertEqual(guests[0]["item_scope"],"any_item")

    def test_wmi_card_exposes_record_alternatives_not_unproven_in_operator(self):
        cards={x["id"]:x for x in self.view["checks"]}
        for name,values in (("domain_joined_non_dc",["1","3"]),
                            ("standalone",["0","2"])):
            card=cards[name]
            self.assertEqual(card["item_scope"],"every_item")
            self.assertEqual(
                card["record_or_field_details"]["whole_record_state_alternatives"],
                values)
            self.assertTrue(
                card["record_or_field_details"]["not_equivalent_to_some_value_in_set"])
            self.assertEqual(card["source_compatible_test_requirement"],
                             "at_least_one_exists_and_all_match")
            self.assertTrue(card["complex_record_requires_expert_disclosure"])

    def test_rights_cards_retain_operator_and_cardinality(self):
        cards={x["id"]:x for x in self.view["checks"]}
        for label in ("deny_local_accounts","deny_guests","deny_domain_admins",
                      "deny_enterprise_admins","deny_everyone"):
            card=cards[label]
            self.assertEqual(card["item_scope"],"any_item")
            self.assertEqual(card["source_compatible_test_requirement"],
                             "at_least_one_exists_and_some_match")
            self.assertEqual(card["record_or_field_details"]["same_item_field"],
                             "trustee_name")
            self.assertEqual(card["record_or_field_details"]["field_requirement"],
                             "at_least_one_exists_and_all_match")
        self.assertFalse(cards["deny_domain_admins"]["record_or_field_details"][
            "regex_dialect_verified"])

    def test_unknown_scope_or_field_is_not_hidden_by_interface(self):
        bad=deepcopy(self.doc)
        bad["checks"]["domain_joined_non_dc"]["must"]["record_requirement"]="optional"
        with self.assertRaises(ValueError):
            project_c_shared_guided(bad)
        bad=deepcopy(self.doc)
        bad["checks"]["deny_local_accounts"]["must"]["same_item_field"]="recorded_user"
        with self.assertRaises(ValueError):
            project_c_shared_guided(bad)

    def test_renaming_source_collection_selector_invalidates_native_contract(self):
        bad=deepcopy(self.doc)
        bad["observations"]["system_role"]["from"]["windows.wmi.query"]["namespace"]=None
        with self.assertRaises(ValueError):
            project_c_shared_guided(bad)

if __name__=="__main__":
    unittest.main()
