"""Source-backed acceptance of common Set collection semantics, not a scanner."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from v04_direct_scap_source import SourceModel
from v04_direct_scap_source import UnsupportedSource
from v04_direct_converter import convert
from audit_v04_direct_benchmark import verify_original, verify_compiled
from v04_native_bundle_compiler import build_bundle
from oval_result_truth_tables import SET_FLAGS, combine_set_flags

ROOT = Path(__file__).resolve().parents[1]
PINS = json.loads((ROOT/'tests/fixtures/v04-direct-prototype/provenance.json').read_text())
XSD = ROOT/'third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd'
XS = '{http://www.w3.org/2001/XMLSchema}'


class DirectArchitectureAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SourceModel(ROOT/'tests/fixtures/v04-direct-prototype'/PINS['fixture'], PINS['zip_sha256'])
        # Fixture selection only. Production discovery/admission has no ID list.
        cls.rules = ['xccdf_mil.disa.stig_rule_SV-'+suffix for suffix in
                     ('278192r1256723_rule','278193r1256726_rule','278194r1256729_rule')]
        cls.documents, cls.trace = convert(cls.source, cls.rules)

    def test_three_original_default_union_graphs_and_compiled_operands(self):
        proofs = verify_original(self.source.root, self.documents, self.trace)
        self.assertEqual([p['outcome'] for p in proofs], ['PROVED']*3)
        self.assertEqual(len(verify_compiled(self.documents, build_bundle(self.documents)[0])), 3)
        for binding in self.trace['rules']:
            source_sets = [self.source.nodes[binding['component']][ident] for ident, info in binding['dependencies'].items()
                           if info['kind']=='object' and 'set' in self.source.nodes[binding['component']][ident][0].tag]
            self.assertTrue(source_sets)
            self.assertTrue(all(not node[0].attrib for node in source_sets))  # Original default UNION, not inferred OR.

    def test_changed_operator_operand_and_quantifier_never_pass_independent_proof(self):
        for mutation in ('operator','operand','quantifier'):
            docs = deepcopy(self.documents)
            a = next(d['assessment'] for d in docs.values() if 'assessment' in d)
            test = next(iter(a['tests'].values()))
            if mutation=='operator':
                test['object']['set']['operator']='intersection'
            elif mutation=='operand':
                # Original outer Set's first operand is itself a referenced Set Object.
                test['object']['set']['operands'].pop()
            else:
                test['require']['items_found']='none'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                verify_original(self.source.root, docs, self.trace)

    def test_all_108_collection_flags_match_original_5123_charts(self):
        xsd=ET.parse(XSD).getroot()
        enum=xsd.find(XS+'simpleType[@name="SetOperatorEnumeration"]')
        charts=enum.findall('.//evaluation_chart')
        self.assertEqual(len(charts),3)
        aliases=dict(zip(('E','C','I','DNE','NC','NA'),SET_FLAGS))
        count=0
        for operator, chart in zip(('UNION','INTERSECTION','COMPLEMENT'),charts):
            rows=[]
            for line in chart.text.splitlines():
                left, sep, right=line.partition('||')
                tokens=left.split()
                if sep and tokens and tokens[-1] in aliases:
                    results=[s.strip() for s in right.split('||')[0].split('|')]
                    if len(results)==6 and all(s in aliases for s in results):
                        rows.append((aliases[tokens[-1]],results))
            self.assertEqual(len(rows),6)
            for second, values in rows:
                for first, expected in zip(SET_FLAGS,values):
                    self.assertEqual(combine_set_flags(operator,first,second),aliases[expected])
                    count+=1
        self.assertEqual(count,108)
        with self.assertRaises(ValueError):
            combine_set_flags('UNION','unknown','complete')

    def test_schema_operator_and_filter_boundary_are_original_contracts(self):
        root=ET.parse(XSD).getroot()
        set_type=root.find(XS+'element[@name="set"]')
        operator=set_type.find('.//'+XS+'attribute[@name="set_operator"]')
        self.assertEqual(operator.get('default'),'UNION')
        docs=' '.join(set_type.itertext())
        self.assertIn('before the set_operator is applied',docs)
        enum=root.find(XS+'simpleType[@name="SetOperatorEnumeration"]')
        text=' '.join(enum.itertext())
        self.assertIn('first declared set',text)
        self.assertIn('single object',text)

    def test_original_ordered_comparisons_and_inclusive_boundary_mutants(self):
        rules=['xccdf_mil.disa.stig_rule_SV-'+suffix for suffix in
               ('278147r1192630_rule','278176r1256743_rule','278204r1182319_rule')]
        documents, trace=convert(self.source,rules)
        self.assertEqual(len(verify_original(self.source.root,documents,trace)),3)
        self.assertEqual(len(verify_compiled(documents,build_bundle(documents)[0])),3)
        # Alter inclusion at the boundary without changing an expected literal.
        mutant=deepcopy(documents)
        changed=[]
        def alter(node):
            if isinstance(node,dict):
                for key in list(node):
                    if key=='less_than_or_equal':
                        node['less_than']=node.pop(key);changed.append(True)
                    else:alter(node[key])
            elif isinstance(node,list):
                for child in node:alter(child)
        alter(mutant)
        self.assertTrue(changed)
        with self.assertRaises(AssertionError):
            verify_original(self.source.root,mutant,trace)
        # A controlled source copy checks the third integer operator; it adds
        # no claim about another original Rule or arbitrary string ordering.
        source=deepcopy(self.source)
        binding=trace['rules'][-1]
        states=[source.nodes[binding['component']][i] for i,v in binding['dependencies'].items() if v['kind']=='state']
        entity=next(c for n in states for c in n if c.get('operation')=='greater than')
        entity.set('operation','greater than or equal')
        docs, changed_trace=convert(source,[rules[-1]])
        self.assertEqual(len(verify_original(source.root,docs,changed_trace)),1)
        self.assertEqual(len(verify_compiled(docs,build_bundle(docs)[0])),1)
        for datatype in ('string','boolean'):
            entity.set('datatype',datatype)
            with self.subTest(datatype=datatype), self.assertRaises(UnsupportedSource):
                convert(source,[rules[-1]])


if __name__=='__main__':unittest.main()
