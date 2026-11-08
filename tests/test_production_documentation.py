"""Generic documentation gates; no scanner-runtime equivalence assertions."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import generate_documentation as gen
import documentation_artifacts as artifacts

PREFIX = 'https://scap-ng.dev/schema/proposed/documentation/'
FROZEN = 'https://scap-ng.dev/schema/v0.4.0/'


def assertions(value):
    if isinstance(value, list):
        return [assertions(v) for v in value]
    if isinstance(value, dict):
        return {k: assertions(v) for k,v in value.items()
                if k != 'description' and not k.startswith('x-doc-')}
    if isinstance(value, str):
        return value.replace(PREFIX, FROZEN)
    return value


class ProductionDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = gen.schemas()
        cls.outputs = gen.generate()
        cls.help = json.loads(cls.outputs[gen.DEST / 'editor-help.json'])
        cls.coverage = json.loads(cls.outputs[gen.DEST / 'coverage.json'])

    def test_all_104_and_initial_ten_are_discovered(self):
        caps = {d['x-doc-capability'] for d,p in self.docs.values() if 'x-doc-capability' in d}
        mappings = {json.loads(p.read_text())['capability'] for p in (ROOT/'schema/capability-mappings').glob('*/*.json')}
        self.assertEqual(caps, mappings)
        self.assertEqual(len(caps),104)
        for cap in gen.QUALIFICATION:
            row = next(c for c in self.coverage['capabilities'] if c['capability'] == cap)
            self.assertEqual(row['missing_descriptions'],0, cap)

    def test_every_mapping_field_and_native_inline_field_is_present(self):
        for p in (ROOT/'schema/capability-mappings').glob('*/*.json'):
            mapping=json.loads(p.read_text()); cap=mapping['capability']; native=mapping['native']
            doc=self.docs[PREFIX+'capabilities/'+cap+'.schema.json'][0]
            obj=doc['$defs']['object']; fields=obj['properties']
            self.assertTrue(set(native.get('selector_map',{}).values()) <= set(fields), cap)
            self.assertTrue(set(native.get('collection_parameters',{})) <= set(fields), cap)
            self.assertEqual(set(native.get('state_field_map',{}).values()),set(doc['$defs']['meanings']['properties']),cap)
            self.assertTrue(set(gen.properties(self.docs,obj['x-doc-validation-ref'])) <= set(fields),cap)

    def test_validation_assertions_equal_frozen_for_all_35_roots(self):
        checked=0
        for base,(doc,path) in self.docs.items():
            if 'x-doc-capability' in doc: continue
            proposed=deepcopy(doc)
            if path.name=='assessment-language.schema.json':
                terms=proposed['$defs'].pop('documentation_terms')
                for uri,value in gen.walk(terms, base+'#'):
                    self.assertFalse(set(value)-{'$defs','$comment','description','x-doc-status','x-doc-scope'},uri)
            original=json.loads((ROOT/'schema'/path.name).read_text())
            self.assertEqual(assertions(proposed),assertions(original),path.name)
            checked+=1
        self.assertEqual(checked,35)

    def test_all_proposed_resources_are_valid_schemas_and_refs_are_local(self):
        gen.check_links(self.docs)
        for doc,path in self.docs.values():
            Draft202012Validator.check_schema(doc)

    def test_native_and_proposed_witness_results(self):
        native={d['$id']:d for p in (ROOT/'schema').glob('*.json') if '$schema' in (d:=json.loads(p.read_text()))}
        registry=Registry().with_resources((u,Resource.from_contents(d)) for u,d in native.items())
        proposed=Registry().with_resources((u,Resource.from_contents(d)) for u,(d,p) in self.docs.items())
        cases=json.loads((ROOT/'docs/review-packs/issue43-phase-a/validation-cases.json').read_text())
        self.assertEqual(len(cases),157)
        cases += json.loads((ROOT/'tests/fixtures/documentation-validation-witnesses.json').read_text())
        self.assertEqual(len(cases),170)
        for case in cases:
            uri=FROZEN+case['schema_file']+'#'+case['pointer']
            old=Draft202012Validator({'$ref':uri},registry=registry).is_valid(case['instance'])
            new=Draft202012Validator({'$ref':uri.replace(FROZEN,PREFIX)},registry=proposed).is_valid(case['instance'])
            self.assertEqual(old,case['expected_valid'],case['name'])
            self.assertEqual(new,old,case['name'])

    def test_all_editorial_approvals_and_semantic_holds_preserved(self):
        approved=held=withheld=0
        for file in ['editorial-batch.json','editorial-batch-2.json']:
            batch=json.loads((ROOT/'docs/research/issue40'/file).read_text())
            for row in batch['proposals']:
                uri=row['schema_uri'].replace(FROZEN,PREFIX)+'#'+row['pointer']
                value=gen.node(self.docs,uri)
                if row['editorial_status'] in ('accepted_as_written','accepted_with_revision'):
                    self.assertEqual(value['description'],row['author_description']);approved+=1
                elif row['classification']=='semantic_decision_needed':
                    if row.get('withheld'):
                        self.assertEqual(value['x-doc-review']['status'],'withheld')
                        withheld+=1
                        continue
                    self.assertEqual(value['x-doc-review']['status'],'semantic-hold')
                    original=json.loads((ROOT/row['schema_file']).read_text())
                    self.assertEqual(value.get('description'),gen.pointer(original,row['pointer']).get('description'));held+=1
        self.assertEqual((approved,held),(46,9))
        self.assertEqual(withheld,1)

    def test_regeneration_is_byte_identical_and_committed_outputs_current(self):
        self.assertEqual(self.outputs,gen.generate())
        for path,text in self.outputs.items():
            self.assertEqual((ROOT/path).read_bytes(),text.encode(),str(path))

    def test_exact_help_context_and_shared_item_require_owner(self):
        for cap in gen.QUALIFICATION:
            entries=[r for r in self.help['routes'] if r['capability']==cap and r['role']=='Item']
            for item in entries:
                req=artifacts.capability_help(self.help,cap,'Require',item['path'])
                self.assertEqual(req['description_pointer'],item['description_pointer'])
        depth=artifacts.capability_help(self.help,'unix.file','Object',['traversal','max_depth'])
        self.assertEqual(depth['mapping_key_occurrence'],'1..1 (required)')
        self.assertIsNone(artifacts.capability_help(self.help,'unix.file','Object',['max_depth']))
        self.assertIsNone(artifacts.capability_help(self.help,'windows.service','Object',['traversal','max_depth']))
        self.assertIsNone(artifacts.capability_help(self.help,'unknown.capability','Item',['name']))
        self.assertIsNone(artifacts.capability_help(self.help,'unix.file','Require',['nonexistent']))

    def test_mapping_cardinality_and_array_member_bounds_stay_separate(self):
        uri=PREFIX+'capability-common.schema.json#/$defs/inline_object'
        self.assertEqual(gen.cardinality(self.docs,uri,'filters'),'0..1')
        value=gen.node(self.docs,uri+'/properties/filters')
        self.assertEqual(value['minItems'],1)
        self.assertIn('"minItems": 1',self.outputs[gen.DEST/'advanced/capability-common.md'])
        self.assertIn('| Definition |',self.outputs[gen.DEST/'shared/variable-expression.md'])
        self.assertIn('"unlimited"',self.outputs[gen.DEST/'advanced/capability-common.md'])

    def test_registry_traversal_discrepancy_is_not_hidden(self):
        row=artifacts.capability_help(self.help,'windows.registry','Object',['traversal'])
        self.assertEqual(row['status'],'semantic-hold')
        self.assertIn('**Not accepted in this inline form.**',self.outputs[gen.DEST/'capabilities/windows.registry.md'])
        child=artifacts.capability_help(self.help,'windows.registry','Object',['traversal','max_depth'])
        self.assertEqual(child['status'],'semantic-hold')

    def test_require_alternatives_keep_comparison_and_existence_separate(self):
        uri=PREFIX+'assessment-language.schema.json#/$defs/test/properties/require'
        forms=list(gen.forms(self.docs,uri))
        self.assertEqual(len(forms),2)
        self.assertEqual(set(gen.properties(self.docs,forms[1])),{'item_requirement'})
        self.assertIn('field_requirement',gen.properties(self.docs,forms[0]))
        self.assertEqual(gen.cardinality(self.docs,forms[0],'field_requirement'),'1..1 (required)')
        page=self.outputs[gen.DEST/'capabilities/unix.file.md']
        self.assertIn('shared Require forms and count policies',page)
        self.assertNotIn('### Condition logic',page)
        self.assertIn('item_presence_requirement',self.outputs[gen.DEST/'shared/assessment-language.md'])

    def test_inactive_and_unreferenced_help_is_explicitly_scoped(self):
        inactive=artifacts.schema_help(self.help,PREFIX+'variable-function-expression.schema.json#')
        self.assertEqual(inactive['scope'],'inactive-migration')
        legacy=artifacts.schema_help(self.help,PREFIX+'capability-common.schema.json#/$defs/authoring_type_resolution')
        self.assertEqual(legacy['scope'],'unreferenced-schema-helper')
        self.assertEqual(legacy['status'],'unresolved-legacy-helper')
        active=artifacts.schema_help(self.help,PREFIX+'variable-expression.schema.json#/$defs/expression/oneOf/3/properties/concat')
        self.assertEqual(active['scope'],'declared-schema')
        self.assertEqual(active['status'],'semantic-hold')

    def test_all_rendered_relative_links_resolve(self):
        for path,text in self.outputs.items():
            if path.suffix!='.md':continue
            for target in re.findall(r'\]\(([^)]+)\)',text):
                if target.startswith(('https:', 'http:', '#')):continue
                target=target.split('#',1)[0]
                self.assertTrue((ROOT/path.parent/target).resolve().exists(),f'{path}: {target}')

    def test_changed_description_reaches_reference_and_all_help_contexts(self):
        docs=deepcopy(self.docs)
        cap=PREFIX+'capabilities/unix.file.schema.json'
        text='Owner UID description changed in the authoritative schema.'
        gen.node(docs,cap+'#/$defs/meanings/properties/owner_uid')['description']=text
        with patch.object(gen,'schemas',return_value=docs):
            output=gen.generate()
        self.assertIn(text,output[gen.DEST/'capabilities/unix.file.md'])
        help_data=json.loads(output[gen.DEST/'editor-help.json'])
        for role in ['Item','Require']:
            self.assertEqual(artifacts.capability_help(help_data,'unix.file',role,['owner_uid'])['description'],text)

    def test_negative_capability_dispatch_and_broken_reference(self):
        bad=deepcopy(self.docs)
        value=bad[PREFIX+'assessment-language.schema.json'][0]['$defs']['test']['x-doc-capability-schemas']
        value['unix.file']=PREFIX+'capabilities/windows.service.schema.json'
        with self.assertRaisesRegex(ValueError,'Incorrect capability association'):
            gen.check_links(bad)
        bad=deepcopy(self.docs)
        bad[PREFIX+'capabilities/unix.file.schema.json'][0]['$defs']['object']['properties']['broken']={'$ref':'missing.schema.json'}
        with self.assertRaisesRegex(ValueError,'Broken schema link'):
            gen.check_links(bad)
        bad=deepcopy(self.docs)
        bad[PREFIX+'capabilities/unix.file.schema.json'][0]['$defs']['meanings']['properties']['owner_uid']={'$ref':PREFIX+'capabilities/windows.service.schema.json#/$defs/meanings/properties/service_name'}
        with self.assertRaisesRegex(ValueError,'Incorrect capability field association'):
            gen.check_links(bad)

    def test_loader_rejects_stale_missing_and_unpinned_artifacts(self):
        pin=sha256((ROOT/gen.DEST/'manifest.json').read_bytes()).hexdigest()
        loaded=artifacts.load(ROOT,pin)
        self.assertEqual(loaded,self.help)
        with self.assertRaisesRegex(ValueError,'unpinned'):
            artifacts.load(ROOT,'0'*64)
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            for path,text in self.outputs.items():
                (root/path).parent.mkdir(parents=True,exist_ok=True);(root/path).write_text(text)
            # Schemas are absent; fail instead of using generic or frozen help.
            with self.assertRaises(FileNotFoundError): artifacts.load(root,pin)
            for _,path in self.docs.values():
                (root/path).parent.mkdir(parents=True,exist_ok=True);(root/path).write_bytes((ROOT/path).read_bytes())
            (root/gen.SOURCE/'provenance.json').write_bytes((ROOT/gen.SOURCE/'provenance.json').read_bytes())
            path=root/gen.DEST/'editor-help.json';path.write_text('{}')
            with self.assertRaisesRegex(ValueError,'Stale documentation resource'):
                artifacts.load(root,pin)

    def test_capability_quality_and_one_historical_attribution(self):
        for doc,path in self.docs.values():
            if 'x-doc-capability' not in doc:continue
            for uri,value in gen.walk(doc,doc['$id']+'#'):
                self.assertIsNone(re.search(r'OVAL|xsi:|\b(?:must|shall|should)\b|\$lt;',value.get('description','')),uri)
            page=self.outputs[gen.DEST/'capabilities'/(doc['x-doc-capability']+'.md')]
            self.assertEqual(page.count('Historical source:'),1)
            self.assertNotIn('`traversal.max_depth`',page)
        self.assertEqual(self.coverage['totals']['missing_capability_descriptions'],8)
        self.assertEqual(self.coverage['totals']['fully_field_documented'],102)

    def test_new_capability_and_field_require_no_generator_changes(self):
        docs=deepcopy(self.docs)
        base=PREFIX+'capabilities/test.discovery.schema.json'
        doc=deepcopy(docs[PREFIX+'capabilities/linux.rpminfo.schema.json'][0])
        doc['$id']=base;doc['x-doc-capability']='test.discovery';doc['title']='test.discovery'
        doc.pop('x-doc-examples',None)  # A new capability cannot inherit RPM fixture associations.
        doc['$defs']['meanings']['properties']['new_field']={'description':'New discovered field.'}
        docs[base]=(doc,gen.SOURCE/'capabilities/test.discovery.schema.json')
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            shutil.copytree(ROOT/'schema',root/'schema')
            shutil.copytree(ROOT/'examples/paired',root/'examples/paired')
            for _,(d,path) in docs.items():
                (root/path).parent.mkdir(parents=True,exist_ok=True);(root/path).write_text(gen.encode(d))
            (root/gen.SOURCE/'provenance.json').write_text('{}')
            generated=gen.generate(root)
        self.assertIn(gen.DEST/'capabilities/test.discovery.md',generated)
        self.assertIn('New discovered field.',generated[gen.DEST/'capabilities/test.discovery.md'])


if __name__=='__main__': unittest.main()
