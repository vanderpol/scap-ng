"""Source-identity and dataflow regressions; no target evaluator claim."""
import sys
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy
sys.path.insert(0,str(Path(__file__).parent))
from test_variable_filter_dependencies import source, variable, component, literal, set_source, add_filter, OD, UNIX, DID
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.collection_graph import collection_types
from scap_ng_roundtrip_v003.native_assessment_to_oval import build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare

class NamedCollections(unittest.TestCase):
    def lower(self,root):
        native,error=lower_definition(root,DID,'test-assessment',collection_graph=True)
        self.assertIsNone(error)
        return native

    def roundtrip(self,root,native):
        regenerated,rid=build(native)
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'original.xml'; b=Path(d)/'regenerated.xml'
            ET.ElementTree(root).write(a,encoding='utf-8')
            regenerated.write(b,encoding='utf-8')
            result=compare(a,b,DID,rid,root_only=True)
        self.assertTrue(result['equal'],result)
        return regenerated.getroot()

    def linked_source(self,distinct=False):
        root=source()
        objects=root.find(f'{{{OD}}}objects')
        obj=ET.SubElement(objects,f'{{{UNIX}}}file_object',id='oval:dependency:obj:2',version='1',comment='User data')
        ET.SubElement(obj,f'{{{UNIX}}}path').text='/etc'
        ET.SubElement(obj,f'{{{UNIX}}}filename').text='passwd'
        values=component('object_component',object_ref='oval:dependency:obj:2',item_field='filename')
        variable(root,1,values)
        test=ET.SubElement(root.find(f'{{{OD}}}tests'),f'{{{UNIX}}}file_test',id='oval:dependency:tst:2',version='1',check='all')
        ET.SubElement(test,f'{{{UNIX}}}object',object_ref='oval:dependency:obj:2')
        ET.SubElement(root.find(f'.//{{{OD}}}criteria'),f'{{{OD}}}criterion',test_ref='oval:dependency:tst:2')
        if distinct:
            copy=deepcopy(obj);copy.set('id','oval:dependency:obj:3');objects.append(copy)
            concat=component('concat');concat.append(values);concat.append(component('object_component',object_ref='oval:dependency:obj:3',item_field='filename'))
            var=root.find(f'.//{{{OD}}}local_variable');var.remove(values);var.append(concat)
        return root

    def test_shared_source_object_has_one_named_collection(self):
        root=self.linked_source();native=self.lower(root);a=native['assessment']
        self.assertEqual(len(a['collections']),2)
        var=next(iter(a['variables'].values()))
        ref=var['expression']['values']['collection']
        self.assertIn(ref,[t['collection'] for t in a['tests'].values()])
        self.assertNotIn('collection_capabilities',var)
        self.assertTrue(all('capability' in c for c in a['collections'].values()))
        emitted=self.roundtrip(root,native)
        self.assertEqual(len(emitted.find(f'{{{OD}}}objects')),2)

    def test_equal_payload_distinct_source_objects_stay_distinct(self):
        root=self.linked_source(True);native=self.lower(root)
        self.assertEqual(len(native['assessment']['collections']),3)
        emitted=self.roundtrip(root,native)
        self.assertEqual(len(emitted.find(f'{{{OD}}}objects')),3)

    def test_variable_only_source_collection_keeps_own_type(self):
        root=self.linked_source();root.find(f'{{{OD}}}tests').remove(root.find(f'{{{OD}}}tests')[1]);criteria=root.find(f'.//{{{OD}}}criteria');criteria.remove(criteria[1])
        native=self.lower(root);a=native['assessment']
        var=next(iter(a['variables'].values()))
        ref=var['expression']['values']['collection']
        self.assertNotIn('collection_capabilities',var)
        self.assertEqual(a['collections'][ref]['capability'],'unix.file')
        self.roundtrip(root,native)

    def test_variable_chain_depth32_preserved(self):
        root=source()
        for n in range(1,32):variable(root,n,component('variable_component',var_ref=f'oval:dependency:var:{n+1}'))
        variable(root,32,literal())
        native=self.lower(root)
        self.assertEqual(len(native['assessment']['variables']),32)
        self.assertTrue(all('variable' in name for name in native['assessment']['variables']))
        self.roundtrip(root,native)

    def test_nested_set_collection_references_roundtrip(self):
        root=set_source(4);native=self.lower(root)
        self.assertEqual(len(native['assessment']['collections']),2)
        self.roundtrip(root,native)

    def test_filter_hidden_variable_roundtrip(self):
        root=source();add_filter(root,'oval:dependency:var:1');variable(root,1,literal())
        native=self.lower(root)
        self.roundtrip(root,native)

    def test_missing_reference_and_variable_cycle_block(self):
        root=source()
        native,error=lower_definition(root,DID,'x',collection_graph=True)
        self.assertIsNone(native);self.assertIn('variable_not_found',error)
        variable(root,1,component('variable_component',var_ref='oval:dependency:var:1'))
        native,error=lower_definition(root,DID,'x',collection_graph=True)
        self.assertIsNone(native);self.assertIn('variable_cycle',error)

    def test_embedded_private_collection_typed_on_variable(self):
        root=self.linked_source()
        root.find(f'{{{OD}}}tests').remove(root.find(f'{{{OD}}}tests')[1])
        criteria=root.find(f'.//{{{OD}}}criteria');criteria.remove(criteria[1])
        native=self.lower(root);a=native['assessment']
        var=next(iter(a['variables'].values()))
        ref=var['expression']['values']['collection']
        # Native authoring fixture: a one-use source can be private. The source
        # converter itself keeps original source Objects named.
        var['expression']['values']['collection']=a['collections'].pop(ref)
        self.assertEqual(var['expression']['values']['collection']['capability'],'unix.file')
        self.roundtrip(root,native)

    def test_embedded_source_cannot_be_referenced_outside_variable(self):
        a={'collections':{},'tests':{},'variables':{
            'a-variable':{'expression':{'values':{'collection':{'capability':'unix.file','select':{}},'field':'filename'}}},
            'b-variable':{'expression':{'values':{'collection':'private-collection','field':'filename'}}}}}
        with self.assertRaisesRegex(ValueError,'Unknown Collection'): collection_types(a)

    def test_named_collection_cycles_rejected_by_consumer(self):
        a={'collections':{'a-collection':{'capability':'unix.file','set':{'members':[{'collection':'a-collection'}]}}},
           'tests':{'test-a':{'capability':'unix.file','collection':'a-collection'}},'variables':{}}
        with self.assertRaisesRegex(ValueError,'cycle'):collection_types(a)

    def test_graph_binding_resource_limit_is_explicit(self):
        from unittest.mock import patch
        root=source();variable(root,1,literal())
        with patch('scap_upconvert_v003.collection_graph.validate_capabilities',side_effect=RecursionError):
            native,error=lower_definition(root,DID,'x',collection_graph=True)
        self.assertIsNone(native)
        self.assertEqual(error,'conversion_resource_limit:python_recursion')

    def test_local_zip_cli_from_another_working_directory(self):
        import hashlib,subprocess,zipfile,json
        root=source();variable(root,1,literal())
        benchmark=f'<Benchmark xmlns="http://checklists.nist.gov/xccdf/1.2" id="b"><Group id="g"><Rule id="xccdf_test_rule_SV-257777r1_rule"><title>Local review</title><check system="{OD}"><check-content-ref name="{DID}" href="oval.xml"/></check></Rule></Group></Benchmark>'
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d);package=folder/'source.zip'
            with zipfile.ZipFile(package,'w') as z:
                z.writestr('benchmark.xml',benchmark)
                z.writestr('oval.xml',ET.tostring(root))
            digest=hashlib.sha256(package.read_bytes()).hexdigest()
            script=Path(__file__).parent/'scap_upconvert_v003/convert_collection_review.py'
            command=[sys.executable,str(script.resolve()),'--input',str(package),'--sha256',digest,
                     '--output',str(folder/'out'),'--rule','SV-257777']
            result=subprocess.run(command,cwd=folder,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr+result.stdout)
            report=json.loads((folder/'out/evidence.json').read_text())
            self.assertEqual(report['status'],'prototype_dataflow_and_roundtrip_checks_passed')
            self.assertTrue(report['rules'][0]['assessments'][0]['reverse_omni_schema_valid'])

    def test_variable_side_type_binding_rejected(self):
        a={'collections':{'x-collection':{'capability':'unix.file'}},'tests':{},'variables':{
            'a-variable':{'collection_capabilities':{'x-collection':'unix.file'}}}}
        with self.assertRaisesRegex(ValueError,'obsolete'): collection_types(a)

if __name__=='__main__':unittest.main()
