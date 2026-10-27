#!/usr/bin/env python3
"""Complete original six-STIG requirements; diagnostic inventory, not admission.

    python tools/inventory_v04_six_source_requirements.py --inputs DIR --output DIR

Broken published bindings stay broken. Unique matching Definitions are recorded
as candidate evidence only, never inserted into the converter's catalog.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import time
import zipfile

from lxml import etree as E

from oval_source_validation import SourceValidator
from v04_direct_converter import AssessmentConverter, load_mappings
from v04_direct_inventory import SourceInventory
from v04_direct_platform_inventory import platform_inventory
from v04_direct_scap_source import SourceModel, OVAL, UnsupportedSource, digest

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'tests/fixtures/v04-direct-six-sources.json'
FAMILIES = frozenset(OVAL + '#' + name for name in ('independent', 'linux', 'unix', 'windows'))
DS = '{http://scap.nist.gov/schema/scap/source/1.2}'


def scope_mappings():
    directory = ROOT / 'schema/v0.4.0/capability-mappings/supported'
    mappings = [json.loads(p.read_text()) for p in sorted(directory.glob('*.json'))]
    return [m for m in mappings if m['source']['namespace'] in FAMILIES]


def candidate_closures(source, inventory, checks):
    candidates, seen = [], set()
    for check in checks:
        if check['system'] != OVAL:
            continue
        for reference in check['references']:
            if reference['component'] is not None:
                continue
            for component, index in source.nodes.items():
                node = index.get(reference['name'])
                if node is None or node.tag != '{' + OVAL + '}definition':
                    continue
                identity = reference['href'], reference['name'], component
                if identity in seen:
                    continue
                seen.add(identity)
                nodes, problems = inventory.closure(component, reference['name'])
                candidates.append({'unresolved_href': reference['href'], 'definition': reference['name'],
                    'candidate_component': component, 'dependencies': nodes, 'problems': problems,
                    'binding_resolved': False})
    return candidates


def closure_validity(nodes, component_checks):
    selected = defaultdict(set)
    for node in nodes:
        selected[node['component']].add(node['id'])
    issues = []
    for component, identifiers in selected.items():
        for issue in component_checks[component]['issues']:
            if issue['source_id'] is None or issue['source_id'] in identifiers:
                issues.append({'component': component, **issue})
    return {'status': 'INVALID' if any(i['kind'] == 'invalid' for i in issues) else 'VALID',
            'issues': issues}


def probe_node(source, component, identifier, kind, mappings):
    try:
        AssessmentConverter(source, component, mappings).reference(identifier, kind)
        return []
    except (UnsupportedSource, ValueError) as error:
        return [str(error)]


def matrix(source, inventory, component_checks, configured, mapped, platforms):
    rows, cache = inventory.rules(), {}
    for row in rows:
        oval_checks = [c for c in row['checks'] if c['system'] == OVAL]
        row['source_method'] = 'OVAL-bearing' if oval_checks else 'manual/OCIL-only'
        candidates = candidate_closures(source, inventory, row['checks'])
        row['candidate_bindings'] = candidates
        nodes = {(n['component'], n['id']): n for n in row['dependencies']}
        for candidate in candidates:
            nodes.update({(n['component'], n['id']): n for n in candidate['dependencies']})
        row['binding_status'] = ('INVALID' if any(ref['component'] is None for c in oval_checks
                                for ref in c['references']) else 'RESOLVED')
        row['oval_closure_validity'] = closure_validity(nodes.values(), component_checks)
        row['applicability'] = []
        for context in row['unconverted_policy_context']['platforms']:
            identity = context['idref']
            record = platforms.get(identity)
            row['applicability'].append({'origin': context['origin'], 'identity': identity,
                'record_sha256': record['sha256'] if record else None,
                'required_capabilities': record['required_capabilities'] if record else [],
                'problems': (record['problems'] + [p for c in record['checks'] for p in c['problems']])
                            if record else ['unresolved original applicability reference']})
        row['required_capabilities'] = sorted({n['capability'] for n in nodes.values() if n['capability']})
        row['missing_enabled_capabilities'] = sorted(set(row['required_capabilities']) -
                                                     {m['capability'] for m in configured})
        row['configured_diagnostics'], row['mapped_diagnostics'] = [], []
        for key, node in sorted(nodes.items()):
            for label, mappings in (('configured', configured), ('mapped', mapped)):
                cache_key = label, key
                if cache_key not in cache:
                    cache[cache_key] = probe_node(source, key[0], key[1], node['kind'], mappings)
                for message in cache[cache_key]:
                    row[label + '_diagnostics'].append({'component': key[0], 'source_id': key[1],
                                                       'kind': node['kind'], 'message': message})
        # References to candidates are visibly distinct from authoritative edges.
        row['candidate_dependencies'] = [list(k) for k in sorted(nodes) if k not in
                                        {(n['component'], n['id']) for n in row['dependencies']}]
        row['dependencies'] = [[n['component'], n['id']] for n in row['dependencies']]
        for candidate in candidates:
            candidate['dependencies'] = [[n['component'], n['id']] for n in candidate['dependencies']]
    return rows


def summary(rows):
    automated = [r for r in rows if r['source_method'] == 'OVAL-bearing']
    counts = {'original_rules': len(rows), 'oval_bearing_rules': len(automated),
              'manual_ocil_only_rules': len(rows) - len(automated),
              'invalid_oval_binding_rules': sum(r['binding_status'] == 'INVALID' for r in automated),
              'invalid_oval_closure_rules': sum(r['oval_closure_validity']['status'] == 'INVALID' for r in automated),
              'unique_tests_including_candidate_closures': 0}
    counts['required_capabilities'] = dict(sorted(Counter(c for r in automated for c in r['required_capabilities']).items()))
    counts['configured_diagnostic_rules'] = dict(sorted(Counter(message for r in automated for message in
                                             {e['message'] for e in r['configured_diagnostics']}).items()))
    counts['mapped_diagnostic_rules'] = dict(sorted(Counter(message for r in automated for message in
                                         {e['message'] for e in r['mapped_diagnostics']}).items()))
    counts['missing_capabilities'] = {}
    for capability in sorted({c for r in automated for c in r['missing_enabled_capabilities']}):
        needed = [r for r in automated if capability in r['missing_enabled_capabilities']]
        counts['missing_capabilities'][capability] = {
            'rules_requiring': len(needed),
            'only_missing_capability': sum(r['missing_enabled_capabilities'] == [capability] for r in needed),
            'only_missing_capability_source_valid_and_bound': sum(
                r['missing_enabled_capabilities'] == [capability] and r['binding_status'] == 'RESOLVED'
                and r['oval_closure_validity']['status'] == 'VALID' for r in needed),
            'unlock_is_not_guaranteed': 'Other unsupported constructs and independent proof can still block these Rules.'}
    return counts


def run(inputs, output):
    lock = json.loads(LOCK.read_text())
    configured, mapped = load_mappings(), scope_mappings()
    validation = SourceValidator(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3')
    output.mkdir(parents=True, exist_ok=True)
    result = {'format': 'scap-ng/direct-six-source-requirements/1',
              'source_pin': {k: lock[k] for k in ('repository', 'revision')},
              'scope': 'Independent/Linux/UNIX/Windows original OVAL; no conversion admission',
              'configured_capabilities': [m['capability'] for m in configured],
              'diagnostic_mapping_capabilities': [m['capability'] for m in mapped], 'sources': {}}
    for name, pin in lock['sources'].items():
        started = time.perf_counter()
        path = inputs / pin['file']
        source = SourceModel(path, pin['sha256'], inventory_broken_references=True)
        inventory = SourceInventory(source)
        with zipfile.ZipFile(path) as archive:
            independent = E.fromstring(archive.read(source.member), E.XMLParser(resolve_entities=False, no_network=True))
        checks = {component.get('id'): validation.validate(component[0])
                  for component in independent.findall(DS + 'component')
                  if component[0].tag == '{' + OVAL + '}oval_definitions'}
        platforms = platform_inventory(source, inventory)
        rows = matrix(source, inventory, checks, configured, mapped, platforms)
        nodes = {component: {} for component in source.components if source.components[component].tag == '{' + OVAL + '}oval_definitions'}
        for (component, identifier), node in inventory.nodes.items():
            original = source.nodes[component][identifier]
            nodes[component][identifier] = {**node, 'attributes': dict(original.attrib),
                'entity_attributes': [{'tag': child.tag, 'attributes': dict(child.attrib)}
                                      for child in original.iter() if child is not original and child.attrib]}
        own_summary = summary(rows)
        own_summary['declared_tests_all_components'] = sum(n['kind'] == 'test' for n in inventory.nodes.values())
        own_summary['declared_definitions_all_components'] = sum(n['kind'] == 'definition' for n in inventory.nodes.values())
        own_summary['applicability_capabilities_by_rule'] = dict(sorted(Counter(
            capability for row in rows if row['source_method'] == 'OVAL-bearing'
            for capability in {c for platform in row['applicability'] for c in platform['required_capabilities']}).items()))
        referenced = {tuple(k) for r in rows for k in r['dependencies'] + r['candidate_dependencies']}
        own_summary['unique_tests_including_candidate_closures'] = sum(inventory.nodes[k]['kind'] == 'test' for k in referenced)
        packet = {'source': pin, 'xml_sha256': source.xml_sha256, 'member': source.member,
                  'catalog_errors': source.catalog_errors, 'component_source_validation': checks,
                  'nodes': nodes, 'rules': rows, 'applicability': platforms, 'summary': own_summary,
                  'candidate_binding_policy': 'Evidence only, never executable resolution or a repaired source.',
                  'elapsed_seconds': time.perf_counter() - started}
        (output / (name + '.json')).write_text(json.dumps(packet, indent=2, sort_keys=True) + '\n')
        result['sources'][name] = {'source': pin, 'summary': own_summary,
                                 'catalog_errors': source.catalog_errors, 'elapsed_seconds': packet['elapsed_seconds'],
                                 'packet_sha256': digest(packet)}
        print(name, json.dumps({k: v for k, v in own_summary.items() if not isinstance(v, dict)}), flush=True)
    (output / 'matrix.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    run(args.inputs, args.output)
