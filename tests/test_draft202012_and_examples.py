"""Resolve all frozen references locally and validate curated 0.4 examples."""
from hashlib import sha256
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
import yaml

from test_schema_integrity import ROOT, PREFIX, load, refs, frozen_paths


PROJECT = ROOT.parent
EXAMPLES = {
    'windows-server-2025-lock-screen.assessment.yaml':
        '8501a018cd98fe1d041e2fd0a4438da3bc4cb031a9087506fcbf1d538bb33b2b',
    'windows-server-2025-sysvol-permissions.assessment.yaml':
        '3fdb03b50b2506cbaf99bd300e0667f5056bd93be7e3e5f0cd3aee68515acba4',
    'linux-home-nosuid.assessment.yaml':
        '52b5e412f5b3c473e9a974d9d7ce9494e6d6afe10a9ae32e8c59db429ee8ebe6',
    'windows-optional-organizational-input.assessment.yaml':
        'c2056c9cc3d594cf78ac8fbc3bb1e2e03e880f74da1477d5e435cb0a00bc2b76',
}


class UniqueYaml(yaml.SafeLoader):
    pass


def unique_mapping(loader, node):
    result = {}
    for key, value in node.value:
        name = loader.construct_object(key, deep=True)
        if not isinstance(name, (str, int, float, bool)) or name in result:
            raise ValueError('duplicate or unsupported YAML mapping key')
        result[name] = loader.construct_object(value, deep=True)
    return result


UniqueYaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def schema_registry():
    resources = {}
    for path in frozen_paths():
        doc = load(path)
        if '$schema' not in doc:
            continue
        resource = Resource.from_contents(doc)
        resources[PREFIX + path.relative_to(ROOT).as_posix()] = resource
        if '$id' in doc:
            resources[doc['$id']] = resource
    return Registry().with_resources(resources.items())


class Draft202012AndExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = schema_registry()

    def test_root_schemas_pass_meta_validation_and_local_refs_resolve(self):
        for path in sorted(ROOT.glob('*.schema.json')):
            with self.subTest(schema=path.name):
                doc = load(path)
                Draft202012Validator.check_schema(doc)
                resolver = self.registry.resolver(base_uri=doc['$id'])
                for ref in refs(doc):
                    resolver.lookup(ref)  # Fails if missing or invalid JSON pointer.

    def test_curated_examples_are_current_and_structurally_valid(self):
        schema = load(ROOT / 'assessment.schema.json')
        language = load(ROOT / 'assessment-language.schema.json')
        self.assertEqual(
            list(language['$defs']['canonical_all_items_requirement']['properties'])[:3],
            ['item_requirement', 'field_requirement', 'fields'],
            'schema declaration order should reflect the editor presentation order')
        validator = Draft202012Validator(schema, registry=self.registry)
        self.assertEqual(len(list((PROJECT / 'examples').glob('*.yaml'))), len(EXAMPLES))
        for name, expected_hash in EXAMPLES.items():
            with self.subTest(example=name):
                raw = (PROJECT / 'examples' / name).read_bytes()
                self.assertEqual(sha256(raw).hexdigest(), expected_hash)
                self.assertIn(b'item_requirement: {', raw)
                self.assertIn(b'field_requirement: {', raw)
                if name == 'windows-server-2025-lock-screen.assessment.yaml':
                    self.assertIn(b'fields: {type: {equals: dword}, value: {equals: 1}}', raw)
                if name == 'linux-home-nosuid.assessment.yaml':
                    self.assertIn(b'fields: {mount_options: {equals: nosuid}}', raw)
                document = yaml.load(raw, Loader=UniqueYaml)
                validator.validate(document)
                body = document['assessment']
                self.assertNotIn('purpose', body)
                self.assertEqual(body['specification']['version'], '0.4.0')
                for test in body['tests'].values():
                    requirement = test['require']
                    self.assertNotIn('items_found', requirement)
                    self.assertNotIn('items_satisfying', requirement)
                    self.assertEqual(set(requirement['item_requirement']),
                                     {'items_found', 'items_satisfying'})
                    self.assertEqual(list(requirement)[:3],
                                     ['item_requirement', 'field_requirement', 'fields'],
                                     'current examples must display Item, Field requirements before predicates')


if __name__ == '__main__':
    unittest.main()

