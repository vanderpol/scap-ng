"""Shared local JSON Schema inspection for generated references and audits.

No schema semantics are inferred from filenames or capability metadata. The
caller may pass a pinned SchemaStore or a repository path; schema URIs resolve
locally and never cause a network request.
"""
from functools import lru_cache
import json
from pathlib import Path
from urllib.parse import urljoin, urldefrag, unquote

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]


class SchemaStore:
    def __init__(self, documents):
        self.documents = documents
        self.registry = Registry().with_resources(
            (uri, Resource.from_contents(doc)) for uri, doc in documents.items())

    def node(self, uri):
        base, fragment = urldefrag(uri)
        if base not in self.documents:
            raise ValueError('Outside pinned local schema pack: ' + uri)
        return pointer(self.documents[base], unquote(fragment))


@lru_cache(maxsize=8)
def _store(snapshot):
    documents = {}
    for name, _mtime, _size in snapshot:
        doc = json.loads(Path(name).read_text())
        if '$schema' in doc and '$id' in doc:
            if doc['$id'] in documents:
                raise ValueError('Duplicate schema identity: ' + doc['$id'])
            documents[doc['$id']] = doc
    return SchemaStore(documents)


def store(root):
    if isinstance(root, SchemaStore):
        return root
    paths = sorted(set((root / 'schema').rglob('*.json')) | set((root / 'docs').rglob('*.schema.json')))
    return _store(tuple((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in paths))


def schema_node(root, uri):
    return store(root).node(uri)


def registry(root):
    return store(root).registry


def pointer(document, path):
    for token in path.lstrip('/').split('/') if path else []:
        token = token.replace('~1', '/').replace('~0', '~')
        document = document[int(token)] if isinstance(document, list) else document[token]
    return document


def code(value):
    return '`' + str(value) + '`'


def absolute(node, uri):
    if isinstance(node, dict):
        return {k: urljoin(uri, v) if k == '$ref' else absolute(v, uri) for k, v in node.items()}
    if isinstance(node, list):
        return [absolute(v, uri) for v in node]
    return node


def parts(node, uri, root=ROOT, context=None, seen=()):
    """Read schema applicators in context; never rewrite the validation schema.

    Unknown conditionals/alternatives remain visible to bound queries. Recursive
    child references are not expanded unless the caller asks for that child.
    """
    if not isinstance(node, dict):
        raise ValueError('Unsupported boolean schema in this inspection context')
    node = absolute(node, uri)
    if '$ref' in node:
        target = node['$ref']
        if target in seen:
            raise ValueError('Recursive schema inspection requires a child boundary: ' + target)
        yield from parts(schema_node(root, target), target, root, context, seen + (target,))
    for child in node.get('allOf', []):
        yield from parts(child, uri, root, context, seen)
    own = {k: v for k, v in node.items() if k not in {'$ref', 'allOf'}}
    if context is not None:
        if 'if' in own:
            valid = Draft202012Validator(own['if'], registry=registry(root)).is_valid(context)
            yield from parts(own.get('then' if valid else 'else', {}), uri, root, context, seen)
            own = {k: v for k, v in own.items() if k not in {'if', 'then', 'else'}}
        for key in ['oneOf', 'anyOf']:
            if key in own:
                choices = [n for n in own[key] if Draft202012Validator(n, registry=registry(root)).is_valid(context)]
                if not choices or (key == 'oneOf' and len(choices) != 1):
                    raise ValueError('Context does not select a valid ' + key + ' branch')
                for choice in choices:
                    yield from parts(choice, uri, root, context, seen)
                own = {k: v for k, v in own.items() if k != key}
    yield own


def bounds(minimum, maximum):
    if maximum is not None and minimum > maximum:
        return 'unspecified (unsatisfiable)'
    return str(minimum) + '..' + ('n' if maximum is None else str(maximum))


def affects(node, name):
    if not isinstance(node, dict):
        return False
    if name in node.get('required', []) or name in node.get('properties', {}):
        return True
    if any(k in node for k in ['minProperties', 'maxProperties', 'additionalProperties', '$ref']):
        return True
    return any(affects(v, name) for v in node.values() if isinstance(v, dict)) or any(
        affects(v, name) for k in ['allOf', 'oneOf', 'anyOf'] for v in node.get(k, []))


def property_occurrences(node, uri, name, root=ROOT, context=None):
    """Count one JSON property/map key, never its inner array values."""
    nodes = list(parts(node, uri, root, context))
    required = set().union(*(set(p.get('required', [])) for p in nodes))
    allowed, closed = set(), []
    minimum, maximum = 0, 1
    for p in nodes:
        if any(k in p for k in ['dependentRequired', 'dependentSchemas']):
            return 'unspecified (dependent constraints)'
        if 'propertyNames' in p and not Draft202012Validator(p['propertyNames'], registry=registry(root)).is_valid(name):
            maximum = 0
        required.update(p.get('required', []))
        allowed.update(p.get('properties', {}))
        if p.get('additionalProperties') is False and not p.get('patternProperties'):
            closed.append(set(p.get('properties', {})))
        if p.get('maxProperties') == 0 or p.get('not') == {'required': [name]}:
            maximum = 0
        if name not in required and 'if' in p and any(affects(p.get(k, {}), name) for k in ['then', 'else']):
            return 'conditional'
        for choice in ['oneOf', 'anyOf']:
            if choice in p:
                other = {k: v for k, v in p.items() if k != choice}
                variants = {property_occurrences({'allOf': [other, branch]}, uri, name, root) for branch in p[choice]}
                if len(variants) > 1:
                    if name in required:
                        continue
                    return 'conditional'
                if variants:
                    # A branch-local required property must not be lost.
                    only = variants.pop()
                    if only == '1..1':
                        minimum = 1
                    elif only == '0..0' and name not in required:
                        maximum = 0
                    elif only != '0..1':
                        return only
    if name in required:
        minimum = 1
    if closed:
        finite = set.intersection(*closed)
        if name not in finite:
            maximum = 0
        min_properties = max([len(required)] + [p.get('minProperties', 0) for p in nodes])
        if name in finite and min_properties > len(finite - {name}):
            minimum = 1
    return bounds(minimum, maximum)


def collection_occurrences(node, uri, kind, root=ROOT, context=None):
    """Array entries or total map entries; named keys are queried separately."""
    low_key, high_key = ('minItems', 'maxItems') if kind == 'array' else ('minProperties', 'maxProperties')
    nodes = list(parts(node, uri, root, context))
    if any('if' in p or 'oneOf' in p or 'anyOf' in p or 'contains' in p or 'dependentRequired' in p or 'dependentSchemas' in p for p in nodes):
        return 'unspecified (conditional)'
    minimum = max([0] + [p.get(low_key, 0) for p in nodes])
    maxima = [p[high_key] for p in nodes if high_key in p]
    if kind == 'array':
        maxima += [len(p.get('prefixItems', [])) for p in nodes if p.get('items') is False]
    if kind == 'map':
        minimum = max(minimum, len(set().union(*(set(p.get('required', [])) for p in nodes))))
        maxima += [len(p.get('properties', {})) for p in nodes if p.get('additionalProperties') is False and not p.get('patternProperties')]
    return bounds(minimum, min(maxima) if maxima else None)


def types(node, uri, root=ROOT):
    nodes = list(parts(node, uri, root))
    explicit = []
    for p in nodes:
        if 'type' in p:
            explicit.extend(p['type'] if isinstance(p['type'], list) else [p['type']])
        for value in ([p['const']] if 'const' in p else p.get('enum', [])):
            explicit.append('null' if value is None else 'boolean' if isinstance(value, bool) else 'integer' if isinstance(value, int) else 'number' if isinstance(value, float) else 'object' if isinstance(value, dict) else 'array' if isinstance(value, list) else 'string')
    if explicit:
        return ' or '.join(dict.fromkeys(explicit))
    choices = [types(branch, uri, root) for p in nodes for key in ['oneOf', 'anyOf'] for branch in p.get(key, [])]
    return ' or '.join(dict.fromkeys(choices)) or 'unspecified'


def display_type(node, uri, root=ROOT):
    base = types(node, uri, root)
    if base == 'object':
        tag = []
        for p in parts(node, uri, root):
            if 'datatype' in p.get('properties', {}):
                for value in parts(p['properties']['datatype'], uri, root):
                    if 'const' in value:
                        tag.append(str(value['const']))
        if tag:
            return '/'.join(dict.fromkeys(tag)) + ' selector'
    for p in parts(node, uri, root):
        for key in ['oneOf', 'anyOf']:
            if key in p:
                return ' or '.join(dict.fromkeys(display_type(n, uri, root) for n in p[key]))
    return base


def options(node, uri, root=ROOT):
    """Only short vocabulary and authoring hints belong beside basic meanings."""
    values, suggestions, enums = [], [], []
    for p in parts(node, uri, root):
        if 'enum' in p:
            enums.append(p['enum'])
        for choice in ['oneOf', 'anyOf']:
            for branch in p.get(choice, []):
                if 'const' in branch:
                    values.append(code(branch['const']))
                elif branch.get('type') == 'integer' and 'minimum' in branch:
                    values.append('integer ≥ ' + str(branch['minimum']))
        if 'default' in p:
            policy = p.get('x-scap-ng-authoring', {})
            label = 'Editor suggestion' if policy.get('new_authoring_only') else 'Schema default annotation'
            suggestions.append(label + ': ' + code(p['default']) + '.')
    if enums:
        values = [code(v) for v in enums[0] if all(v in enum for enum in enums)] + values
    return ' '.join(([', '.join(dict.fromkeys(values)) + '.'] if values else []) + list(dict.fromkeys(suggestions)))


def description_lookup(root, uri, seen=()):
    """Offline lookup at an explicit schema node, following local-pack $refs.

    Returns the exact annotation pointer, never a parent/alternative's prose.
    This is source lookup, not instance-to-caret routing or a VS Code UI model.
    """
    if uri in seen:
        raise ValueError('Cyclic description reference: ' + uri)
    node = schema_node(root, uri)
    if not isinstance(node, dict):
        raise ValueError('Missing description at schema node: ' + uri)
    if 'description' in node:
        if not isinstance(node['description'], str) or not node['description'].strip():
            raise ValueError('Missing description at schema node: ' + uri)
        base, fragment = urldefrag(uri)
        return {'description': node['description'], 'description_pointer': base + '#' + fragment + '/description',
                'lookup_chain': list(seen) + [uri]}
    if '$ref' in node:
        return description_lookup(root, urljoin(uri, node['$ref']), seen + (uri,))
    raise ValueError('Missing description at schema node: ' + uri)
