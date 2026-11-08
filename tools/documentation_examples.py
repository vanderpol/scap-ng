"""Load version-pinned teaching fixtures; validate syntax, never evaluate Tests."""
from hashlib import sha256
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
import yaml


class UniqueYaml(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key, value in node.value:
        name = loader.construct_object(key, deep=True)
        if not isinstance(name, str) or name in result:
            raise ValueError('Duplicate or non-string example mapping key')
        result[name] = loader.construct_object(value, deep=True)
    return result


UniqueYaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def yaml_text(value):
    return yaml.safe_dump(value, sort_keys=False, default_flow_style=None, width=100).rstrip()


class Examples:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.inputs = {}
        self.routes = []
        self.documents = {}
        resources = []
        for path in sorted((self.root / 'schema').rglob('*.json')):
            doc = json.loads(path.read_text())
            if '$schema' in doc and '$id' in doc:
                self.documents[doc['$id']] = doc
                resources.append((doc['$id'], Resource.from_contents(doc)))
        self.registry = Registry().with_resources(resources)

    def read(self, ref):
        path = (self.root / ref['path']).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError('Example path escapes repository')
        raw = path.read_bytes()
        digest = sha256(raw).hexdigest()
        if digest != ref['sha256']:
            raise ValueError('Stale example source: ' + ref['path'])
        self.inputs[ref['path']] = digest
        return raw

    def validate(self, name, instance):
        uri = 'https://scap-ng.dev/schema/v0.4.0/' + name + '.schema.json'
        Draft202012Validator(self.documents[uri], registry=self.registry).validate(instance)

    def load(self, doc):
        annotation = doc.get('x-doc-examples')
        if not annotation:
            return []
        pin = json.loads(self.read(annotation['pin']))
        if pin['version'] != '0.4.0' or pin['namespace'] != 'https://scap-ng.dev/schema/v0.4.0/':
            raise ValueError('Unsupported example schema pin')
        digest = sha256()
        for path in sorted((self.root / 'schema').rglob('*.json')):
            digest.update(path.relative_to(self.root / 'schema').as_posix().encode() + b'\0' + path.read_bytes())
        if digest.hexdigest() != pin['frozen_family_sha256']:
            raise ValueError('Example schema family differs from immutable pin')
        cap = doc['x-doc-capability']
        cases = []
        for ref in annotation['cases']:
            case = yaml.load(self.read(ref), Loader=UniqueYaml)
            if case['capability'] != cap or case['schema_pin'] != annotation['pin']['path']:
                raise ValueError('Wrong capability or schema pin association')
            self.validate('assessment', {'assessment': case['assessment']})
            self.validate('collection-result', case['collection_result'])
            for item in case['collected_items']:
                self.validate('collected-item', item)
                if item['capability'] != cap:
                    raise ValueError('Wrong Item capability')
                for name, value in item['fields'].items():
                    meaning = doc['$defs']['meanings']['properties'].get(name)
                    if meaning is None:
                        raise ValueError('Unknown example Item field: ' + name)
                    if value['datatype'] not in meaning.get('x-doc-datatypes', []):
                        raise ValueError('Example datatype differs from declared field meaning')
                    # Qualification of these primitive teaching fixtures only;
                    # this does not narrow the frozen typed-value grammar.
                    primitive = {'integer': int, 'string': str, 'boolean': bool}.get(value['datatype'])
                    if value['status'] != 'exists' or primitive is None or type(value.get('value')) is not primitive:
                        raise ValueError('Example needs an explicit existing primitive field value')
            tests = case['assessment']['tests']
            if len(tests) != 1 or next(iter(tests.values()))['capability'] != cap:
                raise ValueError('Example must bind exactly one Test to its capability')
            if case['assessment']['specification']['version'] != pin['version']:
                raise ValueError('Assessment version differs from pin')
            collection = case['collection_result']
            ids = [i['id'] for i in case['collected_items']]
            if collection['capability'] != cap or ids != collection['item_refs'] or len(ids) != len(set(ids)):
                raise ValueError('Unlinked or duplicate collected Items')
            if collection['status'] != 'complete' or any(i['status'] != 'exists' for i in case['collected_items']):
                raise ValueError('Initial pairs require explicit successful collections')
            # These fixtures carry expectations, not manufactured evaluator observations.
            expected = case['expected']
            if {'Pass': 'true', 'Fail': 'false'}.get(expected['label']) != expected['technical_outcome']:
                raise ValueError('Teaching policy label differs from technical expectation')
            if case['verification'] != {'status': 'illustrative-unverified', 'native_evaluator': None}:
                raise ValueError('Native evaluation proof requires a separately reviewed receipt')
            cases.append((ref, case))
            self.routes.append({'capability': cap, 'id': case['id'], **ref,
                                'schema_pin': annotation['pin'], 'expected': expected,
                                'verification': case['verification']})
        ids = [c['id'] for _, c in cases]
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate example identity')
        return cases


def render(cases):
    if not cases:
        return ''
    text = '## Examples\n\n'
    text += '**Illustrative expected outcomes; native evaluation unverified.** Syntax validation is reported separately from evaluation. '
    text += 'For these compliance teaching cases only, technical `true` is labelled Pass and `false` Fail; a consuming Rule defines policy outcomes. '
    text += 'Items are explicit synthetic evidence, not observations from a scanned host.\n\n'
    # Reuse authoring across a pair; every linked canonical fixture remains complete.
    shared = all(c['assessment'] == cases[0][1]['assessment'] for _, c in cases)
    if shared:
        assessment = cases[0][1]['assessment']
        text += 'Both cases use this native Test (inline Object and Require):\n\n```yaml\n'
        text += yaml_text({'tests': assessment['tests'], 'evaluate': assessment['evaluate']}) + '\n```\n\n'
    for ref, case in cases:
        label = case['expected']['label']
        text += '### ' + label + ' — expected `' + case['expected']['technical_outcome'] + '` (unverified)\n\n'
        text += case['explanation'] + '\n\n'
        if not shared:
            text += '```yaml\n' + yaml_text({'tests': case['assessment']['tests'], 'evaluate': case['assessment']['evaluate']}) + '\n```\n\n'
        text += '```yaml\n' + yaml_text({'collection_result': case['collection_result'], 'collected_items': case['collected_items']}) + '\n```\n\n'
        text += '[Complete version-pinned fixture](../../../' + ref['path'] + ').\n\n'
    return text
