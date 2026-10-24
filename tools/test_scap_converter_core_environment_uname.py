#!/usr/bin/env python3
"""Immutable environmentvariable58/uname source proofs; Refs #248 #232.

The test-only inverse builds OVAL from emitted native operands, independently
of the production projection, then uses the mature semantic graph comparator.
It supplies no production output or parser.
"""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import scap_converter_core as core
from test_scap_converter_core import legacy_oracle_view
from audit_scap_converter_core_coverage import inventory
from check_current_authoring_contract import violations
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_v04_public_cli_smoke import schema_valid_docs
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_native_bundle_compiler import build_bundle, verify_bundle

ROOT = Path(__file__).resolve().parents[1]
OD = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'
CASES = (
    ('SCAP_NG_ENVIRONMENT58_SOURCE_XML', 'oval:org.mitre.oval.test:def:354', 3),
    ('SCAP_NG_UNAME_SOURCE_XML', 'oval:navy.navwar.niwcatlantic.scc.test:def:932', 1),
)


def native_to_oval(native, original):
    """Independent bounded inverse; require all native graph nodes consumed."""
    native = legacy_oracle_view(native)
    root = ET.fromstring(original)
    definition = root.find('{'+OD+'}definitions')[0]
    criteria = definition.find('{'+OD+'}criteria')
    refs = [c.get('test_ref') for c in criteria]
    source_tests = root.find('{'+OD+'}tests')
    source_objects = root.find('{'+OD+'}objects')
    source_states = root.find('{'+OD+'}states')
    bindings = {t.get('id'): (t, source_objects[i], source_states[i])
                for i, t in enumerate(source_tests)}
    for section in (source_tests, source_objects, source_states):
        section.clear()
    criteria.clear()
    criteria.set('operator', 'AND')
    a = native['assessment']
    names = [item['test'] for item in a['evaluate']['and']]
    assert set(names) == set(a['tests']) and len(names) == len(refs)
    reverse_ops = {'matches_regex': 'pattern match', 'equals': 'equals',
                   'not_equal': 'not equal', 'greater_than': 'greater than',
                   'case_insensitive_not_equal': 'case insensitive not equal'}
    for name, ref in zip(names, refs):
        native_test = a['tests'][name]
        old_t, old_o, old_s = bindings[ref]
        namespace = old_t.tag.split('}')[0]+'}'
        ET.SubElement(criteria, '{'+OD+'}criterion', test_ref=ref)
        t = ET.SubElement(source_tests, old_t.tag, id=ref, version='1',
                          check_existence='at_least_one_exists',
                          check={'at_least_one_exists_and_all_match': 'all',
                                 'at_least_one_exists_and_some_match': 'at least one'}[native_test['require']])
        ET.SubElement(t, namespace+'object', object_ref=old_o.get('id'))
        ET.SubElement(t, namespace+'state', state_ref=old_s.get('id'))
        obj = ET.SubElement(source_objects, old_o.tag, id=old_o.get('id'), version='1')
        if native_test['capability'] == 'unix.uname':
            assert 'object' not in native_test
        else:
            selectors = native_test['object']
            assert set(selectors) == {'object_title', 'pid', 'name'}
            for field in ('pid', 'name'):
                value = selectors[field]
                attrs = {'datatype': 'int' if field == 'pid' else 'string'}
                if value is None:
                    attrs['{'+XSI+'}nil'] = 'true'
                    ET.SubElement(obj, namespace+field, attrs)
                else:
                    assert len(value) == 1
                    op, operand = next(iter(value.items()))
                    attrs['operation'] = reverse_ops[op]
                    ET.SubElement(obj, namespace+field, attrs).text = str(operand)
        state = ET.SubElement(source_states, old_s.tag, id=old_s.get('id'), version='1')
        assert len(native_test['states']) == 1
        expr = native_test['states'][0]
        fields = expr['and'] if native_test['capability'] == 'unix.uname' else [expr]
        for field_expr in fields:
            assert len(field_expr) == 1
            field, predicate = next(iter(field_expr.items()))
            assert predicate['require'] == 'at_least_one_exists_and_all_match'
            ops = {k:v for k,v in predicate.items() if k != 'require'}
            assert len(ops) == 1
            op, operand = next(iter(ops.items()))
            ET.SubElement(state, namespace+field, datatype='string',
                          operation=reverse_ops[op]).text = operand
    return ET.ElementTree(root)


class EnvironmentUnameCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Missing sources fail the dedicated CI gate, never silently skip.
        cls.sources = [(Path(os.environ[env]), did, count) for env,did,count in CASES]
        for path, did, _ in cls.sources:
            if sha256(path.read_bytes()).hexdigest() != core.PINNED_DIRECT_SOURCES[did]:
                raise ValueError('pinned source SHA differs: '+str(path))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def test_source_graph_differential_schema_compile_and_bundle_hashes(self):
        for path,did,count in self.sources:
            with self.subTest(definition=did), patch.object(core, 'lower_definition', wraps=core.lower_definition) as lower:
                native, proof = core.convert(path,did)
                lower.assert_called_once()
                self.assertTrue(proof['original_oval_pinned_direct_graph_attested'])
                self.assertFalse(proof['scanner_parity'])
                self.assertFalse(proof['full_oval_coverage'])
                self.assertEqual(violations(native), [])
                self.assertEqual(proof['source_provenance']['source_definition'],did)
                validate_docs({'authoring/source.json':native}, _schema_validators(ROOT/'schema/v0.4.0'))
                docs = schema_valid_docs()
                docs['authoring/demo/assessments/a1.json'] = native
                docs['authoring/demo/rules/r1.json']['rule']['assessment_choices']['automated']['assessment'] = native['assessment']['id']
                bundle,_ = build_bundle(docs,validate_schema=True)
                checked = verify_bundle(bundle,validate_schema=True)
                self.assertEqual((checked['documents'],checked['programs'],checked['tests']),(3,1,count))
                self.assertFalse(checked['scanner_evaluated'])
                exported = self.work/'inverse.xml'
                native_to_oval(native,path.read_bytes()).write(exported, encoding='utf-8', xml_declaration=True)
                self.assertTrue(compare(path,exported,source_root=did,regenerated_root=did,root_only=True)['equal'])

    def test_exact_environment_selectors_nil_state_comparison_and_types(self):
        native,_ = core.convert(*self.sources[0][:2])
        tests = list(native['assessment']['tests'].values())
        self.assertEqual([t['object']['pid'] for t in tests],[None,{'equals':1},{'greater_than':0}])
        self.assertIs(type(tests[1]['object']['pid']['equals']),int)
        self.assertEqual([t['object']['name'] for t in tests],[{'equals':'HOME'},{'not_equal':'PATH'},{'matches_regex':'^S'}])
        self.assertEqual(tests[1]['require']['fields']['name'],{'values_found':'one_or_more','values_matching':'every','case_insensitive_not_equal':'PATH'})
        self.assertTrue(all(t['require']['items_satisfying']=='one_or_more' for t in tests))

    def test_uname_singleton_all_six_state_fields(self):
        native,_ = core.convert(*self.sources[1][:2])
        test = next(iter(native['assessment']['tests'].values()))
        self.assertNotIn('object',test)
        self.assertNotIn('objects',native['assessment'])
        self.assertEqual(test['require']['items_satisfying'],'every')
        fields = [branch['fields'] for branch in test['require']['and']]
        self.assertEqual([next(iter(f)) for f in fields],['machine_class','node_name','os_name','os_release','os_version','processor_type'])
        self.assertTrue(all(next(iter(f.values())) == {'matches_regex':'.*','values_found':'one_or_more','values_matching':'every'} for f in fields))

    def test_independent_graph_comparison_detects_native_semantic_mutations(self):
        for path,did,_ in self.sources:
            native,_ = core.convert(path,did)
            first = next(iter(native['assessment']['tests'].values()))
            first['require']['items_satisfying'] = ('every' if '354' in did else 'one_or_more')
            exported = self.work/'changed-check.xml'
            native_to_oval(native,path.read_bytes()).write(exported,encoding='utf-8')
            self.assertFalse(compare(path,exported,source_root=did,regenerated_root=did,root_only=True)['equal'])
            native,_ = core.convert(path,did)
            first = next(iter(native['assessment']['tests'].values()))
            if '354' in did:
                first['object']['pid'] = {'equals':0}
            else:
                first['require']['and'][2]['fields']['os_name']['matches_regex'] = 'Linux'
            exported = self.work/'changed-operand.xml'
            native_to_oval(native,path.read_bytes()).write(exported,encoding='utf-8')
            self.assertFalse(compare(path,exported,source_root=did,regenerated_root=did,root_only=True)['equal'])

    def test_other_definition_ids_do_not_expand_capability_coverage(self):
        for path,did,_ in self.sources:
            replacement = did.rsplit(':',1)[0]+':999999'
            mutant = self.work/'unproved-definition.xml'
            mutant.write_bytes(path.read_bytes().replace(did.encode(),replacement.encode()))
            with self.assertRaisesRegex(ValueError,'unproved environmentvariable58/uname source SHA/Definition'):
                core.convert(mutant,replacement)

    def test_source_mutations_fail_before_lowering(self):
        for path,did,_ in self.sources:
            raw=path.read_bytes()
            mutations=[(b'operator="AND"',b'operator="OR"'),(b'<criterion comment=',b'<criterion negate="true" comment='),
                       (b'check_existence="at_least_one_exists"',b'check_existence="none_exist"'),
                       (b'check="',b'check="none satisfy '),(b'operation="pattern match"',b'operation="equals"'),
                       (b'</objects>',b'<unproved/></objects>'),(b'</states>',b'<unproved/></states>')]
            if '354' in did:
                mutations += [(b'xsi:nil="true"',b'xsi:nil="false"'),(b'>1</pid>',b'>2</pid>'),
                              (b'datatype="int"',b'datatype="string"'),(b'case insensitive not equal',b'not equal')]
            else:
                mutations += [(b'>.*</os_name>',b'>Linux</os_name>'),(b'<machine_class operation=',b'<machine_class entity_check="at least one" operation=')]
            for old,new in mutations:
                with self.subTest(definition=did,mutation=old):
                    changed=raw.replace(old,new,1);self.assertNotEqual(raw,changed)
                    mutant=self.work/'source.xml';mutant.write_bytes(changed)
                    with patch.object(core,'lower_definition') as lower:
                        with self.assertRaisesRegex(ValueError,'source SHA'):
                            core.convert(mutant,did)
                        lower.assert_not_called()

    def test_raw_lowering_and_provenance_mutations_fail_closed(self):
        original=core.lower_definition
        def raw_field(d):
            state=next(iter(d['assessment']['tests'].values()))['assertion']['state']
            return state['all'][0] if 'all' in state else state
        mutations=[lambda d,p:d['assessment'].update(purpose='inventory'),
                   lambda d,p:raw_field(d).update(value='changed'),
                   lambda d,p:raw_field(d).update(datatype='integer'),
                   lambda d,p:raw_field(d).update(entity_check='at least one'),
                   lambda d,p:raw_field(d).update(entity_existence='none_exist'),
                   lambda d,p:next(iter(d['assessment']['collections'].values())).update(select={'unproved':0}),
                   lambda d,p:d['assessment'].update(evaluate={'test':'invented'}),
                   lambda d,p:next(iter(d['assessment']['tests'].values()))['assertion'].update(existence='none_exist'),
                   lambda d,p:p['source_test_bindings'].clear(),
                   lambda d,p:p['source_collection_bindings'].clear(),
                   lambda d,p:p.update(source_variable_bindings={'unproved':'extra'})]
        for path,did,_ in self.sources:
            for mutate in mutations:
                def corrupt(*args,**kwargs):
                    doc,err=original(*args,**kwargs);mutate(doc,kwargs['provenance']);return doc,err
                with self.subTest(definition=did,mutation=mutate),patch.object(core,'lower_definition',side_effect=corrupt):
                    with self.assertRaisesRegex(ValueError,'raw 0.3 lowering graph differs'):
                        core.convert(path,did)

    def test_aligned_lowering_mutations_fail_closed(self):
        original=core.postprocess_automated_assessment
        def aligned_field(a):
            state=next(iter(a['states'].values()))['state']
            return state['all'][0] if 'all' in state else state
        mutations=[lambda a:a.update(version=2),lambda a:a['tests'].clear(),
                   lambda a:aligned_field(a).update(operation='not_equal'),
                   lambda a:aligned_field(a).update(value='changed'),
                   lambda a:aligned_field(a).update(datatype='integer'),
                   lambda a:aligned_field(a).update(match='one_or_more'),
                   lambda a:aligned_field(a).update(existence='none'),
                   lambda a:a['states'].clear(),lambda a:a.update(objects={'invented':{}}),
                   lambda a:next(iter(a['tests'].values())).update(match='none')]
        for path,did,_ in self.sources:
            for mutate in mutations:
                def corrupt(*args,**kwargs):
                    doc,report=original(*args,**kwargs);mutate(doc['assessment']);return doc,report
                with self.subTest(definition=did,mutation=mutate),patch.object(core,'postprocess_automated_assessment',side_effect=corrupt):
                    with self.assertRaisesRegex(ValueError,'aligned 0.3 lowering graph differs'):
                        core.convert(path,did)

    def test_no_independent_importer_or_failed_lowering_fallback(self):
        for path,did,_ in self.sources:
            with patch.object(core,'independent_leaf_import',side_effect=AssertionError('no importer bypass')):
                core.convert(path,did)
            with patch.object(core,'lower_definition',return_value=(None,'unproved construct')):
                with self.assertRaisesRegex(ValueError,'0.3 source lowering failed: unproved construct'):
                    core.convert(path,did)

    def test_public_cli_and_identity_override(self):
        for path,did,_ in self.sources:
            out,proof=self.work/'native.json',self.work/'proof.json'
            subprocess.run([sys.executable,str(ROOT/'tools/scap_converter_core.py'),'--source-xml',str(path),
                '--definition-id',did,'--assessment-id','source-verified-assessment','--output',str(out),'--evidence',str(proof)],check=True,capture_output=True,text=True)
            self.assertEqual(json.loads(out.read_text())['assessment']['id'],'source-verified-assessment')
            self.assertEqual(json.loads(proof.read_text())['definition_id'],did)

    def test_coverage_audit_counts_exact_definitions_and_rejects_mutants(self):
        for path,did,count in self.sources:
            result=inventory(path)
            self.assertEqual(result['counts']['definitions'],1)
            self.assertEqual(result['counts']['maintained_v004_core_source_proven'],1)
            row=result['definitions'][0]
            self.assertEqual(row['definition_id'],did)
            self.assertEqual(row['source_sha256'],core.PINNED_DIRECT_SOURCES[did])
            self.assertEqual(row['pinned_direct_lowering_sha256'],core.PINNED_DIRECT_LOWERINGS[did])
            self.assertEqual(row['v003_shape']['tests'],count)
            mutant=self.work/'mutant.xml';mutant.write_bytes(path.read_bytes().replace(b'operator="AND"',b'operator="OR"'))
            result=inventory(mutant)
            self.assertEqual(result['counts']['definitions'],1)
            self.assertEqual(result['definitions'][0]['maintained_v004_core'],'BLOCKED')
            self.assertIn('source SHA',result['definitions'][0]['v004_diagnostic'])


if __name__ == '__main__':
    unittest.main()
