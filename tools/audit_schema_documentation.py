#!/usr/bin/env python3
"""Phase-1 core/shared documentation inventory and annotation-only proposals.

One generic audit/renderer; no canonical files are written. Existing gaps are
explicitly baselined; new/regressed gaps fail --check. Quality rules are triage,
not a claim that every populated description has passed semantic review.
"""
import argparse
from contextlib import contextmanager
from collections import Counter, defaultdict, deque
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

import yaml
from urllib.parse import urljoin, urldefrag

from jsonschema import Draft202012Validator
from schema_documentation import SchemaStore, pointer, types, parts, property_occurrences, collection_occurrences

ROOT = Path(__file__).resolve().parents[1]
# The old Issue #40 workbook is an immutable historical receipt.  The active
# command profile below audits only the current 0.4.1 schema family.
HISTORICAL_DEST = Path('docs/research/issue40')
HISTORICAL_NATIVE_COMMIT = '63110e7762f4963d3e4d407e90b9fcfd9cfe86ad'
HISTORICAL_PILOT_COMMIT = 'f61fff037f18832aa04db140b3e3209dfddf7219'
HISTORICAL_PREFIX = 'https://scap-ng.dev/schema/v0.4.0/'
ACTIVE_DEST = Path('docs/metadata/documentation-0.4.1')
ACTIVE_NATIVE_COMMIT = '0683bbf6fdcbba65c5ffb79f2bf8d41d920e43d9'
ACTIVE_PILOT_COMMIT = HISTORICAL_PILOT_COMMIT
ACTIVE_PREFIX = 'https://scap-ng.dev/schema/v0.4.1/'
DEST = HISTORICAL_DEST
NATIVE_COMMIT = HISTORICAL_NATIVE_COMMIT
PILOT_COMMIT = HISTORICAL_PILOT_COMMIT
ISSUE = 'https://github.com/scap-ng/issues/40'
PREFIX = HISTORICAL_PREFIX
MAPS = {'properties', 'patternProperties', '$defs', 'definitions', 'dependentSchemas'}
ARRAYS = {'allOf', 'oneOf', 'anyOf', 'prefixItems'}
SINGLES = {'items', 'additionalProperties', 'unevaluatedProperties', 'propertyNames', 'if', 'then', 'else', 'not', 'contains', 'unevaluatedItems', 'additionalItems', 'contentSchema'}
CATEGORIES = {'missing_description', 'vague_description', 'missing_example', 'missing_constraint_meaning', 'contradictory_description', 'missing_editor_help_binding', 'missing_scanner_error_semantics', 'unspecified_schema_contract'}
SEVERITIES = {'high': 0, 'medium': 1, 'low': 2}
GROUPS = {'editorial_only', 'clarification_no_validation_change', 'normative_contract_decision_required'}
STATUSES = {'open', 'proposed', 'reviewed', 'resolved', 'deferred'}


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def literal(value):
    return value if isinstance(value, str) else encode(value)


def digest(value):
    return sha256(encode(value).encode()).hexdigest()


def escape(value):
    return value.replace('~', '~0').replace('/', '~1')


def walk(node, path='', guarded=False, parent_description=None, role='document_root', name='root', value_owner=None):
    if not isinstance(node, (dict, bool)):
        return
    public = not guarded and not isinstance(node, bool) and role in {'document_root', 'shared_definition', 'field', 'map_entry'}
    if role == 'alternative' and isinstance(node, dict) and not (set(node) & {'type', 'properties', '$ref', 'enum', 'const', 'items', 'additionalProperties'}):
        public = False  # Pure guard/consistency branch, not an authorable value.
    owner = path if value_owner is None else value_owner
    yield path, node, role, name, public, parent_description, owner
    if not isinstance(node, dict):
        return
    same_description = (path, node['description']) if isinstance(node.get('description'), str) and node['description'].strip() else parent_description
    for keyword in sorted(MAPS):
        for key, value in sorted(node.get(keyword, {}).items()):
            child_role = 'shared_definition' if keyword in {'$defs', 'definitions'} else 'map_entry' if keyword == 'patternProperties' else 'field' if keyword == 'properties' else 'dependent_constraint'
            yield from walk(value, path + '/' + keyword + '/' + escape(key), guarded or keyword == 'dependentSchemas', None, child_role, key)
    for keyword in sorted(ARRAYS):
        for index, value in enumerate(node.get(keyword, [])):
            yield from walk(value, path + '/' + keyword + '/' + str(index), guarded, same_description, 'alternative', name, owner)
    for keyword in sorted(SINGLES):
        value = node.get(keyword)
        if isinstance(value, (dict, bool)):
            child_role = {'items': 'array_entry', 'additionalProperties': 'dynamic_map_value', 'propertyNames': 'dynamic_map_key'}.get(keyword, 'constraint')
            # Guards and overrides are accounted, but not independent public
            # authoring fields. A property literally named "if" is unaffected.
            yield from walk(value, path + '/' + keyword, guarded or keyword in {'if', 'then', 'else', 'not', 'contains', 'unevaluatedProperties'}, same_description if keyword not in {'items', 'additionalProperties'} else None, child_role, name, None if keyword in {'items', 'additionalProperties', 'propertyNames'} else owner)


def family(document):
    title = document.get('title', '').lower()
    properties = document.get('properties', {})
    if 'result' in title or 'evidence' in title or 'provenance' in title or 'materialization' in title:
        return 'results_evidence'
    if 'assessment' in properties or 'assessment' in title:
        return 'assessment_core'
    if 'expression' in title or 'variable' in title:
        return 'expressions_variables'
    if set(properties) & {'benchmark', 'rule', 'tailoring', 'applicability'} or any(x in title for x in ['benchmark', 'rule ', 'tailoring', 'applicability']):
        return 'policy_applicability'
    if any(x in title for x in ['manifest', 'package', 'bundle']):
        return 'packaging'
    return 'shared_language'


def instance_scope(uri, path):
    """Distinguish a schema guard from a property literally named if/then."""
    tokens = path.lstrip('/').split('/') if path else []
    scope, guard, conditional, index = [uri], False, False, 0
    while index < len(tokens):
        key = tokens[index]
        if key in {'$defs', 'definitions'}:
            scope = [uri, key, tokens[index + 1]]; index += 2
        elif key in {'properties', 'patternProperties'}:
            scope += [key, tokens[index + 1]]; index += 2
        elif key == 'dependentSchemas':
            conditional = True; index += 2
        elif key in {'allOf', 'oneOf', 'anyOf'}:
            index += 2
        elif key == 'prefixItems':
            scope += ['tuple', tokens[index + 1]]; index += 2
        else:
            if key in {'if', 'not', 'contains', 'propertyNames', 'unevaluatedProperties'}:
                guard = True
            if key in {'then', 'else'}:
                conditional = True
            if key in {'items', 'additionalProperties'}:
                scope.append(key)
            index += 1
    return tuple(scope), guard, conditional


def discover(root):
    parsed = {str(p.relative_to(root)): json.loads(p.read_text()) for p in sorted((root / 'schema').rglob('*.json'))}
    schemas = {name: doc for name, doc in parsed.items() if isinstance(doc, dict) and doc.get('$schema', '').startswith('https://json-schema.org/') and '$id' in doc}
    stems = {doc['capability'].replace('.', '_') for doc in parsed.values() if isinstance(doc, dict) and doc.get('format', '').startswith('scap-ng-capability-mapping') and isinstance(doc.get('capability'), str)}
    documents = {doc['$id']: doc for doc in schemas.values()}
    if len(documents) != len(schemas):
        raise ValueError('Duplicate schema identity')
    domains = {}
    for doc in schemas.values():
        for definition, body in doc.get('$defs', {}).items():
            for operation, constraint in body.get('dependentSchemas', {}).items():
                domain = constraint.get('properties', {}).get('datatype', {}).get('const')
                if domain is not None:
                    domains[operation] = {'datatype': domain, 'source': doc['$id'] + '#/$defs/' + definition + '/dependentSchemas/' + escape(operation)}
    nodes, excluded = {}, []
    for file, doc in schemas.items():
        inactive = 'inactive' in doc.get('title', '').lower() and 'not referenced by Assessment' in doc.get('description', '')
        for path, node, role, name, public, inherited, owner in walk(doc):
            capability_specific = False
            if doc.get('x-generated-from') and path.startswith('/$defs/'):
                definition = path.split('/')[2]
                capability_specific = any(definition.startswith(stem + '_') for stem in stems)
            if capability_specific:
                if path.count('/') == 2:
                    excluded.append({'file': file, 'pointer': path, 'reason': 'capability-specific generated definition; expansion not authorized'})
                continue
            key = doc['$id'] + '#' + path
            nodes[key] = {'schema_file': file, 'schema_uri': doc['$id'], 'pointer': path, 'role': role, 'element': name,
                          'public': public, 'family': family(doc), 'language_status': 'inactive_migration_candidate' if inactive else 'declared_core_shared',
                          'node': node, 'applicator_description': inherited, 'same_value_owner': owner, 'comparison_domain': domains.get(name)}
    public_scopes = {instance_scope(e['schema_uri'], e['pointer'])[0] for e in nodes.values() if e['public'] and e['role'] == 'field'}
    for entry in nodes.values():
        scope, guard, conditional = instance_scope(entry['schema_uri'], entry['pointer'])
        entry['instance_scope'] = list(scope)
        entry['assertion_context'] = guard
        if entry['role'] == 'field' and conditional and not guard and scope not in public_scopes:
            entry['public'] = True
            entry['role'] = 'conditional_field'
    manifest = [{'file': name, 'sha256': sha256((root / name).read_bytes()).hexdigest(),
                 'classification': 'schema' if name in schemas else 'capability_metadata' if 'capability' in doc else 'non_schema_metadata'} for name, doc in parsed.items()]
    return schemas, documents, nodes, excluded, manifest


