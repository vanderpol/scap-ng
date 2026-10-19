"""Refs #245: native shared Apache fact probe, NOT SCAP 1.4 parity."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_apache_directive_observations import (
    observe_apache_directives,select_directives)

def original():
    return {"population":"main-plus-include-source",
            "status":"complete",
            "provenance":{"snapshot":"test","collection":"precollected-fixture"},
            "files":[
                {"id":"main-1","path":"/etc/httpd/conf/httpd.conf","lines":[
                    {"line":1,"text":"# Session Off"},
                    {"line":2,"text":"Session On"},
                    {"line":3,"text":"SessionCookieName sessionid HttpOnly Secure"}]},
                {"id":"inc-1","path":"/etc/httpd/conf.d/other.conf","lines":[
                    {"line":10,"text":"Session Off"},
                    {"line":20,"text":"SessionCookieName sessionid HttpOnly"}]},
            ]}

class ApacheSharedFactTests(unittest.TestCase):
    def test_one_file_population_feeds_two_independent_checks(self):
        snapshot=original()
        before=deepcopy(snapshot)
        observed=observe_apache_directives(snapshot)
        self.assertEqual(snapshot,before)
        sessions=select_directives(observed,"session")
        cookies=select_directives(observed,"sessioncookiename")
        self.assertEqual(len(sessions["items"]),2)
        self.assertEqual(len(cookies["items"]),2)
        self.assertEqual(sessions["items"][0]["id"],"main-1:2")
        self.assertEqual(cookies["items"][0]["id"],"main-1:3")
        # These are *two distinct policy views* of one observation.
        self.assertFalse(all(x["arguments"].lower()=="on" for x in sessions["items"]))
        self.assertFalse(all("httponly" in x["arguments"].lower() and
                             "secure" in x["arguments"].lower()
                             for x in cookies["items"]))
        self.assertEqual(sessions["status"],cookies["status"])
        self.assertFalse(sessions["evaluation_performed"])
        self.assertFalse(observed["legacy_shellcommand_parity_verified"])
        self.assertFalse(observed["scanner_executed"])

    def test_missing_and_partial_population_are_not_auto_passes(self):
        for status in ("complete","incomplete","error","not_collected","not_applicable"):
            snap={"population":"loaded-files",
                  "status":status,"files":[],"provenance":{"fixture":1}}
            result=observe_apache_directives(snap)
            for key in ("session","sessioncookiename"):
                observed=select_directives(result,key)
                self.assertEqual(observed["status"],status)
                self.assertEqual(observed["items"],[])
                self.assertFalse(observed["evaluation_performed"])
        snap=original()
        snap["status"]="incomplete"
        result=observe_apache_directives(snap)
        self.assertEqual(len(select_directives(result,"session")["items"]),2)
        self.assertEqual(result["status"],"incomplete")

    def test_strict_parent_and_line_identity_prevents_cross_file_laundering(self):
        result=observe_apache_directives(original())
        cookies=select_directives(result,"sessioncookiename")["items"]
        self.assertNotEqual(cookies[0]["file_id"],cookies[1]["file_id"])
        self.assertEqual(cookies[0]["line"],3)
        self.assertEqual(cookies[1]["line"],20)
        # A hypothetical separate-file flag cannot be joined into a good
        # single directive or asserted as source-equivalent.
        self.assertTrue("Secure" in cookies[0]["arguments"])
        self.assertFalse("Secure" in cookies[1]["arguments"])

    def test_mismatched_populations_do_not_become_one_collection(self):
        snap=original()
        a=observe_apache_directives(snap)
        snap["population"]="actually-loaded-DUMP_INCLUDES"
        b=observe_apache_directives(snap)
        self.assertNotEqual(a["population"],b["population"])

    def test_mutation_of_consumer_evidence_does_not_change_original(self):
        observed=observe_apache_directives(original())
        a=select_directives(observed,"session")
        a["items"][0]["arguments"]="Off"
        b=select_directives(observed,"session")
        self.assertEqual(b["items"][0]["arguments"],"On")

    def test_reject_duplicate_file_or_nonmonotonic_line_provenance(self):
        snap=original()
        snap["files"][1]["id"]="main-1"
        with self.assertRaisesRegex(ValueError,"identity"):
            observe_apache_directives(snap)
        snap=original()
        snap["files"][0]["lines"][1]["line"]=1
        with self.assertRaisesRegex(ValueError,"line identity"):
            observe_apache_directives(snap)

    def test_error_collection_does_not_reuse_partial_items_as_success(self):
        snap=original()
        snap["status"]="error"
        with self.assertRaisesRegex(ValueError,"untrusted"):
            observe_apache_directives(snap)

if __name__=="__main__":
    unittest.main()
