#!/usr/bin/env python3
"""Source-backed inventory of the 15 Variable-capable acquisition parameters.

No acquisition is executed, expanded or admitted. Read pinned original XML in
place and include original Object IDs/Variable edges, separately from XSD-legal
constructs absent from that corpus. Record members retain their own semantics.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from audit_v04_oval_test_corpus import PIN, file_inventory, xml_documents

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('independent.shellcommand', 'independent.sql', 'windows.cmdlet', 'windows.wmi.query')
X = '{http://www.w3.org/2001/XMLSchema}'
O = '{http://oval.mitre.org/XMLSchema/oval-definitions-5}'


def audit(source_root):
    pin = json.loads(PIN.read_text())
    if file_inventory(source_root) != pin['files']:
        raise ValueError('original corpus inventory differs from pinned source')
    families, parameters = {}, []
    for capability in FAMILIES:
        mapping = json.loads((ROOT / 'schema/v0.4.0/capability-mappings/supported' / (capability + '.json')).read_text())
        schema_path = ROOT / mapping['source']['definitions_schema']
        schema = ET.parse(schema_path)
        declaration = schema.find(X + 'element[@name="' + mapping['source']['object'] + '"]')
        entities = {e.get('name'): e for e in declaration.findall('.//' + X + 'element')}
        routes = mapping['native'].get('collection_parameter_source_map', {})
        rows = {}
        for target, contract in mapping['native']['collection_parameters'].items():
            if not contract.get('allow_variable'):
                continue
            source, = [name for name in entities if routes.get(name, name) == target]
            entity = entities[source]
            row = {'capability': capability, 'source_field': source, 'native_parameter': target,
                   'original_object': mapping['source']['object'], 'original_entity_type': entity.get('type'),
                   'source_xsd': mapping['source']['definitions_schema'],
                   'source_xsd_sha256': sha256(schema_path.read_bytes()).hexdigest(),
                   'original_entity_documentation': ' '.join(''.join(entity.itertext()).split()),
                   'native_variable_reference_allowed': True, 'native_literal_array_allowed': False,
                   'original_occurrences': 0, 'original_variable_edges': [],
                   'conversion_boundary': 'Literal/singleton constant input or retained named runtime graph. Graph correspondence does not prove invocation multiplicity; no new array expansion.'}
            rows[source] = row
            parameters.append(row)
        families[capability] = (mapping, rows)
    for document, raw in xml_documents(source_root):
        root = ET.fromstring(raw)
        variables = {v.get('id'): v for v in root.findall(O + 'variables/*')}
        for mapping, rows in families.values():
            tag = '{' + mapping['source']['namespace'] + '}' + mapping['source']['object']
            for obj in root.findall(O + 'objects/' + tag):
                for child in obj:
                    field = child.tag.rsplit('}', 1)[-1]
                    if field not in rows:
                        continue
                    row = rows[field]
                    row['original_occurrences'] += 1
                    if child.get('var_ref'):
                        variable = variables.get(child.get('var_ref'))
                        row['original_variable_edges'].append({
                            'document': document, 'document_sha256': sha256(raw).hexdigest(),
                            'object': obj.get('id'), 'variable': child.get('var_ref'),
                            'var_check': child.get('var_check', 'all'),
                            'variable_kind': None if variable is None else variable.tag.rsplit('}', 1)[-1],
                            'variable_expression': None if variable is None else ET.tostring(variable, encoding='unicode')})
    if len(parameters) != 15:
        raise ValueError('approved acquisition audit is no longer exactly 15 parameters')
    return {'format': 'scap-ng/converter-acquisition-review/1',
            'source_revision': pin['revision'] if 'revision' in pin else pin.get('commit'),
            'source_pin': {k: v for k, v in pin.items() if k != 'files'},
            'parameters': parameters,
            'parameters_by_family': dict(Counter(p['capability'] for p in parameters)),
            'record_boundary': 'Whole-record var_ref prohibited by original EntityObjectRecordType; individual EntityObjectFieldType references retain value_match and selection_match.',
            'conclusion': 'The pinned collection has no original multivalue command/query input example. Its two parameter Variable edges are closed single-value literal expressions. This is not evidence for arbitrary array expansion. SQL512 has no original Test in this collection; do not claim implemented/proved support.',
            'grouped_design_obligations': [
                'Separate identity selection (e.g. SQL instances/databases) from invocation inputs (commands/queries); preserve original operation and var_check at their own boundary.',
                'For any proposed multivalue acquisition, specify source-backed zero/one/many cardinality, independent versus correlated inputs, Item identities, order, duplicate behavior, and error/incomplete propagation.',
                'Do not turn collector inputs into ordinary selector predicates or permit whole-record Variables. Reuse existing record-field proofs.',
            ],
            'scope': 'Inventory/design obligations only. No scanner execution, fan-out equivalence or new schema proposal is accepted by this report.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.source_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result['parameters_by_family'], sort_keys=True))
