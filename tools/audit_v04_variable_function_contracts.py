#!/usr/bin/env python3
"""Read-only original OVAL function contracts and transitive source usage (#251/#255).

This emits engineering facts, not NG syntax, source conversion or evaluation.
It intentionally sees functions hidden behind an earlier conversion blocker.
"""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from lxml import etree
from audit_v04_oval_test_corpus import PIN, OVAL_ROOT, OvalDocument, closure, file_inventory, xml_documents
from inventory_v04_six_source_requirements import closure_validity
from oval_source_validation import SourceValidator
from v04_direct_inventory import SourceInventory
from v04_direct_scap_source import ensure

ROOT = Path(__file__).resolve().parents[1]
X = '{http://www.w3.org/2001/XMLSchema}'
S = '{http://purl.oclc.org/dsdl/schematron}'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'
CURRENT_VISITOR_FUNCTIONS = frozenset({'concat', 'regex_capture', 'unique', 'merge'})


def text(node):
    return ' '.join(''.join(node.itertext()).split())


def schema_contracts(schema_root):
    path = schema_root / 'oval-definitions-schema.xsd'
    raw = path.read_bytes()
    root = etree.fromstring(raw)
    group = root.find(X + "group[@name='FunctionGroup']")
    ensure(group is not None, 'missing original FunctionGroup')
    result = {}
    for declaration in group.findall('.//' + X + 'element'):
        name = declaration.get('name')
        type_name = declaration.get('type').split(':')[-1]
        node = root.find(X + "complexType[@name='" + type_name + "']")
        ensure(node is not None, 'missing original function type: ' + type_name)
        sequence = node.find(X + 'sequence')
        ensure(sequence is not None and sequence.find(X + 'group') is not None,
               'unsupported original function particle: ' + name)
        attributes = []
        for attr in node.findall(X + 'attribute'):
            facts = dict(attr.attrib)
            if attr.get('type', '').startswith('oval-def:'):
                simple = root.find(X + "simpleType[@name='" + attr.get('type').split(':')[-1] + "']")
                ensure(simple is not None, 'missing original option type')
                facts['enumeration'] = [n.get('value') for n in simple.findall('.//' + X + 'enumeration')]
            attributes.append(facts)
        rules = []
        for rule in node.findall('.//' + S + 'rule'):
            rules.append({'line': rule.sourceline, 'context': rule.get('context'),
                          'lets': [dict(n.attrib) for n in rule.findall(S + 'let')],
                          'assertions': [{'test': n.get('test'), 'message': text(n)} for n in rule.findall(S + 'assert')]})
        result[name] = {'type': type_name, 'line': node.sourceline,
            'arity': {'minimum': int(sequence.get('minOccurs', '1')),
                      'maximum': sequence.get('maxOccurs', '1')},
            'attributes': attributes, 'schematron': rules,
            'documentation': [text(n) for n in node.findall('./' + X + 'annotation/' + X + 'documentation')],
            'existing_visitor_subset': name in CURRENT_VISITOR_FUNCTIONS}
    enumerations = {}
    for name in ('ArithmeticEnumeration', 'DateTimeFormatEnumeration', 'SortEnumeration', 'OrderEnumeration'):
        node = root.find(X + "simpleType[@name='" + name + "']")
        ensure(node is not None, 'missing original function enumeration: ' + name)
        enumerations[name] = {'line': node.sourceline, 'values': [n.get('value') for n in node.findall('.//' + X + 'enumeration')],
                              'documentation': [text(n) for n in node.findall('.//' + X + 'documentation')]}
    global_rules = []
    for rule in root.findall('.//' + S + 'rule'):
        assertions = rule.findall(S + 'assert')
        if any('inconsistent datatype between' in text(n) or 'use of var_ref is prohibited' in text(n).lower() for n in assertions):
            global_rules.append({'line': rule.sourceline, 'context': rule.get('context'),
                'lets': [dict(n.attrib) for n in rule.findall(S + 'let')],
                'assertions': [{'test': n.get('test'), 'message': text(n)} for n in assertions]})
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name,
            'sha256': sha256(raw).hexdigest(), 'function_group_line': group.sourceline,
            'common_documentation': [text(n) for n in group.findall('./' + X + 'annotation/' + X + 'documentation')],
            'enumerations': enumerations, 'global_variable_schematron': global_rules, 'functions': result}


def source_usage(directory, pin_path, contracts, schema_root):
    pin = json.loads(pin_path.read_text())
    ensure(file_inventory(directory) == pin['files'], 'pinned original collection mismatch')
    names = set(contracts['functions'])
    usage = defaultdict(list)
    validator = SourceValidator(schema_root)
    for path, raw in xml_documents(directory):
        root = ET.fromstring(raw)
        if root.tag != OVAL_ROOT:
            continue
        source = OvalDocument(root, path)
        nodes = {i: n for (_, i), n in SourceInventory(source).nodes.items()}
        definitions = root.find(O + 'tests')
        if definitions is None:
            continue
        report = None
        for test in definitions:
            ident = test.get('id')
            ids, problems = closure(nodes, ident)
            functions = {}
            for node_id in ids:
                if nodes[node_id]['kind'] != 'variable':
                    continue
                variable = source.nodes[path][node_id]
                for child in variable.iter():
                    if child.tag.startswith(O) and child.tag[len(O):] in names:
                        functions.setdefault(child.tag[len(O):], (variable, child))
            if not functions:
                continue
            if report is None:
                report = validator.validate(etree.fromstring(raw))
            validity = closure_validity([nodes[i] for i in ids], {path: report})
            if problems:
                validity = {'status': 'INVALID', 'issues': [{'kind': 'invalid', 'message': p} for p in problems]}
            for name, (variable, call) in sorted(functions.items()):
                usage[name].append({'document': path, 'sha256': sha256(raw).hexdigest(), 'test': ident,
                    'variable': variable.get('id'), 'datatype': variable.get('datatype'),
                    'source_validity': validity, 'function_excerpt': ET.tostring(call, encoding='unicode'),
                    'variable_excerpt': ET.tostring(variable, encoding='unicode')})
    summary = {}
    for name in sorted(names):
        cases = usage[name]
        valid = [c for c in cases if c['source_validity']['status'] == 'VALID' and
                 not any(i['kind'] == 'deprecated' for i in c['source_validity'].get('issues', []))]
        summary[name] = {'transitive_test_uses': len(cases), 'source_valid_nondeprecated_uses': len(valid),
                         'case_identities': [{k: c[k] for k in ('document', 'test', 'variable')} for c in cases],
                         'example': valid[0] if valid else None}
    return {'source_pin': {k: v for k, v in pin.items() if k != 'files'}, 'summary': summary}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema-root', type=Path, default=ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
    parser.add_argument('--source-root', type=Path)
    parser.add_argument('--pin', type=Path, default=PIN)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output exists; refusing overwrite')
    contracts = schema_contracts(args.schema_root)
    result = {'format': 'scap-ng/oval-function-contract-inventory/1', 'authority': 'Engineering evidence only; no proposed syntax is implemented.',
              'schema': contracts}
    if args.source_root:
        result['source_usage'] = source_usage(args.source_root, args.pin, contracts, args.schema_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'functions': len(contracts['functions']), 'remaining_functions': sorted(set(contracts['functions']) - CURRENT_VISITOR_FUNCTIONS)}))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(str(error))
