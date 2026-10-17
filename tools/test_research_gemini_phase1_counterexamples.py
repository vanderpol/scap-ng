#!/usr/bin/env python3
"""#235 independent first-read failures: semantic differences, not a 'grade'.

These tests are separate from unchanged Gemini Phase 1 response. They compare
the actual research language/known source intent against novice paraphrases
and proposed substitute syntax. No OVAL scanner or actual Windows/Apache host.
"""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_native_contract_candidate import EXAMPLES,read
from research_native_contract_evaluator import evaluate
from research_linux_init_permissions import only_these_bits
from oval_result_truth_tables import TRUE,FALSE

def item(id,**fields):
    return {"id":id,"fields":fields}

class FirstReadCounterexamples(unittest.TestCase):
    def test_apache_at_least_one_good_each_kind_is_NOT_sufficient(self):
        native=read(EXAMPLES/"04-apache-two-settings.yaml")["ast"]
        complete={"status":"complete","items":[
            item("keepalive-good",name="KeepAlive",raw_value="On"),
            item("keepalive-bad",name="KeepAlive",raw_value="Off"),
            item("max-okay",name="MaxKeepAliveRequests",integer_value=150),
        ]}
        result=evaluate(native,{"apache.config_directives":complete})
        self.assertEqual(result.result,FALSE)
        # Gemini paraphrased the rule as requiring at least ONE passing
        # directive per type, which is too weak for EACH + MUST.
        naive_any_compliant_keepalive=True
        naive_any_acceptable_max=True
        self.assertTrue(naive_any_compliant_keepalive and naive_any_acceptable_max)

    def test_correct_root_exclusion_is_slash_not_slash_root(self):
        # Two UID-0 accounts illustrate the semantic reversal.
        roots=[{"uid":0,"home_dir":"/"},{"uid":0,"home_dir":"/root"}]
        correct=[x for x in roots if x["uid"]==0 and x["home_dir"]!="/"]
        gemini=[x for x in roots if x["uid"]==0 and x["home_dir"]!="/root"]
        self.assertEqual([x["home_dir"] for x in correct],["/root"])
        self.assertEqual([x["home_dir"] for x in gemini],["/"])
        self.assertNotEqual(correct,gemini)

    def test_exclusively_named_dotfiles_not_equivalent_to_hidden_file_pattern(self):
        source_matching=[".bashrc",".profile",".bash_logout"]
        gemini_named={".bashrc",".profile"}
        self.assertTrue(".bash_logout" not in gemini_named)
        self.assertTrue(".bash_logout" in source_matching)
        # Whether the author must use a regex vs a named file list is a
        # capability decision. This user-proposed list omits a matching file.

    def test_permission_exact_equality_changes_allowable_set(self):
        self.assertTrue(only_these_bits(0o600,"0740"))
        self.assertNotEqual(0o600,0o740)
        self.assertFalse(only_these_bits(0o644,"0740"))
        # Octal equals would incorrectly reject a safely more restrictive
        # mode even with correctly acquired file evidence.

    def test_native_dns_requires_both_key_kinds_and_each_child_within_range(self):
        original=read(EXAMPLES/"08-dns-signing-nested.yaml")["ast"]
        keys=original["nested"]["children"]
        self.assertEqual(len(keys),3)
        self.assertEqual(keys[1]["parent_ref"]["relation"],"zone_signing_keys")
        self.assertEqual(keys[2]["parent_ref"]["relation"],"key_signing_keys")
        # Gemini alternative listed only a ZoneSigningKey subresource;
        # KSKs disappear, so it cannot be called equivalent as written.
        self.assertNotEqual(keys[1]["parent_ref"],keys[2]["parent_ref"])

    def test_native_guest_policy_verified_complete_empty_is_true(self):
        original=read(EXAMPLES/"02-optional-guest.yaml")["ast"]
        result=evaluate(original,{"windows.accounts":{"status":"complete","items":[]}})
        self.assertEqual(result.result,TRUE)
        incomplete=evaluate(original,{"windows.accounts":{"status":"incomplete","items":[]}})
        self.assertNotEqual(incomplete.result,TRUE)

if __name__=="__main__":unittest.main()