def effective_description(key, nodes, store, seen=()):
    if key in seen:
        return None, None, 'reference_cycle'
    if key not in nodes:
        return None, None, 'out_of_scope_reference'
    entry = nodes[key]
    node = entry['node']
    if not isinstance(node, dict):
        return None, None, 'boolean_schema'
    if isinstance(node.get('description'), str) and node['description'].strip():
        return node['description'], key, 'own'
    if '$ref' in node:
        target = urljoin(entry['schema_uri'], node['$ref'])
        # Validate the pointer even when its annotation target is excluded.
        store.node(target)
        text, origin, binding = effective_description(target if '#' in target else target + '#', nodes, store, seen + (key,))
        if text:
            return text, origin, '$ref'
    if entry['applicator_description']:
        path, text = entry['applicator_description']
        return text, entry['schema_uri'] + '#' + path, 'same_instance_applicator'
    for index, part in enumerate(node.get('allOf', [])):
        target = key + '/allOf/' + str(index)
        text, origin, binding = effective_description(target, nodes, store, seen + (key,))
        if text:
            return text, origin, 'allOf'
    return None, None, 'unbound'


def weak(text, name):
    words = re.sub(r'[^a-z0-9]+', ' ', text.lower()).strip()
    title = re.sub(r'[^a-z0-9]+', ' ', name.lower()).strip()
    return words in {title, 'the ' + title, title + ' value', 'the ' + title + ' value', title + ' field', 'string', 'object', 'value'} or bool(re.fullmatch(r'(the )?[a-z0-9_-]+ (field|value|property)\.?', text.lower())) or len(words.split()) < 3


def canonical_missing_target(key, nodes, seen=()):
    if key in seen or key not in nodes:
        return key
    node = nodes[key]['node']
    if isinstance(node, dict) and '$ref' in node and not node.get('description'):
        target = urljoin(nodes[key]['schema_uri'], node['$ref'])
        target += '' if '#' in target else '#'
        if target in nodes and nodes[target]['public']:
            return canonical_missing_target(target, nodes, seen + (key,))
    owner = nodes[key].get('same_value_owner')
    parent_key = nodes[key]['schema_uri'] + '#' + owner if owner is not None else key
    if parent_key != key and parent_key in nodes and nodes[parent_key]['public']:
        return canonical_missing_target(parent_key, nodes, seen + (key,))
    return key


def structural_wording(entry):
    """Conservative proposals explain encoded structure, not guessed runtime rules."""
    node, label = entry['node'], entry['element']
    if not isinstance(node, dict):
        return ('This branch accepts every value.' if node else 'This branch accepts no value.'), 'clarification_no_validation_change', False
    if entry.get('comparison_domain'):
        domain = entry['comparison_domain']['datatype']
        return 'Expected operand for a self-describing `' + domain + '` comparison; any explicit datatype must agree with that comparison domain.', 'clarification_no_validation_change', False
    if 'enum' in node:
        return 'Choose one of ' + ', '.join('`' + literal(v) + '`' for v in node['enum']) + '.', 'clarification_no_validation_change', False
    if 'const' in node:
        return ('Within this conditional branch, this position accepts only ' if entry['role'] == 'conditional_field' else 'This position accepts only ') + '`' + literal(node['const']) + '`.', 'clarification_no_validation_change', False
    if node.get('type') == 'array':
        low, high = node.get('minItems', 0), node.get('maxItems')
        shape = str(low) + (' or more' if high is None else ' to ' + str(high))
        return 'Contains ' + shape + ' entries, each checked against the referenced or inline entry schema; ordering and runtime interpretation require review.', 'normative_contract_decision_required', True
    if 'oneOf' in node or 'anyOf' in node:
        key = 'oneOf' if 'oneOf' in node else 'anyOf'
        return 'The value must satisfy ' + ('exactly one' if key == 'oneOf' else 'at least one') + ' of the declared alternatives; their runtime interpretation requires review.', 'normative_contract_decision_required', True
    if node.get('type') == 'object' or 'properties' in node or 'additionalProperties' in node:
        required = node.get('required', [])
        sentence = 'When this object is present, ' + ', '.join('`' + str(v) + '`' for v in required) + ' must be supplied.' if required else 'No named property is unconditionally required by this object schema.'
        return sentence + ' Its semantic purpose requires owner review.', 'normative_contract_decision_required', True
    if node.get('pattern'):
        return 'The authored text must match `' + node['pattern'] + '`; meaning and reference-resolution obligations require review.', 'normative_contract_decision_required', True
    if node.get('$ref'):
        return 'Uses the shared definition referenced here; context-specific meaning requires review.', 'normative_contract_decision_required', True
    return 'Meaning is not yet documented here; permitted shape alone does not establish runtime behavior.', 'normative_contract_decision_required', True


def source_link(entry):
    return 'https://github.com/vanderpol/scap-ng/blob/' + NATIVE_COMMIT + '/' + entry['schema_file']


