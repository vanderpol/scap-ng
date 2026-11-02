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
        '1a0033280fdfc8defe57104b37268af90860b4b81ce28685f8db5445e7aedca6',
    'windows-server-2025-sysvol-permissions.assessment.yaml':
        '174c93d5e86c0a9478c66507efd1db8deec588cd65c35582738c075d5a563d3c',
    'linux-home-nosuid.assessment.yaml':
        '6a6519e7c7b30ebede613ac3703eb0e3bf1e0cbe3c8add1e816a68c6d7bc102b',
    'windows-optional-organizational-input.assessment.yaml':
        'f3e645b95a7897093364e847abdd6728d68ae8105ce44db19f16ebb0fd0dcb54',
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


if __name__ == '__main__':
    unittest.main()

