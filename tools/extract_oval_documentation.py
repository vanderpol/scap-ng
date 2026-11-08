#!/usr/bin/env python3
"""Extract pinned XSD annotations for mapped capabilities; never scrape HTML.

This is a provenance harvester, not a documentation prose source or a scanner.
The native renderer reads descriptions from proposed JSON Schemas only.
"""
from collections import defaultdict, deque
from hashlib import sha256
import argparse
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
XS='http://www.w3.org/2001/XMLSchema'
X='{'+XS+'}'
PIN5='2f140ee5c5dd1ed9606fcd5afc301f6baeb48706'
PIN6='5afcf590fb5d334687bfdc47f98716424cdb7f3d'
DEST=Path('docs/fidelity/source-documentation.json')


def encode(value):return json.dumps(value,indent=2,ensure_ascii=False)+'\n'
def local(tag):return tag.rsplit('}',1)[-1]
def stem(name):return re.sub(r'\d+$','',re.sub(r'_(?:test|object|state|item)$','',name))


def normalized_text(element):
    def text(node):
        value=node.text or ''
        for child in node:
            boundary='\n\n' if local(child.tag) in ('p','div','li','ul','ol','br') else ''
            value+=boundary+text(child)+boundary+(child.tail or '')
        return value
    return '\n\n'.join(' '.join(p.split()) for p in re.split(r'\n\s*\n',text(element)) if p.strip())


class XSDs:
    def __init__(self,path,pin):
        self.path=Path(path);self.pin=pin;self.files={};self.index={};self.by_namespace={}
        for p in sorted(self.path.glob('*.xsd')):
            namespaces={prefix:uri for event,(prefix,uri) in ET.iterparse(p,events=('start-ns',))}
            root=ET.parse(p).getroot();ns=root.get('targetNamespace','')
            paths={}
            def visit(node,xpath):
                paths[id(node)]=xpath
                groups=defaultdict(list)
                for child in node:groups[child.tag].append(child)
                for tag,children in groups.items():
                    for i,child in enumerate(children,1):
                        key='xs:'+local(tag) if tag.startswith(X) else '*'
                        if child.get('name'):
                            key+="[@name='"+child.get('name')+"']"
                            same=[c for c in children if c.get('name')==child.get('name')]
                            if len(same)>1:key+='['+str(same.index(child)+1)+']'
                        else:key+='['+str(i)+']'
                        visit(child,xpath+'/'+key)
            visit(root,'/xs:schema')
            self.files[p.name]={'root':root,'namespace':ns,'namespaces':namespaces,'paths':paths,'sha256':sha256(p.read_bytes()).hexdigest()}
            self.by_namespace[ns]=p.name
            for node in root:
                if node.tag.startswith(X) and node.get('name'):
                    self.index[(ns,local(node.tag),node.get('name'))]=(p.name,node)

    def declaration(self,file,kind,name):
        data=self.files[file]
        return self.index.get((data['namespace'],kind,name))

    def references(self,file,node):
        data=self.files[file]
        for element in node.iter():
            for key in ('type','base','ref','memberTypes'):
                for token in element.get(key,'').split():
                    if ':' in token:
                        prefix,name=token.split(':',1);ns=data['namespaces'].get(prefix)
                    else:ns=data['namespace'];name=token
                    kinds=[local(element.tag)] if key=='ref' else ['complexType','simpleType']
                    for kind in kinds:
                        if (ns,kind,name) in self.index:yield self.index[(ns,kind,name)]

    def item_candidates(self,definitions_file,names,explicit=None):
        file=definitions_file.replace('-definitions-schema.xsd','-system-characteristics-schema.xsd')
        if file not in self.files:return []
        root=self.files[file]['root']
        if explicit:
            node=next((n for n in root.findall(X+'element') if n.get('name')==explicit),None)
            if node is None:raise ValueError('Explicit Item not found: '+file+':'+explicit)
            return [(file,node,'explicit mapping')]
        bases={stem(n) for n in names if n}
        return [(file,n,'name-family correspondence; preserved as explicit audit mapping') for n in root.findall(X+'element') if n.get('name','').endswith('_item') and stem(n.get('name')) in bases]


