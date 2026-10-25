"""Public 0.4 validator local-resource scopes and fail-closed absence (#251)."""
from copy import deepcopy
from pathlib import Path
import unittest

from test_v04_public_cli_smoke import schema_valid_docs
from validate_native_json_schemas import build_validators, document_errors


class CurrentPublicValidatorTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.validator = build_validators(root / 'schema/v0.4.0')['assessment.schema.json']

    def test_current_scalar_requirement_references_do_not_escape_resource_scope(self):
        doc = schema_valid_docs()['authoring/demo/assessments/a1.json']
        self.assertEqual(list(document_errors(self.validator, doc)), [])

    def test_absence_comparison_rejected_without_repair_or_defaulting(self):
        doc = deepcopy(schema_valid_docs()['authoring/demo/assessments/a1.json'])
        field = next(iter(doc['assessment']['tests'].values()))['require']['fields']['mode']
        field.clear()
        field['values_found'] = 'none'
        self.assertEqual(list(document_errors(self.validator, doc)), [])
        field['equals'] = ''
        self.assertTrue(list(document_errors(self.validator, doc)))


if __name__ == '__main__':
    unittest.main()
