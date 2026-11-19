"""Synthetic XML grammar fixtures: no benchmark content or scanner required."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/'tools/audit_oval_language.py'
spec=importlib.util.spec_from_file_location('audit_oval_language',SOURCE)
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

CORE='''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
 xmlns:core="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 targetNamespace="http://oval.mitre.org/XMLSchema/oval-definitions-5">
 <xs:complexType name="ObjectType"><xs:attribute name="id" type="xs:string" use="required"/></xs:complexType>
 <xs:element name="object" type="core:ObjectType" abstract="true"/>
 <xs:element name="test" abstract="true"/>
 <xs:element name="state" abstract="true"/>
 <xs:element name="set"><xs:complexType><xs:sequence>
   <xs:element name="object_reference" type="xs:string" maxOccurs="unbounded"/>
 </xs:sequence></xs:complexType></xs:element>
 </xs:schema>'''

INDEPENDENT='''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
 xmlns:core="http://oval.mitre.org/XMLSchema/oval-definitions-5"
 xmlns:ind="http://oval.mitre.org/XMLSchema/oval-definitions-5#independent"
 xmlns:oval="http://oval.mitre.org/XMLSchema/oval-common-5"
 xmlns:sch="http://purl.oclc.org/dsdl/schematron"
 targetNamespace="http://oval.mitre.org/XMLSchema/oval-definitions-5#independent">
 <xs:import namespace="http://oval.mitre.org/XMLSchema/oval-definitions-5" schemaLocation="oval-definitions-schema.xsd"/>
 <xs:element name="variable_object" substitutionGroup="core:object">
  <xs:complexType><xs:complexContent><xs:extension base="core:ObjectType">
   <xs:choice><xs:element ref="core:set"/><xs:element name="var_ref" type="xs:string"/></xs:choice>
  </xs:extension></xs:complexContent></xs:complexType>
 </xs:element>
 <xs:element name="variable_test" substitutionGroup="core:test"/>
 <xs:element name="variable_state" substitutionGroup="core:state">
   <xs:complexType><xs:sequence><xs:element name="value" type="xs:string"/></xs:sequence></xs:complexType>
 </xs:element>
 <xs:element name="legacy_test" substitutionGroup="core:test">
   <xs:annotation><xs:appinfo>
     <oval:deprecated_info><oval:version>5.11</oval:version><oval:reason>Use replacement</oval:reason></oval:deprecated_info>
     <sch:pattern id="legacy"><sch:rule context="ind:legacy_test"><sch:report test="true()">deprecated</sch:report></sch:rule></sch:pattern>
   </xs:appinfo></xs:annotation>
 </xs:element>
 </xs:schema>'''

MAPPING={'capability':'variable.value','source':{
    'namespace':'http://oval.mitre.org/XMLSchema/oval-definitions-5#independent',
    'test':'variable_test','object':'variable_object','state':'variable_state'},
    'native':{'test_source':{'kind':'variable'}}}


class PinnedGrammarInventoryTest(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.oval=self.root/'oval-schemas'
        self.maps=self.root/'schema'/'capability-mappings'/'supported'
        self.oval.mkdir()
        self.maps.mkdir(parents=True)
        (self.oval/'oval-definitions-schema.xsd').write_text(CORE)
        (self.oval/'independent-definitions-schema.xsd').write_text(INDEPENDENT)
        (self.maps/'variable.value.json').write_text(json.dumps(MAPPING))

    def test_gap_and_semantic_flag(self):
        data=audit.report(self.oval,self.maps,pin=None)
        rows={item['source_declaration']:item for item in data['entries']}
        self.assertEqual(data['xsd_files'],2)
        self.assertEqual(len(rows),4)
        self.assertEqual(rows['legacy_test']['mapping_status'],'unmapped_declaration')
        self.assertEqual(rows['variable_object']['mapping_status'],'mapped_declaration')
        self.assertEqual(rows['variable_object']['review_flags'],
                         ['variable_object_set_choice_vs_direct_variable_source'])
        self.assertIn('id',[attr['name'] for attr in rows['variable_object']['attributes']])
        self.assertEqual(rows['legacy_test']['deprecations'][0]['version'],'5.11')
        self.assertEqual(data['embedded_schematron_rules'],1)
        self.assertEqual(data['schematron'][0]['context'],'ind:legacy_test')

    def test_missing_xsd_import_is_error(self):
        (self.oval/'oval-definitions-schema.xsd').unlink()
        with self.assertRaisesRegex(ValueError,'missing local XSD'):
            audit.report(self.oval,self.maps,pin=None)

    def test_wrong_source_pin_fails(self):
        with self.assertRaises(Exception):
            audit.report(self.oval,self.maps,pin='f'*40)

    def test_deterministic_output(self):
        first=audit.report(self.oval,self.maps,pin=None)
        second=audit.report(self.oval,self.maps,pin=None)
        self.assertEqual(json.dumps(first,sort_keys=True),json.dumps(second,sort_keys=True))

    def test_orphan_mapping_visible(self):
        changed=dict(MAPPING)
        changed['source']=dict(MAPPING['source'],test='missing_test')
        (self.maps/'variable.value.json').write_text(json.dumps(changed))
        result=audit.report(self.oval,self.maps,pin=None)
        self.assertTrue(any(row['source_qname'].endswith('}missing_test') for row
                            in result['mapping_source_qnames_without_declaration']))


if __name__=='__main__':
    unittest.main()
