#!/usr/bin/env python3
"""#235 native auditor one-AST contract proof against adversarial fixtures."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_native_contract_candidate import (
    EXAMPLES, PROVIDERS, StrictLoader, compile_doc, read)
from research_native_contract_evaluator import evaluate
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN,ERROR,NOT_APPLICABLE
import yaml

def sample(name):
    return read(EXAMPLES/name)["ast"]

def item(ident,**fields):
    return {"id":ident,"fields":fields}

def pop(*items,status="complete",using=None):
    evidence={"status":status,"items":list(items)}
    if using is not None:evidence["using"]=using
    return evidence

def run_case(name,evidence):
    tree=sample(name)
    return evaluate(tree,evidence)

MOUNT="01-required-home.yaml"
GUEST="02-optional-guest.yaml"
REG="03-named-registry.yaml"
APACHE="04-apache-two-settings.yaml"
DNS="05-dns-if-any.yaml"
WIN="06-windows-privilege-or.yaml"
LINUX="07-linux-permission-bits.yaml"

class CandidateBContractTests(unittest.TestCase):
    def test_all_eight_examples_compile_to_single_recursive_ast(self):
        files=sorted(EXAMPLES.glob("*.yaml"))
        self.assertEqual(len(files),8)
        for f in files:
            with self.subTest(file=f.name):
                tree=read(f)
                self.assertIn(tree["ast"]["kind"],{"logic","collection"})

    def test_required_vs_optional_verified_zero(self):
        self.assertEqual(run_case(MOUNT,{"linux.mounts":pop()}).result,FALSE)
        self.assertEqual(run_case(GUEST,{"windows.accounts":pop()}).result,TRUE)

    def test_raw_population_nonzero_but_no_selected_mount_still_fails(self):
        evidence=pop(item("var",mount_point="/var",mount_options=["rw","nosuid"]))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,FALSE)

    def test_every_requires_all_selected_mounts_compliant(self):
        evidence=pop(item("h1",mount_point="/home",mount_options=["rw","nosuid"]),
                     item("h2",mount_point="/home",mount_options=["rw"]))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,FALSE)

    def test_two_compliant_mounts_are_valid_population_not_singleton(self):
        evidence=pop(item("h1",mount_point="/home",mount_options=["rw","nosuid"]),
                     item("h2",mount_point="/home",mount_options=["rw","nosuid"]))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,TRUE)

    def test_incomplete_zero_does_not_satisfy_optional_guests(self):
        self.assertEqual(run_case(GUEST,{"windows.accounts":pop(status="incomplete")}).result,UNKNOWN)
        self.assertEqual(run_case(MOUNT,{"linux.mounts":pop(status="incomplete")}).result,UNKNOWN)

    def test_incomplete_but_known_violating_mount_decisively_fails(self):
        evidence=pop(item("h",mount_point="/home",mount_options=["rw"]),
                     status="incomplete")
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,FALSE)

    def test_incomplete_one_compliant_item_cannot_pass_every(self):
        evidence=pop(item("h",mount_point="/home",mount_options=["nosuid"]),
                     status="incomplete")
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,UNKNOWN)

    def test_missing_selector_is_unknown_not_omitted_as_false(self):
        evidence=pop(item("mystery",mount_options=["rw"]))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,UNKNOWN)

    def test_known_absent_selector_is_a_proven_nonmatch(self):
        evidence=pop(item("no-point",mount_point={"field_status":"absent"},
                          mount_options=["rw"]))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,FALSE)

    def test_unreadable_selector_is_error(self):
        evidence=pop(item("unreadable",mount_point={"field_status":"error"},
                          mount_options=["nosuid"]))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,ERROR)

    def test_known_absent_required_property_does_not_satisfy_requirement(self):
        evidence=pop(item("home",mount_point="/home",
                          mount_options={"field_status":"absent"}))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,FALSE)

    def test_unknown_required_property_is_not_false_by_default(self):
        evidence=pop(item("home",mount_point="/home",
                          mount_options={"field_status":"unknown"}))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,UNKNOWN)

    def test_unreadable_required_property_is_error(self):
        evidence=pop(item("home",mount_point="/home",
                          mount_options={"field_status":"error"}))
        self.assertEqual(run_case(MOUNT,{"linux.mounts":evidence}).result,ERROR)

    def test_duplicate_item_identity_is_error_not_pass(self):
        x=item("h",mount_point="/home",mount_options=["nosuid"])
        self.assertEqual(run_case(MOUNT,{"linux.mounts":pop(x,x)}).result,ERROR)

    def test_provider_error_distinct_from_noncompliance(self):
        self.assertEqual(run_case(MOUNT,{"linux.mounts":pop(status="error")}).result,ERROR)
        self.assertEqual(run_case(MOUNT,{"linux.mounts":pop(status="not collected")}).result,UNKNOWN)
        self.assertEqual(run_case(MOUNT,{"linux.mounts":pop(status="not applicable")}).result,NOT_APPLICABLE)

    def test_named_registry_compiles_to_exactly_one_with_singleton_contract(self):
        tree=sample(REG)
        self.assertEqual(tree["mode"],"exactly_one")
        self.assertTrue(tree["singleton"])
        using=tree["using"]
        self.assertEqual(run_case(REG,{"windows.registry_value":pop(
            item("registry",name="AlwaysInstallElevated",value=0),using=using)}).result,TRUE)
        self.assertEqual(run_case(REG,{"windows.registry_value":pop(using=using)}).result,FALSE)

    def test_named_registry_duplicate_provider_identity_is_error(self):
        using=sample(REG)["using"]
        evidence=pop(item("v1",name="AlwaysInstallElevated",value=0),
                     item("v2",name="AlwaysInstallElevated",value=0),using=using)
        self.assertEqual(run_case(REG,{"windows.registry_value":evidence}).result,ERROR)

    def test_named_registry_wrong_or_omitted_view_is_error(self):
        using=sample(REG)["using"]
        first=pop(item("v",value=0))
        self.assertEqual(run_case(REG,{"windows.registry_value":first}).result,ERROR)
        bad=copy.deepcopy(using)
        bad["view"]="32bit"
        self.assertEqual(run_case(REG,{"windows.registry_value":
                                         pop(item("v",value=0),using=bad)}).result,ERROR)

    def test_native_dns_reverse_only_zone_passes_optional_forward_policy(self):
        evidence=pop(item("reverse",name="a.in-addr.arpa",
                          direction="reverse",directory_integration=False,signed=False))
        self.assertEqual(run_case(DNS,{"windows.dns.zones":evidence}).result,TRUE)

    def test_native_dns_nonintegrated_forward_zone_fails(self):
        evidence=pop(item("forward",direction="forward",
                          directory_integration=False,signed=False))
        self.assertEqual(run_case(DNS,{"windows.dns.zones":evidence}).result,FALSE)

    def test_linux_native_bitmask_uses_typed_octals(self):
        using=sample(LINUX)["using"]
        ok=pop(item("f1",mode=0o600),using=using)
        bad=pop(item("f1",mode=0o644),using=using)
        self.assertEqual(run_case(LINUX,{"linux.files_from_account_homes":ok}).result,TRUE)
        self.assertEqual(run_case(LINUX,{"linux.files_from_account_homes":bad}).result,FALSE)

    def test_linux_root_file_global_minimum(self):
        using=sample(LINUX)["using"]
        self.assertEqual(run_case(LINUX,{"linux.files_from_account_homes":
                                         pop(using=using)}).result,FALSE)

    def test_windows_any_fallback_witness_works_without_member_role(self):
        tree=sample(WIN)
        using=tree["children"][1]["using"]
        fixtures={"windows.computer_role":pop(
            item("role",role="nonmember")),
            "windows.user_rights":pop(item("p",principal="Everyone",right="SeDenyRemoteInteractiveLogonRight"),
                                     using=using)}
        self.assertEqual(evaluate(tree,fixtures).result,TRUE)

    def test_windows_and_requires_guest_and_localaccount(self):
        tree=sample(WIN)
        rights=tree["children"][0]["children"][1]["using"]
        fixtures={"windows.computer_role":pop(item("role",role="domain_member")),
                  "windows.user_rights":pop(item("guest",principal="Guests"),
                                             item("local",principal="LocalAccount"),using=rights)}
        self.assertEqual(evaluate(tree,fixtures).result,TRUE)
        fixtures["windows.user_rights"]=pop(item("guest",principal="Guests"),using=rights)
        self.assertEqual(evaluate(tree,fixtures).result,FALSE)

    def test_boolean_or_true_remains_true_with_other_error(self):
        tree=sample(WIN)
        using=tree["children"][1]["using"]
        fixtures={"windows.computer_role":pop(status="error"),
                  "windows.user_rights":pop(item("everyone",principal="Everyone"),using=using)}
        self.assertEqual(evaluate(tree,fixtures).result,TRUE)

    def test_boolean_and_false_remains_false_with_other_error(self):
        tree=sample(APACHE)
        fixtures={"apache.config_directives":pop(
            item("a",name="KeepAlive",raw_value="Off"),
            item("b",name="MaxKeepAliveRequests",integer_value={"field_status":"error"}))}
        self.assertEqual(evaluate(tree,fixtures).result,FALSE)

    def test_real_apache_can_have_both_directives_but_not_source_parity(self):
        tree=sample(APACHE)
        fixtures={"apache.config_directives":pop(
            item("a",name="KeepAlive",raw_value="On"),
            item("b",name="MaxKeepAliveRequests",integer_value=150))}
        self.assertEqual(evaluate(tree,fixtures).result,TRUE)
        # This does not prove any of four OVAL shellcommand Items exist.

    def test_source_ast_rejects_nonnative_object_state_concepts(self):
        doc={"id":"x","title":"x","require":{"object":"a","state":"b"}}
        with self.assertRaisesRegex(ValueError,"exactly one"):
            compile_doc(doc)

    def test_unknown_typed_provider_rejected(self):
        doc={"id":"x","title":"x","require":{"each":"apache.stig_pass_verdict",
             "must":{"value":{"equals":True}}}}
        with self.assertRaisesRegex(ValueError,"unknown population"):
            compile_doc(doc)

    def test_named_registry_requires_all_acquisition_identifiers(self):
        doc={"id":"x","title":"x","require":{"resource":"windows.registry_value",
            "using":{"hive":"HKLM","key":"a","name":"b"},
            "must":{"value":{"equals":0}}}}
        with self.assertRaisesRegex(ValueError,"must exactly match"):
            compile_doc(doc)

    def test_field_predicate_typo_rejected_by_provider_catalog(self):
        doc={"id":"x","title":"x","require":{"each":"linux.mounts",
            "must":{"mount_pont":{"equals":"/home"}}}}
        with self.assertRaisesRegex(ValueError,"does not expose field"):
            compile_doc(doc)

    def test_untyped_numeric_bound_rejected(self):
        doc={"id":"x","title":"x","require":{"each":"windows.dns.zones",
            "must":{"directory_integration":{"at_least":"1"}}}}
        with self.assertRaisesRegex(ValueError,"typed numeric"):
            compile_doc(doc)

    def test_gemini_acquisition_options_unknown_key_rejected(self):
        doc={"id":"x","title":"x","require":{
            "each":"linux.files_from_account_homes",
            "acquisition_options":{"account_filter":{"uid":{"equals":0}}},
            "minimum_resources":1,
            "must":{"mode":{"only_these_bits":"0740"}}}}
        with self.assertRaisesRegex(ValueError,"unsupported population properties"):
            compile_doc(doc)

    def test_gemini_misspelled_account_home_field_rejected(self):
        using={"account_filter":{"uid":{"equals":0},
                "home_directory":{"not_equals":"/root"}},
               "filename":r"^\.[^\s\.]+","max_depth":1,
               "follow_symlinks":False}
        doc={"id":"x","title":"x","require":{
            "each":"linux.files_from_account_homes","using":using,
            "minimum_resources":1,"must":{"mode":{"only_these_bits":"0740"}}}}
        with self.assertRaisesRegex(ValueError,"unrecognized account field"):
            compile_doc(doc)

    def test_gemini_filename_dictionary_not_a_regex_rejected(self):
        using={"account_filter":{"uid":{"equals":0},
                "home_dir":{"not_equals":"/"}},
               "filename":{".bashrc":None,".profile":None},"max_depth":1,
               "follow_symlinks":False}
        doc={"id":"x","title":"x","require":{
            "each":"linux.files_from_account_homes","using":using,
            "minimum_resources":1,"must":{"mode":{"only_these_bits":"0740"}}}}
        with self.assertRaisesRegex(ValueError,"filename regular expression string"):
            compile_doc(doc)

    def test_gemini_unimplemented_depth_two_rejected_not_silent(self):
        using={"account_filter":{"uid":{"equals":0},
                "home_dir":{"not_equals":"/"}},
               "filename":r"^\.[^\s\.]+","max_depth":2,
               "follow_symlinks":False}
        doc={"id":"x","title":"x","require":{
            "each":"linux.files_from_account_homes","using":using,
            "minimum_resources":1,"must":{"mode":{"only_these_bits":"0740"}}}}
        with self.assertRaisesRegex(ValueError,"only depth 1"):
            compile_doc(doc)

    def test_gemini_wrong_octal_operator_rejected(self):
        using={"account_filter":{"uid":{"equals":0},
                "home_dir":{"not_equals":"/"}},
               "filename":r"^\.[^\s\.]+","max_depth":1,
               "follow_symlinks":False}
        doc={"id":"x","title":"x","require":{
            "each":"linux.files_from_account_homes","using":using,
            "minimum_resources":1,"must":{"permissions":{"octal_equals":"0740"}}}}
        with self.assertRaisesRegex(ValueError,"does not expose field"):
            compile_doc(doc)

    def test_bad_symlink_parameter_type_rejected(self):
        using={"account_filter":{"uid":{"equals":0}},
               "filename":r"^\.[^\s\.]+","max_depth":1,
               "follow_symlinks":"false"}
        doc={"id":"x","title":"x","require":{
            "each":"linux.files_from_account_homes","using":using,
            "minimum_resources":1,"must":{"mode":{"only_these_bits":"0740"}}}}
        with self.assertRaisesRegex(ValueError,"must be a Boolean"):
            compile_doc(doc)

    def test_unapproved_bitmask_non_octal_rejected(self):
        doc={"id":"x","title":"x","require":{"each":"linux.files_from_account_homes",
            "using":{"account_filter":{},"filename":"x","max_depth":1,"follow_symlinks":False},
            "must":{"mode":{"only_these_bits":740}}}}
        with self.assertRaisesRegex(ValueError,"four-digit octal"):
            compile_doc(doc)

    def test_invalid_duplicate_yaml_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate YAML key"):
            yaml.load("id: one\nid: two\n",Loader=StrictLoader)

    def test_unregistered_child_relation_rejected(self):
        doc={"id":"x","title":"x","require":{
            "each":"windows.dns.zones","as":"zone",
            "must":{"each":"$zone.unknown_children",
                    "minimum_resources":1,
                    "must":{"validity_hours":{"between":[48,168]}}}}}
        with self.assertRaisesRegex(ValueError,"undeclared typed child relation"):
            compile_doc(doc)

    def test_signed_zone_has_two_explicit_and_complete_key_populations(self):
        tree=sample("08-dns-signing-nested.yaml")
        self.assertEqual(tree["as"],"zone")
        self.assertEqual(tree["nested"]["kind"],"logic")
        self.assertEqual(len(tree["nested"]["children"]),3)
        self.assertEqual(tree["nested"]["children"][1]["parent_ref"],
                         {"alias":"zone","relation":"zone_signing_keys"})

        def signing_child(ident,kind,value,zone_id="zone"):
            return item(ident,zone_id=zone_id,kind=kind,validity_hours=value)
        good_zone=item("zone",direction="forward",signed=True,
            zone_signing_keys=pop(signing_child("z","ZoneSigningKey",72)),
            key_signing_keys=pop(signing_child("k","KeySigningKey",168)))
        fixtures={"windows.dns.zones":pop(good_zone)}
        self.assertEqual(evaluate(tree,fixtures).result,TRUE)
        bad_key=copy.deepcopy(good_zone)
        bad_key["fields"]["zone_signing_keys"]["items"][0]["fields"]["validity_hours"]=169
        self.assertEqual(evaluate(tree,{"windows.dns.zones":pop(bad_key)}).result,FALSE)

    def test_nested_mismatched_zone_key_fails_closed(self):
        zone=item("zone",direction="forward",signed=True,
             zone_signing_keys=pop(item("z",zone_id="other",kind="ZoneSigningKey",validity_hours=72)),
             key_signing_keys=pop(item("k",zone_id="zone",kind="KeySigningKey",validity_hours=72)))
        self.assertEqual(evaluate(sample("08-dns-signing-nested.yaml"),
                                  {"windows.dns.zones":pop(zone)}).result,ERROR)

    def test_nested_child_without_explicit_status_cannot_pass(self):
        zone=item("zone",direction="forward",signed=True,
             zone_signing_keys=[item("z",zone_id="zone",validity_hours=72)],
             key_signing_keys=pop(item("k",zone_id="zone",validity_hours=72)))
        self.assertEqual(evaluate(sample("08-dns-signing-nested.yaml"),
                                  {"windows.dns.zones":pop(zone)}).result,UNKNOWN)

    def test_nested_child_partial_evidence_cannot_pass(self):
        zone=item("zone",direction="forward",signed=True,
             zone_signing_keys=pop(item("z",zone_id="zone",validity_hours=72),status="incomplete"),
             key_signing_keys=pop(item("k",zone_id="zone",validity_hours=72)))
        self.assertEqual(evaluate(sample("08-dns-signing-nested.yaml"),
                                  {"windows.dns.zones":pop(zone)}).result,UNKNOWN)

    def test_each_outer_zone_has_own_key_populations(self):
        z1=item("one",direction="forward",signed=True,
             zone_signing_keys=pop(item("z1",zone_id="one",validity_hours=72)),
             key_signing_keys=pop(item("k1",zone_id="one",validity_hours=72)))
        z2=item("two",direction="forward",signed=True,
             zone_signing_keys=pop(item("z2",zone_id="two",validity_hours=72)),
             key_signing_keys=pop())
        self.assertEqual(evaluate(sample("08-dns-signing-nested.yaml"),
                                  {"windows.dns.zones":pop(z1,z2)}).result,FALSE)
        # A compliant key found for zone one cannot satisfy zone two.

    def test_nested_no_forward_zone_is_not_a_required_signing_population(self):
        self.assertEqual(evaluate(sample("08-dns-signing-nested.yaml"),
                                  {"windows.dns.zones":pop()}).result,FALSE)
        # Distinct from optional DNS Active Directory integration rule.

if __name__=="__main__":unittest.main()
