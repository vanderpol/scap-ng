#!/usr/bin/env python3
"""Independent unsigned 0.4 package consumer; no compiler imports or execution.

Checks manifest bytes, external authoring identity, references and independently
walked program/source operands. Does not authenticate a publisher or scan a host.
Refs #251.
"""
import argparse
from collections import Counter
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import zipfile

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = {'id': 'scap-ng.pre-alpha.assessment', 'version': '0.4.0'}
KINDS = {'benchmark': 'benchmark', 'rule': 'rule', 'assessment': 'assessment',
         'applicability': 'applicability_catalog'}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(isinstance(key, str) and key not in result, 'duplicate/nonstring mapping key')
        result[key] = value
    return result


def read_json(raw):
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


class UniqueYaml(yaml.SafeLoader):
    pass


UniqueYaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: unique((loader.construct_object(k, deep=True),
                                loader.construct_object(v, deep=True)) for k, v in node.value))


def archive_members(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        require(len(names) == len(set(names)), 'duplicate archive member')
        for info in archive.infolist():
            p = PurePosixPath(info.filename)
            require(not p.is_absolute() and '..' not in p.parts and '\\' not in info.filename
                    and info.filename == p.as_posix() and not info.is_dir(), 'unsafe archive member')
            require(info.file_size <= 100_000_000 and not info.flag_bits & 1, 'unsupported member size/encryption')
        require(sum(i.file_size for i in archive.infolist()) <= 1_000_000_000, 'oversized archive')
        require(archive.testzip() is None, 'archive CRC mismatch')
        return {name: archive.read(name) for name in names}


def authoring(path):
    result = {}
    for name, raw in archive_members(path).items():
        if not name.startswith('authoring/') or not name.endswith(('.json', '.yaml')):
            continue
        doc = read_json(raw) if name.endswith('.json') else yaml.load(raw, Loader=UniqueYaml)
        require(isinstance(doc, dict) and len(doc) == 1, 'invalid source document')
        kind, body = next(iter(doc.items()))
        key = (kind, body['id'])
        require(key not in result, 'duplicate source identity')
        result[key] = (name, doc)
    require(result, 'empty authoring archive')
    return result


@lru_cache(maxsize=4)
def validators(schema_root):
    resources = {}
    for path in Path(schema_root).rglob('*.json'):
        schema = json.loads(path.read_text())
        if isinstance(schema, dict) and '$schema' in schema:
            uri = 'https://scap-ng.dev/schema/v0.4.0/' + path.relative_to(schema_root).as_posix()
            resources[uri] = Resource.from_contents(schema)
            if '$id' in schema:
                resources[schema['$id']] = Resource.from_contents(schema)
    registry = Registry().with_resources(resources.items())
    return {kind: Draft202012Validator(json.loads((Path(schema_root) / filename).read_text()), registry=registry)
            for kind, filename in {**{k: k + '.schema.json' for k in KINDS},
                                   'manifest': 'package-manifest.schema.json'}.items()}


def expression_plan(a):
    """Independent postorder translation, including exact source AST locations."""
    plan, tests, dependencies = [], set(), set()
    def visit(node, path, output=None):
        output = plan if output is None else output
        if isinstance(node, dict) and 'if' in node:
            require({'if', 'then', 'else'} <= set(node) and not set(node) - {'if', 'then', 'else', 'else_if'},
                    'conditional requires if/then/final else')
            alternatives = node.get('else_if', [])
            require(isinstance(alternatives, list) and ('else_if' not in node or alternatives), 'invalid ordered else_if')
            choices = [(node, path)] + [(choice, path + ['else_if', i]) for i, choice in enumerate(alternatives)]
            branches = []
            for i, (choice, at) in enumerate(choices):
                require(isinstance(choice, dict) and (i == 0 or set(choice) == {'if', 'then'}), 'invalid else_if entry')
                condition, selected = [], []
                visit(choice['if'], at + ['if'], condition)
                visit(choice['then'], at + ['then'], selected)
                branches.append({'condition': condition, 'then': selected, 'path': at})
            fallback = []
            visit(node['else'], path + ['else'], fallback)
            output.append({'op': 'select_first_true', 'branches': branches, 'else': fallback, 'path': path})
            return
        require(isinstance(node, dict) and len(node) == 1, 'unsupported result expression')
        op, value = next(iter(node.items()))
        if op in ('test', 'assessment'):
            table = a.get('tests', {}) if op == 'test' else a.get('dependencies', {})
            require(value in table, 'unresolved expression reference')
            (tests if op == 'test' else dependencies).add(value)
            output.append({'op': 'read_' + op, 'id': value, 'path': path})
        elif op in ('and', 'or', 'one', 'xor'):
            require(isinstance(value, list) and value, 'empty expression')
            encoded = {'and': 'all', 'or': 'any', 'xor': 'odd'}.get(op, op)
            for i, child in enumerate(value):
                visit(child, path + [encoded, i], output)
            output.append({'op': encoded, 'count': len(value), 'path': path})
        elif op == 'not':
            visit(value, path + ['not'], output)
            output.append({'op': 'not', 'path': path})
        elif op in ('not_applicable', 'not_evaluated'):
            require(isinstance(value, dict) and set(value) == {'reason'} and isinstance(value['reason'], str)
                    and value['reason'].strip(), 'invalid reason-bearing terminal')
            output.append({'op': op, 'reason': value['reason'], 'path': path})
        else:
            raise ValueError('unsupported result operator: ' + op)
    visit(a['evaluate'], ['evaluate'])
    return plan, {'tests': sorted(tests), 'dependencies': sorted(dependencies)}


def references(a, assessments):
    objects, variables = a.get('shared_objects', {}), a.get('variables', {})
    for dependency in a.get('dependencies', {}).values():
        target = dependency if isinstance(dependency, str) else dependency.get('assessment')
        require(target in assessments, 'unresolved Assessment dependency')
    edges = {}
    def walk(node, owner):
        if isinstance(node, list):
            for child in node:
                walk(child, owner)
        elif isinstance(node, dict):
            for key, value in node.items():
                if key in ('object', 'variable') and isinstance(value, str):
                    require(value in (objects if key == 'object' else variables), 'unresolved ' + key)
                    edges.setdefault(owner, set()).add((key, value))
                if key == 'for_each':
                    require(isinstance(value, dict) and value.get('in') in objects, 'unresolved for_each Object')
                    edges.setdefault(owner, set()).add(('object', value['in']))
                walk(value, owner)
    for category, table in (('object', objects), ('variable', variables), ('test', a.get('tests', {}))):
        for ident, definition in table.items():
            if category == 'test' and isinstance(definition.get('object'), str):
                obj = objects.get(definition['object'], {})
                require(obj.get('capability') == definition.get('capability'), 'Object capability mismatch')
            walk(definition, (category, ident))
    visiting, visited = set(), set()
    def check(node):
        require(node not in visiting, 'cyclic Object/Variable graph')
        if node not in visited:
            visiting.add(node)
            for child in edges.get(node, ()):
                check(child)
            visiting.remove(node)
            visited.add(node)
    for node in edges:
        check(node)
    return len(objects), len(variables)


def verify(path, *, source=None, schema_root=None):
    members = archive_members(path)
    manifest = read_json(members['META-INF/manifest.json'])
    require(canonical(manifest) == members['META-INF/manifest.json'], 'noncanonical manifest')
    require(manifest['format'] == 'scap-ng-package-manifest' and manifest['format_version'] == '0.4.0',
            'unsupported package version')
    validation = validators(str(schema_root or ROOT / 'schema/v0.4.0'))
    validation['manifest'].validate(manifest)
    prov = manifest['build_provenance']
    require(prov['stage'] == 'compiled-native-0.4.0-program-not-scanner-validated/0.1', 'unsupported stage')
    require(prov['scanner_evaluation_verified'] is False and prov['publisher_signature_verified'] is False
            and all(v is None for v in manifest['signature'].values()), 'unsupported trust/runtime claim')
    require(manifest['integrity'] == {'algorithm': 'sha-256', 'unexpected_members': 'reject'}, 'integrity policy')
    declared = ['META-INF/manifest.json'] + [r['path'] for r in manifest['objects'].values()] + [
        r['path'] for r in prov['compiled_programs'].values()]
    require(len(declared) == len(set(declared)) and set(declared) == set(members), 'unlisted/missing archive member')
    expected, docs, automations, types = {'META-INF/manifest.json'}, {}, {}, Counter()
    def member(info):
        name = info['path']
        require(name not in expected and name in members, 'missing/duplicate manifest path')
        expected.add(name)
        raw = members[name]
        require(len(raw) == info['size'] and sha256(raw).hexdigest() == info['sha256'], 'member hash/size mismatch')
        value = read_json(raw)
        require(canonical(value) == raw, 'noncanonical content')
        return value
    for ident, info in manifest['objects'].items():
        doc = member(info)
        require(isinstance(doc, dict) and len(doc) == 1, 'invalid package document')
        kind, body = next(iter(doc.items()))
        require(KINDS.get(kind) == info['type'] and body['id'] == ident
                and body.get('version') == info['version'], 'document identity/version mismatch')
        docs[(kind, ident)] = doc
        types[kind] += 1
        if kind == 'assessment' and body.get('mode') == 'automated':
            require(body['specification'] == SPEC, 'unsupported Assessment version')
            automations[ident] = body
    require(types['benchmark'] == 1, 'expected exactly one Benchmark')
    benchmark = next(d['benchmark'] for d in docs.values() if 'benchmark' in d)
    require(manifest['entrypoint'] == manifest['benchmark_id'] == benchmark['id']
            and benchmark.get('version') == manifest['benchmark_version'], 'Benchmark entrypoint mismatch')
    require(benchmark['assessment_specifications'] == [SPEC], 'unsupported Benchmark schema version')
    require(set(benchmark['rules']) == {k[1] for k in docs if k[0] == 'rule'}
            and len(benchmark['rules']) == types['rule'], 'Benchmark Rule inventory mismatch')
    assessments = {key[1] for key in docs if key[0] == 'assessment'}
    if benchmark.get('applicability_catalog'):
        require(('applicability', benchmark['applicability_catalog']) in docs, 'unresolved applicability catalog')
    conditions = {name for d in docs.values() if 'applicability' in d
                  for name in d['applicability']['conditions']}
    policy_ids = set(benchmark['rules']) | {g['id'] for g in benchmark.get('groups', []) if isinstance(g, dict)}
    links = 0
    for doc in docs.values():
        if 'rule' in doc:
            rule = doc['rule']
            choices = rule['assessment_choices']
            require(rule['default_assessment_choice'] in choices, 'unresolved default choice')
            for condition in rule.get('applicability', []):
                require(isinstance(condition, str) and condition in conditions, 'unresolved Rule applicability')
            clauses = [c if isinstance(c, str) else v for c in rule.get('requires', [])
                       for v in ([c] if isinstance(c, str) else c['any_of'])]
            require(set(clauses + rule.get('conflicts', [])) <= policy_ids, 'unresolved policy Rule/Group')
            for choice in choices.values():
                require(choice['assessment'] in assessments, 'unresolved Rule Assessment')
                links += 1
        if 'applicability' in doc:
            for condition in doc['applicability']['conditions'].values():
                require(condition['assessment'] in assessments, 'unresolved applicability Assessment')
    graph = [{'kind': k[0], 'id': k[1], 'sha256': digest(docs[k])} for k in sorted(docs)]
    require(digest(graph) == prov['source_graph_sha256'] and len(docs) == prov['source_documents']
            and links == prov['rule_choice_links'], 'graph inventory/digest mismatch')
    if source is not None:
        own = next(name.split('/')[1] for (_, ident), (name, doc) in source.items()
                   if ident == benchmark['id'] and 'benchmark' in doc)
        selected = {key: doc for key, (name, doc) in source.items() if name.split('/')[1] in (own, 'shared')}
        require(selected == docs, 'external authoring/package graph mismatch')
    require(set(prov['compiled_programs']) == set(automations), 'program inventory mismatch')
    totals = Counter()
    for ident, a in automations.items():
        obj_count, var_count = references(a, assessments)
        program = member(prov['compiled_programs'][ident])
        require(set(program) == {'format', 'assessment_id', 'assessment_source_sha256',
                'test_instructions', 'result_instructions', 'result_requires',
                'result_expression_sha256', 'scanner_evaluated'}, 'unsupported program fields')
        require(program['format'] == 'scap-ng-0.4.0-native-assessment-program/0.1'
                and program['assessment_id'] == ident and program['scanner_evaluated'] is False
                and program['assessment_source_sha256'] == digest(a), 'program source identity mismatch')
        actual_tests = program['test_instructions']
        require([x['test_id'] for x in actual_tests] == sorted(a['tests']), 'Test program inventory mismatch')
        for instruction in actual_tests:
            test = a['tests'][instruction['test_id']]
            opcode = 'CHECK_COLLECTION_PRESENCE' if set(test['require']) == {'items_found'} else 'CHECK_ITEM_CONDITION'
            require(instruction == {'test_id': instruction['test_id'], 'opcode': opcode,
                'capability': test['capability'], 'source_test_sha256': digest(test), 'operands': test},
                'compiled Test operand mismatch')
        plan, required = expression_plan(a)
        require(program['result_instructions'] == plan and program['result_requires'] == required
                and program['result_expression_sha256'] == digest(a['evaluate']), 'result program/source mismatch')
        totals.update(tests=len(actual_tests), shared_objects=obj_count, variables=var_count)
    require(expected == set(members), 'unlisted archive member')
    for (kind, _), doc in docs.items():
        validation[kind].validate(doc)
    return {'status': 'INDEPENDENT_PACKAGE_CONSUMER_PASS', 'benchmark': benchmark['id'],
            'bundle_sha256': sha256(Path(path).read_bytes()).hexdigest(), 'documents': len(docs),
            'programs': len(automations), **totals, 'source_graph_sha256': digest(graph),
            'external_source_compared': source is not None, 'scanner_evaluated': False,
            'publisher_trust_verified': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--source-json', type=Path)
    parser.add_argument('--source-yaml', type=Path)
    parser.add_argument('--schema-root', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    sources = authoring(args.source_json) if args.source_json else None
    if args.source_yaml:
        other = authoring(args.source_yaml)
        require(sources is not None and {k: d for k, (_, d) in sources.items()} ==
                {k: d for k, (_, d) in other.items()}, 'external YAML/JSON mismatch')
    result = verify(args.bundle, source=sources, schema_root=args.schema_root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
