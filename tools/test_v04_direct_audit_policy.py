"""Original audit-policy system acquisition against the approved 0.4 contract."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from v04_direct_scap_source import SourceModel, UnsupportedSource, OVAL
from v04_direct_inventory import SourceInventory
from v04_direct_converter import convert, AssessmentConverter, load_mappings
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_expanded_source_proof import ExpandedSource, original_audit_contract
from v04_native_bundle_compiler import build_bundle
from validate_native_json_schemas import build_validators, document_errors

ROOT=Path(__file__).resolve().parents[1]
PINS=json.loads((ROOT/'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
CAP='windows.auditeventpolicysubcategories'


class AuditPolicyDirectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=SourceModel(ROOT/'tests/fixtures/v04-direct-prototype'/PINS['fixture'],PINS['zip_sha256'])
        cls.rules=[r['source_rule'] for r in SourceInventory(cls.source).rules() if CAP in r['needed_capabilities']]
        cls.docs,cls.trace=convert(cls.source,cls.rules)

    def test_all_original_closures_compile_and_prove_without_native_singleton_objects(self):
        self.assertEqual(len(self.rules),43)
        self.assertEqual(len(verify_original(self.source.root,self.docs,self.trace)),43)
        self.assertEqual(len(verify_compiled(self.docs,build_bundle(self.docs)[0])),43)
        for d in self.docs.values():
            if 'assessment' in d:
                self.assertNotIn('shared_objects',d['assessment'])
                for test in d['assessment']['tests'].values():
                    self.assertEqual(test['capability'],CAP)
                    self.assertNotIn('object',test)
        fields,values=original_audit_contract()
        self.assertTrue(fields)
        self.assertEqual(values,{'AUDIT_SUCCESS','AUDIT_FAILURE','AUDIT_SUCCESS_FAILURE','AUDIT_NONE'})
        self.assertNotIn('kerberos_ticket_events',fields)

    def source_entity(self,source):
        binding=self.trace['rules'][0]
        state=next(source.nodes[binding['component']][i] for i,n in binding['dependencies'].items() if n['kind']=='state')
        return binding,state,state[0]

    def test_original_invalid_enums_datatypes_and_deprecated_fields_fail_closed(self):
        for mutation in ('enum','datatype','deprecated-field'):
            source=deepcopy(self.source)
            binding,state,entity=self.source_entity(source)
            if mutation=='enum':entity.text='NOT_AN_AUDIT_ENUM'
            elif mutation=='datatype':entity.set('datatype','boolean')
            else:entity.tag=entity.tag.rsplit('}',1)[0]+'}kerberos_ticket_events'
            with self.subTest(mutation=mutation),self.assertRaises(UnsupportedSource):
                convert(source,[binding['source_rule']])
            with self.assertRaises(ValueError):
                ExpandedSource(source.components[binding['component']]).state(state.get('id'),CAP)

    def test_singleton_selectors_and_variable_object_acquisition_are_not_invented(self):
        binding=self.trace['rules'][0]
        identifier=next(i for i,n in binding['dependencies'].items() if n['kind']=='object')
        source=deepcopy(self.source)
        obj=source.nodes[binding['component']][identifier]
        ET.SubElement(obj,obj.tag.rsplit('}',1)[0]+'}selector').text='invented'
        with self.assertRaises(UnsupportedSource):convert(source,[binding['source_rule']])
        component=ET.Element('{'+OVAL+'}object_component',object_ref=identifier,item_field='credential_validation')
        visitor=AssessmentConverter(self.source,binding['component'],load_mappings())
        with self.assertRaises(UnsupportedSource):visitor.function(component)

    def test_native_operand_mutants_and_meaningless_objects_are_rejected(self):
        docs=deepcopy(self.docs)
        a=next(d['assessment'] for d in docs.values() if 'assessment' in d)
        test=next(iter(a['tests'].values()))
        test['object']={}
        validators=build_validators(ROOT/'schema/v0.4.0')
        self.assertTrue(list(document_errors(validators['assessment.schema.json'],{'assessment':a})))
        with self.assertRaises(ValueError):build_bundle(docs)
        with self.assertRaises(AssertionError):verify_original(self.source.root,docs,self.trace)
        docs=deepcopy(self.docs)
        a=next(d['assessment'] for d in docs.values() if 'assessment' in d)
        def change(node):
            if isinstance(node,dict):
                for k,v in node.items():
                    if k=='equals' and isinstance(v,str) and v.startswith('AUDIT_'):node[k]='NOT_THE_ORIGINAL_AUDIT_VALUE'
                    else:change(v)
            elif isinstance(node,list):
                for v in node:change(v)
        change(a)
        with self.assertRaises(AssertionError):verify_original(self.source.root,docs,self.trace)


if __name__=='__main__':unittest.main()