def _audit(root=ROOT):
    schemas, documents, nodes, excluded, manifest = discover(root)
    store = SchemaStore(documents)
    notes = json.loads((root / DEST / 'review-notes.json').read_text())
    findings, proposals, inventory = {}, {}, []
    operator_targets = {}
    for key, entry in sorted(nodes.items(), key=lambda kv: ('/$defs/field_predicate_body/properties/' not in kv[1]['pointer'], kv[0])):
        if entry['public'] and entry.get('comparison_domain'):
            operator_targets.setdefault(entry['element'], key)
    curated = {note['schema_uri'] + '#' + note['pointer']: note for note in notes['proposals']}
    def add(key, category, explanation, severity='medium', confidence='confirmed', correction=None, group=None, provisional=None, evidence=None):
        target = canonical_missing_target(key, nodes) if category == 'missing_description' else key
        if target not in nodes:
            return
        entry = nodes[target]
        identifier = 'gap-' + sha256((target + '|' + entry['role'] + '|' + category).encode()).hexdigest()[:16]
        if identifier not in findings:
            word, default_group, default_provisional = structural_wording(entry)
            note = curated.get(target)
            replacement = correction or (note['proposed_description'] if note else word)
            approval = group or (note['approval_category'] if note else default_group)
            is_provisional = provisional if provisional is not None else note.get('provisional', False) if note else default_provisional
            existing = entry['node'].get('description') if isinstance(entry['node'], dict) else None
            findings[identifier] = {'id': identifier, **{k: entry[k] for k in ['schema_file', 'schema_uri', 'pointer', 'role', 'element', 'family', 'language_status']},
                'inherited_shared_definition': target if target != key else None,
                'category': category, 'severity': severity, 'confidence': confidence, 'impact': explanation,
                'existing_description': existing, 'proposed_replacement': replacement, 'minimal_correction': 'Review the exact proposed annotation at this canonical pointer; do not copy it into every consumer.',
                'approval_category': approval, 'owner_decision_needed': approval == 'normative_contract_decision_required',
                'decision_link': ISSUE + '#issuecomment-6715925830' if approval == 'normative_contract_decision_required' else None,
                'provisional': is_provisional, 'evidence': evidence or (note.get('evidence') if note else None) or [{'kind': 'native_schema', 'uri': target, 'link': source_link(entry)}],
                'status': 'open', 'disposition': 'pending', 'resolution_pointer': None, 'affected_nodes': []}
        findings[identifier]['affected_nodes'].append(key)
        return identifier
    for key, entry in sorted(nodes.items()):
        node = entry['node']
        own = node.get('description') if isinstance(node, dict) else None
        effective, origin, binding = effective_description(key, nodes, store)
        quality = 'missing' if not effective else 'weak_candidate' if weak(effective, entry['element']) else 'present_not_semantically_reviewed'
        if key in curated and effective and curated[key].get('existing_review') == 'useful_with_specific_gap':
            quality = 'reviewed_deficient' if set(curated[key]['categories']) & {'vague_description', 'contradictory_description'} else 'reviewed_useful_with_specific_gap'
        inventory.append({k: entry[k] for k in ['schema_file', 'schema_uri', 'pointer', 'role', 'element', 'public', 'family', 'language_status']} | {
            'own_description': own, 'effective_description': effective, 'description_source': origin, 'offline_help_binding': binding,
            'quality': quality, 'direct_ref': node.get('$ref') if isinstance(node, dict) else None,
            'same_instance_parent': entry['schema_uri'] + '#' + entry['applicator_description'][0] if entry['applicator_description'] else None,
            'instance_scope': entry['instance_scope'], 'assertion_context': entry['assertion_context'],
            'same_value_owner': entry['schema_uri'] + '#' + entry['same_value_owner'],
            'constraint_facts': {k: node[k] for k in ['type', 'enum', 'const', 'required', 'default', 'minimum', 'maximum', 'minItems', 'maxItems', 'minProperties', 'maxProperties'] if k in node} if isinstance(node, dict) else {},
            'schema_keywords': sorted(node) if isinstance(node, dict) else [], 'examples_present': bool(node.get('examples')) if isinstance(node, dict) else False})
        if not entry['public'] or entry['language_status'] == 'inactive_migration_candidate':
            continue
        if isinstance(node, dict) and 'description' in node and (not isinstance(node['description'], str) or not node['description'].strip()):
            add(key, 'vague_description', 'The description annotation is malformed or empty, so it cannot provide useful help.', severity='high')
        if effective is None and binding != 'out_of_scope_reference':
            add(key, 'missing_description', 'No own, referenced or same-instance applicator description explains this public element.')
        elif effective and re.search(r'not yet documented|semantic purpose requires|runtime interpretation requires|meaning.*requires.*review', effective, re.I):
            add(key, 'unspecified_schema_contract', 'Provisional wording explicitly leaves meaning unresolved; it cannot count as useful documentation coverage.', severity='high', correction=effective, group='normative_contract_decision_required', provisional=True)
        elif effective and weak(effective, entry['element']):
            add(origin or key, 'vague_description', 'Wording repeats a name/type or generic field label instead of explaining useful meaning.', confidence='heuristic_review_required')
        if isinstance(node, dict) and 'default' in node and not re.search(r'default|suggest|serializ|fallback', effective or '', re.I):
            policy = node.get('x-scap-ng-authoring', {})
            proposed = re.sub(r'\([^)]*OVAL[^)]*\)', '', (effective or structural_wording(entry)[0]).split('. ')[0]).strip().rstrip('.') + '.' + (' Editors may suggest `' + str(node['default']) + '` for new authoring and must serialize an explicit value.' if policy.get('new_authoring_only') and policy.get('serialize_explicitly') else ' The schema default annotation is `' + str(node['default']) + '`; automatic runtime insertion is not established by this annotation.')
            proposed = re.sub(r'\s+(?:and\s+)?[a-z0-9_]+ maps OVAL[^.]*', '', proposed, flags=re.I)
            add(key, 'missing_constraint_meaning', 'A default annotation is visible but its authoring/runtime role is not explained here.', correction=proposed, group='clarification_no_validation_change', provisional=False)
        if isinstance(node, dict) and 'if' in node and effective and not re.search(r'when|if|unless|conditional|status|redact|require', effective, re.I):
            add(key, 'missing_constraint_meaning', 'Conditional assertions affect this public value, but their contextual meaning needs review.', confidence='heuristic_review_required')
    for key, note in curated.items():
        if key not in nodes:
            raise ValueError('Review note points outside discovered schemas: ' + key)
        entry = nodes[key]
        existing = entry['node'].get('description')
        if existing != note['existing_description']:
            raise ValueError('Curated wording precondition drifted: ' + key)
        for category in note['categories']:
            add(key, category, note['impact'], severity=note['severity'], correction=note['proposed_description'], group=note['approval_category'], provisional=note.get('provisional', False), evidence=note['evidence'])
    # Do not claim live editor integration from local description resolution.
    root_entry = next(e for e in nodes.values() if e['pointer'] == '' and 'automated' in documents[e['schema_uri']].get('properties', {}).get('assessment', {}).get('properties', {}).get('mode', {}).get('enum', []))
    add(root_entry['schema_uri'] + '#', 'missing_editor_help_binding', 'The audit resolves local $ref help, but no running editor or exact deployed-pack association is exercised; live contextual-help coverage remains unverified.', severity='high', confidence='integration_unverified',
        correction='Automated Assessment document; editor association with this exact schema pack must be verified separately.', group='clarification_no_validation_change', provisional=True)
    # One proposal per canonical pointer, even when multiple gap categories apply.
    grouped = defaultdict(list)
    for finding in findings.values():
        finding['affected_nodes'] = sorted(set(finding['affected_nodes']))
        grouped[finding['schema_uri'] + '#' + finding['pointer']].append(finding)
    for key, gaps in sorted(grouped.items()):
        gaps.sort(key=lambda g: (0 if key in curated else 1, SEVERITIES[g['severity']], g['category']))
        chosen = gaps[0]
        note = curated.get(key)
        replacement = note['proposed_description'] if note else chosen['proposed_replacement']
        entry = nodes[key]
        if not isinstance(entry['node'], dict):
            continue  # Boolean schema annotation cannot be added without wrapping.
        identifier = 'proposal-' + sha256(key.encode()).hexdigest()[:16]
        group = note['approval_category'] if note else chosen['approval_category']
        old = entry['node'].get('description')
        operations = ([{'op': 'test', 'path': entry['pointer'] + '/description', 'value': old}] if old is not None else [])
        operations += [{'op': 'replace' if old is not None else 'add', 'path': entry['pointer'] + '/description', 'value': replacement}]
        if note and 'proposed_examples' in note:
            previous = entry['node'].get('examples')
            if previous is not None:
                operations += [{'op': 'test', 'path': entry['pointer'] + '/examples', 'value': previous}]
            operations += [{'op': 'replace' if previous is not None else 'add', 'path': entry['pointer'] + '/examples', 'value': note['proposed_examples']}]
        if chosen['category'] == 'missing_editor_help_binding' and not note:
            replacement = old
            chosen['minimal_correction'] = 'Verify the actual editor pack pin and document association; an annotation edit does not establish deployed help.'
            operations = []  # Editor deployment association is not an annotation fix.
        shared_meaning = None
        parent_path = entry['pointer'].rsplit('/properties/', 1)[0] if '/properties/' in entry['pointer'] else None
        if entry['element'] in {'variable', 'input'} and parent_path is not None:
            parent = pointer(documents[entry['schema_uri']], parent_path)
            if isinstance(parent, dict) and set(parent.get('properties', {})) == {entry['element']} and entry['element'] in parent.get('required', []):
                target = PREFIX + 'capability-common.schema.json#/$defs/' + entry['element'] + '_reference/properties/' + entry['element']
                if key != target and target in curated:
                    shared_meaning = target
                    replacement = curated[target]['proposed_description']
                    operations = []
                    group = 'normative_contract_decision_required'
        if entry.get('comparison_domain') and key != operator_targets[entry['element']]:
            shared_meaning = operator_targets[entry['element']]
            replacement = structural_wording(nodes[shared_meaning])[0]
            operations = []
            group = 'normative_contract_decision_required'
        evidence = deepcopy(note['evidence'] if note else chosen['evidence'])
        if entry.get('comparison_domain'):
            evidence.append({'kind': 'native_typed_domain_binding', 'uri': entry['comparison_domain']['source']})
        if shared_meaning:
            evidence.append({'kind': 'proposed_shared_description_binding_not_current_inheritance', 'uri': shared_meaning})
        proposal = {'id': identifier, 'schema_file': entry['schema_file'], 'schema_uri': entry['schema_uri'], 'pointer': entry['pointer'], 'role': entry['role'],
            'existing_description': old, 'proposed_description': replacement, 'gap_ids': sorted(g['id'] for g in gaps), 'approval_category': group,
            'provisional': True if shared_meaning else note.get('provisional', False) if note else chosen['provisional'], 'status': 'proposed', 'disposition': 'pending',
            'owner_decision_needed': group == 'normative_contract_decision_required',
            'decision_link': ISSUE + '#issuecomment-6715925830' if group == 'normative_contract_decision_required' else None,
            'decision_kind': 'shared_annotation_binding' if shared_meaning else 'runtime_contract' if note and group == 'normative_contract_decision_required' else 'native_basis_required_for_wording' if group == 'normative_contract_decision_required' else 'editor_integration' if chosen['category'] == 'missing_editor_help_binding' else 'annotation_wording',
            'evidence': evidence,
            'basis': 'proposed_shared_annotation_binding' if shared_meaning else 'curated_native_contract_review' if note else 'encoded_structure_only_not_a_semantic_resolution',
            'proposed_description_ref': shared_meaning,
            'binding_warning': 'Do not point at the existing whole validator: differing identifier constraints could tighten acceptance. Review annotation-only shared binding in a future pack.' if shared_meaning else None,
            'precondition': {'file_sha256': sha256((root / entry['schema_file']).read_bytes()).hexdigest(), 'old_description_present': old is not None},
            'operations': operations, 'review_priority': min(SEVERITIES[g['severity']] for g in gaps),
            'non_annotation_followup': (chosen['category'] == 'missing_editor_help_binding' and not note) or bool(shared_meaning),
            'before_after_examples': note.get('before_after_examples', []) if note else []}
        proposals[identifier] = proposal
        for gap in gaps:
            gap['proposal_id'] = identifier
            gap['proposed_replacement'] = replacement
            gap['approval_category'] = group
            gap['owner_decision_needed'] = proposal['owner_decision_needed']
            gap['decision_link'] = proposal['decision_link']
            gap['proposed_description_ref'] = shared_meaning
            if shared_meaning:
                gap['minimal_correction'] = proposal['binding_warning']
                gap['provisional'] = True
    dispositions = notes.get('dispositions', {})
    unknown = set(dispositions) - set(proposals)
    if unknown:
        raise ValueError('Review disposition points at an unknown proposal: ' + str(sorted(unknown)))
    for identifier, review in dispositions.items():
        proposal = proposals[identifier]
        for name in ['disposition', 'status', 'approval_link', 'resolution_pointer']:
            if name in review:
                proposal[name] = review[name]
        for gap in findings.values():
            if gap.get('proposal_id') == identifier:
                gap['disposition'] = proposal['disposition']
                gap['status'] = review.get('gap_status', 'open')
                gap['resolution_pointer'] = review.get('resolution_pointer')
    ordered = sorted(findings.values(), key=lambda g: (SEVERITIES[g['severity']], g['schema_uri'], g['pointer'], g['category']))
    crosswalk = sorted(proposals.values(), key=lambda p: (p['review_priority'], p['basis'] != 'curated_native_contract_review', p['schema_uri'], p['pointer']))
    return {'schemas': schemas, 'documents': documents, 'nodes': nodes, 'store': store, 'inventory': inventory, 'findings': ordered, 'crosswalk': crosswalk,
            'manifest': manifest, 'excluded': excluded, 'notes': notes,
            'source_root': root,
            'documentation_profile': 'historical-0.4.0' if PREFIX == HISTORICAL_PREFIX else 'active-0.4.1'}


