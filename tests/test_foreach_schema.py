"""Canonical 0.4.1 for_each authoring admission and boundary tests."""
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
PREFIX = "https://scap-ng.dev/schema/v0.4.1/"


def load(path):
    return json.loads(path.read_text())


def registry():
    resources = {}
    for path in SCHEMA.glob("*.json"):
        document = load(path)
        if "$schema" not in document:
            continue
        resource = Resource.from_contents(document)
        resources[PREFIX + path.name] = resource
        resources[document["$id"]] = resource
    return Registry().with_resources(resources.items())


def assessment_object(**overrides):
    document = {
        "assessment": {
            "id": "foreach-correlation-assessment",
            "version": 1,
            "assessment_title": "Correlated collection expansion",
            "mode": "automated",
            "class": "compliance",
            "specification": {
                "id": "scap-ng.pre-alpha.assessment",
                "version": "0.4.1",
            },
            "shared_objects": {
                "users-object": {
                    "object_title": "Source users",
                    "capability": "unix.file",
                    "filepath": {"equals": "/etc/passwd"},
                }
            },
            "tests": {
                "home-test": {
                    "test_title": "Check each selected path",
                    "capability": "unix.file",
                    "object": {
                        "for_each": {"item": "user", "in": "users-object", "reduce": "every"},
                        "filepath": {"from": "user.full_path"},
                    },
                    "require": {
                        "item_requirement": {
                            "items_found": "one_or_more",
                            "items_satisfying": "every",
                        },
                        "field_requirement": {
                            "values_found": "one_or_more",
                            "values_matching": "one_or_more",
                        },
                        "fields": {"full_path": {"equals": "/etc/passwd"}},
                    },
                    "reported_elements": "all",
                }
            },
            "evaluate": {"test": "home-test"},
        }
    }
    document["assessment"].update(overrides)
    return document


class ForEachSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = Draft202012Validator(
            load(SCHEMA / "assessment.schema.json"), registry=registry()
        )

    def assert_valid(self, document):
        errors = list(self.validator.iter_errors(document))
        self.assertEqual(errors, [], "\n".join(str(error) for error in errors))

    def test_named_source_and_correlated_selector_are_admitted(self):
        self.assert_valid(assessment_object())

    def test_chained_source_expansion_is_admitted(self):
        document = assessment_object()
        document["assessment"]["shared_objects"]["users-object"]["for_each"] = {
            "item": "parent",
            "in": "root-object",
            "reduce": "every",
        }
        self.assert_valid(document)

    def test_selector_binding_requires_lexical_alias_and_field(self):
        document = assessment_object()
        document["assessment"]["tests"]["home-test"]["object"]["filepath"] = {
            "from": "user"
        }
        self.assertTrue(list(self.validator.iter_errors(document)))

    def test_source_reference_is_a_named_object_id(self):
        document = assessment_object()
        document["assessment"]["tests"]["home-test"]["object"]["for_each"]["in"] = "users"
        self.assertTrue(list(self.validator.iter_errors(document)))

    def test_reduction_is_explicit(self):
        document = assessment_object()
        del document["assessment"]["tests"]["home-test"]["object"]["for_each"]["reduce"]
        self.assertTrue(list(self.validator.iter_errors(document)))

    def test_every_capability_selector_scope_is_audited(self):
        mappings = sorted((ROOT / "schema" / "capability-mappings" / "supported").glob("*.json"))
        generated = load(ROOT / "schema" / "native-selector.schema.json")["$defs"]
        contracts = load(ROOT / "schema" / "native-selector-contracts.json")["resolved"]
        self.assertGreaterEqual(len(mappings), 100)
        for path in mappings:
            mapping = load(path)
            capability = mapping["capability"]
            selectors = mapping.get("native", {}).get("selector_map", {})
            definition_name = capability.replace(".", "_") + "_object"
            with self.subTest(capability=capability):
                reviewed = capability in contracts
                if reviewed:
                    # Only reviewed selector contracts get a closed generated
                    # overlay.  Unreviewed selector mappings remain a deliberate
                    # runtime/source-conformance hold, not an invented schema.
                    self.assertIn(definition_name, generated)
                    properties = generated[definition_name]["oneOf"][1]["properties"]
                    self.assertIn("for_each", properties)
                    for selector in selectors:
                        node = properties[selector]
                        options = node.get("oneOf", [node])
                        binding = [option for option in options
                                   if option.get("$ref", "").endswith("/$defs/foreach_selector_binding")]
                        self.assertEqual(len(binding), 1, selector)
                    for parameter in mapping.get("native", {}).get("collection_parameters", {}):
                        node = properties.get(parameter, {})
                        self.assertNotIn("foreach_selector_binding", json.dumps(node))
                else:
                    # Unreviewed selector mappings, parameter-only, and fixed-result capabilities cannot use a
                    # selector binding.  They must not acquire a generated
                    # overlay that could make for_each an untyped command
                    # repeater.  Their explicit disposition is recorded by this
                    # all-mapping audit rather than silently omitted.
                    self.assertNotIn(definition_name, generated)


if __name__ == "__main__":
    unittest.main()
