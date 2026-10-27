"""Source-backed unresolved acquisition conflict; no schema or lowering proposal."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import OvalDocument, probe_mappings
from oval_source_validation import SourceValidator
from test_generate_capability_schema_v04 import materialize, validate
from v04_direct_converter import AssessmentConverter, load_mappings

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v04-filehash-acquisition-conflict'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
I = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#independent}'


class FileHashAcquisitionConflictTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pin = json.loads((FIXTURE / 'provenance.json').read_text())
        cls.raw = (FIXTURE / Path(cls.pin['path']).name).read_bytes()
        cls.root = ET.fromstring(cls.raw)
        cls.schema = materialize('file.hash')

    def test_original_multi_algorithm_and_complement_objects_are_valid(self):
        self.assertEqual(sha256(self.raw).hexdigest(), self.pin['sha256'])
        source = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3').validate(etree.fromstring(self.raw))
        self.assertEqual(source['status'], 'VALID', source)
        objects = self.root.find(O + 'objects')
        self.assertEqual(len(objects), 3)
        self.assertEqual([n.find(I + 'hash_type').get('var_check') for n in objects],
                         ['at least one', 'none satisfy', 'at least one'])
        self.assertEqual([len(n.findall(O + 'value')) for n in self.root.find(O + 'variables')], [2, 4])

    def test_current_native_acquisition_requires_one_literal_algorithm(self):
        obj = {'capability': 'file.hash', 'full_path': {'equals': '/bin/ls'}, 'filesystem': 'all'}
        errors = validate(self.schema, 'object', obj)
        self.assertTrue(errors)
        def causes(error):
            yield error
            for child in error.context:
                yield from causes(child)
        self.assertTrue(any(e.validator == 'required' and 'algorithm' in e.message
                            for error in errors for e in causes(error)))
        obj['algorithm'] = 'md5'
        self.assertFalse(validate(self.schema, 'object', obj))
        for algorithm in (['md5', 'sha1'], {'variable': 'algorithms'}, {'equals': 'md5'}):
            bad = deepcopy(obj)
            bad['algorithm'] = algorithm
            self.assertTrue(validate(self.schema, 'object', bad))

    def test_unmapped_original_acquisition_fails_closed_without_activation(self):
        mappings = probe_mappings()
        mapping = next(m for m in mappings if m['capability'] == 'file.hash')
        self.assertNotIn('hash_type', mapping['native']['selector_map'])
        self.assertNotIn('hash_type', mapping['native'].get('collection_parameter_source_map', {}))
        self.assertNotIn('file.hash', {m['capability'] for m in load_mappings()})
        for obj in self.root.find(O + 'objects'):
            visitor = AssessmentConverter(OvalDocument(self.root, 'original.xml'), 'original.xml', mappings)
            with self.subTest(object=obj.get('id')), self.assertRaisesRegex(ValueError, 'unsupported Object field: hash_type'):
                visitor.reference(obj.get('id'), 'object')


if __name__ == '__main__':
    unittest.main()
