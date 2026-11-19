#!/usr/bin/env python3
"""Read-only OVAL 5.12.3 XSD grammar and SCAP-NG primary-mapping inventory.

Not an XML Schema validator or a certificate of semantic/runtime equivalence.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

X = '{http://www.w3.org/2001/XMLSchema}'
SCH = '{http://purl.oclc.org/dsdl/schematron}'
OVAL = '{http://oval.mitre.org/XMLSchema/oval-common-5}'
BASE = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'
PIN = '2f140ee5c5dd1ed9606fcd5afc301f6baeb48706'
ROLES = ('test', 'object', 'state')


def parse(path):
    namespaces = {}
    for _, (prefix, uri) in ET.iterparse(path, events=('start-ns',)):
        if prefix in namespaces and namespaces[prefix] != uri:
            raise ValueError(f'namespace prefix rebound: {path} {prefix}')
        namespaces[prefix] = uri
    return namespaces, ET.parse(path).getroot()


def distinct(rows):
    return [json.loads(item) for item in sorted({json.dumps(row, sort_keys=True)
                                                  for row in rows})]


class Grammar:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.files = {}
        self.globals = {}
        paths = sorted(self.directory.glob('*.xsd'))
        if not paths:
            raise ValueError('no OVAL XSD files')
        for path in paths:
            prefixes, root = parse(path)
            ns = root.get('targetNamespace', '')
            self.files[path.name] = {
                'path': path, 'namespace': ns, 'prefixes': prefixes,
                'sha256': sha256(path.read_bytes()).hexdigest()
            }
            for node in root:
                if node.tag.startswith(X) and node.get('name'):
                    key = (ns, node.tag[len(X):], node.get('name'))
                    if key in self.globals:
                        raise ValueError(f'duplicate source declaration: {key}')
                    self.globals[key] = (path.name, node)
                if node.tag in (X+'import', X+'include', X+'redefine'):
                    location = node.get('schemaLocation')
                    if location and not (self.directory/location).is_file():
                        raise ValueError(f'missing local XSD import/include: {path.name} -> {location}')

    def resolve(self, file, token):
        if not token:
            return None
        if ':' in token:
            prefix, name = token.split(':', 1)
            ns = self.files[file]['prefixes'].get(prefix)
            if ns is None:
                raise ValueError(f'unknown source QName prefix {token} in {file}')
            return (ns, name)
        # The official source qualifies foreign global references. An
        # unqualified local type is resolved against the target namespace.
        ns = self.files[file]['namespace']
        if any(key[0] == ns and key[2] == token for key in self.globals):
            return (ns, token)
        return ('', token)

    def describe(self, file, node):
        pending = [(file, node)]
        seen = set()
        elements, attributes, choices, enums, deprecated = [], [], [], [], []
        while pending:
            current_file, current = pending.pop()
            marker = (current_file, id(current))
            if marker in seen:
                continue
            seen.add(marker)
            for part in current.iter():
                kind = part.tag[len(X):] if part.tag.startswith(X) else ''
                if kind in ('element', 'attribute') and (part.get('name') or part.get('ref')):
                    fields = elements if kind == 'element' else attributes
                    fields.append({k:part.get(k) for k in
                                   ('name','ref','type','use','minOccurs','maxOccurs',
                                    'default','fixed','nillable') if part.get(k) is not None})
                elif kind == 'choice':
                    choices.append({
                        'minOccurs':part.get('minOccurs','1'),
                        'maxOccurs':part.get('maxOccurs','1'),
                        'branches':[{'kind':child.tag[len(X):], 'name':child.get('name'),
                                     'ref':child.get('ref')}
                                    for child in part if child.tag.startswith(X)
                                    and child.tag != X+'annotation']
                    })
                elif kind == 'enumeration' and part.get('value') is not None:
                    enums.append(part.get('value'))
                elif part.tag == OVAL+'deprecated_info':
                    deprecated.append({
                        'version':part.findtext(OVAL+'version'),
                        'reason':' '.join((part.findtext(OVAL+'reason') or '').split())
                    })
                for attr in ('type','base','ref','memberTypes'):
                    for token in part.get(attr,'').split():
                        resolved = self.resolve(current_file, token)
                        if resolved is None:
                            continue
                        types = ('element','attribute','group','attributeGroup') if attr == 'ref' else ('complexType','simpleType')
                        for candidate in types:
                            found = self.globals.get((*resolved[:1], candidate, resolved[1]))
                            if found and (found[0],id(found[1])) not in seen:
                                pending.append(found)
        return {'elements':distinct(elements), 'attributes':distinct(attributes),
                'choices':distinct(choices), 'enumerations':sorted(set(enums)),
                'deprecations':distinct(deprecated), 'resolved_declarations':len(seen)}

    def entries(self):
        rows = []
        for (ns, kind, name), (file, node) in sorted(self.globals.items()):
            if kind != 'element':
                continue
            parent = self.resolve(file,node.get('substitutionGroup'))
            if parent is None or parent[0] != BASE or parent[1] not in ROLES:
                continue
            row = {'source_qname':f'{{{ns}}}{name}', 'role':parent[1],
                   'source_file':file, 'source_file_sha256':self.files[file]['sha256'],
                   'source_declaration':name}
            row.update(self.describe(file,node))
            rows.append(row)
        return rows

    def schematron(self):
        rows = []
        for file, data in sorted(self.files.items()):
            _, doc = parse(data['path'])
            for pattern in doc.iter(SCH+'pattern'):
                for rule in pattern.iter(SCH+'rule'):
                    for assertion in rule:
                        if assertion.tag in (SCH+'assert', SCH+'report'):
                            rows.append({'source_file':file,'pattern':pattern.get('id'),
                                         'context':rule.get('context'),
                                         'kind':assertion.tag[len(SCH):],
                                         'test':assertion.get('test'),
                                         'message':' '.join(''.join(assertion.itertext()).split())})
        return rows


def report(oval_dir, mapping_root, pin=PIN):
    oval_dir = Path(oval_dir)
    if pin:
        checkout = oval_dir.parent if oval_dir.name == 'oval-schemas' else oval_dir
        actual = subprocess.check_output(
            ['git','-C',str(checkout),'rev-parse','HEAD'], text=True,
            stderr=subprocess.DEVNULL).strip()
        if actual != pin:
            raise ValueError(f'wrong OVAL checkout {actual} != {pin}')
    grammar = Grammar(oval_dir)
    if pin and len(grammar.files) != 54:
        raise ValueError(f'expected 54 pinned XSD files, got {len(grammar.files)}')
    entries = grammar.entries()
    names = {(row['source_qname'], row['role']) for row in entries}
    primary = {}
    for path in sorted(Path(mapping_root).rglob('*.json')):
        record = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(record,dict) or 'capability' not in record or 'source' not in record:
            continue
        source = record['source']
        for role in ROLES:
            if source.get(role) and source.get('namespace'):
                key = (f'{{{source["namespace"]}}}{source[role]}',role)
                primary.setdefault(key,[]).append((path,record))
    for row in entries:
        matches = primary.get((row['source_qname'],row['role']),[])
        row['mapping_status'] = 'mapped_declaration' if matches else 'unmapped_declaration'
        row['canonical_capabilities'] = sorted({record['capability'] for _,record in matches})
        row['mapping_paths'] = sorted(str(path.relative_to(mapping_root)) for path,_ in matches)
        row['further_semantic_review_required'] = True
        direct_variable = any(record.get('native',{}).get('test_source',{}).get('kind')=='variable'
                              for _,record in matches)
        has_set = any(child.get('ref','').endswith(':set') for choice in row['choices']
                      for child in choice['branches'] if child.get('ref'))
        row['review_flags'] = (['variable_object_set_choice_vs_direct_variable_source']
                               if row['role']=='object' and direct_variable and has_set else [])
    sch = grammar.schematron()
    counts = Counter(row['mapping_status'] for row in entries)
    counts.update({f'role:{role}':sum(row['role']==role for row in entries)
                   for role in ROLES})
    missing = [{'source_qname':qname,'role':role,'mapping':str(path.relative_to(mapping_root)),
                'capability':record['capability']}
               for (qname,role),matches in sorted(primary.items()) if (qname,role) not in names
               for path,record in matches]
    return {
        'format':'scap-ng/oval-source-grammar-inventory/1',
        'qualification':'XSD declarations and mapping inventory only; NOT source semantic/RI parity proof.',
        'source_pin':pin,'xsd_files':len(grammar.files),
        'source_files':{key:data['sha256'] for key,data in sorted(grammar.files.items())},
        'summary':dict(sorted(counts.items())),
        'embedded_schematron_rules':len(sch), 'schematron':sch,
        'entries':entries,'mapping_source_qnames_without_declaration':missing
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--oval-dir',type=Path,required=True)
    parser.add_argument('--mapping-root',type=Path,
                        default=Path(__file__).resolve().parents[1]/'schema/capability-mappings')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--skip-pin-check',action='store_true',
                        help='Synthetic test fixtures only; no source authority')
    args = parser.parse_args()
    result = report(args.oval_dir,args.mapping_root,None if args.skip_pin_check else PIN)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'xsd_files':result['xsd_files'],'summary':result['summary'],
                      'embedded_schematron_rules':result['embedded_schematron_rules'],
                      'orphan_mappings':len(result['mapping_source_qnames_without_declaration'])},
                     sort_keys=True))


if __name__ == '__main__':
    main()
