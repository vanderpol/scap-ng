"""Refs #245: independent cross-Rule shared-observation source pinning."""
from copy import deepcopy
import unittest

from research_c_external_observations import (
    catalog_digest,resolve_external_observations,compile_c_pinned_catalog
)
from research_c_one_frontend import normalize_c_frontend

ENTRY={"from":{"windows.passwordpolicy":{}}}
REF="shared/windows/password_policy@2026-10"

def assessment(name):
    return {
        "id":name,
        "observations":{"password_policy":{"use":REF,"sha256":catalog_digest(ENTRY)}},
        "checks":{name:{"observation":"password_policy",
                        "must":{"every_item":{"password_hist_len":{
                            "greater_than_or_equal":24}}}}},
        "require":{"check":name},
    }

class ExternalObservationResearchTests(unittest.TestCase):
    def test_independent_assessments_resolve_same_pinned_source(self):
        catalog={REF:ENTRY}
        a,b=assessment("first"),assessment("second")
        original_a,original_b=deepcopy(a),deepcopy(b)
        x,y=(resolve_external_observations(doc,catalog) for doc in (a,b))
        self.assertEqual(a,original_a)
        self.assertEqual(b,original_b)
        self.assertEqual(x["pinned_catalog_dependencies"][0]["sha256"],
                         y["pinned_catalog_dependencies"][0]["sha256"])
        for res in (x,y):
            view=normalize_c_frontend(res["resolved_C_ast"])
            self.assertEqual(
                view["observations"]["password_policy"]["from"]["arguments"],{})
            self.assertFalse(res["catalog_signature_verified"])
            self.assertFalse(res["cross_rule_runtime_collection_sharing_verified"])
            self.assertFalse(res["source_oval_parity_verified"])

    def test_changed_source_same_version_rejected(self):
        a=assessment("first");old=deepcopy(a)
        changed={REF:{"from":{"windows.passwordpolicy":{"altered":"scope"}}}}
        with self.assertRaisesRegex(ValueError,"digest mismatch"):
            resolve_external_observations(a,changed)
        self.assertEqual(a,old)

    def test_unresolved_or_unpinned_version_rejected(self):
        a=assessment("first")
        with self.assertRaisesRegex(ValueError,"unresolved"):
            resolve_external_observations(a,{})
        a["observations"]["password_policy"]["use"]="shared/windows/password_policy"
        with self.assertRaisesRegex(ValueError,"version-pinned"):
            resolve_external_observations(a,{REF:ENTRY})

    def test_inline_and_import_conflict_rejected(self):
        a=assessment("first")
        a["observations"]["password_policy"]["from"]=ENTRY["from"]
        with self.assertRaisesRegex(ValueError,"requires use and immutable digest only"):
            resolve_external_observations(a,{REF:ENTRY})

    def test_broken_short_or_uppercase_hash_rejected(self):
        for digest in ("deadbeef","X"*64,"A"*64,0,None):
            a=assessment("first")
            a["observations"]["password_policy"]["sha256"]=digest
            with self.subTest(digest=digest),self.assertRaisesRegex(
                ValueError,"full lowercase SHA-256"
            ):
                resolve_external_observations(a,{REF:ENTRY})

    def test_source_object_provenance_preserved(self):
        source={"from":{"unix.file":{"full_path":"/etc/passwd"}},
                "source_object":"file-ident"}
        ref="shared/linux/account_files@1"
        a=assessment("first")
        a["observations"]["password_policy"]={
            "use":ref,"sha256":catalog_digest(source)}
        result=resolve_external_observations(a,{ref:source})
        self.assertEqual(
            result["resolved_C_ast"]["observations"]["password_policy"]["source_object"],
            "file-ident")

    def test_other_version_never_binds_implicitly(self):
        a=assessment("first")
        with self.assertRaisesRegex(ValueError,"unresolved"):
            resolve_external_observations(
                a,{"shared/windows/password_policy@2025-01":ENTRY})

    def test_noncanonical_catalog_content_rejected(self):
        with self.assertRaises(ValueError):
            catalog_digest({"from":{"windows.passwordpolicy":{"nan":float("nan")}}})
        with self.assertRaises(ValueError):
            catalog_digest({"from":{"windows.passwordpolicy":{}},"extra":"unsafe"})

    def test_catalog_import_compiles_into_two_independent_native_A_checks(self):
        first=assessment("first")
        second=assessment("second")
        second["checks"]["second"]["must"]={
            "every_item":{"password_complexity":True}}
        x=compile_c_pinned_catalog(first,{REF:ENTRY})
        y=compile_c_pinned_catalog(second,{REF:ENTRY})
        self.assertNotIn("object",x["compiled"]["tests"]["first"])
        self.assertNotIn("object",y["compiled"]["tests"]["second"])
        self.assertEqual(x["catalog_dependencies"][0]["sha256"],
                         y["catalog_dependencies"][0]["sha256"])
        self.assertFalse(x["catalog_signature_verified"])
        self.assertFalse(x["cross_rule_runtime_collection_sharing_verified"])

    def test_cross_rule_same_scoped_evidence_read_twice_but_not_recollected(self):
        from research_c_observation_bindings import (
            freeze_observation,read_observation
        )
        cat={REF:ENTRY}
        a,b=(resolve_external_observations(assessment(i),cat)
             for i in ("one","two"))
        req=a["resolved_C_ast"]["observations"]["password_policy"]["from"]
        self.assertEqual(req,
                         b["resolved_C_ast"]["observations"]["password_policy"]["from"])
        scope={
            "host":"target-1","snapshot":"scan-1",
            "execution_identity":"scanner-admin",
            "environment":"system-env","provider_version":"v0.4-A",
            "input_fingerprint":"none","parent_identity":"root",
        }
        evidence={
            "status":"complete",
            "items":[{"id":"policy-item","fields":{"history":24}}],
            "provenance":{"source":"typed-test-fixture"},
        }
        frozen=freeze_observation(req,scope,evidence)
        first=read_observation(frozen,req,scope)
        second=read_observation(frozen,req,scope)
        self.assertEqual(first,second)
        self.assertFalse(frozen["runtime_collector_executed"])
        self.assertFalse(frozen["source_oval_parity_verified"])
        first["items"].clear()
        self.assertEqual(len(read_observation(frozen,req,scope)["items"]),1)
        for field in scope:
            other=dict(scope);other[field]+="-different"
            with self.subTest(field=field),self.assertRaisesRegex(
                ValueError,"boundary"
            ):
                read_observation(frozen,req,other)

    def test_cross_rule_partial_and_error_observations_never_upgrade_status(self):
        from research_c_observation_bindings import (
            freeze_observation,read_observation
        )
        request={"windows.passwordpolicy":{}}
        scope={
            "host":"target-1","snapshot":"scan-1",
            "execution_identity":"scanner-admin",
            "environment":"system-env","provider_version":"v0.4-A",
            "input_fingerprint":"none","parent_identity":"root",
        }
        for status in ("complete","incomplete","error",
                       "not_collected","not_applicable"):
            evidence={
                "status":status,"items":[],
                "provenance":{"source":"typed-test-fixture"},
            }
            frozen=freeze_observation(request,scope,evidence)
            got=read_observation(frozen,request,scope)
            with self.subTest(status=status):
                self.assertEqual(got["status"],status)
                self.assertEqual(got["items"],[])

if __name__=="__main__":
    unittest.main()
