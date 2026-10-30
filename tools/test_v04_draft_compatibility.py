"""Pinned originals and fail-closed draft-only compatibility regressions (#260)."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from unittest import TestCase, main
import xml.etree.ElementTree as ET

from v04_direct_scap_source import SourceModel, DS, OVAL, XCCDF, XLINK, xml_identity
from v04_direct_converter import AssessmentConverter, convert_rule, load_mappings
from v04_direct_inventory import SourceInventory
from v04_native_bundle_compiler import build_bundle, compile_assessment_program, verify_bundle
from audit_v04_eight_assessment_pilot import verify_program
from oval_result_truth_tables import evaluate_collected_object_test
from validate_native_json_schemas import build_validators, document_errors

ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'tests/fixtures/v04-draft-compatibility'
PINS=json.loads((F/'provenance.json').read_text())['sources']
CAT='urn:oasis:names:tc:entity:xmlns:xml:catalog'
AD='xccdf_navy.navwar.niwcatlantic.scc.ms_rule_SV-243466r959010_rule'
AL='xccdf_mil.disa.stig_rule_SV-274017r1120039_rule'

class DraftCompatibilityTests(TestCase):
    @classmethod
    def setUpClass(cls):cls.validators=build_validators(ROOT/'schema/v0.4.0')

    def source(self,which='Active_Directory_Domain',draft=True):
        pin=next(p for p in PINS if which in p['file'])
        self.assertEqual(sha256((F/pin['file']).read_bytes()).hexdigest(),pin['sha256'])
        return SourceModel(F/pin['file'],pin['sha256'],inventory_broken_references=True,draft_compatibility=draft)

    def entry(self,s):
        href=next(r.get('href') for c in s.rules[AD].findall('{'+XCCDF+'}check') if c.get('system')==OVAL
                  for r in c.findall('{'+XCCDF+'}check-content-ref'))
        catalog=s.checklist.find('{'+CAT+'}catalog')
        return href,catalog,next(n for n in catalog if n.get('name')==href)

    def compile(self,s,rule):
        original=xml_identity(s.root)
        docs,binding=convert_rule(s,rule,load_mappings())
        a=next(v['assessment'] for v in docs.values() if 'assessment' in v)
        self.assertFalse(list(document_errors(self.validators['assessment.schema.json'],{'assessment':a})))
        verify_program(a,compile_assessment_program(a))
        self.assertEqual(xml_identity(s.root),original)
        self.assertFalse(binding['independent_static_proof_eligible'])
        self.assertEqual(binding['conversion_status'],'CONVERTED_UNVERIFIED')
        return a,binding

    def test_original_catalog_chain_resolves_with_qname_identity_and_warning(self):
        s=self.source();href,_,entry=self.entry(s)
        a,b=self.compile(s,AD)
        w,=b['conversion_warnings']
        self.assertEqual(w['original_element_qname'],'{'+DS+'}uri')
        self.assertEqual(w['href'],href)
        self.assertEqual(w['component_ref'],entry.get('uri'))
        self.assertEqual(w['definition'],'oval:navy.navwar.niwcatlantic.scc.windows:def:243466')
        self.assertIn(href,s.catalog)
        self.assertTrue(s.catalog_errors)  # Broken, unused older entry retained.
        rows=SourceInventory(s).rules()
        self.assertFalse(next(r for r in rows if r['source_rule']==AD)['inventory_problems'])

    def test_standard_binding_is_preferred_when_same_exact_target_exists(self):
        s=self.source();href,cat,entry=self.entry(s)
        standard=deepcopy(entry);standard.tag='{'+CAT+'}uri';cat.append(standard);s.index()
        self.assertIn(href,s.catalog)
        self.assertNotIn(href,s.catalog_warnings)

    def test_conflicting_standard_and_extension_targets_fail_closed(self):
        s=self.source();href,cat,entry=self.entry(s)
        standard=deepcopy(entry);standard.tag='{'+CAT+'}uri'
        standard.set('uri','#'+s.checklist.get('id'));cat.append(standard);s.index()
        self.assertNotIn(href,s.catalog)
        self.assertIn('conflicting',s.catalog_errors[href]['message'])
        with self.assertRaises(ValueError):convert_rule(s,AD,load_mappings())

    def test_duplicate_nonlocal_missing_and_wrong_namespace_entries_never_search_components(self):
        for change in ['duplicate','nonlocal','missing-ref','missing-component','namespace']:
            s=self.source();href,cat,entry=self.entry(s)
            if change=='duplicate':cat.append(deepcopy(entry))
            elif change=='nonlocal':entry.set('uri','https://example.invalid/content.xml')
            elif change=='missing-ref':entry.set('uri','#missing-ref')
            elif change=='missing-component':s.references[entry.get('uri')[1:]].set(XLINK,'#missing-component')
            else:entry.tag='{https://example.invalid/foreign}uri'
            s.index()
            with self.subTest(change=change):
                self.assertNotIn(href,s.catalog)
                with self.assertRaises(ValueError):convert_rule(s,AD,load_mappings())
                # The requested Definition still exists somewhere: never use it as fallback.
                self.assertTrue(any('oval:navy.navwar.niwcatlantic.scc.windows:def:243466' in n for n in s.nodes.values()))

    def test_wrong_kind_exact_component_target_cannot_convert_definition(self):
        s=self.source();_,_,entry=self.entry(s)
        s.references[entry.get('uri')[1:]].set(XLINK,'#'+s.benchmark_component);s.index()
        with self.assertRaises(ValueError):convert_rule(s,AD,load_mappings())

    def test_strict_source_does_not_admit_extension(self):
        with self.assertRaises(ValueError):convert_rule(self.source(draft=False),AD,load_mappings())

    def test_original_all_exist_draft_keeps_full_source_context_and_compiles(self):
        s=self.source('Amazon_Linux_2023');a,b=self.compile(s,AL)
        w,=b['conversion_warnings']
        self.assertEqual(w['code'],'test_all_exist_unproved')
        self.assertEqual(w['original_check_existence'],'all_exist')
        self.assertEqual(s.node(w['component'],w['source_test'],'test').get('check_existence'),'all_exist')
        self.assertEqual(a['tests'][w['native_test']]['require']['items_found'],'one_or_more')
        self.assertIn('source_variable_context',b)
        self.assertIn('missing expected targets remain distinguishable',w['collection_obligations'])
        with self.assertRaises(ValueError):convert_rule(self.source('Amazon_Linux_2023',draft=False),AL,load_mappings())

    def test_field_all_exist_is_every_and_never_normalized_to_item_presence(self):
        s=self.source('Amazon_Linux_2023');v=AssessmentConverter(s,next(iter(s.components)),load_mappings())
        field=ET.fromstring('<value xmlns="'+OVAL+'#windows" check_existence="all_exist">value</value>')
        m=next(m for m in load_mappings() if m['capability']=='windows.registry')
        self.assertEqual(v.predicate(field,m)['values_found'],'every')
        self.assertEqual(v.conversion_warnings,[])

    def test_population_boundary_reference_results_cannot_promote_warning_to_verified(self):
        s=self.source('Amazon_Linux_2023');_,b=self.compile(s,AL)
        cases=[('complete',0,0,0,0,'false'),('complete',1,0,0,0,'true'),('complete',3,0,0,0,'true'),
            ('complete',1,1,0,0,'false'),('complete',1,0,1,0,'error'),('complete',1,0,0,1,'unknown'),
            ('incomplete',1,0,0,0,'unknown'),('error',1,0,0,0,'error'),('not collected',1,0,0,0,'unknown')]
        for flag,exists,absent,error,unknown,expected in cases:
            with self.subTest(flag=flag,exists=exists,absent=absent,error=error,unknown=unknown):
                self.assertEqual(evaluate_collected_object_test(flag,existence='all_exist',has_state=False,
                    exists=exists,does_not_exist=absent,error=error,not_collected=unknown),expected)
                self.assertFalse(b['independent_static_proof_eligible'])
        self.assertEqual(b['conversion_warnings'][0]['scanner_runtime'],'NOT_RUN')

    def test_cli_never_combines_draft_admission_with_strict_verified_upgrade(self):
        pin=next(p for p in PINS if 'Amazon_Linux_2023' in p['file'])
        result=subprocess.run([sys.executable,str(ROOT/'tools/v04_direct_converter.py'),str(F/pin['file']),
            '--sha256',pin['sha256'],'--rule',AL,'--draft','--verify','--output','unused-output'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('separate admission modes',result.stderr)

if __name__=='__main__':main()
