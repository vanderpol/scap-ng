#!/usr/bin/env python3
"""Windows DNS structured synthetic fixtures; no actual Windows DNS server."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_dns_zone_key_evidence import normalize

def zone(name,*,reverse=False,ad=True,signed=True,kind="Primary",auto=False):
    return {"ZoneName":name,"ZoneType":kind,"IsAutoCreated":auto,
            "IsReverseLookupZone":reverse,"IsDsIntegrated":ad,"IsSigned":signed}

def key(zone_name,ident,kind="ZoneSigningKey",days=2,hours=0):
    return {"KeyId":ident,"ZoneName":zone_name,"KeyType":kind,
            "Days":days,"Hours":hours}

class DnsEvidenceTests(unittest.TestCase):
    def test_reverse_zone_without_forward_zones(self):
        result=normalize([zone("1.168.192.in-addr.arpa",reverse=True)],[])
        self.assertEqual(result["status"],"complete")
        self.assertEqual(result["forward_zone_count"],0)
        self.assertEqual(result["zone_count"],1)

    def test_zero_zones_complete_is_known_empty_not_incomplete(self):
        result=normalize([],[])
        self.assertEqual(result["status"],"complete")
        self.assertEqual(result["forward_zone_count"],0)

    def test_partial_zero_zones_is_not_verified_absence(self):
        result=normalize([],[],zones_status="incomplete")
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["forward_zone_count"],0)

    def test_excluded_zone_classes_are_not_forward_zones(self):
        result=normalize([
            zone("TrustAnchors"),
            zone("autocreated.test",auto=True),
            zone("forwarder.test",kind="Forwarder"),
            zone("example.test",ad=False)],[])
        self.assertEqual(result["status"],"complete")
        self.assertEqual([x["name"] for x in result["zones"]],["example.test"])
        self.assertFalse(result["zones"][0]["directory_integration"])

    def test_both_signing_key_types_remain_distinct_per_zone(self):
        result=normalize([zone("corp.test")],
                         [key("corp.test","z1",days=2),
                          key("corp.test","k1",kind="KeySigningKey",days=7),
                          key("corp.test","z2",days=7,hours=1)])
        self.assertEqual(result["status"],"complete")
        one=result["zones"][0]
        self.assertEqual([x["validity_hours"] for x in one["zone_signing_keys"]],[48,169])
        self.assertEqual([x["validity_hours"] for x in one["key_signing_keys"]],[168])
        self.assertEqual(one["zone_signing_keys"][0]["zone_id"],one["id"])

    def test_an_unrelated_zone_key_is_never_silently_attached(self):
        result=normalize([zone("corp.test")],
                         [key("other.test","z9")])
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["zones"][0]["zone_signing_keys"],[])
        self.assertIn("key_parent_not_in_normalized_zones",
                      {x["reason"] for x in result["diagnostics"]})

    def test_missing_signature_or_zone_fields_are_not_known_nonmatches(self):
        row=zone("corp.test")
        del row["IsSigned"]
        result=normalize([row],[])
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["zones"],[])
        self.assertIn("zone_fields_missing",{x["reason"] for x in result["diagnostics"]})

    def test_missing_key_hours_are_not_numeric_zero(self):
        k=key("corp.test","z1")
        del k["Hours"]
        result=normalize([zone("corp.test")],[k])
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["zones"][0]["zone_signing_keys"],[])

    def test_numeric_text_is_not_implicitly_coerced(self):
        result=normalize([zone("corp.test")],
                         [key("corp.test","z1",days="2")])
        self.assertEqual(result["status"],"incomplete")
        self.assertIn("key_validity_typed_duration_invalid",
                      {x["reason"] for x in result["diagnostics"]})

    def test_duplicate_zone_names_case_insensitive_mark_incomplete(self):
        result=normalize([zone("corp.test"),zone("CORP.TEST")],[])
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["zone_count"],1)
        self.assertIn("duplicate_zone_identity",{x["reason"] for x in result["diagnostics"]})

    def test_duplicate_signing_key_ids_are_not_silently_deduplicated(self):
        result=normalize([zone("corp.test")],
                         [key("corp.test","dup"),key("corp.test","dup")])
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(len(result["zones"][0]["zone_signing_keys"]),1)
        self.assertIn("duplicate_signing_key_identity",
                      {x["reason"] for x in result["diagnostics"]})

    def test_bool_is_not_valid_numeric_hours(self):
        result=normalize([zone("corp.test")],
                         [key("corp.test","z1",days=True)])
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["zones"][0]["zone_signing_keys"],[])

    def test_partial_key_collection_is_not_an_empty_success(self):
        result=normalize([zone("corp.test")],[],keys_status="incomplete")
        self.assertEqual(result["status"],"incomplete")
        self.assertEqual(result["zones"][0]["key_signing_keys"],[])
        self.assertEqual(result["key_source_status"],"incomplete")

    def test_explicit_key_source_error_is_preserved(self):
        result=normalize([zone("corp.test")],[],keys_status="error")
        self.assertEqual(result["status"],"error")
        self.assertEqual(result["zone_count"],1)

    def test_signing_key_source_output_zero_on_exception_cannot_be_assumed_native(self):
        # Source-derived catch {Write-Output '0'} could create a string
        # comparison value 0. This provider uses typed duration fields and
        # does NOT replicate source's exception suppression behavior.
        result=normalize([zone("corp.test")],
                         [key("corp.test","k",kind="KeySigningKey",days=0,hours=0)])
        self.assertEqual(result["status"],"complete")
        self.assertEqual(result["zones"][0]["key_signing_keys"][0]["validity_hours"],0)
        self.assertLess(0,48)

if __name__=="__main__":unittest.main()
