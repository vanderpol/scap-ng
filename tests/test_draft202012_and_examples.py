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
        '957cdba19b9b6be80497734121659c31e3269db1ce24218119f65aa9afe771e1',
    'windows-server-2025-sysvol-permissions.assessment.yaml':
        'd8b3fd97fb9c5b5d83be712a081a97a62a013d3db2439b3d1528a73a1d4df5e8',
    'linux-home-nosuid.assessment.yaml':
        'b88d34d2ed41a7b5abcbdedb4a4c44a5b3ad2291a8ae0cbb66b316f783e48cf8',
    'windows-optional-organizational-input.assessment.yaml':
        '8f19d25fe07d881b1dc816a0b48ee431df05f9b58e85a1e59f5fd601393bda34',
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
        validator = Draft202012Validator(schema, registry=self.registry)
        self.assertEqual(len(list((PROJECT / 'examples').glob('*.yaml'))), len(EXAMPLES))
        for name, expected_hash in EXAMPLES.items():
            with self.subTest(example=name):
                raw = (PROJECT / 'examples' / name).read_bytes()
                self.assertEqual(sha256(raw).hexdigest(), expected_hash)
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


if __name__ == '__main__':
    unittest.main()

