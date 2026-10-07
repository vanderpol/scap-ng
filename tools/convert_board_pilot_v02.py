"""Reproduce six Board cases through the maintained converter and mappings.

This adapter selects pinned source closures and assigns reviewed local names.
It contains no OVAL-to-NG semantic lowering; that remains in the existing tools.
It never writes or derives expected results. See the package conversion-plan.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.assessment_oval_vocabulary import align_assessment_vocabulary
from scap_upconvert_v003.native_capability_mapping import apply_ready_capability_mappings, apply_capability_mapping
from scap_ng_roundtrip_v003.native_assessment_to_oval import build
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from validate_native_json_schemas import build_validators, document_errors
from validate_generated_capability_semantics import validate_assessment_capability_semantics
from check_current_authoring_contract import violations
from oval_semantic_ir import collect_refs

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'board/review-content/0.2.0'
MAPPINGS = ROOT / 'schema/v0.2.0/capability-mappings/supported'
PLAN = PACKAGE / 'conversion-plan.json'


def local(tag):
    return tag.rsplit('}', 1)[-1]


def node_form(node, omit_criteria=False):
    """Namespace-aware, whitespace-insensitive source identity comparison."""
    return (node.tag, sorted(node.attrib.items()), (node.text or '').strip(),
            [node_form(child) for child in node if not (omit_criteria and local(child.tag) == 'criteria')])


def verify_source(plan, source_root):
    sha = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=source_root, check=True,
                         capture_output=True, text=True).stdout.strip()
    if sha != plan['source_revision']:
        raise ValueError(f'Expected pinned Self-Assertion revision; found {sha}')
    for case in plan['cases']:
        full_path = source_root / case['source_file']
        # Hash the exact Git blob, independent of Windows checkout newlines.
        blob = subprocess.run(['git', 'show', plan['source_revision'] + ':' + case['source_file']],
                              cwd=source_root, capture_output=True, check=True).stdout
        if hashlib.sha256(blob).hexdigest() != case['source_sha256']:
            raise ValueError(f"Pinned source blob differs: {case['source_file']}")
        if full_path.read_bytes().replace(b'\r\n', b'\n') != blob.replace(b'\r\n', b'\n'):
            raise ValueError(f"Source working file differs beyond checkout newlines: {case['source_file']}")
        original = ET.fromstring(blob)
        full_nodes = {n.get('id'): n for n in original.iter() if n.get('id')}
        selected = ET.parse(PACKAGE / case['source_extract']).getroot()
        nodes = {n.get('id'): n for n in selected.iter() if n.get('id')}
        for identity, node in nodes.items():
            fragment = identity == case['source_definition'] and case['source_scope'] == 'selected_criterion_closure'
            if node_form(node, omit_criteria=fragment) != node_form(full_nodes[identity], omit_criteria=fragment):
                raise ValueError(f'Extract changed source node {identity}')
        if case['source_scope'] == 'selected_criterion_closure':
            criteria = next(n for n in nodes[case['source_definition']] if local(n.tag) == 'criteria')
            if criteria.get('operator', 'AND') != 'AND' or criteria.get('negate', 'false') != 'false':
                raise ValueError('Selected criterion scope must be explicitly an AND fragment')
            full_leaves = {n.get('test_ref'): n for n in full_nodes[case['source_definition']].iter() if local(n.tag) == 'criterion'}
            selected_leaves = list(criteria)
            if {n.get('test_ref') for n in selected_leaves} != set(case['selected_test_ids']):
                raise ValueError('Unexpected criterion scope')
            for leaf in selected_leaves:
                if node_form(leaf) != node_form(full_leaves[leaf.get('test_ref')]):
                    raise ValueError('Criterion changed during extraction')
        # Every extracted node is reachable; references are neither missing
        # nor supplemented with unrelated content.
        reached, pending = set(), [case['source_definition']]
        while pending:
            identity = pending.pop()
            if identity in reached:
                continue
            reached.add(identity)
            refs, missing, _ = collect_refs(identity, nodes[identity], set(nodes))
            if missing:
                raise ValueError(f'Unresolved source references: {missing}')
            pending.extend(refs - reached)
        if reached != set(nodes):
            raise ValueError('Extraneous source nodes in closure')
    return sha


def state_refs(value):
    if isinstance(value, list):
        for child in value:
            yield from state_refs(child)
    elif isinstance(value, dict):
        if 'action' in value and 'state' in value:
            yield value['state']
        else:
            for child in value.values():
                yield from state_refs(child)


def source_bindings(source, provenance, aligned):
    """Recover source identities before mapping; do not interpret predicates."""
    nodes = {n.get('id'): n for n in source.iter() if n.get('id')}
    bindings = {}
    for source_id, name in provenance.get('source_collection_bindings', {}).items():
        bindings[source_id] = 'objects/' + name.replace('-collection', '-object')
    for source_id, name in provenance.get('source_variable_bindings', {}).items():
        bindings[source_id] = 'variables/' + name
    for source_id, name in provenance.get('source_test_bindings', {}).items():
        bindings[source_id] = 'tests/' + name
        originals = [n.get('state_ref') for n in nodes[source_id] if n.get('state_ref')]
        generated = aligned['assessment']['tests'][name].get('states', [])
        if len(originals) != len(generated):
            raise ValueError('Source/converted Test State crosswalk mismatch')
        for original, generated_name in zip(originals, generated):
            prior = bindings.setdefault(original, 'states/' + generated_name)
            if prior != 'states/' + generated_name:
                raise ValueError('Conflicting State binding')
    for source_id, binding in list(bindings.items()):
        if not binding.startswith('objects/'):
            continue
        originals = [n.text.strip() for n in nodes[source_id].iter() if local(n.tag) == 'filter']
        generated = list(state_refs(aligned['assessment']['objects'][binding.split('/')[1]]))
        if len(originals) != len(generated):
            raise ValueError('Source/converted filter State crosswalk mismatch')
        for original, generated_name in zip(originals, generated):
            prior = bindings.setdefault(original, 'states/' + generated_name)
            if prior != 'states/' + generated_name:
                raise ValueError('Conflicting filter State binding')
    return bindings


def rename_graph(document, bindings, names):
    """Reference-only alpha-renaming using exact OVAL identity, not node order.

    This fixed six-case presentation plan does not change global converter
    name generation. Unrelated source content cannot allocate these names.
    """
    result = copy.deepcopy(document)
    assessment = result['assessment']
    remaps = {section: {} for section in ('objects', 'states', 'variables', 'tests')}
    for source_id, target in names.items():
        section, new_name = target.split('/')
        old_section, old_name = bindings[source_id].split('/')
        if section != old_section:
            raise ValueError('Identity plan cannot move nodes between kinds')
        remaps[section][old_name] = new_name
    reference_sections = dict(object='objects', state='states', variable='variables', test='tests')
    def references(value):
        if isinstance(value, list):
            return [references(child) for child in value]
        if not isinstance(value, dict):
            return value
        out = {}
        for key, child in value.items():
            if key in reference_sections and isinstance(child, str):
                out[key] = remaps[reference_sections[key]].get(child, child)
            elif key == 'states' and isinstance(child, list):
                out[key] = [remaps['states'].get(name, name) for name in child]
            else:
                out[key] = references(child)
        return out
    for section, mapping in remaps.items():
        current = assessment.get(section, {})
        if set(current) != set(mapping):
            raise ValueError(f'Unplanned or omitted native {section}: {set(current) ^ set(mapping)}')
        if len(set(mapping.values())) != len(mapping):
            raise ValueError('Native name collision')
        if current:
            assessment[section] = {mapping[name]: references(node) for name, node in sorted(current.items(), key=lambda pair:mapping[pair[0]])}
        else:
            assessment.pop(section, None)
    assessment['evaluate'] = references(assessment['evaluate'])
    # Source accounting is persisted in the established separate provenance.
    assessment.pop('provenance', None)
    return result


def execution_form(document):
    """Normalize only presentation metadata and two accepted Constant forms."""
    def normalize(value):
        if isinstance(value, list):
            return [normalize(child) for child in value]
        if not isinstance(value, dict):
            return value
        out = {key: normalize(child) for key, child in value.items() if key != 'title' and not key.endswith('_title')}
        if out.get('kind') == 'constant' and 'expression' in out:
            if set(out['expression']) != {'literal'}:
                raise ValueError('Native refinement cannot rewrite a computed expression')
            out['value'] = out.pop('expression')['literal']
        return out
    return normalize(document)


def convert_case(case, source=None):
    source_path = PACKAGE / case['source_extract']
    source = source if source is not None else ET.parse(source_path).getroot()
    provenance = {}
    intermediate, error = lower_definition(source, case['source_definition'], 'board.' + case['name'],
                                           collection_graph=True, provenance=provenance)
    if error:
        raise ValueError(f"{case['name']}: converter: {error}")
    with tempfile.TemporaryDirectory(prefix='board-roundtrip-') as temporary:
        tree, reverse_id = build(intermediate)
        reverse = Path(temporary) / 'source-roundtrip.xml'
        tree.write(reverse, encoding='utf-8')
        # Compare against this input, including stability-test permutations.
        actual_source = Path(temporary) / 'selected-source.xml'
        ET.ElementTree(source).write(actual_source, encoding='utf-8')
        parity = compare(actual_source, reverse, case['source_definition'], reverse_id, root_only=True)
        if not parity['equal']:
            raise ValueError(f"{case['name']}: intermediate semantic roundtrip: {parity}")
    aligned = align_assessment_vocabulary(intermediate)
    # This adapter reproduces the frozen 0.2.0 Board package even though the
    # shared current converter now targets 0.3.0. Make the historical target
    # explicit before applying the versioned 0.2 capability mappings.
    aligned["assessment"]["specification"]["version"] = "0.2.0"
    # 0.2.0 requires an explicit reporting selection on every Test. The
    # conversion preserves the complete source evidence surface.
    for test in aligned.get("assessment", {}).get("tests", {}).values():
        test["reported_elements"] = "all"
    bindings = source_bindings(source, provenance, aligned)
    mapped = apply_ready_capability_mappings(aligned, MAPPINGS)
    for capability in case['explicit_mapping_calls']:
        mapping = json.loads((MAPPINGS / (capability + '.json')).read_text(encoding='utf-8'))
        mapped = apply_capability_mapping(mapped, mapping)
    mechanical = rename_graph(mapped, bindings, case['native_bindings'])
    refined = copy.deepcopy(mechanical)
    assessment = refined['assessment']
    assessment['assessment_title'] = case['assessment_title']
    for section, prefix in (('objects', 'object'), ('states', 'state'), ('tests', 'test'), ('variables', 'variable')):
        for name, node in assessment.get(section, {}).items():
            node.pop('title', None)
            node[prefix + '_title'] = name.replace('-', ' ').capitalize()
            if node.get('kind') == 'constant':
                node['value'] = node.pop('expression')['literal']
    if execution_form(mechanical) != execution_form(refined):
        raise ValueError('Native refinement changed executable semantics')
    validator = build_validators(ROOT / 'schema/v0.2.0')['assessment.schema.json']
    for label, document in (('mechanical', mechanical), ('native', refined)):
        errors = [str(error) for error in document_errors(validator, document)]
        errors.extend(str(row) for row in validate_assessment_capability_semantics(document))
        errors.extend(str(row) for row in violations(document))
        if errors:
            raise ValueError(f"{case['name']} {label}: {errors}")
    return mechanical, refined


def dump(document):
    return yaml.safe_dump(document, sort_keys=False, allow_unicode=True)


def generated_files(case):
    mechanical, refined = convert_case(case)
    return {f"mechanical/{case['name']}.assessment.yaml": dump(mechanical),
            f"content/{case['name']}.assessment.yaml": dump(refined)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, help='Verify the full pinned Self-Assertion checkout against extracts')
    parser.add_argument('--output', type=Path, help='Write only the six mechanical/refined pairs to this directory')
    parser.add_argument('--check', action='store_true', help='Regenerate and compare committed outputs without writing')
    args = parser.parse_args()
    if not args.output and not args.check:
        parser.error('Choose --output or --check')
    plan = json.loads(PLAN.read_text(encoding='utf-8'))
    components = {**plan['converter_components'], **plan['mapping_components'],
                  'tools/convert_board_pilot_v02.py':plan['conversion_adapter_sha256']}
    baseline_changes = []
    for path, expected in components.items():
        # Code hashes normalize checkout line endings, not executable text.
        code_hash = hashlib.sha256((ROOT / path).read_text(encoding='utf-8').encode('utf-8')).hexdigest()
        if code_hash != expected:
            baseline_changes.append({"path": path, "expected": expected, "actual": code_hash})
    if baseline_changes:
        raise ValueError("Converter baseline components changed; review/re-pin the plan explicitly: " + json.dumps(baseline_changes, sort_keys=True))
    if args.source_root:
        verify_source(plan, args.source_root)
    for case in plan['cases']:
        for path, text in generated_files(case).items():
            if args.check and (PACKAGE / path).read_bytes() != text.encode('utf-8'):
                raise ValueError(f'Committed conversion differs: {path}')
            if args.output:
                destination = args.output / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(text, encoding='utf-8', newline='\n')
        print(f"{case['name']}: intermediate roundtrip + strict mechanical/native validation passed")
    print('Six cases; human review pending; no collectors or large corpus run.')


if __name__ == '__main__':
    main()
