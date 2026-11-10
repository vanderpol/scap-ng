#!/usr/bin/env python3
"""Generate the proposed schema-derived reference and exact-context editor help.

The committed JSON Schemas are the only description source. This renderer does
not import OVAL, capability mappings, editorial worksheets or Markdown prose.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import urldefrag, urljoin

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('proposed-schema/documentation')
DEST = Path('docs/reference')
QUALIFICATION = ('unix.file', 'windows.registry', 'independent.shellcommand',
                 'windows.file', 'windows.service', 'linux.rpminfo',
                 'linux.partition', 'independent.textfilecontent',
                 'linux.systemdunitproperty', 'windows.wmi.query')


def encode(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + '\n'


def escape(value):
    return str(value).replace('~', '~0').replace('/', '~1')


def pointer(doc, path):
    for token in path.lstrip('/').split('/') if path else []:
        token = token.replace('~1', '/').replace('~0', '~')
        doc = doc[int(token)] if isinstance(doc, list) else doc[token]
    return doc


def schemas(root=ROOT):
    docs = {}
    for path in sorted((root / SOURCE).rglob('*.schema.json')):
        doc = json.loads(path.read_text())
        uri = doc['$id']
        if uri in docs:
            raise ValueError('Duplicate schema identity: ' + uri)
        docs[uri] = (doc, path.relative_to(root))
    return docs


def location(uri):
    base, fragment = urldefrag(uri)
    return base + "#" + fragment


def node(docs, uri):
    base, frag = urldefrag(uri)
    return pointer(docs[base][0], frag)


def resolve(docs, uri, seen=()):
    """Exact annotation owner, never a parent or unrelated alternative."""
    uri = location(uri)
    if uri in seen:
        return None, None
    value = node(docs, uri)
    if isinstance(value, dict):
        if value.get('description'):
            return value['description'], uri
        if 'x-doc-description-ref' in value:
            return resolve(docs, urljoin(uri, value['x-doc-description-ref']), seen + (uri,))
        if '$ref' in value:
            return resolve(docs, urljoin(uri, value['$ref']), seen + (uri,))
    return None, None


def documentation_scope(docs, uri):
    """Inherit availability metadata, never a description or validation rule."""
    base, fragment = urldefrag(uri)
    while True:
        value = node(docs, base+'#'+fragment)
        if isinstance(value,dict) and isinstance(value.get('x-doc-scope'),str):
            return value['x-doc-scope']
        if not fragment:
            return 'declared-schema'
        fragment = fragment.rsplit('/',1)[0]


def walk(value, uri):
    """Actual schema nodes only; custom annotations are data, not subschemas."""
    if not isinstance(value, dict):
        return
    yield uri, value
    for key in ('properties', '$defs', 'patternProperties', 'dependentSchemas'):
        for name, child in value.get(key, {}).items():
            yield from walk(child, uri + '/' + key + '/' + escape(name))
    for key in ('items', 'contains', 'additionalProperties', 'unevaluatedProperties',
                'propertyNames', 'not', 'if', 'then', 'else'):
        if isinstance(value.get(key), dict):
            yield from walk(value[key], uri + '/' + key)
    for key in ('oneOf', 'anyOf', 'allOf', 'prefixItems'):
        for i, child in enumerate(value.get(key, [])):
            yield from walk(child, uri + '/' + key + '/' + str(i))


def components(docs, uri, seen=()):
    """Unconditional composition; alternatives stay advanced constraints."""
    uri = location(uri)
    if uri in seen:
        return
    value = node(docs, uri)
    if not isinstance(value, dict):
        return
    yield uri, value
    if '$ref' in value:
        yield from components(docs, urljoin(uri, value['$ref']), seen + (uri,))
    for i, _ in enumerate(value.get('allOf', [])):
        yield from components(docs, uri + '/allOf/' + str(i), seen + (uri,))


def properties(docs, uri):
    found = {}
    value = node(docs, uri)
    # Inline Object fields come from the validation schema, with annotations
    # overriding only their presentation. New schema fields need no renderer edit.
    if isinstance(value, dict) and value.get('x-doc-role') == 'Object' and 'x-doc-validation-ref' in value:
        validation = value['x-doc-validation-ref']
        if validation != uri:
            found.update(properties(docs, validation))
    for owner, part in components(docs, uri):
        for name, value in part.get('properties', {}).items():
            # A local description/shape is more useful than an empty overlay.
            target = owner + '/properties/' + escape(name)
            if name not in found or owner == location(uri) or value.get('description') or value.get('type'):
                found[name] = target
    return found


def shape(docs, uri, seen=()):
    uri = location(uri)
    if uri in seen:
        return set(), set()
    value = node(docs, uri)
    if not isinstance(value, dict):
        return set(), set()
    types = value.get('type', [])
    types = {types} if isinstance(types, str) else set(types)
    values = {json.dumps(x, ensure_ascii=False) for x in value.get('enum', [])}
    if 'const' in value:
        values.add(json.dumps(value['const'], ensure_ascii=False))
    for literal in value.get('enum', []) + ([value['const']] if 'const' in value else []):
        types.add('null' if literal is None else 'boolean' if isinstance(literal, bool)
                  else 'integer' if isinstance(literal, int) else 'number' if isinstance(literal, float) else 'string')
    if '$ref' in value:
        t, e = shape(docs, urljoin(uri, value['$ref']), seen + (uri,))
        types |= t; values |= e
    for key in ('allOf', 'oneOf', 'anyOf'):
        for i, _ in enumerate(value.get(key, [])):
            t, e = shape(docs, uri + '/' + key + '/' + str(i), seen + (uri,))
            types |= t; values |= e
    return types, values


def forms(docs, uri, seen=()):
    """Preserve alternative object forms without flattening their required keys."""
    uri = location(uri)
    if uri in seen:
        return
    if properties(docs, uri):
        yield uri
        return
    for owner, part in components(docs, uri):
        for key in ('oneOf', 'anyOf'):
            if key in part:
                for i, _ in enumerate(part[key]):
                    yield from forms(docs, owner+'/'+key+'/'+str(i), seen+(uri,))
                return
    yield uri


def cardinality(docs, parent, name):
    """Named YAML keys occur at most once; arrays have separate item bounds."""
    required, conditional = False, False
    for _, part in components(docs, parent):
        required |= name in part.get('required', [])
        for key in ('oneOf', 'anyOf', 'then', 'else'):
            children = part.get(key, [])
            if isinstance(children, dict):
                children = [children]
            conditional |= any(name in c.get('required', []) for c in children if isinstance(c, dict))
    return '1..1 (required)' if required else 'Conditional (at most 1)' if conditional else '0..1'


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def link(root, path, uri):
    base, fragment = urldefrag(uri)
    target = root[base][1]
    # Pages are one directory below docs/reference (capabilities or shared).
    return f'[{cell(fragment or "schema")}](' + '../../../' + target.as_posix() + '#' + fragment + ')'


def row(docs, parent, name, uri, description=None, validation=None, definition=False, value_datatypes=None):
    value = node(docs, uri)
    validation = validation or value.get('x-doc-validation-ref', uri)
    t, _ = shape(docs, validation)
    desc, owner = resolve(docs, uri)
    desc = description if description is not None else desc
    # One sentence/paragraph in basic tables; the exact full annotation stays accessible.
    brief = re.split(r'(?<=[.!?])\s+(?=[A-Z`])', desc.split('\n\n')[0])[0] if desc else '**Unresolved description**'
    named = 'Definition' if definition else cardinality(docs, parent, name)
    if value.get('x-doc-availability'):
        brief = '**Not accepted in this inline form.** ' + brief
        t = {'not accepted'}
    elif value_datatypes:
        t = set(value_datatypes) if len(value_datatypes)<=4 else {str(len(value_datatypes))+' declared types; see details'}
    if value.get('x-doc-review', {}).get('status') == 'semantic-hold':
        brief = '**Semantic hold.** Existing wording requires a native contract decision; see details.'
    elif value.get('x-doc-review', {}).get('status') == 'withheld':
        brief = '**Withheld.** Retained schema definition; not approved for native authoring.'
    return f'| `{cell(name)}` | {cell(", ".join(sorted(t)) or "See schema")} | {named} | {cell(brief)} | {link(docs, None, uri)} |'


TABLE = '| Field | Schema type | Occurrences | Description | Details |\n| --- | --- | --- | --- | --- |\n'
CAP_TABLE = TABLE.replace('Schema type','Value datatype')


def check_links(docs):
    for base, (doc, _) in docs.items():
        for uri, value in walk(doc, base + '#'):
            for key in ('$ref', 'x-doc-validation-ref', 'x-doc-description-ref'):
                if key in value:
                    target = urljoin(uri, value[key])
                    try:
                        node(docs, target)
                    except (KeyError, IndexError, TypeError) as e:
                        raise ValueError('Broken schema link at ' + uri + ': ' + target) from e
                    target_doc = docs[urldefrag(target)[0]][0]
                    if 'x-doc-capability' in doc and 'x-doc-capability' in target_doc:
                        if doc['x-doc-capability'] != target_doc['x-doc-capability']:
                            raise ValueError('Incorrect capability field association: ' + uri)
            for role, target in value.get('x-doc-roles', {}).items():
                node(docs, urljoin(base, target))
            for cap, target in value.get('x-doc-capability-schemas', {}).items():
                if node(docs, target).get('x-doc-capability') != cap:
                    raise ValueError('Incorrect capability association: ' + cap)


def advanced_page(docs, base, doc):
    text = '# ' + doc.get('title', 'Schema') + ' — advanced constraints\n\n'
    text += 'Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.\n\n'
    text += '| Pointer | Local constraints | Documentation status |\n| --- | --- | --- |\n'
    keys = ('type', 'enum', 'const', 'default', 'required', 'minItems', 'maxItems',
            'minProperties', 'maxProperties', 'minimum', 'maximum', 'minLength',
            'maxLength', 'pattern', 'additionalProperties', 'unevaluatedProperties')
    for uri, value in walk(doc, base + '#'):
        constraints = {k:v for k,v in value.items() if k in keys and not isinstance(v, dict)}
        if 'x-doc-validation-ref' in value:
            t,e=shape(docs,value['x-doc-validation-ref'])
            constraints['validation_reference']=value['x-doc-validation-ref']
            constraints['type_alternatives']=sorted(t)
            if e:
                constraints['literal_alternatives_in_referenced_shape']=[json.loads(x) for x in sorted(e)]
        if value.get('x-doc-declared-shape'):
            constraints['declaration_only']=value['x-doc-declared-shape']
        if value.get('x-doc-values'):
            constraints['declared_values_not_new_validation_restrictions']=value['x-doc-values']
        if constraints or value.get('x-doc-review') or value.get('x-doc-status'):
            status = value.get('x-doc-review', {}).get('status', value.get('x-doc-status', 'existing-native'))
            text += '| ' + link(docs, None, uri) + ' | ' + cell(json.dumps(constraints, ensure_ascii=False)) + ' | ' + status + ' |\n'
            if value.get('x-doc-review'):
                text += '\n' + link(docs,None,uri) + ': ' + value.get('description','No description approved.') + '\n\n'
                text += value['x-doc-review'].get('note','Editorial receipt: '+value['x-doc-review']['source']+' case '+value['x-doc-review']['case']) + '\n\n'
                text += '| Pointer | Local constraints | Documentation status |\n| --- | --- | --- |\n'
            elif '\n\n' in value.get('description',''):
                text += '\n'+link(docs,None,uri)+': '+value['description']+'\n\n'
                text += '| Pointer | Local constraints | Documentation status |\n| --- | --- | --- |\n'
    return text


def generate(root=ROOT):
    docs = schemas(root)
    check_links(docs)
    outputs, metadata, gaps, coverage, duplicates = {}, [], [], [], []
    schema_routes, shared_coverage = [], []
    texts = defaultdict(list)
    for base, (doc, _) in docs.items():
        for uri, value in walk(doc, base + '#'):
            if value.get('x-doc-review', {}).get('status') in ('semantic-hold','withheld'):
                gaps.append({'schema_pointer':uri, 'reason':value['x-doc-review']['status'],
                             'existing_wording':value.get('description'), 'engineering_note':value['x-doc-review'].get('note'),
                             'proposed_wording':None, 'status':'Original editorial decision preserved; no new behavior approved.'})
            description, owner = resolve(docs, uri)
            if description:
                schema_routes.append({'schema_pointer': uri, 'description_pointer': owner + '/description',
                                      'scope':documentation_scope(docs,uri),
                                      'status': node(docs, owner).get('x-doc-review', {}).get('status', node(docs, owner).get('x-doc-status', 'existing-native'))})
            if value.get('description'):
                texts[value['description']].append(uri)
                metadata.append({'schema_pointer': uri, 'description_pointer': uri + '/description',
                                 'description': value['description'],
                                 'scope':documentation_scope(docs,uri),
                                 'status': value.get('x-doc-review', {}).get('status', value.get('x-doc-status', 'existing-native'))})
    for text, owners in sorted(texts.items()):
        if len(owners) > 1:
            duplicates.append({'description': text, 'owners': owners, 'disposition': 'Review context before sharing; identical wording alone does not prove identical semantics.'})
    routes = []
    for base, (doc, path) in sorted(docs.items()):
        if 'x-doc-capability' not in doc:
            continue
        cap = doc['x-doc-capability']
        page = f'# {cap}\n\nProposed documentation; frozen 0.4.0 validation is unchanged.\n\n'
        if doc.get('description'):
            page += doc['description']+'\n\n'
        page += '**Contract status: unresolved.** ' + doc['x-doc-contract']['note'] + '\n\n'
        page += 'Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. '
        page += 'Value datatypes are declarations; [advanced constraints](../advanced/'+cap+'.md) retain the validated encodings and any broader schema acceptance.\n\n'
        caprows = []
        for role, target in doc['x-doc-roles'].items():
            start = urljoin(base, target)
            page += '## ' + role + '\n\n'
            role_description, _ = resolve(docs,start)
            if role_description:
                page += role_description+'\n\n'
            if role == 'Require':
                page += 'Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). '
                page += 'Capability-specific comparison-domain declarations, where different, are listed below.\n\n'
                overrides=[]
                for name, child in properties(docs,start+'/properties/fields').items():
                    value=node(docs,child)
                    if value.get('x-doc-comparison-datatypes') and value['x-doc-comparison-datatypes']!=value.get('x-doc-datatypes'):
                        overrides.append((name,child,value['x-doc-comparison-datatypes']))
                if overrides:
                    page += CAP_TABLE
                    for name,child,domains in overrides:
                        page += row(docs,start+'/properties/fields',name,child,value_datatypes=domains)+'\n'
                    page += '\n'
            parent = start
            if role in ('Item', 'Require'):
                parent += '/properties/fields'
            groups = [(parent, None, None)]
            seen = set()
            while groups:
                current, title, inherited_status = groups.pop(0)
                if current in seen:
                    continue
                seen.add(current)
                if title:
                    page += '### ' + title + '\n\n'
                    if inherited_status == 'semantic-hold':
                        page += '**Semantic hold inherited from the parent field; these children do not make the parent accepted.**\n\n'
                if role != 'Require':
                    page += CAP_TABLE
                for name, target_uri in properties(docs, current).items():
                    value = node(docs, target_uri)
                    text, owner = resolve(docs, target_uri)
                    actual = node(docs, owner) if owner else value
                    status = value.get('x-doc-status', actual.get('x-doc-status', 'existing-native' if text else 'unresolved'))
                    if inherited_status == 'semantic-hold':
                        status = inherited_status
                    validation = value.get('x-doc-validation-ref')
                    if role == 'Item':
                        validation = urljoin(base, '../collected-item.schema.json#/properties/fields/additionalProperties')
                    if role == 'Require':
                        validation = urljoin(base, '../assessment-language.schema.json#/$defs/canonical_field_predicate')
                    display = 'Shared Item field meaning.' if role == 'Require' and text else None
                    domains=value.get('x-doc-datatypes',actual.get('x-doc-datatypes',[]))
                    declared=value.get('x-doc-declared-shape',{}).get('type')
                    if not domains and declared:domains=[declared]
                    if role != 'Require':
                        page += row(docs, current, name, target_uri, display, validation,value_datatypes=domains) + '\n'
                    route = {'capability': cap, 'role': role, 'path': (title.split('.') if title else []) + [name],
                             'schema_pointer': target_uri, 'description_pointer': owner + '/description' if owner else None,
                             'description': text, 'status': status, 'mapping_key_occurrence': cardinality(docs, current, name),
                             'validation_pointer': validation or value.get('x-doc-validation-ref'),
                             'declared_datatypes': domains,
                             'comparison_datatypes': actual.get('x-doc-comparison-datatypes', []),
                             'declared_collection_shape': value.get('x-doc-declared-shape')}
                    routes.append(route); caprows.append(route)
                    if not text:
                        gaps.append({'capability': cap, 'role': role, 'schema_pointer': target_uri,
                                     'reason': 'missing description', 'proposed_wording': actual.get('x-doc-gap-proposal', f'Meaning of {name.replace("_", " ")} requires source review.'), 'status': 'unresolved; proposal is not authoritative'})
                    if value.get('x-doc-availability'):
                        gaps.append({'capability': cap, 'role': role, 'schema_pointer': target_uri,
                                     'reason': 'mapping/schema discrepancy', 'proposed_wording': value['x-doc-availability'], 'status': 'semantic hold'})
                    expand = all(part.get('x-doc-expand',True) for _,part in components(docs,target_uri))
                    if expand and properties(docs, target_uri) and name not in ('set', 'filters'):
                        groups.append((target_uri, name if not title else title + '.' + name, status))
                page += '\n'
            # Advanced schema constraints are kept out of basic description columns.
            page += 'Validation shape: ' + link(docs, None, node(docs, start)['x-doc-validation-ref']) + '.\n\n'
        page += '## Advanced constraints and evidence\n\n'
        page += '[Local schema constraints](../advanced/' + cap + '.md) retain allowed literals, defaults and bounds outside the basic field tables.\n\n'
        page += '| Role / field | Declared datatype or collection shape | Annotation status |\n| --- | --- | --- |\n'
        for r in caprows:
            if r['role'] == 'Require':
                continue
            declared = ', '.join(r['declared_datatypes'])
            if r['declared_collection_shape']:
                declared = json.dumps(r['declared_collection_shape'], sort_keys=True)
            # Routine scalar domains are already prominent in the basic table.
            # Keep only parameter declarations and broad domains here.
            if declared and (r['declared_collection_shape'] or len(r['declared_datatypes'])>4):
                page += f'| {r["role"]}.`{".".join(r["path"])}` | {cell(declared)} | {r["status"]} |\n'
        page += '\n'
        page += 'See the [schema](../../../' + path.as_posix() + ') for exact description owners, native datatype declarations and collection-parameter declarations. '
        page += 'Declarations are documentation annotations; they add no datatype or required-field restriction. '
        page += 'Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.\n\n'
        src = doc['x-doc-source']
        page += f'Historical source: {src["language"]}, commit `{src["oval_commit"]}`, `{src["oval_schema"]}`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **{src["scope"]}**.\n'
        outputs[DEST / 'capabilities' / (cap + '.md')] = page
        outputs[DEST / 'advanced' / (cap + '.md')] = advanced_page(docs, base, doc)
        missing = sum(not r['description'] for r in caprows)
        source_derived = sum(r['status'] == 'source-derived' for r in caprows)
        coverage.append({'capability': cap, 'fields_discovered': len(caprows), 'fields_documented': len(caprows)-missing,
                         'missing_descriptions': missing, 'source_derived_fields': source_derived,
                         'unresolved_fields': sum(r['status'] in ('unresolved', 'semantic-hold') for r in caprows),
                         'unresolved_contracts': 1, 'coverage_status': 'complete-field-descriptions' if missing == 0 else 'partial-field-descriptions',
                         'runtime_contract_status': 'unresolved', 'generated_pages': 1})
        gaps.append({'capability': cap, 'schema_pointer': base + '#/x-doc-contract', 'reason': 'unresolved native collection/evaluation contract',
                     'proposed_wording': doc['x-doc-contract']['note'], 'status': 'semantic hold; no runtime claim'})
    # Shared/core pages preserve schema hierarchy, references and exact pointers.
    for base, (doc, path) in sorted(docs.items()):
        if 'x-doc-capability' in doc:
            continue
        libraries = [u for u,v in walk(doc,base+'#') if v.get('x-doc-scope')=='description-library']
        page = '# ' + doc.get('title', path.stem) + '\n\n'
        discovered = documented = basic_discovered = basic_documented = 0
        page += 'Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. '
        page += 'Conditional requirements and alternatives remain linked in the schema.\n\n'
        text, _ = resolve(docs, base + '#')
        if text:
            page += text.split('\n\n')[0] + '\n\n'
        for uri, value in walk(doc, base + '#'):
            if any(uri==u or uri.startswith(u+'/') for u in libraries):
                continue
            if not ('properties' in value or '$defs' in value):
                continue
            fragment = urldefrag(uri)[1]
            # Keep conditional/alternative constraint copies out of the main tables.
            # They remain in the complete inventory and advanced reference.
            basic = not re.search(r'/(?:allOf|if|then|else|not)(?:/|$)', fragment)
            if re.search(r'/(?:anyOf|oneOf)/', fragment):
                basic &= bool(re.fullmatch(r'/(?:\$defs/[^/]+/)?(?:anyOf|oneOf)/[0-9]+(?:/properties/[^/]+|/items)*', fragment))
            if basic:
                page += '## `' + (fragment or '/') + '`\n\n' + TABLE
            for key in ('properties', '$defs'):
                for name, child in value.get(key, {}).items():
                    if child.get('x-doc-scope')=='description-library':
                        continue
                    target = uri + '/' + key + '/' + escape(name)
                    if basic:
                        page += row(docs, uri, name, target, definition=key == '$defs') + '\n'
                    description, owner = resolve(docs, target)
                    discovered += 1
                    documented += bool(description)
                    basic_discovered += bool(basic)
                    basic_documented += bool(basic and description)
                    if not description:
                        gaps.append({'schema_pointer': target, 'reason': 'missing shared description',
                                     'scope':documentation_scope(docs,target),
                                     'proposed_wording': child.get('x-doc-gap-proposal'), 'status': 'No safe wording established for this exact context; research required.'})
            if basic:
                page += '\n'
        page += '## Advanced constraints\n\n[Local constraints](../advanced/' + path.name.removesuffix('.schema.json') + '.md) and [complete JSON Schema](../../../' + path.as_posix() + ') contain conditional requirements, alternatives, bounds and validation expressions. '
        page += 'A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. '
        page += 'A definition is reusable schema grammar, not itself an authored mapping key.\n'
        outputs[DEST / 'shared' / (path.name.removesuffix('.schema.json') + '.md')] = page
        outputs[DEST / 'advanced' / (path.name.removesuffix('.schema.json') + '.md')] = advanced_page(docs, base, doc)
        shared_coverage.append({'schema':base, 'fields_discovered':discovered, 'fields_documented':documented,
                                'missing_descriptions':discovered-documented, 'basic_fields_discovered':basic_discovered,
                                'basic_fields_documented':basic_documented, 'generated_pages':2})
    totals = {'capabilities': len(coverage), 'fully_field_documented': sum(c['missing_descriptions'] == 0 for c in coverage),
              'partial_capabilities': sum(c['missing_descriptions'] > 0 for c in coverage),
              'fields_discovered': sum(c['fields_discovered'] for c in coverage),
              'fields_documented': sum(c['fields_documented'] for c in coverage),
              'missing_capability_descriptions': sum(c['missing_descriptions'] for c in coverage),
              'unresolved_native_contracts': sum(c['unresolved_contracts'] for c in coverage),
              'shared_description_gaps': sum(g['reason'] == 'missing shared description' for g in gaps),
              'capability_pages': len(coverage), 'shared_pages': sum('x-doc-capability' not in d for d, _ in docs.values()),
              'advanced_pages': len(docs),
              'description_owners': len(metadata), 'duplicate_text_groups': len(duplicates),
              'capability_unique_description_owners':len({r['description_pointer'] for r in routes if r['description_pointer']}),
              'preserved_semantic_holds':sum(g['reason']=='semantic-hold' for g in gaps),
              'preserved_withheld_definitions':sum(g['reason']=='withheld' for g in gaps)}
    totals['shared_fields_discovered'] = sum(c['fields_discovered'] for c in shared_coverage)
    totals['shared_fields_documented'] = sum(c['fields_documented'] for c in shared_coverage)
    totals['shared_basic_fields_discovered'] = sum(c['basic_fields_discovered'] for c in shared_coverage)
    totals['shared_basic_fields_documented'] = sum(c['basic_fields_documented'] for c in shared_coverage)
    outputs[DEST / 'coverage.json'] = encode({'totals': totals, 'capabilities': coverage, 'shared_schemas':shared_coverage,
        'shared_gap_scopes':dict(sorted(Counter(g['scope'] for g in gaps if g['reason']=='missing shared description').items()))})
    outputs[DEST / 'gaps.jsonl'] = ''.join(json.dumps(g, sort_keys=True, ensure_ascii=False) + '\n' for g in gaps)
    outputs[DEST / 'duplicate-descriptions.json'] = encode(duplicates)
    outputs[DEST / 'editor-help.json'] = encode({'format': 'schema-documentation-help-1', 'descriptions': metadata, 'schema_routes': schema_routes, 'routes': routes,
        'policy': 'Exact capability/role/path only. No generic parent fallback. Missing or stale packs must not produce authoritative help.'})
    outputs[DEST / 'qualification.json'] = encode({'initial_ten': list(QUALIFICATION), 'initial_ten_present': all(c in {x['capability'] for x in coverage} for c in QUALIFICATION),
        'all_capabilities_processed': len(coverage), 'checks': ['local references resolve', 'exact capability associations', 'one mapping key per named field', 'nested properties retain parent', 'shared description owners resolve'],
        'runtime_equivalence': 'not tested or claimed'})
    index = '# Proposed SCAP-NG reference\n\nGenerated from proposed JSON Schemas; 0.4.0 remains frozen. Field-description coverage does not establish complete scanner contracts.\n\n'
    index += 'Field-route totals count Object, Item and Require contexts, including reused meanings. Unique description owners are reported separately. Shared gaps count exact named-schema nodes, including repeated conditional constraints; they are not a count of distinct missing language features.\n\n'
    index += '| Measure | Count |\n| --- | ---: |\n' + ''.join(f'| {k.replace("_", " ")} | {v} |\n' for k,v in totals.items()) + '\n'
    platforms = defaultdict(list)
    for c in coverage:
        platforms[c['capability'].split('.')[0]].append(c)
    for platform, caps in sorted(platforms.items()):
        index += '## [' + platform + '](platforms/' + platform + '.md)\n\n' + ''.join(f'- [{c["capability"]}](capabilities/{c["capability"]}.md): {c["fields_documented"]}/{c["fields_discovered"]} field routes; native contract unresolved.\n' for c in caps) + '\n'
        guide = '# ' + platform + ' capability reference\n\nProposed schema-derived documentation for this capability family. Collection and evaluation contracts remain subject to the status shown on each page.\n\n'
        guide += '| Capability | Documented field routes | Missing descriptions |\n| --- | ---: | ---: |\n'
        guide += ''.join(f'| [{c["capability"]}](../capabilities/{c["capability"]}.md) | {c["fields_documented"]}/{c["fields_discovered"]} | {c["missing_descriptions"]} |\n' for c in caps)
        guide += '\nShared language: [Require and comparisons](../shared/assessment-language.md), [Variables and retained functions](../shared/variable-expression.md), [collection grammar](../shared/capability-common.md), [result values](../shared/result-types.md).\n'
        outputs[DEST / 'platforms' / (platform + '.md')] = guide
    index += '## Shared grammar\n\n' + ''.join(f'- [{path.stem}](shared/{path.name.removesuffix(".schema.json")}.md)\n' for _, (doc,path) in sorted(docs.items()) if 'x-doc-capability' not in doc)
    outputs[DEST / 'README.md'] = index
    # Versioned offline transport integrity. Source schemas, generated pages and metadata are bound together.
    files = {str(p): sha256(v.encode()).hexdigest() for p,v in sorted(outputs.items())}
    inputs = {str(p): sha256((root / p).read_bytes()).hexdigest() for _, p in docs.values()}
    outputs[DEST / 'manifest.json'] = encode({'format': 'scap-ng-proposed-documentation-1', 'review_only': True,
                                             'provenance_sha256': sha256((root / SOURCE / 'provenance.json').read_bytes()).hexdigest(),
                                             'coverage_debt_sha256': sha256((root / SOURCE / 'coverage-debt.json').read_bytes()).hexdigest() if (root / SOURCE / 'coverage-debt.json').exists() else None,
                                             'schemas': dict(sorted(inputs.items())), 'generated': files})
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = generate()
    debt_file = ROOT / SOURCE / 'coverage-debt.json'
    allowed = set(json.loads(debt_file.read_text())['missing_description_pointers'])
    missing = {r['schema_pointer'] for line in outputs[DEST / 'gaps.jsonl'].splitlines()
               if (r := json.loads(line))['reason'] in ('missing description', 'missing shared description')}
    if missing - allowed:
        raise SystemExit('New documentation gaps require descriptions: ' + ', '.join(sorted(missing - allowed)))
    stale = [str(p) for p, text in outputs.items() if not (ROOT / p).exists() or (ROOT / p).read_text() != text]
    existing = set(p.relative_to(ROOT) for p in (ROOT / DEST).rglob('*') if p.is_file())
    extra = existing - set(outputs)
    if args.check:
        if stale or extra:
            raise SystemExit('Stale documentation: ' + ', '.join(stale + sorted(map(str,extra))))
    else:
        for p in extra:
            (ROOT / p).unlink()
        for path, text in outputs.items():
            (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / path).write_text(text)
    coverage = json.loads(outputs[DEST / 'coverage.json'])
    print(encode(coverage['totals']).strip())


if __name__ == '__main__':
    main()
