#!/usr/bin/env python3
"""Evidence/Audit: new OVAL 6.0 tests only; preserve the 5.12.3 baseline.

Source contracts are review evidence, not native schemas or scanner conformance.
Read upstream Git blobs at the pinned commit, preserving bytes on Windows too.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from lxml import etree as ET

ROOT=Path(__file__).resolve().parents[1]
UPSTREAM='5afcf590fb5d334687bfdc47f98716424cdb7f3d'
X='{http://www.w3.org/2001/XMLSchema}'
SCH='{http://purl.oclc.org/dsdl/schematron}'

def sha(data):return hashlib.sha256(data).hexdigest()
def tree(path):return ET.parse(str(path),ET.XMLParser(resolve_entities=False,no_network=True)).getroot()
def globals(root,suffix):return {n.get('name'):n for n in root.findall(X+'element') if n.get('name','').endswith(suffix)}
def type_node(node,qname,roots):
    if not qname:return None
    prefix,local=qname.split(':',1) if ':' in qname else (None,qname)
    ns=node.nsmap.get(prefix)
    for root in roots:
        if root.get('targetNamespace')==ns:
            return next((n for n in root if isinstance(n.tag,str) and n.tag in (X+'complexType',X+'simpleType') and n.get('name')==local),None)
    return None

def particles(node):
    kinds={X+k for k in ('complexType','complexContent','simpleContent','extension','restriction','sequence','choice','all','group','element','any')}
    result=[]
    for child in node:
        if isinstance(child.tag,str) and child.tag in kinds:
            result.append({'kind':child.tag.removeprefix(X),'attributes':dict(child.attrib),'children':particles(child)})
    return result

def contract(node,roots,seen=None):
    seen=set() if seen is None else seen
    key=(node.getroottree().getroot().get('targetNamespace'),node.get('name'),node.tag)
    if key in seen:raise ValueError('Circular type inheritance')
    seen=seen|{key};inherited=[]
    # Only inherit the outer declaration's base/type, not bases of field types.
    targets=[]
    if node.get('type'):targets.append(node.get('type'))
    for path in ['./'+X+'complexType/'+X+'complexContent/*','./'+X+'complexContent/*',
                 './'+X+'simpleContent/*','./'+X+'complexType/'+X+'simpleContent/*']:
        for n in node.findall(path):
            if n.get('base'):targets.append(n.get('base'))
    for target in targets:
        parent=type_node(node,target,roots)
        if parent is not None:
            contract(parent,roots,seen)
            identity='{'+parent.getroottree().getroot().get('targetNamespace')+'}'+parent.get('name')
            inherited.append({'type':target,'type_ref':identity})
    fields=[]
    for field in node.iter(X+'element'):
        if field is node:continue
        fields.append({'name':field.get('name'),'ref':field.get('ref'),'type':field.get('type'),
                       'min_occurs':field.get('minOccurs','1'),'max_occurs':field.get('maxOccurs','1'),
                       'nillable':field.get('nillable','false'),'default':field.get('default'),'fixed':field.get('fixed')})
    attributes=[dict(n.attrib) for n in node.iter(X+'attribute')]
    facets=[{'kind':n.tag.removeprefix(X),'value':n.get('value')} for n in node.iter()
            if isinstance(n.tag,str) and n.tag in {X+k for k in ('enumeration','pattern','minInclusive','maxInclusive','minExclusive','maxExclusive','length','minLength','maxLength')}]
    refs=[{'kind':n.tag.removeprefix(X),'ref':n.get('ref'),'min_occurs':n.get('minOccurs','1'),'max_occurs':n.get('maxOccurs','1')}
          for n in node.iter() if isinstance(n.tag,str) and n.tag in (X+'group',X+'attributeGroup') and n.get('ref')]
    assertions=[{'context':rule.get('context'),'test':assertion.get('test')}
                for rule in node.iter(SCH+'rule') for assertion in rule.findall(SCH+'assert')]
    return {'content_model':particles(node),'fields':fields,'attributes':attributes,'facets':facets,'group_refs':refs,'inherited':inherited,'assertions':assertions}

def scan(before,after):
    roots=[tree(p) for p in sorted(after.glob('*.xsd'))]
    mappings={}
    for path in sorted((ROOT/'schema/v0.1.0/capability-mappings').glob('*.json')):
        m=json.loads(path.read_text())
        if 'capability' in m:
            source=m.get('source',{});family=Path(source.get('definitions_schema','')).name.removesuffix('-definitions-schema.xsd')
            mappings[(family,source.get('test'))]=m['capability']
    rows=[];files=[];all_types={}
    for path in sorted(after.glob('*-definitions-schema.xsd')):
        family=path.name.removesuffix('-definitions-schema.xsd');root=tree(path)
        old_path=before/path.name;old=globals(tree(old_path),'_test') if old_path.exists() else {}
        tests=globals(root,'_test');added=sorted(set(tests)-set(old))
        files.append({'file':path.name,'before_sha256':sha(old_path.read_bytes()) if old_path.exists() else None,
                      'after_sha256':sha(path.read_bytes()),'added_tests':added})
        if not added:continue
        sc_path=after/(family+'-system-characteristics-schema.xsd');sc=tree(sc_path)
        for test in added:
            stem=test.removesuffix('_test');nodes={kind:globals(owner,'_'+kind).get(stem+'_'+kind)
                for kind,owner in [('test',root),('object',root),('state',root),('item',sc)]}
            if any(n is None for n in nodes.values()):raise ValueError('Incomplete new-test contract: '+test)
            types={}
            pending=list(nodes.values());visited=set()
            while pending:
                owner=pending.pop()
                for child in owner.iter():
                    if not isinstance(child.tag,str):continue
                    for attr in ('type','base'):
                        value=child.get(attr);n=type_node(child,value,roots)
                        if n is None:continue
                        identity='{'+n.getroottree().getroot().get('targetNamespace')+'}'+n.get('name')
                        if identity in visited:continue
                        visited.add(identity);types[identity]=contract(n,roots);pending.append(n)
            for identity,value in types.items():
                if identity in all_types and all_types[identity]!=value:raise ValueError('Inconsistent shared type')
                all_types[identity]=value
            rows.append({'family':family,'test':test,'provisional_native_name':family+'.'+stem,
                'existing_native_mapping':mappings.get((family,test)),
                'definitions_file':path.name,'items_file':sc_path.name,'items_sha256':sha(sc_path.read_bytes()),
                'contracts':{kind:contract(n,roots) for kind,n in nodes.items()},'type_refs':sorted(types),
                'disposition':'needs_native_design_and_fixtures' if (family,test) not in mappings else 'mapped_requires_conformance_review'})
    return {'format':'scap-ng.oval-new-tests-audit.1','upstream_repository':'OVAL-Community/OVAL','upstream_tag':'v6.0','upstream_commit':UPSTREAM,
        'scope':'Only test names added to v6.0 relative to the vendored 5.12.3 definitions inventory. Existing-test/core/result/namespace/encapsulation differences are excluded. Associated new-test inheritance and type constraints are inventory evidence, not a semantic-equivalence claim.',
        'baseline':'third_party/scap-1.4-schemas/oval_5.12.3','definition_files':files,'new_tests':rows,'referenced_types':all_types}

def materialize(repo,destination):
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    if head!=UPSTREAM:raise ValueError('Upstream checkout must be pinned to '+UPSTREAM)
    paths=subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','--name-only',UPSTREAM,'oval-schemas'],text=True).splitlines()
    for path in paths:
        if path.endswith('.xsd'):
            raw=subprocess.check_output(['git','-C',str(repo),'show',UPSTREAM+':'+path]);(destination/Path(path).name).write_bytes(raw)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--upstream-repo',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=ROOT/'docs/audit/capability-coverage-2026-10-03/oval-new-tests.json');ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        materialize(args.upstream_repo,Path(tmp));result=scan(ROOT/'third_party/scap-1.4-schemas/oval_5.12.3',Path(tmp))
        result['source_schema_compilation']={}
        for family in sorted({row['family'] for row in result['new_tests']}):
            for kind in ('definitions','system-characteristics'):
                filename=family+'-'+kind+'-schema.xsd'
                ET.XMLSchema(ET.parse(str(Path(tmp)/filename)))
                result['source_schema_compilation'][filename]='passed'
    encoded=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.check:
        if json.loads(args.output.read_text())!=result:raise ValueError('New-test inventory differs; review and refresh the audit')
    else:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(encoded,encoding='utf-8')
    print(json.dumps({'new_tests':len(result['new_tests']),'families':sorted({r['family'] for r in result['new_tests']}),'mode':'checked' if args.check else 'written'}))
if __name__=='__main__':main()
