"""Native Input reference + explicit decimal conversion in 0.4.1 (structural only)."""
import json
from pathlib import Path
import unittest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1] / "schema"
URI = "https://scap-ng.dev/schema/v0.4.1/"

class InputFunctionExpressionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sources = {}
        for path in ROOT.glob("*.schema.json"):
            doc = json.loads(path.read_text())
            resource = Resource.from_contents(doc)
            sources[doc["$id"]] = resource
            sources[URI + path.name] = resource
        cls.schema = json.loads((ROOT / "variable-expression.schema.json").read_text())
        cls.validator = Draft202012Validator(cls.schema, registry=Registry().with_resources(sources.items()))

    def test_original_octalmask_chain_is_valid(self):
        inp = {"input": "var-accounts-user-umask-input"}
        def digit(i):
            return {"to_integer": {"substring": {"substring_start": i, "substring_length": 1, "value": inp}}}
        expression = {"arithmetic": {"arithmetic_operation": "add", "values": [
            {"arithmetic": {"arithmetic_operation": "multiply", "values": [{"literal": 64}, digit(1)]}},
            {"arithmetic": {"arithmetic_operation": "multiply", "values": [{"literal": 8}, digit(2)]}},
            digit(3)
        ]}}
        self.validator.validate({"kind": "local", "expression": expression})

    def test_malformed_input_and_legacy_function_fail(self):
        for expression in ({"input": ""}, {"input": "external-variable"},
                           {"input": "user-input", "literal": "077"},
                           {"to_integer": {"input": "wrong-name"}},
                           {"function": {"name": "cast", "arguments": [], "options": {}}}):
            self.assertTrue(list(self.validator.iter_errors({"kind": "local", "expression": expression})))
        self.assertTrue(list(self.validator.iter_errors({
            "kind": "local", "datatype": "integer",
            "expression": {"input": "umask-input"}})))

if __name__ == "__main__":
    unittest.main()
