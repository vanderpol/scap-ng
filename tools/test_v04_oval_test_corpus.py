"""Coverage inventory and fail-closed boundaries, using pinned original OVAL."""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import (OVAL_ROOT, OvalDocument, audit,
    assessment_for, check_conversion, closure, closure_blockers, file_inventory,
    probe_mappings, summarize, xml_documents)
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import UnsupportedSource
from validate_native_json_schemas import build_validators

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tests/fixtures/v04-current-source-proofs/ind-def_shellcommand_windows_test.xml'


class CorpusCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ET.parse(SOURCE).getroot()
        cls.mappings = load_mappings()
        cls.validator = build_validators(ROOT / 'schema/v0.4.0')['assessment.schema.json']

    def model(self, root=None):
        source = OvalDocument(deepcopy(self.root if root is None else root), 'original.xml')
        graph = SourceInventory(source)
        nodes = {identifier: n for (_, identifier), n in graph.nodes.items()}
        identifier = next(i for i, n in nodes.items() if n['kind'] == 'test')
        return source, nodes, identifier

    def test_original_dependencies_and_distinct_file_scopes(self):
        source, nodes, identifier = self.model()
        dependencies, problems = closure(nodes, identifier)
        self.assertFalse(problems)
        self.assertIn(identifier, dependencies)
        self.assertIn('object', {nodes[i]['kind'] for i in dependencies})
        # Reused source IDs in different files must not merge semantic nodes.
        other = OvalDocument(deepcopy(self.root), 'second.xml')
        self.assertIsNot(source.nodes['original.xml'][identifier], other.nodes['second.xml'][identifier])

    def test_inventory_does_not_stop_at_unsupported_capability(self):
        source, nodes, identifier = self.model()
        nodes[identifier]['capability'] = 'unsupported.reference'
        dependencies, _ = closure(nodes, identifier)
        self.assertGreater(len(dependencies), 1)

    def test_missing_wrong_kind_and_cycles_stay_visible(self):
        _, nodes, identifier = self.model()
        nodes[identifier]['references'] += [{'id': 'missing', 'kind': 'variable'},
                                           {'id': identifier, 'kind': 'state'}]
        _, problems = closure(nodes, identifier)
        self.assertTrue(any('missing' in p for p in problems))
        self.assertTrue(any('cyclic dependency' in p for p in problems))
        nodes[identifier]['references'] = [{'id': identifier, 'kind': 'variable'}]
        # A wrong-kind edge to a separately indexed node must also be diagnosed.
        other = next(i for i in nodes if i != identifier)
        nodes[identifier]['references'] = [{'id': other, 'kind': 'definition'}]
        self.assertTrue(closure(nodes, identifier)[1])

    def test_original_conversion_validation_compilation_and_independent_proof(self):
        source, _, identifier = self.model()
        visitor = AssessmentConverter(source, 'original.xml', self.mappings)
        result = check_conversion(visitor, identifier, self.validator)
        self.assertTrue(result['converted'], result)
        self.assertTrue(result['schema_valid'], result)
        self.assertTrue(result['compiled'], result)
        self.assertEqual(result['source_proof'], 'PROVED', result)

    def test_old_wmi_is_not_upgraded(self):
        root = deepcopy(self.root)
        tests = root.find(OVAL_ROOT.removesuffix('oval_definitions') + 'tests')
        original = tests[0]
        original.tag = '{http://oval.mitre.org/XMLSchema/oval-definitions-5#windows}wmi_test'
        source, _, _ = self.model(root)
        visitor = AssessmentConverter(source, 'original.xml', self.mappings)
        result = check_conversion(visitor, original.get('id'), self.validator)
        self.assertFalse(result['converted'])
        self.assertIn('wmi_test', result['diagnostics'][0]['message'])

    def test_unresolved_variable_is_not_bound_from_another_file(self):
        source, nodes, identifier = self.model()
        target = next(n for n in source.nodes['original.xml'].values() if n.tag.endswith('_object'))
        entity = next(iter(target))
        entity.set('var_ref', 'oval:missing:var:1')
        entity.text = None
        result = check_conversion(AssessmentConverter(source, 'original.xml', self.mappings), identifier, self.validator)
        self.assertFalse(result['converted'], result)
        self.assertIn('unresolved variable', result['diagnostics'][0]['message'])

    def test_duplicate_identifiers_are_not_silently_overwritten(self):
        root = deepcopy(self.root)
        group = next(g for g in root if any(c.get('id') for c in g))
        group.append(deepcopy(group[0]))
        with self.assertRaisesRegex(UnsupportedSource, 'duplicate/missing ID'):
            OvalDocument(root, 'duplicate.xml')

    def test_support_payloads_are_hashed_and_nested_xml_is_read_without_extraction(self):
        import zipfile
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / 'reference.txt').write_text('reference')
            with zipfile.ZipFile(directory / 'support.zip', 'w') as archive:
                archive.writestr('../sample.xml', '<reference/>')
            self.assertEqual(len(file_inventory(directory)), 2)
            documents = list(xml_documents(directory))
            self.assertEqual(documents, [('support.zip!../sample.xml', b'<reference/>')])
            self.assertFalse((directory.parent / 'sample.xml').exists())

    def test_missing_or_changed_collection_fails_before_conversion(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(UnsupportedSource, 'pinned collection mismatch'):
                audit(Path(temporary))

    def test_compiled_unproved_is_not_counted_as_source_proved(self):
        row = {'capability': 'windows.registry', 'scope': 'in_scope', 'converted': True,
               'schema_valid': True, 'compiled': True, 'source_proof': 'MISMATCH',
               'diagnostics': [{'stage': 'source_proof', 'message': 'operand differs'}]}
        summary = summarize([row])['windows.registry']
        self.assertEqual(summary['compiled'], 1)
        self.assertEqual(summary['source_proof'], {'MISMATCH': 1})
        self.assertNotIn('PROVED', summary['source_proof'])

    def test_typed_closure_probe_retains_supported_cmdlet_nil_parameters(self):
        root = ET.parse(SOURCE.with_name('win-def_cmdlet_test.xml')).getroot()
        source = OvalDocument(root, 'cmdlet.xml')
        nodes = {identifier: n for (_, identifier), n in SourceInventory(source).nodes.items()}
        identifier = next(i for i, n in nodes.items() if n['kind'] == 'test')
        assessment_for(AssessmentConverter(source, 'cmdlet.xml', self.mappings), identifier)
        dependencies, _ = closure(nodes, identifier)
        self.assertEqual(closure_blockers(source, 'cmdlet.xml', nodes, dependencies, self.mappings), [])

    def test_metadata_probes_do_not_enable_mac_or_change_production_admission(self):
        enabled = {m['capability'] for m in load_mappings()}
        probes = {m['capability'] for m in probe_mappings()}
        self.assertGreater(len(probes), len(enabled))
        self.assertTrue(enabled < probes)
        self.assertFalse(any(c.startswith(('macos.', 'esx.')) for c in probes))
        self.assertEqual(enabled, {m['capability'] for m in load_mappings()})


if __name__ == '__main__':
    unittest.main()