@contextmanager
def profile(active=False):
    global DEST, NATIVE_COMMIT, PILOT_COMMIT, ISSUE, PREFIX
    previous = DEST, NATIVE_COMMIT, PILOT_COMMIT, ISSUE, PREFIX
    if active:
        DEST, NATIVE_COMMIT, PILOT_COMMIT, ISSUE, PREFIX = (ACTIVE_DEST, ACTIVE_NATIVE_COMMIT,
            ACTIVE_PILOT_COMMIT, 'https://github.com/scap-ng/issues/67', ACTIVE_PREFIX)
    else:
        DEST, NATIVE_COMMIT, PILOT_COMMIT, ISSUE, PREFIX = (HISTORICAL_DEST,
            HISTORICAL_NATIVE_COMMIT, HISTORICAL_PILOT_COMMIT, 'https://github.com/scap-ng/issues/40', HISTORICAL_PREFIX)
    try:
        yield
    finally:
        DEST, NATIVE_COMMIT, PILOT_COMMIT, ISSUE, PREFIX = previous


@contextmanager
def historical_workspace(root):
    # Historical research is read from its recorded Git commit, never from
    # today's active schema directory. This keeps old receipts byte-provable.
    with tempfile.TemporaryDirectory(prefix='scap-ng-historical-docs-') as directory:
        workspace = Path(directory)
        archive = subprocess.run(['git', '-C', str(root), 'archive', HISTORICAL_NATIVE_COMMIT],
                                 check=True, capture_output=True).stdout
        with tarfile.open(fileobj=__import__('io').BytesIO(archive), mode='r:') as stream:
            stream.extractall(workspace)
        yield workspace


def audit(root=ROOT, *, active=None):
    # ``active`` is explicit for production callers. The None compatibility
    # form retains the pre-migration Python API for isolated unit fixtures;
    # it does not drive the active CLI or publish artifacts.
    if active is None:
        with profile(False):
            return _audit(root)
    if active:
        with profile(True):
            return _audit(root)
    # Callers that already materialized an archival workspace can avoid a
    # second archive operation (review-pack generation uses this path).
    if (root / '.git').exists() is False and (root / 'schema').is_dir():
        with profile(False):
            return _audit(root)
    with historical_workspace(root) as workspace:
        with profile(False):
            return _audit(workspace)


def schema_children(node, path):
    if not isinstance(node, dict):
        return
    for key in MAPS - {'$defs', 'definitions'}:
        for name in node.get(key, {}):
            yield path + '/' + key + '/' + escape(name)
    for key in ARRAYS:
        for index in range(len(node.get(key, []))):
            yield path + '/' + key + '/' + str(index)
    for key in SINGLES:
        if isinstance(node.get(key), (dict, bool)):
            yield path + '/' + key


def language_catalog(result):
    docs, store = result['documents'], result['store']
    candidates = [uri for uri, doc in docs.items() if 'automated' in doc.get('properties', {}).get('assessment', {}).get('properties', {}).get('mode', {}).get('enum', [])]
    if len(candidates) != 1:
        raise ValueError('Assessment entry discovery is ambiguous: ' + str(candidates))
    entry = candidates[0]
    visited, queue = set(), deque([entry + '#'])
    while queue:
        key = queue.popleft()
        if key in visited:
            continue
        visited.add(key)
        uri, path = urldefrag(key)
        node = store.node(key)
        if isinstance(node, dict) and '$ref' in node:
            target = urljoin(uri, node['$ref'])
            queue.append(target if '#' in target else target + '#')
        queue.extend(uri + '#' + child for child in schema_children(node, path))
    root = docs[entry]['properties']['assessment']['properties']
    variable_uri = urljoin(entry, root['variables']['additionalProperties']['$ref'])
    variable_document = store.node(variable_uri)
    declaration_uri = urljoin(variable_uri, variable_document['$ref'])
    declaration = store.node(declaration_uri)
    expression_uri = urljoin(declaration_uri, declaration['properties']['expression']['$ref'])
    expression = store.node(expression_uri)
    forms = []
    for index, branch in enumerate(expression['oneOf']):
        if len(branch.get('properties', {})) != 1:
            raise ValueError('Unrecognized variable expression branch')
        name, shape = next(iter(branch['properties'].items()))
        key = expression_uri + '/oneOf/' + str(index) + '/properties/' + escape(name)
        forms.append({'name': name, 'schema_pointer': key, 'assessment_reachable': key in visited,
                      'role': 'component' if name in {'literal', 'variable', 'values'} else 'transform',
                      'argument_shape': shape.get('type', 'shared expression reference' if '$ref' in shape else 'unspecified'),
                      'min_items': shape.get('minItems'), 'max_items': shape.get('maxItems'),
                      'return_datatype': 'not encoded at this syntax node; semantic contract review required' if name not in {'literal', 'variable', 'values'} else 'component; see declaration/literal type rules rather than a function signature',
                      'examples_present': len(shape.get('examples', []))})
    controls = []
    helpers = []
    inactive = []
    for record in result['inventory']:
        key = record['schema_uri'] + '#' + record['pointer']
        record['assessment_reachable'] = key in visited
        if record['public'] and record['role'] == 'field' and record['element'] in {'if', 'then', 'else_if', 'else', 'and', 'or', 'xor', 'one', 'not', 'foreach', 'for_each', 'elseif'}:
            controls.append({'name': record['element'], 'schema_pointer': key, 'assessment_reachable': key in visited})
        if record['role'] == 'shared_definition' and record['element'].startswith('foreach'):
            helpers.append({'name': record['element'], 'schema_pointer': key, 'assessment_reachable': key in visited,
                            'incoming_refs': sum(1 for r in result['inventory'] if r['direct_ref'] and urljoin(r['schema_uri'], r['direct_ref']) == key)})
        if record['language_status'] == 'inactive_migration_candidate' and record['element'] == 'name':
            node = store.node(key)
            if isinstance(node, dict) and 'enum' in node:
                inactive += [{'name': name, 'schema_pointer': key, 'status': 'inactive candidate, not accepted Assessment syntax'} for name in node['enum']]
    return {'assessment_entry': entry, 'variable_expression_root': expression_uri, 'active_variable_forms': forms,
            'control_flow_fields': controls, 'unreachable_shared_foreach_helpers': helpers,
            'inactive_function_call_names': inactive,
            'spelling_notes': {'else_if': any(c['name'] == 'else_if' and c['assessment_reachable'] for c in controls),
                               'elseif': any(c['name'] == 'elseif' and c['assessment_reachable'] for c in controls),
                               'foreach_or_for_each_authored_placement': any(c['name'] in {'foreach', 'for_each'} and c['assessment_reachable'] for c in controls)}}


