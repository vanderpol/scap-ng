"""Strict native YAML I/O, presentation-only plans and logical edge extraction."""
from hashlib import sha256
from pathlib import Path
import re

import yaml

from v04_a_authoring_graph_index import canonical_json
from verify_v04_package_consumer import UniqueYaml
from v04_direct_yaml import authoring_yaml

KINDS = frozenset({'benchmark', 'rule', 'assessment', 'applicability'})
MAX_BYTES = 5_000_000


def digest(value):
    return sha256(canonical_json(value)).hexdigest()


def parse(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('native document exceeds 5 MB budget')
    try:
        doc = yaml.load(raw, Loader=UniqueYaml)
    except yaml.YAMLError as error:
        problem = ValueError('invalid YAML: '+str(error))
        problem.problem_mark = getattr(error,'problem_mark',None)
        raise problem from error
    # Bound alias expansion and reject recursive aliases before canonicalization.
    stack, count = [(doc, frozenset(), 0)], 0
    while stack:
        value, parents, depth = stack.pop()
        count += 1
        if count > 500_000 or depth > 128:
            raise ValueError('native node/depth budget exceeded')
        if isinstance(value, (dict, list)):
            if id(value) in parents:
                raise ValueError('recursive YAML alias')
            lineage = parents | {id(value)}
            stack.extend((v, lineage, depth + 1) for v in
                         (value.values() if isinstance(value, dict) else value))
    canonical_json(doc)  # Reject non-JSON scalars and NaN/Infinity.
    if not isinstance(doc, dict) or len(doc) != 1:
        raise ValueError('expected exactly one native document root')
    kind, body = next(iter(doc.items()))
    if kind not in KINDS or not isinstance(body, dict):
        raise ValueError('unsupported native kind; Profiles remain embedded in Benchmarks')
    if not isinstance(body.get('id'), str) or not body['id']:
        raise ValueError('missing native logical ID')
    return doc


def read(root, relative):
    path = root / relative
    if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root.parent):
        raise ValueError('symlink authoring paths are not eligible')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('authoring path escapes library')
    return path.read_bytes()


def title(body):
    value = body.get('assessment_title', body.get('title', body.get('id', '')))
    if isinstance(value, list):
        value = next((v.get('text', '') for v in value if isinstance(v, dict)), '')
    return str(value)


def slug(value, maximum=48):
    words = re.findall('[a-z0-9]+', value.lower())
    return ('-'.join(words)[:maximum].rstrip('-') or 'native-content')


def filename(kind, body):
    ident = body['id']
    words = re.findall('[a-z0-9]+', ident.lower())
    stop = {'the', 'must', 'be', 'configured', 'to', 'that', 'is', 'are', 'a', 'an',
            'with', 'have', 'has', 'all', 'on', 'for', 'of', 'assessment', 'rule'}
    useful = [w for w in words if w not in stop and not re.fullmatch('[a-f0-9]{8,}', w)]
    shortened = '-'.join(useful[:6])[:48].rstrip('-') or slug(title(body))
    # Truncation/reduction can lose native disambiguation; retain injectivity.
    if shortened != ident:
        shortened += '-' + sha256((kind+'\0'+ident).encode()).hexdigest()[:8]
    if shortened.lower() in {'con','prn','aux','nul',*(f'com{i}' for i in range(10)),*(f'lpt{i}' for i in range(10))}:
        shortened = 'native-' + shortened
    return shortened + '.yaml'


