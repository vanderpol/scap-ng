"""Original function contracts and masked dependencies remain source facts."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from audit_v04_variable_function_contracts import schema_contracts, source_usage, CURRENT_VISITOR_FUNCTIONS
from audit_v04_oval_test_corpus import file_inventory

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3'


class VariableFunctionInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = schema_contracts(SCHEMA)

    def test_original_thirteen_signatures_and_nine_remaining_names(self):
        functions = self.contracts['functions']
        self.assertEqual(len(functions), 13)
        self.assertEqual(set(functions) - CURRENT_VISITOR_FUNCTIONS,
                         {'arithmetic', 'begin', 'count', 'end', 'escape_regex', 'glob_to_regex',
                          'split', 'substring', 'time_difference'})
        self.assertNotIn('to_lower', functions)
        self.assertNotIn('to_upper', functions)
        self.assertEqual(functions['arithmetic']['arity'], {'minimum': 2, 'maximum': 'unbounded'})
        self.assertEqual(functions['count']['arity'], {'minimum': 1, 'maximum': 'unbounded'})
        self.assertEqual(functions['time_difference']['arity'], {'minimum': 1, 'maximum': '2'})
        attrs = {a['name']: a for a in functions['time_difference']['attributes']}
        self.assertEqual(attrs['format_1']['default'], 'year_month_day')
        self.assertIn('cim_datetime', attrs['format_2']['enumeration'])
        self.assertEqual(functions['glob_to_regex']['attributes'][0]['default'], 'false')

    def test_embedded_schematron_and_required_optional_options_are_not_conflated(self):
        functions = self.contracts['functions']
        self.assertTrue(functions['substring']['schematron'])
        self.assertTrue(any('datatype of string' in a['message'] for rule in functions['substring']['schematron']
                            for a in rule['assertions']))
        self.assertTrue(all(a['use'] == 'required' for a in functions['substring']['attributes']))
        # Original regex_capture pattern is optional in XSD, despite prose.
        # The inventory must not silently strengthen its original declaration.
        pattern, = functions['regex_capture']['attributes']
        self.assertNotIn('use', pattern)
        self.assertNotIn('default', pattern)

    def test_pinned_original_transitive_usage_includes_shared_nested_components(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); source = base / 'source'; source.mkdir()
            raw = (ROOT / 'tests/fixtures/v04-direct-variables/oval-def_concat_function.xml').read_bytes()
            (source / 'original.xml').write_bytes(raw)
            pin = base / 'pin.json'; pin.write_text(json.dumps({'files': file_inventory(source)}))
            result = source_usage(source, pin, self.contracts, SCHEMA)
            row = result['summary']['concat']
            self.assertEqual(row['transitive_test_uses'], 4)
            self.assertEqual(row['source_valid_nondeprecated_uses'], 4)
            self.assertIn('variable', row['example'])
            self.assertIn('concat', row['example']['function_excerpt'])
            self.assertEqual((source / 'original.xml').read_bytes(), raw)
            (source / 'original.xml').write_bytes(raw + b'\n')
            with self.assertRaisesRegex(ValueError, 'pinned original collection mismatch'):
                source_usage(source, pin, self.contracts, SCHEMA)

    def test_cli_retains_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'evidence.json'; output.write_text('keep existing work')
            result = subprocess.run([sys.executable, str(ROOT / 'tools/audit_v04_variable_function_contracts.py'),
                                     '--output', str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('refusing overwrite', result.stderr)
            self.assertEqual(output.read_text(), 'keep existing work')