def apply_preview(result, proposals):
    documents = deepcopy(result['documents'])
    for proposal in proposals:
        key = proposal['schema_uri'] + '#' + proposal['pointer']
        if key not in result['nodes'] or not isinstance(result['nodes'][key]['node'], dict):
            raise ValueError('Annotation target is not a discovered schema node')
        for operation in proposal['operations']:
            path = operation['path']
            if path.rsplit('/', 1)[-1] not in {'description', 'examples', 'title'}:
                raise ValueError('Validation keyword in annotation proposal: ' + path)
            parent_path, name = path.rsplit('/', 1)
            if parent_path != proposal['pointer']:
                raise ValueError('Annotation operation must target its exact schema node')
            parent = pointer(documents[proposal['schema_uri']], parent_path)
            if operation['op'] == 'test':
                if parent.get(name) != operation['value']:
                    raise ValueError('Annotation precondition failed: ' + path)
            elif operation['op'] in {'add', 'replace'}:
                if operation['op'] == 'replace' and name not in parent:
                    raise ValueError('Replacement target is missing: ' + path)
                parent[name] = deepcopy(operation['value'])
            else:
                raise ValueError('Unsupported patch operation')
    return documents


def baseline_for(result):
    return {'format': 'scap-ng-documentation-gap-baseline-1', 'native_commit': NATIVE_COMMIT,
            'known_gaps': {g['id']: digest({k: g[k] for k in ['schema_uri', 'pointer', 'role', 'category', 'existing_description', 'impact', 'severity']}) for g in result['findings']}}


def baseline_regressions(result, baseline):
    current = baseline_for(result)['known_gaps']
    known = baseline['known_gaps']
    return {'new': sorted(set(current) - set(known)), 'changed': sorted(k for k in current.keys() & known.keys() if current[k] != known[k]),
            'no_longer_detected_not_automatically_resolved': sorted(set(known) - set(current))}


def validate_register(result):
    seen = set()
    proposals = {p['id']: p for p in result['crosswalk']}
    for gap in result['findings']:
        key = (gap['schema_uri'], gap['pointer'], gap['role'], gap['category'])
        if key in seen:
            raise ValueError('Duplicate documentation gap')
        seen.add(key)
        if gap['category'] not in CATEGORIES or gap['approval_category'] not in GROUPS or gap['status'] not in STATUSES:
            raise ValueError('Invalid gap vocabulary')
        if gap['status'] == 'resolved':
            if not gap['resolution_pointer']:
                raise ValueError('A resolved gap requires a resolution pointer')
            result['store'].node(gap['resolution_pointer'])
        result['store'].node(gap['schema_uri'] + '#' + gap['pointer'])
        if gap.get('proposal_id') not in proposals:
            raise ValueError('Gap lacks an exact wording proposal')
    for proposal in proposals.values():
        text = proposal['proposed_description']
        if not proposal['non_annotation_followup'] and (not isinstance(text, str) or not text.strip() or (weak(text, proposal['pointer'].rsplit('/', 1)[-1]) and not proposal['provisional'])):
            raise ValueError('Malformed or filler non-provisional proposed wording')
        if proposal['owner_decision_needed'] and not proposal['decision_link']:
            raise ValueError('Owner decision lacks a source link')
        if proposal['status'] not in STATUSES:
            raise ValueError('Unsupported proposal status')
        if proposal['disposition'] not in {'pending', 'accepted', 'rejected', 'deferred'}:
            raise ValueError('Unsupported review disposition')
        if proposal['disposition'] == 'accepted':
            if not proposal.get('approval_link'):
                raise ValueError('Accepted wording needs an explicit approval link')
            if proposal.get('resolution_pointer') and result['store'].node(proposal['resolution_pointer']) != proposal['proposed_description']:
                raise ValueError('Accepted canonical wording drifted')
    return True


def md(value, maximum=None):
    text = str(value if value is not None else '—').replace('|', '&#124;').replace('\n', ' ')
    return text[:maximum - 1] + '…' if maximum and len(text) > maximum else text


def table_count(counter, heading):
    return ['### ' + heading, '', '| Value | Count |', '| --- | ---: |'] + ['| ' + key + ' | ' + str(value) + ' |' for key, value in sorted(counter.items())] + ['']


def report(result, catalog):
    public = [r for r in result['inventory'] if r['public'] and r['language_status'] != 'inactive_migration_candidate']
    rows = ['# Core/shared documentation: Phase 1', '',
            '**Inventory and wording proposals only. No schema edits or new runtime semantics are accepted.**', '',
            f'Pin: `{NATIVE_COMMIT}`; renderer dependency: PR #39 `{PILOT_COMMIT}`. All JSON inputs are enumerated in [schema-manifest.json](schema-manifest.json).', '',
            f'Discovered **{len(result["schemas"])} schema documents** among {len(result["manifest"])} JSON inputs. Audited {len(result["inventory"])} schema nodes, including {len(public)} public current-core/shared nodes. {len(result["excluded"])} generated capability definitions are explicit scope exclusions; no capability expansion is authorized.', '',
            'Public prose owners are named properties/definitions and roots. Anonymous array/map/alternative schemas and guard overrides remain inventoried with their exact constraints; their containing public element owns explanatory prose, while named fields inside them remain public. Fields introduced only in conditional branches are included, rather than discarded as guard overrides. Curated branch notes are additional targeted findings.', '',
            f'Found **{len(result["findings"])} deduplicated findings** at {len(result["crosswalk"])} canonical proposal locations. Presence is not useful-quality approval. Structural-only/provisional proposals remain open for review; generic filler cannot close a gap.', '',
            '[Batch 1 editorial receipt](EDITORIAL-REVIEW.md) · [Batch 2 pending review](EDITORIAL-REVIEW-2.md) · [Phase 1 wording inventory](CROSSWALK.md) · [two bounded previews](PILOTS.md) · [machine inventory](inventory.jsonl) · [gap register](gaps.jsonl) · [full crosswalk](crosswalk.jsonl) · [annotation patch](proposed-annotations.patch.json).', '']
    rows += table_count(Counter('own' if r['own_description'] else 'inherited' if r['effective_description'] else 'missing' for r in public), 'Description presence')
    rows += table_count(Counter(r['quality'] for r in public), 'Useful-quality review state')
    rows += table_count(Counter(p['decision_kind'] for p in result['crosswalk']), 'Review decision kind')
    rows += table_count(Counter({group: sum(p['approval_category'] == group for p in result['crosswalk']) for group in GROUPS}), 'Proposal approval category')
    for title, key in [('Gap category', 'category'), ('Severity', 'severity'), ('Role', 'role'), ('Document family', 'family')]:
        rows += table_count(Counter(g[key] for g in result['findings']), title)
    rows += ['## Actual language boundary', '', 'Active Variable forms: ' + ', '.join('`' + f['name'] + '`' for f in catalog['active_variable_forms']) + '.', '',
             'The broader canonical function-call migration document is inactive; its names are not active authoring/runtime support. The actual branch spelling is `else_if`, not `elseif`. Shared foreach helper definitions exist but have no Assessment reference path; they are not a demonstrated authored placement.', '',
             '## Review priorities', '', '1. Resolve concat casting/status/return obligations, regex dialect/status behavior, sorting edge cases and generic typed-value consistency before calling them editorial fixes.',
             '2. Review the concrete shared reference/predicate/evaluation wording and two previews.',
             '3. Triage remaining structural-only proposals by impact; they expose gaps and are not approved descriptions.',
             '4. Verify exact editor-pack association separately. Offline $ref resolution is tested; live hover integration is not.', '',
             '## Reproduce / gate', '', '```sh', 'python tools/audit_schema_documentation.py', 'python tools/audit_schema_documentation.py --check', 'python -m unittest discover -s tests -v', '```', '',
             'The explicit baseline permits preexisting findings but rejects new/changed findings and stale output. Disappearing findings are reported, never automatically marked resolved. Update a baseline only as an explicit review action; no baseline rewrite occurs in normal generation.', '',
             '**STOP for Jack\'s review. No Phase 2, merge, bulk annotations, editor repin or 104-capability expansion.**', '']
    return '\n'.join(rows)


