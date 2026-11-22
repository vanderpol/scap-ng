"""Conformance witnesses for declarative Benchmark CPE identity metadata."""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "https://scap-ng.dev/schema/v0.4.1/"
HASH = "7fca3bf5636bdc0d38bc714dc968ebe43c3b57b7a4b3b215115102e56c3b8913"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class DeclarativeCPEMetadata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {}
        for path in ROOT.joinpath("schema").glob("*.schema.json"):
            document = load(path)
            cls.documents[document["$id"]] = document
        cls.identity = {
            "value": "cpe:/o:canonical:ubuntu_linux:24.04::~~lts~~~",
            "binding": "cpe_uri_2_2",
            "source": {
                "kind": "cpe_platform",
                "id": "cpe:/o:canonical:ubuntu_linux:24.04::~~lts~~~",
                "idref": "#platform-ubuntu-2404",
                "sha256": HASH,
            },
        }
        cls.formatted = {
            "value": "cpe:2.3:o:microsoft:windows_11:23h2:*:*:*:*:*:*:*",
            "binding": "cpe_formatted_string_2_3",
            "source": {
                "kind": "cpe_platform",
                "id": "cpe:2.3:o:microsoft:windows_11:23h2:*:*:*:*:*:*:*",
                "sha256": "a" * 64,
            },
        }

    def validator(self, uri):
        base, fragment = uri.split("#", 1) if "#" in uri else (uri, "")
        schema = self.documents[base]
        for token in fragment.lstrip("/").split("/") if fragment else []:
            token = token.replace("~1", "/").replace("~0", "~")
            schema = schema[int(token)] if isinstance(schema, list) else schema[token]
        resolver = RefResolver(base, self.documents[base], store=self.documents)
        return Draft202012Validator(schema, resolver=resolver)

    def test_zero_one_and_multiple_declared_identities(self):
        validator = self.validator(PREFIX + "cpe-identity.schema.json")
        for value in (self.identity, self.formatted):
            validator.validate(value)
        self.assertEqual([], list(validator.iter_errors(self.identity)))
        self.assertEqual([], list(validator.iter_errors(self.formatted)))

        platform = {
            "id": "fixture-platform",
            "title": "fixture",
            "expected_cpe_identities": [self.identity, self.formatted],
        }
        platform_schema = load(ROOT / "schema" / "benchmark.schema.json")
        platform_validator = self.validator(PREFIX + "benchmark.schema.json#/properties/benchmark/properties/platform")
        platform_validator.validate(platform)
        platform_validator.validate({"id": "fixture-platform", "title": "fixture"})
        platform_validator.validate({**platform, "expected_cpe_identities": []})
        self.assertIn("expected_cpe_identities", platform_schema["properties"]["benchmark"]["properties"]["platform"]["properties"])

    def test_result_echo_is_distinct_and_lossless(self):
        validator = self.validator(PREFIX + "benchmark-result.schema.json#/properties/benchmark_result/properties/benchmark")
        result_benchmark = {
            "id": "fixture-benchmark",
            "version": "1",
            "expected_cpe_identities": [self.identity, self.formatted],
        }
        validator.validate(result_benchmark)
        self.assertEqual(result_benchmark["expected_cpe_identities"], [self.identity, self.formatted])

    def test_source_provenance_and_binding_are_strict(self):
        validator = self.validator(PREFIX + "cpe-identity.schema.json")
        invalids = []
        missing = copy.deepcopy(self.identity)
        del missing["source"]["sha256"]
        invalids.append(missing)
        bad_binding = copy.deepcopy(self.identity)
        bad_binding["binding"] = "string-equality"
        invalids.append(bad_binding)
        bad_hash = copy.deepcopy(self.identity)
        bad_hash["source"]["sha256"] = "not-a-sha"
        invalids.append(bad_hash)
        extra = copy.deepcopy(self.identity)
        extra["source"]["unexpected"] = True
        invalids.append(extra)
        for item in invalids:
            with self.subTest(item=item):
                self.assertTrue(list(validator.iter_errors(item)))

    def test_metadata_does_not_create_an_applicability_expression(self):
        platform_validator = self.validator(PREFIX + "benchmark.schema.json#/properties/benchmark/properties/platform")
        platform = {
            "id": "fixture-platform",
            "title": "declared only",
            "expected_cpe_identities": [self.identity],
        }
        platform_validator.validate(platform)
        self.assertNotIn("applicability", platform)


if __name__ == "__main__":
    unittest.main()
