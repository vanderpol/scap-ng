#!/usr/bin/env python3
"""Real SCAP 1.4-derived Linux initialization-file authoring counterexamples.

Tests compare explicit simple-source constraints, NOT OVAL scanner parity.
"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import yaml
from research_linux_init_permissions import (
    ALLOWED_MODE,FLAG_BITS,mode_complies,eight_flag_comparisons,
    evaluate,per_user_required_root_files,only_these_bits
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"research/assessment-simplification/english-first-04/canonical-operators/linux-files.canonical.research.yaml"

def account(ident,uid,home,username=None):
    return {"id":ident,"uid":uid,"username":username or ident,"home_dir":home}

def file(ident,account_id,home,name=".bashrc",mode=0o700,kind="file"):
    return {"id":ident,"account_id":account_id,
            "directory":home,"name":name,"mode":mode,"kind":kind}

def scan(accounts,files,accounts_status="complete",files_status="complete"):
    return {"accounts":accounts,"files":files,"accounts_status":accounts_status,
            "files_status":files_status}

ROOT_1=account("root-one",0,"/root")
ROOT_2=account("root-two",0,"/srv/root-two")
USER=account("jane",1001,"/home/jane")

class LinuxInitializationSourceConstraintTests(unittest.TestCase):
    def test_all_4096_modes_same_result_as_eight_source_bit_checks(self):
        for mode in range(0o10000):
            with self.subTest(mode=oct(mode)):
                self.assertEqual(mode_complies(mode),all(eight_flag_comparisons(mode).values()))

    def test_typed_octal_operator_refuses_numeric_and_non_octal_literals(self):
        self.assertTrue(only_these_bits(0o600,"0740"))
        self.assertFalse(only_these_bits(0o644,"0740"))
        for value in (740,"740","0780","0o740",True,None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError,"four-digit octal STRING"):
                    only_these_bits(0o600,value)

    def test_gemini_ssh_mode_0400_is_subset_of_0600(self):
        from research_linux_init_permissions import only_these_bits
        self.assertTrue(only_these_bits(0o400,"0600"))
        self.assertTrue(only_these_bits(0o600,"0600"))
        self.assertFalse(only_these_bits(0o640,"0600"))
        self.assertFalse(only_these_bits(0o644,"0600"))
        # Owner UID and other SSH config policies remain independent.

    def test_numeric_less_than_0740_is_NOT_permission_subsetting(self):
        self.assertLessEqual(0o644,0o740)
        self.assertFalse(mode_complies(0o644)) # other_read is prohibited
        self.assertTrue(mode_complies(0o740))
        self.assertTrue(mode_complies(0o600))
        self.assertFalse(mode_complies(0o741))
        self.assertFalse(mode_complies(0o4740)) # setuid prohibited

    def test_zero_non_system_initialization_files_is_acceptable(self):
        self.assertEqual(evaluate(scan([ROOT_1,USER],[file("r",ROOT_1["id"],"/root")]),"non_system").result,"true")

    def test_zero_root_initialization_files_fails_globally(self):
        self.assertEqual(evaluate(scan([ROOT_1,USER],[file("u",USER["id"],"/home/jane")]),"root").result,"false")

    def test_two_root_users_one_with_no_files_merged_root_union_passes(self):
        snapshot=scan([ROOT_1,ROOT_2],[file("r2","root-two","/srv/root-two")])
        result=evaluate(snapshot,"root")
        self.assertEqual((result.result,result.accounts_selected,result.files_selected),("true",2,1))
        self.assertFalse(per_user_required_root_files(snapshot))
        # Proves earlier nested every-account/inner minimum=1 rewrite changes source logic.

    def test_one_root_bad_file_fails_even_if_another_file_is_good(self):
        snapshot=scan([ROOT_1,ROOT_2],[
            file("r1","root-one","/root",mode=0o600),
            file("r2","root-two","/srv/root-two",mode=0o644)
        ])
        self.assertEqual(evaluate(snapshot,"root").result,"false")

    def test_source_account_exclusion_excludes_home_directory_slash(self):
        snapshot=scan([account("root-top",0,"/"),ROOT_1],[
            file("top","root-top","/",mode=0o777),
            file("r1","root-one","/root",mode=0o600)])
        x=evaluate(snapshot,"root")
        self.assertEqual((x.result,x.accounts_selected,x.files_selected),("true",1,1))

    def test_non_matching_usernames_and_uid_excluded(self):
        snapshot=scan([USER,account("-invalid",1001,"/home/invalid",username="---"),
            account("system",999,"/home/system")],
            [file("u","jane","/home/jane",mode=0o700),
             file("bad","-invalid","/home/invalid",mode=0o777),
             file("bad2","system","/home/system",mode=0o777)])
        x=evaluate(snapshot,"non_system")
        self.assertEqual((x.result,x.accounts_selected,x.files_selected),("true",1,1))

    def test_dir_and_non_matching_hidden_names_do_not_enter_file_test(self):
        snapshot=scan([ROOT_1],[
            file("ordinary","root-one","/root",name="visible",mode=0o777),
            file("dot-dot","root-one","/root",name="..",mode=0o777),
            file("directory","root-one","/root",name=".config",kind="directory",mode=0o777),
            file("selected","root-one","/root",name=".profile",mode=0o600)])
        x=evaluate(snapshot,"root")
        self.assertEqual((x.result,x.files_selected),("true",1))

    def test_root_incomplete_cannot_confirm_no_files(self):
        snapshot=scan([ROOT_1],[],files_status="incomplete")
        self.assertEqual(evaluate(snapshot,"root").result,"unknown")

    def test_non_system_incomplete_zero_does_not_automatically_pass(self):
        snapshot=scan([USER],[],files_status="incomplete")
        self.assertEqual(evaluate(snapshot,"non_system").result,"unknown")

    def test_observed_violation_decisive_despite_incomplete_discovery(self):
        snapshot=scan([USER],[file("bad","jane","/home/jane",mode=0o644)],files_status="incomplete")
        self.assertEqual(evaluate(snapshot,"non_system").result,"false")

    def test_missing_user_field_cannot_be_silently_filtered(self):
        snapshot=scan([{"id":"incomplete-account","username":"jane","uid":1001}],[])
        self.assertEqual(evaluate(snapshot,"non_system").result,"unknown")

    def test_missing_mode_is_not_a_compliant_permission(self):
        snapshot=scan([ROOT_1],[{k:v for k,v in file("r1","root-one","/root").items() if k!="mode"}])
        self.assertEqual(evaluate(snapshot,"root").result,"unknown")

    def test_ambiguous_identity_denied(self):
        snapshot=scan([ROOT_1],[
            file("same","root-one","/root",mode=0o700),
            file("same","root-one","/root",mode=0o644)])
        self.assertEqual(evaluate(snapshot,"root").result,"error")

    def test_source_conscious_authoring_form_counts_global_root_files(self):
        research=(ROOT/"research/requirements-first-language/experiments/linux-init-global-population.yaml")
        new=yaml.safe_load(research.read_text())
        self.assertEqual(len(new["require"]["all"]),2)
        other,root=new["require"]["all"]
        self.assertEqual(other["each"],"linux.files")
        self.assertEqual(root["each"],"linux.files")
        self.assertNotIn("minimum_resources",other)
        self.assertEqual(root["minimum_resources"],1)
        for branch in (other,root):
            # The minimum count is outside the account-source mapping.
            # A per-account minimum would change the original union.
            self.assertEqual(branch["must"]["mode"],{"only_these_bits":"0740"})
            self.assertEqual(branch["using"]["from_account_homes"]["account_source"],"linux.accounts")
        self.assertEqual(other["using"]["from_account_homes"]["where"]["uid"],{"at_least":1000})
        self.assertEqual(root["using"]["from_account_homes"]["where"]["uid"],{"equals":0})

    def test_original_source_document_contract_is_pinned(self):
        doc=yaml.safe_load(SOURCE.read_text())
        self.assertEqual(doc["sources"]["users-username-object"]["where"]["username"]["matches_regex"],r"[\w]+")
        self.assertEqual(doc["sources"]["only-root-users-uid-0-home-dirs-excluding-root-directory-object"]["inspect"],"unix.password")
        self.assertEqual(doc["sources"]["only-non-system-users-uid-999-home-dirs-excluding-root-object"]["inspect"],"unix.password")
        checks=doc["checks"]
        root=next(v for k,v in checks.items() if k.startswith("local-initialization-files-root-"))
        user=next(v for k,v in checks.items() if k.startswith("local-initialization-files-non-system-users-"))
        self.assertEqual(root["require"]["items"],"at_least_one")
        self.assertEqual(user["require"]["items"],"if_present")
        self.assertEqual(root["require"]["match"],"all")
        self.assertEqual(user["require"]["match"],"all")
        for test in (root,user):
            self.assertEqual(test["require"]["fields"]["presence"],"all")
            eight=test["require"]["fields"]["and"]
            self.assertEqual({next(iter(v.keys())) for v in eight},set(FLAG_BITS))
            self.assertEqual(len(eight),8)
            self.assertTrue(all(next(iter(v.values()))=={"equals":False} for v in eight))
            traversal=test["gather"]["union"][0]["from"]["traversal"]
            self.assertEqual(traversal,{"max_depth":1,"recurse":"symlinks"})
            self.assertEqual(test["gather"]["union"][0]["exclude_if"],[{"type":{"is":"directory"}}])

if __name__=="__main__":unittest.main()
