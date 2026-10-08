"""Ensure Registry type compatibility rules declare and review every supported enum.

The source enum is intentionally not assumed to map all types to a scalar
datatype. Some values require dedicated complex representation decisions.
"""
import json
import unittest
from pathlib import Path
from validate_generated_capability_semantics import REGISTRY_TYPE_VALUE_DATATYPES

ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"schema/v0.3.0/capability-mappings/supported/windows.registry.json"

# Explicitly tracked exceptions, not silent datatype guesses.
UNRESOLVED_COMPLEX_REGISTRY_TYPES={
    "none", "resource_list", "full_resource_descriptor",
    "resource_requirements_list",
}


class RegistryTypeCoverageTests(unittest.TestCase):
    def test_every_registry_type_classified(self):
        mapping=json.loads(MAP.read_text(encoding="utf-8"))
        supported=set(mapping["native"]["state_value_enums"]["type"])
        classified=set(REGISTRY_TYPE_VALUE_DATATYPES)|UNRESOLVED_COMPLEX_REGISTRY_TYPES
        self.assertEqual(supported,classified,
                         "Every OVAL Registry type requires a reviewed primitive mapping or explicit unresolved exception")
        self.assertFalse(set(REGISTRY_TYPE_VALUE_DATATYPES)&UNRESOLVED_COMPLEX_REGISTRY_TYPES)

    def test_unresolved_complex_types_remain_explicit(self):
        self.assertEqual({
            "none", "resource_list", "full_resource_descriptor",
            "resource_requirements_list",
        },UNRESOLVED_COMPLEX_REGISTRY_TYPES)


if __name__=="__main__":
    unittest.main()