def crosswalk_report(result):
    curated = [p for p in result['crosswalk'] if p['basis'] == 'curated_native_contract_review']
    rows = ['# Proposed wording crosswalk', '',
            'For the owner-requested short author-facing candidates, start with [Editorial review batch 1](EDITORIAL-REVIEW.md). The table below retains the original Phase 1 Codex drafts, not editorial approval.', '',
            'The table shows the source-reviewed priority set; the [complete machine crosswalk](crosswalk.jsonl) includes every deficient canonical target. It is a review proposal, not a second documentation authority. Structural-only remainder text is explicitly provisional where meaning cannot be established; no proposal is approved or applied.', '',
            '| Schema URI + pointer | Role | Existing wording | Defect | Proposed replacement | Basis / decision | Status |', '| --- | --- | --- | --- | --- | --- | --- |']
    gaps = {g['id']: g for g in result['findings']}
    for p in curated:
        categories = ', '.join(gaps[g]['category'] for g in p['gap_ids'])
        rows.append('| ' + ' | '.join([md(p['schema_uri'] + '#' + p['pointer']), md(p['role']), md(p['existing_description'], 170), md(categories), md(p['proposed_description']), md(p['approval_category']) + ('; **provisional**' if p['provisional'] else ''), 'proposed / pending']) + ' |')
    rows += ['', '## Exact application model', '',
             'The [patch bundle](proposed-annotations.patch.json) has per-file SHA-256 preconditions and exact add/replace/test operations. Only `description`, `examples` or `title` annotation destinations are permitted. New annotations use an absent-old-value precondition; replacements test the old text. There is no command that writes the bundle to frozen schemas.', '',
             'Approve wording by proposal ID with an approval link and accepted/rejected/deferred disposition. An accepted annotation must later move into the coordinated next-version canonical schema and drive renderer/editor help from that same node. Do not keep independently maintained Markdown copies.', '',
             'Inline Input/Variable wrapper copies and typed comparison copies are mapped to one proposed shared description per role/domain; their existing validation shapes are not assumed equivalent. These consumer bindings are non-annotation follow-ups with no copied description patch. A future annotation-only shared binding needs review. Editor deployment association is likewise a non-annotation follow-up with no fake description patch. Assertion-only/Boolean schemas are inventoried but not treated as separate public prose fields; wrapping them would require a separately reviewed structural proposal.', '',
             '## High-impact before/after review', '']
    for p in curated:
        for example in p['before_after_examples']:
            rows += ['- `' + p['id'] + '`: **Before:** ' + example['before'] + ' **After:** ' + example['after']]
    rows += ['', 'All schema acceptance tests are structural. No scanner execution, function-runtime parity or release-readiness result is claimed.', '']
    return '\n'.join(rows)


def resolved_text(node, uri, store, seen=()):
    if not isinstance(node, dict):
        return None
    if node.get('description'):
        return node['description']
    if '$ref' in node:
        target = urljoin(uri, node['$ref'])
        if target not in seen:
            value = resolved_text(store.node(target), target, store, seen + (target,))
            if value:
                return value
    for part in node.get('allOf', []):
        value = resolved_text(part, uri, store, seen)
        if value:
            return value
    return None


def pilot_report(result, catalog):
    core = next(p for p in result['crosswalk'] if p['schema_uri'].endswith('/assessment-language.schema.json') and p['pointer'] == '/$defs/canonical_all_items_requirement')
    concat = next(f for f in catalog['active_variable_forms'] if f['name'] == 'concat')
    function = next(p for p in result['crosswalk'] if p['schema_uri'] + '#' + p['pointer'] == concat['schema_pointer'])
    documents = apply_preview(result, [core, function])
    store = SchemaStore(documents)
    rows = ['# Two bounded schema-driven previews', '',
            '**Unapproved annotation preview in memory only.** The same inspector used by PR #39 reads types, occurrence bounds and local references here. No per-schema renderer is introduced. These pages are generated from native schemas plus exact proposed annotation operations, not hand-maintained guide text.', '',
            '## Assessment core: comparison Require', '', '`' + core['schema_uri'] + '#' + core['pointer'] + '`', '',
            '**Before:** ' + (core['existing_description'] or 'No description.'), '', '**Proposed:** ' + core['proposed_description'], '',
            '| Field | Type | Occurrences | Description |', '| --- | --- | --- | --- |']
    node = store.node(core['schema_uri'] + '#' + core['pointer'])
    properties = node['properties']
    for name, child in properties.items():
        rows.append('| ' + ' | '.join([md('`' + name + '`'), md(types(child, core['schema_uri'], store)), md(property_occurrences(node, core['schema_uri'], name, store)), md(resolved_text(child, core['schema_uri'], store) or 'Undocumented here; shared/structural proposal requires review.')]) + ' |')
    rows += ['', 'Counts are contextual: the Item/field parent policies are required for comparison; selection of `fields` versus Boolean groups remains conditional. Existence-only requirements use their separate shared schema. Unsupported/indeterminate constraints are reported, not guessed.', '',
             '## Shared concat family', '', '`' + function['schema_uri'] + '#' + function['pointer'] + '`', '',
             '| Signature element | Schema shape / bounds | Contract |', '| --- | --- | --- |']
    node = store.node(concat['schema_pointer'])
    rows += ['| `concat(components…)` | ' + collection_occurrences(node, function['schema_uri'], 'array', store) + ' ordered entries | ' + md(function['proposed_description']) + ' |',
             '| component | Shared expression `$ref`; recursive nesting allowed by grammar | Arguments are syntax-validated; conversion/status obligations remain **provisional**. |',
             '| return datatype | Not encoded at this function syntax node | Owner must confirm the native return/conversion/status contract; no runtime result is inferred from validation. |', '',
             '**Before:** ' + function['existing_description'], '', '**Proposed:** ' + function['proposed_description'], '',
             'Signature notation above is descriptive; native source uses the named `concat` key. Minimal schema example (not executed):', '', '```json', json.dumps({'concat': [{'literal': 'a'}, {'literal': 'b'}]}, indent=2), '```', '',
             'The syntax still rejects fewer than two components. Annotation previews preserve the entire validation assertion tree; positive/negative witnesses are checked before and after. No arithmetic, substring or inactive function-call grammar is added.', '',
             'Historical concat basis: pinned OVAL 5.12.3 `ConcatFunctionType`, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`; source attribution is review evidence, not automatic native semantics.', '']
    return '\n'.join(rows)


