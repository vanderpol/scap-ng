#!/usr/bin/env python3
"""Regression tests for source-invalid automated Assessment quarantine."""
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scap_upconvert_v003 import convert_collection_review as review


def check(selector, *, manual=False, definition="oval:test:def:1"):
    node=ET.Element("{"+review.NS["x"]+"}check")
    node.set("selector",selector)
    if manual:
        content=ET.SubElement(node,"{"+review.NS["x"]+"}check-content")
        content.text="Verify this requirement manually."
    else:
        ref=ET.SubElement(node,"{"+review.NS["x"]+"}check-content-ref")
        ref.set("href","oval.xml")
        ref.set("name",definition)
    return node


class SourceDefectQuarantineTests(unittest.TestCase):
    def rec(self):
        return {
            "id":"SV-TEST",
            "title":"Test rule",
            "checks":[
                check("default",definition="oval:test:def:bad"),
                check("automated",definition="oval:test:def:bad"),
                check("manual",manual=True),
            ],
        }

    def test_classifier_is_narrow(self):
        self.assertEqual(
            review.source_defect_reason("invalid_oval_record_datatype"),
            "invalid_oval_record_datatype",
        )
        self.assertEqual(
            review.source_defect_reason(
                "test_collection_capability_mismatch:unix.file!=independent.shellcommand"
            ),
            "test_collection_capability_mismatch",
        )
        self.assertEqual(
            review.source_defect_reason("Filter capability mismatch: example"),
            "filter_collection_capability_mismatch",
        )
        self.assertIsNone(review.source_defect_reason("definition_not_found"))
        self.assertIsNone(review.source_defect_reason("roundtrip_mismatch"))

    def test_known_source_defect_uses_verified_manual_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            tmp=root/"tmp"
            tmp.mkdir()
            original=ET.Element("{"+review.OD+"}oval_definitions")
            with patch.object(
                review,
                "unsupported_definition_features",
                return_value=[],
            ), patch.object(
                review,
                "lower_definition",
                return_value=(None,"invalid_oval_record_datatype"),
            ):
                result,failed=review.convert_rule(
                    self.rec(),original,root,None,tmp
                )

            self.assertFalse(failed)
            self.assertIn("manual",result["selectors"])
            self.assertEqual(
                result["selectors"]["default"],
                result["selectors"]["manual"],
            )
            self.assertNotIn("automated",result["selectors"])
            self.assertEqual(
                result["source_defect_fallbacks"][0]["classification"],
                "source_content_defect",
            )
            self.assertEqual(
                result["source_defect_fallbacks"][0]["error"],
                "invalid_oval_record_datatype",
            )
            self.assertTrue(
                (root/result["selectors"]["manual"]).exists()
            )
            self.assertFalse((root/"assessments"/"automated").exists())

    def test_unknown_error_still_blocks_even_with_manual(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            tmp=root/"tmp"
            tmp.mkdir()
            original=ET.Element("{"+review.OD+"}oval_definitions")
            with patch.object(
                review,
                "unsupported_definition_features",
                return_value=[],
            ), patch.object(
                review,
                "lower_definition",
                return_value=(None,"definition_not_found"),
            ):
                result,failed=review.convert_rule(
                    self.rec(),original,root,None,tmp
                )

            self.assertTrue(failed)
            blocked=[
                row for row in result["assessments"]
                if row.get("status")=="blocked"
            ]
            self.assertTrue(blocked)
            self.assertNotIn("source_defect_fallbacks",result)


if __name__=="__main__":
    unittest.main()
