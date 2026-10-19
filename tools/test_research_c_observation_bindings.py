"""Refs #245: shared evidence remains shared, but independent policy outcomes differ."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_c_observation_bindings import freeze_observation,read_observation

def scope():
    return {"host":"test-host","snapshot":"scan-1",
            "execution_identity":"scanner-uid","environment":"shell-env-1",
            "provider_version":"0.4-A","input_fingerprint":"no-input",
            "parent_identity":"root-context"}

def request():
    return {"capability":"independent.shellcommand",
            "collect":{"shell":"bash","command":"source-exact",
                       "pattern":"Session",
                       "error_if_exit_status_not_0":False,
                       "error_if_stderr_exists":False}}

def evidence():
    return {"status":"complete",
            "items":[{"id":"item-a","fields":{"stdout_line":["Session On"]}},
                     {"id":"item-b","fields":{"stdout_line":["Session Off"]}}],
            "provenance":{"command":"source-exact","item_order":"document"}}

class SharedObservationEvidenceTests(unittest.TestCase):
    def test_same_collected_items_allow_different_rules_without_changing_fact(self):
        frozen=freeze_observation(request(),scope(),evidence())
        a=read_observation(frozen,request(),scope())
        b=read_observation(frozen,request(),scope())
        self.assertEqual(a,b)
        self.assertTrue(any("Session On" in row["fields"]["stdout_line"] for row in a["items"]))
        self.assertFalse(all("Session On" in row["fields"]["stdout_line"] for row in b["items"]))
        a["items"].clear()
        self.assertEqual(len(read_observation(frozen,request(),scope())["items"]),2)

    def test_collection_scope_is_part_of_observation_identity(self):
        frozen=freeze_observation(request(),scope(),evidence())
        for field in scope():
            changed=scope()
            changed[field]+="-changed"
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError,"boundary"):
                    read_observation(frozen,request(),changed)

    def test_acquisition_selectors_and_flags_are_not_interchangeable(self):
        frozen=freeze_observation(request(),scope(),evidence())
        for field,new in (("pattern","SessionCookieName"),
                          ("command","different command"),
                          ("shell","powershell"),
                          ("error_if_stderr_exists",True)):
            req=request()
            req["collect"][field]=new
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError,"boundary"):
                    read_observation(frozen,req,scope())

    def test_complete_empty_is_distinct_from_uncollected_and_error(self):
        for status in ("complete","incomplete","error","not_collected","not_applicable"):
            e={"status":status,"items":[],"provenance":{"source":"fixture"}}
            got=read_observation(freeze_observation(request(),scope(),e),
                                 request(),scope())
            self.assertEqual(got["status"],status)
            self.assertEqual(got["items"],[])

    def test_mutated_cached_evidence_is_rejected(self):
        frozen=freeze_observation(request(),scope(),evidence())
        frozen["evidence"]["items"].pop()
        with self.assertRaisesRegex(ValueError,"boundary"):
            read_observation(frozen,request(),scope())

    def test_duplicate_source_item_identifiers_are_rejected(self):
        e=evidence()
        e["items"][1]["id"]=e["items"][0]["id"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            freeze_observation(request(),scope(),e)

if __name__=="__main__":
    unittest.main()
