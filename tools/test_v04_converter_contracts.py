"""Schema-driven contract refresh, canonical routing and real cmdlet select."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
import io

from v04_converter_contracts import ROOT, contract, fingerprint, main, snapshot
from test_generate_capability_schema_v04 import validate


def mapping(name):
    return json.loads((ROOT / 'schema/v0.4.0/capability-mappings/supported' / (name + '.json')).read_text())


class ConverterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = snapshot()

    def test_all_current_mappings_export_current_native_contracts(self):
        paths = list((ROOT / 'schema/v0.4.0/capability-mappings/supported').glob('*.json'))
        self.assertEqual(len(self.catalog['capabilities']), len(paths))
        self.assertEqual(self.catalog['schema_version'], '0.4.0')
        for item in self.catalog['capabilities']:
            native = mapping(item['capability'])['native']
            declared_fields = set(native.get('selector_map', {}).values()) | set(native.get('collection_parameters', {}))
            for name in ('select', 'collect'):
                if name in item['object_fields']:
                    self.assertIn(name, declared_fields, 'Generic wrappers are not declared acquisition fields')
            self.assertNotIn('state', item['schema']['$defs'])

    def test_cmdlet_select_record_stays_valid_while_generic_wrappers_fail(self):
        data = mapping('windows.cmdlet')
        result = contract(data)
        self.assertEqual(data['migration_crosswalk']['object']['select'], 'object.select')
        self.assertIn('select', result['object_fields'])
        value = {'capability': 'windows.cmdlet', 'module_name': None, 'module_id': None,
                 'module_version': None, 'verb': 'Get', 'noun': 'ComputerInfo',
                 'parameters': None, 'select': {'fields': {'property': {
                     'equals': 'BiosFirmwareType', 'selection_match': 'every'}}}}
        self.assertFalse(validate(result['schema'], 'object', value))
        for change in ({'select': {'hive': {'equals': 'local_machine'}}}, {'collect': {'noun': 'ComputerInfo'}}):
            with self.subTest(change=change):
                self.assertTrue(validate(result['schema'], 'object', {**value, **change}))
        value['select'] = None
        self.assertFalse(validate(result['schema'], 'object', value))

    def test_obsolete_wrapper_paths_and_stale_filesystem_scope_are_rejected(self):
        for value in ('select.name', 'collect.name'):
            data = mapping('windows.service')
            data.setdefault('migration_crosswalk', {}).setdefault('object', {})['service_name'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'obsolete acquisition path'):
                contract(data)
        data = mapping('windows.registry')
        data['migration_crosswalk'].setdefault('traversal', {})['recurse_file_system.all'] = 'any'
        with self.assertRaisesRegex(ValueError, 'native all'):
            contract(data)

    def test_nonexistent_native_target_is_a_mapping_error_not_an_invented_field(self):
        data = mapping('windows.wmi.query')
        data['native']['collection_parameter_source_map']['wql'] = 'invented_query'
        with self.assertRaisesRegex(ValueError, 'unknown native Object field invented_query'):
            contract(data)

    def test_ordinary_field_change_refreshes_data_without_a_python_capability_branch(self):
        data = mapping('windows.registry')
        data['native']['state_field_map']['last_write_time'] = 'write_time'
        data['native']['field_datatypes']['write_time'] = data['native']['field_datatypes'].pop('last_write_time')
        original = deepcopy(data)
        result = contract(data)
        self.assertIn('write_time', result['require_fields'])
        self.assertNotIn('last_write_time', result['require_fields'])
        self.assertEqual(data, original)
        self.assertNotEqual(result['schema_sha256'], contract(mapping('windows.registry'))['schema_sha256'])

    def test_catalog_is_reproducible_and_reports_unresolved_source_correspondence(self):
        self.assertEqual(fingerprint(self.catalog), fingerprint(snapshot()))
        data = mapping('windows.wmi.query')
        del data['native']['collection_parameter_source_map']['wql']
        del data['migration_crosswalk']['object']['wql']
        self.assertEqual(contract(data)['parameters_without_explicit_source_route'], ['query'])
        workflow = (ROOT / '.github/workflows/v04-converter-schema-sync.yml').read_text()
        self.assertIn('schema/v0.4.0/**', workflow)
        self.assertIn('contents: read', workflow)
        self.assertIn('actions/upload-artifact@v4', workflow)

    def test_invalid_mapping_fails_process_but_preserves_review_artifact(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            mappings = root / 'schema/v0.4.0/capability-mappings/supported'
            mappings.mkdir(parents=True)
            (mappings / 'broken.json').write_text('{"invalid"')
            output = root / 'contract-report.json'
            with patch('v04_converter_contracts.ROOT', root), patch('sys.argv', ['contracts', '--output', str(output)]):
                with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as raised:
                    main()
            self.assertEqual(raised.exception.code, 1)
            result = json.loads(output.read_text())
            self.assertEqual(result['summary']['invalid_contracts'], 1)
            self.assertEqual(result['failures'][0]['capability'], 'broken')


if __name__ == '__main__':
    unittest.main()
