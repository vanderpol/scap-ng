#!/usr/bin/env python3
"""Prove schema checks cannot be borrowed from unrelated XML exports."""
from copy import deepcopy
import unittest

from combine_v04_oval_xml_proofs import combine


def fixtures():
    src="a"*64
    native="b"*64
    first="c"*64
    second="d"*64
    cases=[{"case_id":f"Case {i}","status":"EQUAL","semantic_equal":True,
            "source_definition":f"oval:original:def:{i}",
            "regenerated_definition":"oval:scap-ng.v04.pilot:def:1",
            "source_sha256":src,"native_sha256":native,
            "regenerated_sha256":hashval}
           for i,hashval in enumerate((first,second),1)]
    report={"format":"scap-ng-v04-oval-xml-roundtrip-report-1",
            "status":"PASS","cases":cases}
    xsds=[{"status":"PASS","oval_schema_version":"5.12.3",
           "xml_sha256":h,"diagnostics":[]} for h in (first,second)]
    return report,xsds


class CombinedProofTests(unittest.TestCase):
    def test_complete_two_case_pilot(self):
        s,x=fixtures()
        r=combine(s,x)
        self.assertEqual(r["case_count"],2)
        self.assertEqual(r["status"],"PASS_LIMITED_040_NATIVE_ROUNDTRIP_PILOT")
        self.assertFalse(r["full_oval_xml_roundtrip_conformance"])

    def test_failed_or_cross_case_schema_evidence_fails(self):
        for mutate in (
            lambda s,x:x.pop(),
            lambda s,x:x[0].update(xml_sha256="f"*64),
            lambda s,x:x[0].update(status="FAIL"),
            lambda s,x:x[0].update(diagnostics=["bad filter"]),
            lambda s,x:x[0].update(oval_schema_version="5.11"),
            lambda s,x:x[0].update(xml_sha256=x[1]["xml_sha256"]),
            lambda s,x:s.update(status="FAIL"),
            lambda s,x:s["cases"][0].update(semantic_equal=False),
        ):
            s,x=fixtures()
            with self.subTest(mutation=str(mutate)),self.assertRaises(ValueError):
                mutate(s,x)
                combine(s,x)


if __name__=="__main__":
    unittest.main()
