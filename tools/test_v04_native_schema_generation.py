"""Full-contract parity, import isolation and schema-driven refresh boundaries."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from generate_capability_schema_v04 import generate

ROOT = Path(__file__).resolve().parents[1]
MAPPINGS = ROOT / 'schema/v0.4.0/capability-mappings/supported'
X = '{http://www.w3.org/2001/XMLSchema}'


def mapping(name):
    return json.loads((MAPPINGS / (name + '.json')).read_text())


class NativeSchemaGenerationTests(unittest.TestCase):
    def test_every_full_generated_contract_matches_reviewed_baseline(self):
        lock = json.loads((ROOT / 'tests/fixtures/v04-native-generator-parity.json').read_text())
        actual = {}
        for path in sorted(MAPPINGS.glob('*.json')):
            source = json.loads(path.read_text())
            schema = generate(source, ROOT)
            actual[source['capability']] = sha256(json.dumps(schema, sort_keys=True,
                separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(len(actual), 100)
        self.assertEqual(actual, lock['full_schema_sha256'])

    def test_no_historical_generator_or_wrapper_flattener_can_be_imported(self):
        program = '''
import importlib.abc, json, pathlib, sys
class DenyHistoricalGenerator(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'generate_capability_schema', 'flatten_v04_object_schema'}:
            raise AssertionError('historical generator imported: ' + fullname)
sys.meta_path.insert(0, DenyHistoricalGenerator())
from generate_capability_schema_v04 import generate
root = pathlib.Path(sys.argv[1])
for path in (root/'schema/v0.4.0/capability-mappings/supported').glob('*.json'):
    generate(json.loads(path.read_text()), root)
from v04_direct_scap_source import SourceModel
from v04_direct_converter import convert
from validate_native_json_schemas import build_validators, document_errors
from v04_native_bundle_compiler import build_bundle
fixture = root/'tests/fixtures/v04-direct-prototype'
pin = json.loads((fixture/'provenance.json').read_text())
source = SourceModel(fixture/pin['fixture'], pin['zip_sha256'])
documents, _ = convert(source, pin['rules'])
validators = build_validators(root/'schema/v0.4.0')
for document in documents.values():
    kind, = document
    assert not list(document_errors(validators[kind+'.schema.json'], document))
build_bundle(documents)
'''
        result = subprocess.run([sys.executable, '-c', program, str(ROOT)],
                                cwd=ROOT / 'tools', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_definitions_are_parsed_once_per_generation(self):
        for capability, expected in (('windows.registry', 2), ('variable.value', 2),
                                     ('independent.family', 2), ('independent.unknown', 1)):
            with self.subTest(capability=capability), patch('xml.etree.ElementTree.parse', wraps=ET.parse) as parse:
                generate(mapping(capability), ROOT)
                self.assertEqual(parse.call_count, expected)
                self.assertEqual(len({str(c.args[0]) for c in parse.call_args_list}), expected)

    def test_new_source_fields_and_type_changes_refresh_without_python_edits(self):
        from lxml import etree as source_xml
        source = mapping('windows.registry')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = []
            for field, filename in (('definitions_schema', 'windows-definitions-schema.xsd'),
                                    ('system_characteristics_schema', 'windows-system-characteristics-schema.xsd')):
                relative = Path(source['source']['definitions_schema']).with_name(filename)
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, path)
                paths.append(path)
            source['native']['state_field_map']['fixture_flag'] = 'fixture_flag'
            # Preserve source namespace declarations used by QName attributes.
            trees = [source_xml.parse(str(p)) for p in paths]
            for tree, name, dtype in ((trees[0], 'registry_state', 'oval-def:EntityStateBoolType'),
                                      (trees[1], 'registry_item', 'oval-sc:EntityItemBoolType')):
                global_node = tree.getroot().find(X + 'element[@name="' + name + '"]')
                source_xml.SubElement(global_node.find('.//' + X + 'sequence'), X + 'element',
                                      name='fixture_flag', type=dtype, minOccurs='0')
            for tree, path in zip(trees, paths):
                tree.write(path)
            first = generate(source, root)
            predicate = next(p for p in first['$defs']['state_predicate']['oneOf'] if 'fixture_flag' in p['properties'])
            self.assertEqual(predicate['properties']['fixture_flag']['allOf'][1]['properties']['datatype']['enum'], ['boolean'])
            for tree, path in zip(trees, paths):
                entity = next(n for n in tree.iter(X + 'element') if n.get('name') == 'fixture_flag')
                entity.set('type', entity.get('type').replace('Bool', 'Int'))
                tree.write(path)
            second = generate(source, root)
            predicate = next(p for p in second['$defs']['state_predicate']['oneOf'] if 'fixture_flag' in p['properties'])
            self.assertEqual(predicate['properties']['fixture_flag']['allOf'][1]['properties']['datatype']['enum'], ['integer'])
            item = second['$defs']['collected_item']['allOf'][1]['properties']['fields']['properties']['fixture_flag']
            self.assertEqual(item['allOf'][1]['properties']['datatype']['enum'], ['integer'])

    def test_direct_flat_objects_and_legitimate_cmdlet_select_parameter(self):
        registry = generate(mapping('windows.registry'), ROOT)['$defs']['object']['properties']
        self.assertTrue({'hive', 'key', 'name'} <= set(registry))
        self.assertFalse({'select', 'collect'} & set(registry))
        cmdlet = generate(mapping('windows.cmdlet'), ROOT)['$defs']['object']['properties']
        self.assertIn('select', cmdlet)
        self.assertNotIn('collect', cmdlet)

    def test_capability_source_kinds_and_unknown_kind_rejection(self):
        for capability, kind in (('independent.family', 'none'), ('variable.value', 'variable')):
            schema = generate(mapping(capability), ROOT)
            self.assertNotIn('object', schema['$defs'])
            self.assertNotIn('object', schema['$defs']['test']['properties'])
            if kind == 'variable':
                self.assertIn('variable', schema['$defs']['test']['required'])
        source = mapping('windows.registry')
        source['native']['test_source'] = {'kind': 'unreviewed'}
        with self.assertRaisesRegex(ValueError, 'unknown native Test source kind'):
            generate(source, ROOT)

    def test_property_collisions_cannot_reintroduce_generic_wrappers(self):
        for field in ('capability', 'collect', 'select'):
            source = mapping('windows.registry')
            source['native']['selector_map']['hive'] = field
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'property collision'):
                generate(source, ROOT)


if __name__ == '__main__':
    unittest.main()
