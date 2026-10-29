"""Original-pinned IOS XE line/global identity and mutation checks (#251)."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from unittest import TestCase, main, mock
import xml.etree.ElementTree as ET
from lxml import etree

from audit_v04_oval_test_corpus import OvalDocument, assessment_for, check_conversion
from audit_v04_eight_assessment_pilot import verify_program
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, CAPABILITIES, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import digest, xml_identity
from v04_expanded_source_proof import ExpandedSource, ExpandedNative
from v04_native_bundle_compiler import compile_assessment_program
from v04_scalar_source_proof import contract
from validate_native_json_schemas import build_validators

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'tests/fixtures/v04-iosxe-line-global'
CASES=json.loads((FIXTURE/'provenance.json').read_text())['cases']
NS='{http://oval.mitre.org/XMLSchema/oval-definitions-5#iosxe}'

class IosxeLineGlobalTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=build_validators(ROOT/'schema/v0.4.0')['assessment.schema.json']
        cls.validator=SourceValidator(ROOT/'third_party/scap-1.4-schemas/oval_5.12.3')

    def original(self,index=0):
        case=CASES[index];raw=(FIXTURE/case['fixture']).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(),case['sha256'])
        root=ET.fromstring(raw);nodes={n.get('id'):n for n in root.iter() if n.get('id')}
        self.assertEqual(set(nodes),{d['id'] for d in case['dependencies']})
        for d in case['dependencies']:self.assertEqual(digest(xml_identity(nodes[d['id']])),d['sha256'])
        return root

    def visitor(self,root):
        return AssessmentConverter(OvalDocument(root,'original.xml'),'original.xml',load_mappings())

    def proved(self,root,test):
        before=ET.tostring(root)
        result=check_conversion(self.visitor(root),test,self.schema)
        self.assertTrue(result['schema_valid'],result)
        self.assertTrue(result['compiled_operands_verified'],result)
        self.assertEqual(result['source_proof'],'PROVED',result)
        self.assertEqual(ET.tostring(root),before)
        return assessment_for(self.visitor(root),test)

    def test_original_closures_valid_nondeprecated_and_all_66_tests_prove(self):
        count=0
        for i,case in enumerate(CASES):
            root=self.original(i)
            checked=self.validator.validate(etree.fromstring(ET.tostring(root)))
            nodes=list(SourceInventory(OvalDocument(root,'original.xml')).nodes.values())
            validity=closure_validity(nodes,{'original.xml':checked})
            self.assertEqual(validity['status'],'VALID',validity)
            self.assertFalse(any(v['kind']=='deprecated' for v in validity['issues']))
            for test in case['tests']:
                with self.subTest(fixture=case['fixture'],test=test):self.proved(root,test)
                count+=1
        self.assertEqual(count,66)
        self.assertEqual(sum(len(c['rules']) for c in CASES),38)

    def test_frozen_identity_fields_match_original_xsd_and_mapping_hash(self):
        x='{http://www.w3.org/2001/XMLSchema}'
        for kind in ['line','global']:
            record=contract('iosxe.'+kind)
            schema=ET.parse(ROOT/record['source']['definitions_schema']).getroot()
            state=schema.find(x+'element[@name="'+kind+'_state"]')
            fields={n.get('name') for n in state.findall('.//'+x+'sequence/'+x+'element')}
            self.assertEqual(fields,set(record['fields']))
            self.assertTrue(all(k==v for k,v in record['fields'].items()))
        with mock.patch('v04_direct_converter.CAPABILITIES',CAPABILITIES+('ios.line',)):
            with self.assertRaisesRegex(ValueError,'outside approved direct-converter scope'):load_mappings()

    def test_selector_state_and_aggregation_mutants_reject_independently(self):
        root=self.original(2)
        test='oval:mil.disa.stig.cisco.iosxe:tst:16000'
        a=self.proved(root,test);key=a['evaluate']['test']
        for change in ['selector','state','count']:
            mutant=deepcopy(a);t=mutant['tests'][key]
            if change=='selector':t['object']['show_subcommand']['equals']='different command'
            elif change=='state':
                # Replace the complete predicate, retaining valid field grammar.
                t['require']['fields']={'config_line':{'equals':'changed','datatype':'string','values_found':'one_or_more','values_matching':'every'}}
            else:t['require']['items_satisfying']='none'
            self.assertFalse(list(self.schema.iter_errors({'assessment':mutant})))
            self.assertNotEqual(ExpandedSource(root).test(test),ExpandedNative(mutant).test(key))
            with self.assertRaises((ValueError,AssertionError)):verify_program(mutant,compile_assessment_program(a))

    def test_unknown_selector_namespace_attribute_and_nil_fail_closed(self):
        for change in ['field','namespace','attribute','nil']:
            root=self.original(2)
            obj=next(n for n in root.iter() if n.tag==NS+'line_object')
            entity=obj.find(NS+'show_subcommand')
            if change=='field':entity.tag=NS+'invented'
            elif change=='namespace':entity.tag='{http://oval.mitre.org/XMLSchema/oval-definitions-5#ios}show_subcommand'
            elif change=='attribute':entity.set('invented','true')
            else:entity.set('{http://www.w3.org/2001/XMLSchema-instance}nil','true')
            with self.subTest(change=change),self.assertRaises(ValueError):ExpandedSource(root).object(obj.get('id'))
            test=next(n.get('id') for n in root.iter() if any(c.get('object_ref')==obj.get('id') for c in n))
            with self.assertRaises(ValueError):assessment_for(self.visitor(root),test)

    def test_all_exist_stays_blocked_and_source_token_is_unchanged(self):
        root=self.original(2);test=next(n for n in root.iter() if n.tag==NS+'line_test')
        test.set('check_existence','all_exist')
        with self.assertRaises(ValueError):ExpandedSource(root).test(test.get('id'))
        with self.assertRaises(ValueError):assessment_for(self.visitor(root),test.get('id'))
        self.assertEqual(test.get('check_existence'),'all_exist')

    def test_existence_and_field_matching_axes_are_distinct(self):
        for found in ['at_least_one_exists','only_one_exists','any_exist']:
            for matching in ['all','at least one','only one','none satisfy']:
                root=self.original(2);test=next(n for n in root.iter() if n.tag==NS+'line_test')
                test.set('check_existence',found);test.set('check',matching)
                self.proved(root,test.get('id'))

if __name__=='__main__':main()
