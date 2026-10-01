#!/usr/bin/env python3
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))

from result_messages import render_core_message


class ResultMessageTests(unittest.TestCase):
    def test_unexpected_existence(self):
        self.assertEqual(
            "Expected no matching items; observed 2 matching items.",
            render_core_message({"code":"unexpected_existence","observed_count":2}),
        )

    def test_required_item_missing(self):
        self.assertEqual(
            "Required item was not found: /etc/example.",
            render_core_message({
                "code":"required_item_missing",
                "requirement":"/etc/example",
            }),
        )

    def test_required_match_missing(self):
        self.assertEqual(
            "No collected item satisfied the required condition: mode = 0644.",
            render_core_message({
                "code":"required_match_missing",
                "requirement":"mode = 0644",
            }),
        )

    def test_value_mismatch(self):
        self.assertEqual(
            "mode: observed '0666'; expected '0644'.",
            render_core_message({
                "code":"value_mismatch",
                "field":"mode",
                "observed":"0666",
                "expected":"0644",
            }),
        )

    def test_cardinality_mismatch(self):
        self.assertEqual(
            "Observed 3 matching items; expected cardinality exactly_one.",
            render_core_message({
                "code":"cardinality_mismatch",
                "observed_count":3,
                "expected":"exactly_one",
            }),
        )

    def test_collection_error(self):
        self.assertEqual(
            "Collection failed for capability linux.rpm.",
            render_core_message({
                "code":"collection_error",
                "capability":"linux.rpm",
            }),
        )

    def test_missing_organizational_input(self):
        self.assertEqual(
            "Required organizational input is missing: password_age.",
            render_core_message({
                "code":"missing_organizational_input",
                "input":"password_age",
            }),
        )

    def test_missing_required_value_mismatch_fields_is_rejected(self):
        with self.assertRaises(ValueError):
            render_core_message({"code":"value_mismatch","observed":"0666"})

    def test_unknown_reason_is_rejected(self):
        with self.assertRaises(ValueError):
            render_core_message({"code":"vendor_custom"})


if __name__=="__main__":
    unittest.main()
