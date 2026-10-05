#!/usr/bin/env python3
import unittest

from source_content_authorship import author_from_oval_definition_id


class SourceContentAuthorshipTests(unittest.TestCase):
    def test_disa_definition(self):
        self.assertEqual(
            author_from_oval_definition_id("oval:mil.disa.stig.windows11:def:253254"),
            "DISA",
        )

    def test_navwar_definition(self):
        self.assertEqual(
            author_from_oval_definition_id(
                "oval:navy.navwar.niwcatlantic.scc.unix.apache:def:214228"
            ),
            "NIWC",
        )

    def test_niwc_definition(self):
        self.assertEqual(
            author_from_oval_definition_id("oval:example.niwc.project:def:42"),
            "NIWC",
        )

    def test_unknown_definition_does_not_guess(self):
        self.assertIsNone(
            author_from_oval_definition_id("oval:org.example.publisher:def:1")
        )

    def test_missing_definition_does_not_guess(self):
        self.assertIsNone(author_from_oval_definition_id(None))


if __name__ == "__main__":
    unittest.main()
