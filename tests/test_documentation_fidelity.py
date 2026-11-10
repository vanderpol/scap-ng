from copy import deepcopy
from pathlib import Path
import json,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import audit_documentation_fidelity as fidelity
import generate_documentation as reference
from extract_oval_documentation import XSDs,normalized_text

class DocumentationFidelityTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.outputs=fidelity.audit();cls.coverage=json.loads(cls.outputs[fidelity.BASE/'coverage.json'])
  cls.source=json.loads((ROOT/fidelity.BASE/'source-documentation.json').read_text())
  cls.rows=[json.loads(l) for l in (ROOT/fidelity.BASE/'crosswalk.jsonl').read_text().splitlines()]

 def test_all_104_source_reconciliations_and_version_boundaries(self):
  t=self.coverage['totals'];self.assertEqual(t['capabilities'],104);self.assertEqual(t['complete_source_reconciliations'],104)
  self.assertEqual((t['within_5123'],t['outside_5123']),(100,4))
  self.assertEqual(t['capability_statement_bindings'],sum(t[k] for k in ['retained','adapted','withheld','excluded']))
  self.assertEqual({c['capability'] for c in self.coverage['capabilities'] if c['outside_5123']},{'esx.host_account','esx.host_advancedsetting','esx.host_service','esx.host_vib'})

 def test_exact_source_ids_roles_and_deprecated_contributors(self):
  for d in self.source['documents'].values():
   self.assertTrue(d['xpath'].startswith('/xs:schema/'))
   self.assertEqual(len(d['file_sha256']),64)
  roles={b['role'] for c in self.source['capabilities'] for b in c['documentation']}
  self.assertTrue({'test','object','state','item','shared_type'}<=roles)
  self.assertTrue(any('deprecated' in d['basis'] for c in self.source['capabilities'] for d in c['declarations']))

 def test_every_retained_passage_has_schema_destination_and_withheld_has_none(self):
  for r in self.rows:
   if r['classification']in('A','B'):
    self.assertTrue(r['destination_pointer'].endswith('/description'));self.assertTrue(r['destination_text'])
   else:self.assertFalse(r.get('destination'))
  self.assertEqual(self.outputs,fidelity.audit())

 def test_lost_applicable_description_is_rejected(self):
  row=next(r for r in self.rows if r['classification']in('A','B'))
  docs=deepcopy(reference.schemas());reference.node(docs,row['destination'])['description']='Missing source passage.'
  with patch.object(fidelity.reference,'schemas',return_value=docs):
   with self.assertRaisesRegex(ValueError,'Lost applicable source passage'):fidelity.audit()

 def test_shellcommand_guidance_and_unapproved_contracts_are_separate(self):
  doc=json.loads((ROOT/reference.SOURCE/'capabilities/independent.shellcommand.schema.json').read_text())
  text=doc['description'].lower()
  for term in ['privilege','harm','fragile','excessive','standard error','trust','signing','external executable','empty output']:
   self.assertIn(term,text)
  rows=json.loads(self.outputs[fidelity.BASE/'shellcommand-review.json'])
  self.assertTrue(any(r['classification']=='D' and 'default shell' in r['source_text'].lower() for r in rows))
  self.assertTrue(any(r['classification']=='D' and 'digitally signed' in r['source_text'].lower() for r in rows))
  self.assertTrue(any(r['classification']=='D' and 'one item' in r['source_text'].lower() for r in rows))
  self.assertFalse(any(r['classification']in('A','B') and 'longest' in r['source_text'] for r in rows))

 def test_source_copy_errors_are_withheld_not_native_requirements(self):
  for cap,phrase in [('macos.firmwarepassword','File Vault'),('linux.sestatus','counts of profiles'),('windows.regkeyeffectiverights','Windows files')]:
   doc=json.loads((ROOT/reference.SOURCE/f'capabilities/{cap}.schema.json').read_text())
   self.assertNotIn(phrase,doc['description'])
   self.assertTrue(any(r['capability']==cap and r['classification']=='D' for r in self.rows))

 def test_overview_field_help_and_value_datatypes_share_schema_source(self):
  outputs=reference.generate();help_data=json.loads(outputs[reference.DEST/'editor-help.json'])
  uri='https://scap-ng.dev/schema/proposed/documentation/capabilities/independent.shellcommand.schema.json#'
  owner=next(d for d in help_data['descriptions'] if d['schema_pointer']==uri)
  page=outputs[reference.DEST/'capabilities/independent.shellcommand.md']
  self.assertIn(owner['description'],page);self.assertIn('| `exit_status` | integer |',page)
  self.assertIn('## Object',page);self.assertIn('## Item',page);self.assertIn('## Require',page)
  self.assertNotIn('### Condition logic',page)

 def test_xsd_extraction_keeps_multiple_annotations_and_reference_types(self):
  xml='''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:t="urn:test" targetNamespace="urn:test"><xs:simpleType name="Meaning"><xs:annotation><xs:documentation>Type warning.</xs:documentation></xs:annotation><xs:restriction base="xs:string"/></xs:simpleType><xs:element name="sample_object"><xs:annotation><xs:documentation>First paragraph.\n\nSecurity warning.</xs:documentation><xs:documentation>Second annotation.</xs:documentation></xs:annotation><xs:complexType><xs:sequence><xs:element name="field" type="t:Meaning"/></xs:sequence></xs:complexType></xs:element></xs:schema>'''
  with tempfile.TemporaryDirectory()as t:
   p=Path(t)/'test.xsd';p.write_text(xml);lib=XSDs(t,'pin');f,node=lib.declaration('test.xsd','element','sample_object')
   annotations=list(node.iter('{http://www.w3.org/2001/XMLSchema}documentation'))
   self.assertEqual(len(annotations),2);self.assertIn('\n\nSecurity warning.',normalized_text(annotations[0]))
   self.assertEqual(next(lib.references(f,node))[1].get('name'),'Meaning')

if __name__=='__main__':unittest.main()