def editorial_batch(result, root=None, filename="editorial-batch.json"):
    """Validate a review receipt against the exact schema snapshot that produced it.

    Inference from result['source_root'] prevents an archived 0.4.0 worksheet
    from silently reading today's active 0.4.1 files. An explicitly supplied
    root remains available for negative fixture tests.
    """
    root = Path(root) if root is not None else Path(result.get('source_root', ROOT))
    file = root / DEST / filename
    if not file.exists():
        return None
    batch = json.loads(file.read_text())
    rows = batch['proposals']
    descriptions = [r for r in rows if r['author_description'] is not None]
    minimum = 20 if filename == 'editorial-batch.json' else 25
    if not minimum <= len(descriptions) <= 30 or len(rows) > 30:
        raise ValueError(f'Editorial batch must contain {minimum}–30 descriptions and at most 30 cases')
    if batch['native_commit'] != NATIVE_COMMIT or batch['phase1_commit'] != '823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2' or batch['workflow']['canonical_installation_authorized'] is not False:
        raise ValueError('Editorial worksheet may not authorize canonical installation')
    if len({r['id'] for r in rows}) != len(rows) or len({(r['schema_uri'], r['pointer']) for r in rows}) != len(rows):
        raise ValueError('Duplicate editorial case')
    required = ({'references', 'evaluation', 'variables', 'Require', 'functions', 'results', 'document roots'}
                if filename == 'editorial-batch.json' else
                {'references', 'evaluation', 'variables', 'Require', 'Inputs', 'results', 'document roots'})
    if not required <= {r['category'] for r in rows}:
        raise ValueError('Editorial sample lacks the required diversity')
    if not batch['workflow']['normative_approval'].startswith('pending'):
        raise ValueError('Independent editorial/normative approval is not asserted by this batch')
    blocked = {r['schema_pointer'] for r in language_catalog(result)['unreachable_shared_foreach_helpers'] if not r['assessment_reachable']}
    prior = {p['id']: p for p in result['crosswalk']}
    inventory = {r['schema_uri'] + '#' + r['pointer']: r for r in result['inventory']}
    checked = 0
    for row in rows:
        key = row['schema_uri'] + '#' + row['pointer']
        if key not in result['nodes'] or row['schema_file'] != result['nodes'][key]['schema_file']:
            raise ValueError('Unknown editorial schema pointer: ' + key)
        node = result['store'].node(key)
        if row['source_sha256'] != sha256((root / row['schema_file']).read_bytes()).hexdigest() or row['existing_wording'] != node.get('description'):
            raise ValueError('Editorial existing-wording precondition drifted: ' + key)
        info = inventory[key]
        inherited = {'text': info['effective_description'], 'source': info['description_source']} if info['description_source'] and info['description_source'] != key else None
        if row['inherited_wording'] != inherited:
            raise ValueError('Editorial inherited wording drifted: ' + key)
        origin = row['codex_proposal_source']
        if origin['kind'] == 'phase1_crosswalk':
            if origin['commit'] != batch['phase1_commit'] or row['codex_proposal'] != prior[origin['proposal_id']]['proposed_description']:
                raise ValueError('Original Codex proposal drifted: ' + key)
        elif origin['kind'] != 'new_bounded_draft_from_pinned_native_sources':
            raise ValueError('Unsupported Codex-draft origin')
        if not row['engineering_note'].strip() or not row['codex_proposal'].strip():
            raise ValueError('Missing independent engineering note or original draft')
        if row['classification'] not in {'editorial', 'semantic_decision_needed'}:
            raise ValueError('Unsupported editorial classification')
        if row['classification'] == 'semantic_decision_needed' and row['semantic_status'] != 'pending_semantic_review':
            raise ValueError('Semantic decision must remain pending')
        text = row['author_description']
        if key in blocked and (text is not None or not row['withheld']):
            raise ValueError('Unreachable helper must remain withheld')
        if row['withheld']:
            if text is not None or row['classification'] != 'semantic_decision_needed':
                raise ValueError('Withheld author help must not advertise unresolved syntax')
        else:
            if not isinstance(text, str) or not text.strip() or weak(text, row['element']) or len(text) > 220 or len(re.findall(r'[.!?](?:\s|$)', text)) > 2:
                raise ValueError('Author description must be a short one/two-sentence candidate')
            if re.search(r'\b(schema|structurally accepts|native contract|source lineage|owner review|pending|not yet specified)\b', text, re.I):
                raise ValueError('Engineering/status prose leaked into author help')
            if text == row['engineering_note']:
                raise ValueError('Author help and engineering note must stay independent')
        validate_editorial_receipt(batch, row, filename)
        if filename != 'editorial-batch.json':
            if row['proposed_description_owner'] != key:
                raise ValueError('Each concept needs one exact proposed description owner')
            for consumer in row['related_consumer_pointers']:
                result['store'].node(consumer)
        for evidence in row['evidence']:
            result['store'].node(evidence)
        for case in row['checks']:
            result['store'].node(case['schema_uri'])
            if 'instance_file' in case:
                path = (root / case['instance_file']).resolve()
                if not path.is_relative_to((root / 'examples').resolve()):
                    raise ValueError('Editorial example must be a pinned repository example')
                if sha256(path.read_bytes()).hexdigest() != case['instance_sha256']:
                    raise ValueError('Pinned editorial example drifted')
                instance = yaml.safe_load(path.read_bytes())
            else:
                instance = case['instance']
            validator = Draft202012Validator({'$ref': case['schema_uri']}, registry=result['store'].registry)
            if validator.is_valid(instance) != case['expected_valid']:
                raise ValueError('Editorial syntax witness disagrees: ' + row['id'] + ' / ' + case['label'])
            checked += 1
    if filename in {'editorial-batch.json', 'editorial-batch-2.json'}:
        reviewed = deepcopy(batch)
        reviewed.pop('review_receipt')
        reviewed['workflow']['editorial_review'] = ('pending ChatGPT editorial review' if filename == 'editorial-batch.json' else 'pending owner editorial review')
        for row in reviewed['proposals']:
            row['author_description'] = row.pop('reviewed_author_description')
            row.pop('editorial_review_url')
            row['editorial_status'] = 'pending_editorial_review'
        expected_digest = ('da9f062faedf9d957afe57f5ab76eab81e72b913042fe27d912f82b297bfd36d'
                           if filename == 'editorial-batch.json' else '6d0644c3a64fdf1c14f3bdee056e810943b076ad3ea135faf4d433760206a96e')
        if digest(reviewed) != expected_digest:
            raise ValueError('Reviewed source dossier must remain unchanged')
    return batch, checked


def validate_editorial_receipt(batch, row, filename="editorial-batch.json"):
    """Record the explicit owner ID lists without upgrading semantic holds."""
    receipt = batch['review_receipt']
    review_url = 'https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721578815'
    authorization = 'https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721594181'
    commit = 'c742e0d6039c56d70eab973bc28f9ccb01f5241e'
    if filename == 'editorial-batch-2.json':
        review_url = 'https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721712939'
        authorization = 'https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721723400'
        commit = '47bbe94f65e970edffd35433b1d744596a671322'
    if (receipt['review_url'] != review_url or row.get('editorial_review_url') != review_url
            or receipt['authorization_url'] != authorization
            or receipt['reviewed_commit'] != commit):
        raise ValueError('Editorial receipt approval provenance drifted')
    accepted = '01 02 03 05 06 08 09 10 11 12 14 19 20 22 23 24 25 27'.split()
    revisions = {
        '04': 'Combines Test and Assessment outcomes using Boolean operators and conditional expressions.',
        '07': "Compares a collected field's values or checks for confirmed absence.",
        '13': 'Sets how many observed values must be present for a field.'}
    holds = '15 16 17 18 21 26'.split()
    withheld = ['28']
    if filename == 'editorial-batch-2.json':
        accepted = '01 02 03 04 05 08 09 10 11 12 13 14 15 20 21 22 23 24 25 26 27 28'.split()
        revisions = {
            '06': 'Selects a constant or locally derived Variable.',
            '18': 'Declares that this branch cannot be evaluated and provides a reason.',
            '19': 'Declares that this branch does not apply and provides a reason.'}
        holds, withheld = ['07', '16', '17'], []
    if (receipt['accepted_as_written'] != accepted or receipt['accepted_with_revision'] != sorted(revisions)
            or receipt['semantic_holds'] != holds or receipt['withheld'] != withheld):
        raise ValueError('Editorial receipt must preserve explicit reviewed ID lists')
    identifier = row['id']
    status = ('accepted_as_written' if identifier in accepted else 'accepted_with_revision' if identifier in revisions
              else 'draft_style_acceptable_semantic_hold' if identifier in holds else 'withheld' if identifier in withheld else None)
    expected = revisions.get(identifier, row['reviewed_author_description'])
    if status is None or row['editorial_status'] != status or row['author_description'] != expected:
        raise ValueError('Editorial receipt status or approved wording drifted')
    if identifier in holds + withheld and row['classification'] != 'semantic_decision_needed':
        raise ValueError('Editorial receipt cannot clear semantic holds')
    if identifier in accepted + list(revisions) and row['classification'] != 'editorial':
        raise ValueError('Editorial subset classification drifted')