def scope_for(relative):
    parts = Path(relative).parts
    # Human-readable v2 libraries use authoring/<short-stig>/... as their
    # authoring root. Physical layout identifies the private namespace; YAML
    # references still resolve by exact kind, logical ID and version.
    if len(parts) >= 3 and parts[:2] == ('shared', 'assessments'):
        if len(parts) < 4 or parts[2] not in ('automated', 'manual'):
            raise ValueError('shared Assessments require an explicit method directory')
        return 'shared'
    if parts and parts[0] == 'standalone':
        return 'standalone'
    if len(parts) >= 2 and parts[0] not in ('benchmarks', 'applicability', 'rules', 'assessments'):
        if parts[1] in ('benchmark.yaml', 'applicability.yaml'):
            return parts[0]
        if len(parts) >= 3 and parts[1] == 'rules':
            return parts[0]
        if len(parts) >= 4 and parts[1:3] in (('assessments', 'automated'), ('assessments', 'manual')):
            return parts[0]
    if parts[0] in ('benchmarks', 'applicability') and len(parts) == 2:
        return Path(parts[1]).stem
    if parts[0] == 'rules' and len(parts) >= 3:
        return parts[1]
    if parts[:2] == ('assessments', 'local') and len(parts) >= 4:
        return parts[2]
    if parts[:2] == ('assessments', 'shared'):
        if len(parts) < 4 or parts[2] != 'global':
            raise ValueError('only existing global shared visibility is supported')
        return 'shared'
    return 'standalone'


def edges(doc):
    """Yield typed ID links; no relative-path or newest-version fallback."""
    kind, body = next(iter(doc.items()))
    result = []
    def segment(value):return str(value).replace('~','~0').replace('/','~1')
    def add(target_kind, ident, field, version=None, purpose=None):
        result.append({'kind': target_kind, 'id': ident, 'field': field,
                       'version': version, 'purpose': purpose})
    if kind == 'benchmark':
        for n, ident in enumerate(body.get('rules') or []):
            add('rule', ident, f'/benchmark/rules/{n}')
        if body.get('applicability_catalog'):
            add('applicability', body['applicability_catalog'], '/benchmark/applicability_catalog')
        for n, profile in enumerate(body.get('profiles') or []):
            for j, ident in enumerate(profile.get('disabled_rules') or []):
                add('rule', ident, f'/benchmark/profiles/{n}/disabled_rules/{j}')
    if kind == 'rule':
        choices = body.get('assessment_choices') or {}
        if body.get('default_assessment_choice') not in choices:
            raise ValueError('undeclared Rule default choice')
        for label, choice in choices.items():
            add('assessment', choice.get('assessment'), '/rule/assessment_choices/'+segment(label),
                choice.get('expected_version'))
    if kind == 'applicability':
        for label, condition in (body.get('conditions') or {}).items():
            add('assessment', condition.get('assessment'), '/applicability/conditions/'+segment(label),
                condition.get('expected_version'), 'applicability')
    if kind == 'assessment':
        for label, dep in (body.get('dependencies') or {}).items():
            ident = dep.get('assessment')
            if dep.get('expected_id', ident) != ident:
                raise ValueError('dependency expected_id differs from logical target')
            add('assessment', ident, '/assessment/dependencies/'+segment(label),
                dep.get('expected_version'), dep.get('purpose'))
    for edge in result:
        if not isinstance(edge['id'], str) or not edge['id'] or any(s in edge['id'] for s in ('/', '\\')):
            raise ValueError('reference must name one exact logical ID, not a source path')
    return result


def version(body):
    value = body.get('version')
    return value.get('value') if isinstance(value, dict) else value


def validate(doc):
    from v04_canonical_source_ir import validate_docs
    from v04_canonical_unsigned_package import _package_validators
    validate_docs({'native.yaml': doc}, _package_validators())
    kind, body = next(iter(doc.items()))
    if kind=='assessment':
        stack=[body]
        while stack:
            value=stack.pop()
            if isinstance(value,dict):
                if isinstance(value.get('input'),str) and value['input'] not in (body.get('inputs') or {}):
                    raise ValueError('unresolved declared Assessment Input: '+value['input'])
                stack.extend(value.values())
            elif isinstance(value,list):stack.extend(value)
    if kind == 'assessment' and body.get('mode') == 'automated':
        from v04_native_bundle_compiler import compile_assessment_program
        return digest(compile_assessment_program(body))
    return None


def canonical_yaml(doc):
    raw = authoring_yaml(doc).encode('utf-8')
    if parse(raw) != doc:
        raise ValueError('presentation round-trip changed native content')
    return raw
