"""Refs #245: two independent native rules use one Apache line observation."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_apache_directive_observations import observe_apache_directives
from research_c_apache_directive_requirements import evaluate_directive_requirement

def observed(lines, status="complete"):
    return observe_apache_directives({
        "population":"specific-loaded-file-population",
        "status":status,
        "provenance":{"source":"precollected-test","snapshot":"one"},
        "files":[{"id":"file-1","path":"/etc/httpd/conf/httpd.conf",
                  "lines":[{"line":i+1,"text":v} for i,v in enumerate(lines)]}]
                if status in ("complete","incomplete") and lines else []})

def check(obs, directive="session", every=True):
    return evaluate_directive_requirement(
        obs,directive,expected="on" if directive=="session"
        else ("httponly","secure"),every_item=every)

class NativeSharedFactOutcomes(unittest.TestCase):
    def test_same_observation_supplies_two_policies(self):
        o=observed(["Session On","Session Off",
                    "SessionCookieName sid HttpOnly Secure",
                    "SessionCookieName sid HttpOnly"])
        self.assertEqual(check(o,"session",True)["outcome"],"false")
        self.assertEqual(check(o,"session",False)["outcome"],"true")
        self.assertEqual(check(o,"sessioncookiename",True)["outcome"],"false")
        self.assertEqual(check(o,"sessioncookiename",False)["outcome"],"true")
        self.assertTrue(check(o,"session")["native_policy_not_source_equivalent"])

    def test_both_pass_using_one_good_item_per_requirement(self):
        o=observed(["Session On","SessionCookieName sid HttpOnly Secure"])
        self.assertEqual(check(o,"session")["outcome"],"true")
        self.assertEqual(check(o,"sessioncookiename")["outcome"],"true")

    def test_no_data_and_failed_acquisition_are_not_pass(self):
        for status,result in (("complete","false"),("incomplete","unknown"),
                              ("error","error"),("not_collected","unknown"),
                              ("not_applicable","not_applicable")):
            o=observed([],status)
            with self.subTest(status=status):
                self.assertEqual(check(o)["outcome"],result)
                self.assertEqual(check(o,"sessioncookiename")["outcome"],result)

    def test_incomplete_evidence_respects_item_quantifier(self):
        good=observed(["Session On"],"incomplete")
        bad=observed(["Session Off"],"incomplete")
        self.assertEqual(check(good,every=True)["outcome"],"unknown")
        self.assertEqual(check(good,every=False)["outcome"],"true")
        self.assertEqual(check(bad,every=True)["outcome"],"false")
        self.assertEqual(check(bad,every=False)["outcome"],"unknown")

    def test_declared_policy_cannot_coerce_into_other_directives(self):
        o=observed(["Session On"])
        with self.assertRaises(ValueError):
            evaluate_directive_requirement(o,"session",expected="Off",every_item=True)
        with self.assertRaises(ValueError):
            evaluate_directive_requirement(o,"sessioncookiename",
                                           expected=("Secure",),every_item=True)

if __name__=="__main__":
    unittest.main()