def editorial_report(result, filename="editorial-batch.json"):
    validated = editorial_batch(result, filename=filename)
    if validated is None:
        return None
    batch, checked = validated
    rows = batch['proposals']
    number = 1 if filename == 'editorial-batch.json' else 2
    lines = [f'# Editorial review batch {number}', '',
             '**No canonical edits or normative approval.**', '',
             ('Batch 1 editorial receipt: **21 accepted descriptions** (18 as written, 3 revised), **6 semantic holds**, **1 withheld**. '
              'Uses the explicit reviewed list of 18 accepted IDs plus the three approved wording revisions. [Independent review]('
              + batch['review_receipt']['review_url'] + ') · [Owner authorization](' + batch['review_receipt']['authorization_url'] + ').'
              if number == 1 else 'Batch 2 editorial receipt: **25 accepted descriptions** (22 as written, 3 revised), **3 semantic holds**. [Independent review](' + batch['review_receipt']['review_url'] + ') · [Owner authorization](' + batch['review_receipt']['authorization_url'] + ').'), '',
             'Native pin: `' + batch['native_commit'] + '`. Full schema URIs use `https://scap-ng.dev/schema/v0.4.0/`; every file/pointer and source hash is recorded in [' + filename + '](' + filename + ').', '',
             str(checked) + ' positive/negative syntax witnesses were checked against the pinned definitions, including parent-context cases. They do not execute collection, evaluation or transformations and do not establish runtime equivalence.', '',
             '## Edited author-facing candidates', '',
             '| Case / element | `author_description` | Classification / disposition |', '| --- | --- | --- |']
    for row in rows:
        text = row['author_description'] or '**Withheld — no supported-placement description proposed.**'
        classification = 'editorial' if row['classification'] == 'editorial' else '**semantic decision needed**'
        lines.append('| [' + row['id'] + ' ' + md(row['element']) + '](#case-' + row['id'] + ') | ' + md(text) + ' | ' + classification + '; ' + row['editorial_status'].replace('_', ' ') + ' |')
    lines += ['', '## Sources, initial drafts and engineering notes', '',
              'Open a case for its exact pointer, existing local/inherited help, original Codex proposal and separate engineering note. Source verification is an editorial prerequisite, not approval to install a description.', '']
    for row in rows:
        key = row['schema_uri'] + '#' + row['pointer']
        note_origin = row['codex_proposal_source']
        origin_text = ('Phase 1 `' + note_origin['proposal_id'] + '` at `' + note_origin['commit'] + '`') if note_origin['kind'] == 'phase1_crosswalk' else 'New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.'
        lines += ['<a id="case-' + row['id'] + '"></a>', '<details>', '<summary>' + row['id'] + ' — ' + row['element'] + '</summary>', '',
                  '**Exact schema pointer:** `' + key + '`', '',
                  '**Source file:** [' + row['schema_file'] + '](' + source_link({'schema_file': row['schema_file']}) + ')', '',
                  '**Existing local wording:** ' + (row['existing_wording'] or 'No local description.'), '']
        if row['inherited_wording']:
            lines += ['**Existing inherited wording:** ' + row['inherited_wording']['text'], '', '**Inherited source:** `' + row['inherited_wording']['source'] + '`', '']
        if row['editorial_status'] == 'accepted_with_revision':
            lines += ['**Wording before editorial revision:** ' + row['reviewed_author_description'], '']
        lines += ['**Codex proposal:** ' + row['codex_proposal'], '', '**Draft provenance:** ' + origin_text, '',
                  '**Edited `author_description`:** ' + (row['author_description'] or 'Withheld.'), '',
                  '**Separate `engineering_note`:** ' + row['engineering_note'], '',
                  '**Classification:** ' + row['classification'] + '; **editorial status:** ' + row['editorial_status'] + '; **semantic status:** ' + row['semantic_status'] + '.', '',
                  '**Proposed description authority:** `' + row.get('proposed_description_owner', key) + '`; related consumers: ' + (', '.join('`' + p + '`' for p in row.get('related_consumer_pointers', [])) or 'none separately bound in this worksheet') + '.', '',
                  '**Source/syntax checks:** ' + str(len(row['checks'])) + ' witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.', '', '</details>', '']
    lines += ['## Review gate', '',
              'Approve style separately from behavior. A semantic-decision row remains pending even if its sentence reads well. The batch 1 foreach case remains withheld until placement is decided. The bulk patch and frozen schemas remain unchanged. Eight approved descriptions are demonstrated only in the [isolated next-version proposal](../../pilots/approved-annotations/RECEIPT.md); no production editor installation is authorized.', '',
              '**Stop for editorial review.** No bulk shortening of the 1,580 findings, schema edit, editor repin, migration or merge.', '']
    return '\n'.join(lines)


def _artifacts(result):
    catalog = language_catalog(result)
    validate_register(result)
    public = [r for r in result['inventory'] if r['public'] and r['language_status'] != 'inactive_migration_candidate']
    manifest = {'native_commit': NATIVE_COMMIT, 'renderer_dependency': {'pr': 39, 'commit': PILOT_COMMIT}, 'files': result['manifest'],
                'excluded_capability_definitions': result['excluded'], 'language': catalog,
                'coverage': {'schemas': len(result['schemas']), 'all_schema_nodes': len(result['inventory']), 'public_current_nodes': len(public),
                             'findings': len(result['findings']), 'proposal_targets': len(result['crosswalk']),
                             'quality_review_is_not_complete': True}}
    bundle = {'format': 'scap-ng-annotation-patch-proposal-1', 'native_commit': NATIVE_COMMIT, 'auto_apply_authorized': False,
              'files': {}, 'non_annotation_followups': [p['id'] for p in result['crosswalk'] if p['non_annotation_followup']]}
    for p in result['crosswalk']:
        if not p['operations']:
            continue
        value = bundle['files'].setdefault(p['schema_file'], {'sha256_precondition': p['precondition']['file_sha256'], 'proposals': []})
        value['proposals'].append({'proposal_id': p['id'], 'approval_category': p['approval_category'], 'old_description_present': p['precondition']['old_description_present'], 'operations': p['operations']})
    output = {'schema-manifest.json': json.dumps(manifest, indent=2) + '\n',
              'inventory.jsonl': ''.join(encode(r) + '\n' for r in result['inventory']),
              'gaps.jsonl': ''.join(encode(r) + '\n' for r in result['findings']),
              'crosswalk.jsonl': ''.join(encode(r) + '\n' for r in result['crosswalk']),
              'proposed-annotations.patch.json': json.dumps(bundle, indent=2) + '\n',
              'REPORT.md': report(result, catalog), 'CROSSWALK.md': crosswalk_report(result)}
    if result.get('documentation_profile') == 'historical-0.4.0':
        output['PILOTS.md'] = pilot_report(result, catalog)
    seen = set()
    for filename, report_name in [('editorial-batch.json', 'EDITORIAL-REVIEW.md'), ('editorial-batch-2.json', 'EDITORIAL-REVIEW-2.md')]:
        validated = editorial_batch(result, filename=filename)
        if validated is None:
            continue
        keys = {(r['schema_uri'], r['pointer']) for r in validated[0]['proposals']}
        if seen & keys:
            raise ValueError('Editorial batches must not repeat schema targets')
        seen |= keys
        output[report_name] = editorial_report(result, filename=filename)
    return output



def artifacts(result):
    with profile(result.get('documentation_profile') == 'active-0.4.1'):
        return _artifacts(result)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--diff-baseline', action='store_true', help='Read-only new/changed/disappearing finding IDs')
    parser.add_argument('--write-baseline', action='store_true', help='Explicit research-baseline action; never applies schema annotations')
    args = parser.parse_args()
    try:
        with profile(True):
            result = _audit()
            outputs = _artifacts(result)
            baseline_path = ROOT / DEST / 'baseline.json'
            if args.write_baseline:
                if args.check or args.diff_baseline:
                    raise ValueError('Read-only checks cannot write a baseline')
                baseline_path.write_text(json.dumps(baseline_for(result), indent=2, sort_keys=True) + '\n')
            if not baseline_path.exists():
                raise ValueError('Explicit baseline missing; review the inventory before creating it')
            differences = baseline_regressions(result, json.loads(baseline_path.read_text()))
            if args.diff_baseline:
                print(json.dumps(differences, indent=2))
                return 1 if differences['new'] or differences['changed'] else 0
            if differences['no_longer_detected_not_automatically_resolved']:
                print(str(len(differences['no_longer_detected_not_automatically_resolved'])) + ' findings no longer detected; no resolution is inferred.')
            if differences['new'] or differences['changed']:
                raise ValueError('New/regressed documentation findings: ' + encode(differences))
            for name, content in outputs.items():
                target = ROOT / DEST / name
                if args.check:
                    if not target.exists() or target.read_bytes() != content.encode():
                        raise ValueError('Stale documentation inventory: ' + str(target.relative_to(ROOT)))
                else:
                    target.write_bytes(content.encode())
            print(('Checked' if args.check else 'Generated') + f' {len(outputs)} Phase-1 artifacts; {len(result["findings"])} baselined findings; no canonical schemas written.')
            return 0
    except (ValueError, KeyError) as exc:
        print('Core/shared documentation audit: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