def harvest(oval5,oval6,root=ROOT):
    libraries={'5.12.3':XSDs(oval5,PIN5),'6.0':XSDs(oval6,PIN6)}
    documents={};capabilities=[];files={}
    for p in sorted((root/'schema/capability-mappings').glob('*/*.json')):
        mapping=json.loads(p.read_text());cap=mapping['capability'];source=mapping['source']
        version='6.0' if source.get('upstream_commit')==PIN6 else '5.12.3';lib=libraries[version]
        filename=Path(source['definitions_schema']).name
        declarations=[];direct=[]
        for role in ('test','object','state'):
            name=source.get(role)
            if not name:continue
            found=lib.declaration(filename,'element',name)
            if not found:raise ValueError('Mapped declaration missing: '+cap+':'+name)
            declarations.append((role,filename,name,'primary mapping'))
            direct.append((role,*found,'primary mapping'))
        for file,item,basis in lib.item_candidates(filename,[source.get(r) for r in ('test','object','state')],source.get('item')):
            direct.append(('item',file,item,basis));declarations.append(('item',file,item.get('name'),basis))
        # Preserve explicit multi-construct contributors; rejected deprecated
        # aliases are recorded separately, never silently treated as supported.
        related=[]
        for alias,target in mapping.get('migration_crosswalk',{}).get('capability',{}).items():
            if alias==source['test'].removesuffix('_test'):continue
            for role in ('test','object','state'):
                found=lib.declaration(filename,'element',alias+'_'+role)
                if found:
                    basis='contributing migration alias' if target==cap else 'rejected/deprecated related source'
                    related.append((role,*found,basis));declarations.append((role,filename,alias+'_'+role,basis))
        queue=deque((role,file,node,basis,True) for role,file,node,basis in direct+related)
        visited=set();members=[]
        while queue:
            role,file,node,basis,is_direct=queue.popleft();data=lib.files[file]
            key=(file,data['paths'][id(node)])
            if key in visited:continue
            visited.add(key)
            files[version+'/'+file]={'version':version,'commit':lib.pin,'path':'oval-schemas/'+file,'sha256':data['sha256']}
            for annotation in node.iter(X+'documentation'):
                text=normalized_text(annotation)
                if not text:continue
                xpath=data['paths'][id(annotation)]
                identity=sha256((lib.pin+'\0'+file+'\0'+xpath).encode()).hexdigest()[:24]
                record={'id':identity,'version':version,'commit':lib.pin,'file':'oval-schemas/'+file,'file_sha256':data['sha256'],
                        'xpath':xpath,'namespace_bindings':{'xs':XS},'text':text,'text_sha256':sha256(text.encode()).hexdigest(),
                        'xml':ET.tostring(annotation,encoding='unicode')}
                if identity in documents and documents[identity]['text']!=text:raise ValueError('Source identity collision')
                documents[identity]=record
                members.append({'documentation':identity,'role':role if is_direct else 'shared_type','declaration':node.get('name'),
                                'basis':basis,'direct':is_direct,'declaration_xpath':data['paths'][id(node)]})
            for ref_file,ref_node in lib.references(file,node):
                queue.append(('shared_type',ref_file,ref_node,'referenced type/group/attribute declaration',False))
        capabilities.append({'capability':cap,'mapping':str(p.relative_to(root)),'mapping_sha256':sha256(p.read_bytes()).hexdigest(),
                             'source_version':version,'outside_5123':version!='5.12.3','declarations':[{'role':r,'file':f,'name':n,'basis':b} for r,f,n,b in declarations],
                             'documentation':sorted({json.dumps(m,sort_keys=True) for m in members})})
    for cap in capabilities:cap['documentation']=[json.loads(m) for m in cap['documentation']]
    return {'format':'scap-ng-xsd-documentation-extraction-1','source_repository':'https://github.com/OVAL-Community/OVAL',
            'pins':{'5.12.3':PIN5,'6.0-new-tests':PIN6},'files':dict(sorted(files.items())),
            'capabilities':capabilities,'documents':dict(sorted(documents.items()))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--oval-dir',required=True,type=Path)
    parser.add_argument('--oval6-dir',required=True,type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    for version,path,pin in [('5.12.3',args.oval_dir,PIN5),('6.0',args.oval6_dir,PIN6)]:
        actual=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True).strip()
        if actual!=pin:raise SystemExit('Wrong OVAL '+version+' checkout: '+actual)
    result=harvest(args.oval_dir,args.oval6_dir)
    raw=encode(result);dest=ROOT/DEST
    if args.check:
        if not dest.exists() or dest.read_text()!=raw:raise SystemExit('Stale XSD documentation extraction')
    else:dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(raw)
    print(encode({'capabilities':len(result['capabilities']),'source_documents':len(result['documents']),
                  'capability_document_bindings':sum(len(c['documentation']) for c in result['capabilities']),
                  'source_files':len(result['files']),'outside_5123':sum(c['outside_5123'] for c in result['capabilities'])}).strip())


if __name__=='__main__':main()
