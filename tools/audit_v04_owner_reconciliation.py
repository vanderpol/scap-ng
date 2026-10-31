#!/usr/bin/env python3
"""Read-only Decisions 1–28 drift/default inventory; no corpus conversion (#255/#268)."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
from scap_ng_library.documents import parse

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
XS = '{http://www.w3.org/2001/XMLSchema}'
OD = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'
SOURCE = 'third_party/scap-1.4-schemas/oval_5.12.3'
MAPPINGS = 'schema/v0.4.0/capability-mappings/supported'


def walk(value, pointer=''):
    yield pointer, value
    if isinstance(value, dict):
        for key, child in value.items():
            escaped = str(key).replace('~', '~0').replace('/', '~1')
            yield from walk(child, pointer + '/' + escaped)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, pointer + '/' + str(index))


def slug_capability(name):
    from v04_native_capability_names import canonical_capability
    return canonical_capability(name)


class SourceDefaults:
    """QName dependency census, preserving exact declarations, not filling XML.

    A reachable declaration is evidence to review, not a statement that every
    occurrence inherits it. Restriction/extension and omitted source behavior
    remain explicit in the declaration/context fields. No XSD default becomes
    an NG editor default through this traversal.
    """
    def __init__(self, root):
        self.root = root
        self.documents, self.symbols, self.defaults = {}, {}, {}
        for path in sorted((root / SOURCE).glob('*.xsd')):
            tree = E.parse(str(path), E.XMLParser(resolve_entities=False, no_network=True))
            schema = tree.getroot()
            relative = path.relative_to(root).as_posix()
            self.documents[relative] = tree
            namespace = schema.get('targetNamespace', '')
            for child in schema:
                if isinstance(child.tag, str) and child.get('name'):
                    self.symbols[(E.QName(child).localname, '{' + namespace + '}' + child.get('name'))] = child
            for node in schema.iter():
                if node.tag not in (XS + 'attribute', XS + 'element') or node.get('default') is None:
                    continue
                key = relative + ':' + str(node.sourceline)
                parents = [p.get('name') for p in node.iterancestors() if p.get('name')]
                self.defaults[key] = {'source_path': relative, 'source_line': node.sourceline,
                    'source_xpath': tree.getpath(node), 'attribute': node.get('name'),
                    'declaration_kind': E.QName(node).localname,
                    'source_type': node.get('type'), 'source_default': node.get('default'),
                    'declaration_context': parents, 'source_sha256': sha256(path.read_bytes()).hexdigest(),
                    'reachability_limit': 'QName dependency census; occurrence-specific overrides require review'}

    def reachable(self, mapping):
        source = mapping['source']
        pending = [self.symbols.get(('element', '{' + source['namespace'] + '}' + source[role]))
                   for role in ('test', 'object', 'state') if source.get(role)]
        seen, defaults = set(), set()
        while pending:
            node = pending.pop()
            if node is None or node in seen:
                continue
            seen.add(node)
            for child in node.iter():
                if not isinstance(child.tag, str):
                    continue
                if child.tag in (XS + 'attribute', XS + 'element') and child.get('default') is not None:
                    path = Path(child.base).resolve().relative_to(self.root.resolve()).as_posix()
                    defaults.add(path + ':' + str(child.sourceline))
                for attribute, kinds in [('type', ('complexType', 'simpleType')),
                                         ('base', ('complexType', 'simpleType')),
                                         ('ref', (E.QName(child).localname,))]:
                    value = child.get(attribute)
                    if value is None:
                        continue
                    prefix, name = value.split(':', 1) if ':' in value else (None, value)
                    namespace = child.nsmap.get(prefix, '')
                    qualified = '{' + namespace + '}' + name
                    pending.extend(self.symbols.get((kind, qualified)) for kind in kinds)
        return sorted(defaults)


def control(attribute, contexts):
    test = 'TestType' in contexts
    if attribute == 'check_existence':
        return ('require.items_found' if test else 'require.field_requirement.values_found',
                'one_or_more', 'Serialize source-effective cardinality; preserve field/Item distinction', [1, 2, 3, 9])
    return {
        'entity_check': ('require.field_requirement.values_matching', 'every', 'Serialize the complete field pair and local exceptions', [2, 3]),
        'operation': ('object.<selector>.<operation> / require.fields.<field>.<operation>', 'equals', 'Operation is an explicit YAML key; source nondefaults retained', [4, 7, 22]),
        'datatype': ('capability predicate / Variable / Input type', 'deterministic inference', 'Not a universal NG string default; conflicts fail', [4]),
        'state_operator': ('require.and/or/one/xor', 'and', 'Serialize the actual source logical boundary; no Boolean flattening', [2, 7]),
        'operator': ('require.and/or/one/xor', 'and', 'Preserve State versus whole-Test scope', [2, 7]),
        'set_operator': ('object.set.operator', 'union', 'Only if a Set exists; never synthesize one for a default', [7]),
        'action': ('object.filters[].include/exclude', 'exclude', 'Preserve source filter position and error semantics', [7]),
        'recurse_file_system': ('object.filesystem', 'local', 'OVAL omitted all -> explicit all; defined -> same; editor local is distinct', [7, 28]),
        'recurse_direction': ('object.traversal (presence)', 'no traversal when disabled', 'No invented recurse:none; scope and depth remain separate', [7, 27, 28]),
        'recurse': ('object.traversal.recurse', 'capability-specific, only when enabled', 'Windows directories; Unix/independent symlinks_and_directories; explicit junctions preserved', [7, 27]),
        'max_depth': ('object.traversal.max_depth', 'unlimited when unbounded', 'OVAL -1 -> unlimited; bounded nonnegative integer retained', [27]),
        'error_if_exit_status_not_0': ('object.error_if_exit_status_not_0', 'PENDING_OWNER_DEFAULT_REVIEW', 'Source omitted false stays false; new authoring policy not inferred', [7]),
        'error_if_stderr_exists': ('object.error_if_stderr_exists', 'PENDING_OWNER_DEFAULT_REVIEW', 'Source omitted false stays false; new authoring policy not inferred', [7]),
    }.get(attribute, ('UNMAPPED_SOURCE_DEFAULT', 'NOT_PROPOSED', 'Audit source applicability and explicit native representation before default activation', []))


def document_drift(root):
    """Inspect native documents only; pinned fixture drift is historical evidence."""
    findings, documents = [], Counter()
    for folder, scope in [('docs/examples', 'CURRENT_EXAMPLE'), ('tests/fixtures', 'FIXTURE_REQUIRES_HISTORY_CLASSIFICATION')]:
        for path in sorted((root / folder).rglob('*')):
            if path.suffix not in ('.json', '.yaml', '.yml') or not path.is_file() or path.stat().st_size > 5_000_000:
                continue
            try:
                doc = json.loads(path.read_text()) if path.suffix == '.json' else parse(path.read_bytes())
            except (ValueError, UnicodeError, KeyError, TypeError):
                continue
            if not isinstance(doc, dict) or not isinstance(doc.get('assessment'), dict):
                continue
            assessment = doc['assessment']
            documents[scope] += 1
            relative = path.relative_to(root).as_posix()
            def add(pointer, old, expected, decisions):
                findings.append({'path': relative, 'pointer': pointer, 'obsolete_field': old,
                    'expected_shape': expected, 'impact': scope, 'owner_decision': decisions,
                    'status': 'OPEN' if scope == 'CURRENT_EXAMPLE' else 'PRESERVE_PINNED_OR_EXPLICITLY_MIGRATE_NEW_COPY',
                    'rule': next(iter(re.findall(r'SV-\d+', path.as_posix())), None)})
            if 'purpose' in assessment:
                add('/assessment/purpose', 'purpose', 'invocation context at consumer', [6])
            if 'states' in assessment:
                add('/assessment/states', 'states', 'canonical Test require condition', [2, 3])
            for pointer, node in walk(assessment, '/assessment'):
                if isinstance(node, dict) and isinstance(node.get('capability'), str) and slug_capability(node['capability']) != node['capability']:
                    add(pointer + '/capability', node['capability'], slug_capability(node['capability']), [5])
                if isinstance(node, str) and node == 'may_be_absent':
                    add(pointer, node, 'zero_or_more', [1])
            tests = assessment.get('tests') or {}
            if not isinstance(tests, dict):
                add('/assessment/tests', 'legacy Tests collection shape', 'mapping keyed by native Test ID', [2, 10])
                tests = {}
            for ident, test in tests.items():
                if not isinstance(test, dict):
                    continue
                pointer = '/assessment/tests/' + ident
                requirement = test.get('require', {})
                if isinstance(requirement, dict) and set(requirement) != {'items_found'}:
                    pair = requirement.get('field_requirement')
                    if not isinstance(pair, dict) or set(pair) != {'values_found', 'values_matching'}:
                        add(pointer + '/require/field_requirement', 'missing complete Test field_requirement',
                            'explicit values_found +values_matching pair; preserve field exceptions', [2, 3])
                if 'reported_elements' not in test:
                    add(pointer + '/reported_elements', 'missing reported_elements', 'explicit all or reviewed selection', [14])
                for key in ('state', 'states', 'states_match', 'collected_items_require'):
                    if key in test:
                        add(pointer + '/' + key, key, 'canonical require grammar', [2, 3])
            identifiers = [('/assessment/id', assessment.get('id'))]
            for section in ('tests', 'shared_objects', 'variables', 'inputs', 'dependencies'):
                identifiers.extend(('/assessment/' + section + '/' + ident, ident) for ident in (assessment.get(section) or {}))
            for pointer, ident in identifiers:
                if isinstance(ident, str) and (len(ident) > 64 or re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', ident) is None):
                    add(pointer, 'native ID constraint', 'meaningful lower-case slug <=64 chars; original IDs stay external', [10])
    return findings, dict(documents)


def audit(root=ROOT):
    from generate_capability_schema_v04 import generate
    mappings = [json.loads(p.read_text()) for p in sorted((root / MAPPINGS).glob('*.json'))]
    if len(mappings) != 100:
        raise ValueError('exactly 100 version-local supported capability contracts required')
    source = SourceDefaults(root)
    parity = json.loads((root / 'tests/fixtures/v04-native-generator-parity.json').read_text())['full_schema_sha256']
    consumers = defaultdict(list)
    capabilities, drift = [], []
    for mapping in mappings:
        cap = mapping['capability']
        reachable = source.reachable(mapping)
        for key in reachable:
            consumers[key].append(cap)
        capabilities.append({'capability': cap, 'mapping': MAPPINGS + '/' + cap + '.json',
            'source': mapping['source'], 'source_default_declarations': reachable,
            'selector_case_semantics': mapping['native'].get('selector_case_semantics', {}),
            'native_expected_name': slug_capability(cap)})
        schema = generate(mapping, root)
        generated_sha = sha256(json.dumps(schema, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        capabilities[-1]['generated_schema_sha256'] = generated_sha
        capabilities[-1]['reviewed_generator_lock_matches'] = parity.get(cap) == generated_sha
        if parity.get(cap) != generated_sha:
            drift.append({'path': 'tests/fixtures/v04-native-generator-parity.json',
                'pointer': '/full_schema_sha256/' + cap, 'obsolete_field': 'generated contract fingerprint',
                'expected_shape': 'Review complete generated-contract delta before accepting a new fingerprint',
                'impact': cap, 'owner_decision': [1, 3, 4, 5, 7, 22, 23, 27, 28], 'status': 'REVIEW_REQUIRED_NO_REBASELINE'})
        if slug_capability(cap) != cap:
            drift.append({'path': MAPPINGS + '/' + cap + '.json', 'pointer': '/capability',
                'obsolete_field': cap, 'expected_shape': slug_capability(cap), 'impact': 'native name migration; source QNames unchanged',
                'owner_decision': [5], 'status': 'OPEN'})
    annotations = []
    for path in sorted((root / 'schema/v0.4.0').glob('*.schema.json')):
        for pointer, node in walk(json.loads(path.read_text())):
            if isinstance(node, dict) and 'default' in node and node.get('x-scap-ng-authoring', {}).get('hide_when_default'):
                annotations.append({'ng_schema_path': path.relative_to(root).as_posix() + '#' + pointer,
                    'default': node['default'], 'annotation': node['x-scap-ng-authoring'],
                    'type': node.get('type'), 'enum': node.get('enum'), 'reference': node.get('$ref'),
                    'control_count': 1, 'scalar_members': len(node['default']) if isinstance(node['default'], dict) else 1,
                    'serialization': 'Required applicable source value must be present; annotation never inserts it',
                    'owner_decision': [7, 28] if 'filesystem_scope' in pointer else [7]})
    catalog = []
    for key, row in source.defaults.items():
        path, suggestion, serialization, decisions = control(row['attribute'], row['declaration_context'])
        catalog.append({**row, 'applicable_capabilities': sorted(consumers[key]), 'ng_control': path,
            'source_default_origin': 'XSD_' + row['declaration_kind'].upper() + '_DECLARATION',
            'omitted_source_behavior': ('Default applies only to an existing empty element, not an absent optional element'
                if row['declaration_kind'] == 'element' else 'Apply this attribute use only after resolving occurrence-specific restrictions/overrides'),
            'ng_editor_suggestion': suggestion, 'serialization_rule': serialization,
            'hideable': 'ONLY_IF_EXISTING_ANNOTATION_APPLIES' if row['attribute'] in ('check_existence', 'entity_check', 'recurse_file_system') else 'NOT_APPROVED_AS_ADDITIONAL_HIDDEN_DEFAULT',
            'owner_decision': decisions, 'status': 'REACHABLE_SOURCE_DECLARATION' if consumers[key] else 'OUTSIDE_SUPPORTED_SOURCE_CLOSURE',
            'source_equivalence': 'CONDITIONAL_NOT_PROVED_BY_DEFAULT_DECLARATION'})
    current_paths = [root / 'tools/v04_direct_converter.py', root / 'tools/v04_field_requirement.py',
                     root / 'tools/v04_canonical_result_plan.py', root / 'tools/v04_native_bundle_compiler.py']
    for path in current_paths:
        for number, line in enumerate(path.read_text().splitlines(), 1):
            for token, expected, decisions in [('may_be_absent', 'zero_or_more', [1]),
                    ("'purpose': 'assessment'", 'purpose at invocation only', [6]),
                    ('conditional result semantics require separate six-state acceptance', 'approved ordered conditional compilation', [8, 24, 25, 26])]:
                if token in line:
                    drift.append({'path': path.relative_to(root).as_posix(), 'line': number,
                        'obsolete_field': token, 'expected_shape': expected, 'impact': 'current producer/compiler compatibility',
                        'owner_decision': decisions, 'status': 'PRODUCER_TOKEN_REQUIRES_SOURCE_VS_NATIVE_ROLE_REVIEW'})
    native_drift, document_counts = document_drift(root)
    drift.extend(native_drift)
    return {'format': 'scap-ng/owner-contract-reconciliation/1', 'capability_count': len(mappings),
        'capabilities': capabilities, 'drift': drift, 'drift_summary': dict(Counter(x['obsolete_field'] for x in drift)),
        'document_counts': document_counts,
        'annotated_hideable_controls': annotations, 'annotated_control_count': len(annotations),
        'source_default_declarations': catalog,
        'source_defaults_summary': {'all_xsd_raw_declarations': len(catalog),
            'definitions_xsd_raw_declarations': sum(r['source_path'].endswith('definitions-schema.xsd') for r in catalog),
            'definitions_attribute_defaults': sum(r['source_path'].endswith('definitions-schema.xsd') and r['declaration_kind'] == 'attribute' for r in catalog),
            'definitions_element_defaults': sum(r['source_path'].endswith('definitions-schema.xsd') and r['declaration_kind'] == 'element' for r in catalog),
            'reachable_declarations': sum(bool(c['applicable_capabilities']) for c in catalog)},
        'limitations': ['Read-only QName dependency audit, not complete occurrence-level XSD PSVI evaluation',
            'Reachable default may be narrowed/overridden; declaration context and exact XPath/line retained',
            'No editor default annotations or native/schema changes performed by this audit',
            'No conversion, corpus regeneration, proof/status/hash rebaseline, result-oracle correction or scanner claim']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.root)
    with args.output.open('x') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    print(json.dumps({key: report[key] for key in ('capability_count', 'drift_summary', 'annotated_control_count', 'source_defaults_summary')}))
