#!/usr/bin/env python3
"""Validate checked-in SCAP-NG 0.3 showcase result examples."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v0.3.0"
EXAMPLE_DIR = ROOT / "specification" / "examples" / "0.3.0" / "results"

CASES = {
    "scan-result.json": "scan-result.schema.json",
    "benchmark-result.json": "benchmark-result.schema.json",
    "assessment-result.json": "assessment-result.schema.json",
    "assessment-result-bounded-evidence.json": "assessment-result.schema.json",
    "manual-assessment-result.json": "assessment-result.schema.json",
}


def schema_store():
    store = {}
    for path in SCHEMA_DIR.glob("*.schema.json"):
        document = json.loads(path.read_text(encoding="utf-8"))
        if "$id" in document:
            store[document["$id"]] = document
    return store


class ShowcaseResultExamplesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.store = schema_store()

    def test_all_showcase_results_validate_against_0_3(self):
        for example_name, schema_name in CASES.items():
            with self.subTest(example=example_name):
                schema = json.loads(
                    (SCHEMA_DIR / schema_name).read_text(encoding="utf-8")
                )
                Draft202012Validator.check_schema(schema)
                validator = Draft202012Validator(
                    schema,
                    resolver=RefResolver.from_schema(schema, store=self.store),
                )
                document = json.loads(
                    (EXAMPLE_DIR / example_name).read_text(encoding="utf-8")
                )
                errors = sorted(
                    validator.iter_errors(document),
                    key=lambda error: tuple(map(str, error.absolute_path)),
                )
                if errors:
                    details = "\n".join(
                        f"{'/'.join(map(str, error.absolute_path))}: {error.message}"
                        for error in errors
                    )
                    self.fail(f"{example_name} failed {schema_name}:\n{details}")


if __name__ == "__main__":
    unittest.main()
