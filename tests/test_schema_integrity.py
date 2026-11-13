"""Active 0.4.1 schema-family byte and reference integrity, without network."""
from hashlib import sha256
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / 'schema'
PREFIX = 'https://scap-ng.dev/schema/v0.4.1/'
EXPECTED_JSON = 145
EXPECTED_SCHEMAS = 35
EXPECTED_REFS = 680
# Owner-approved pre-release 0.4 amendment; prior freeze digest remains in
# docs/PROVENANCE.md and the previous immutable Git commit.
EXPECTED_DIGEST = '578315d1e00bd39449ed597ed3d39555384276bd36198a54ca0b1e3c17e72829'


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_bytes(), object_pairs_hook=strict_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError('nonfinite JSON number: ' + value)))


def refs(value):
    if isinstance(value, list):
        for item in value:
            yield from refs(item)
    elif isinstance(value, dict):
        if '$ref' in value:
            yield value['$ref']
        for item in value.values():
            yield from refs(item)


def frozen_digest(paths):
    checksum = sha256()
    for path in sorted(paths):
        checksum.update(path.relative_to(ROOT).as_posix().encode('utf-8') + b'\0')
        checksum.update(path.read_bytes())
    return checksum.hexdigest()


def frozen_paths():
    """Only the flat release-owned schema tree, not stray local work files."""
    return sorted((*ROOT.glob('*.json'),
                   *(ROOT / 'capability-mappings').rglob('*.json')))


class FrozenSchemaIntegrity(unittest.TestCase):
    def test_family_has_exact_frozen_json_bytes(self):
        paths = frozen_paths()
        self.assertEqual(len(paths), EXPECTED_JSON)
        self.assertEqual(frozen_digest(paths), EXPECTED_DIGEST)

    def test_root_schemas_parse_and_have_unique_draft_ids(self):
        roots = sorted(ROOT.glob('*.schema.json'))
        self.assertEqual(len(roots), EXPECTED_SCHEMAS)
        identifiers = set()
        for path in roots:
            with self.subTest(schema=path.name):
                document = load(path)
                self.assertEqual(document['$schema'],
                                 'https://json-schema.org/draft/2020-12/schema')
                self.assertEqual(document['$id'], PREFIX + path.name)
                self.assertEqual(document['x-scap-ng-version'], '0.4.1')
                self.assertNotIn(document['$id'], identifiers)
                identifiers.add(document['$id'])

    def test_all_json_documents_parse_and_refs_count_is_frozen(self):
        for path in frozen_paths():
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertIsInstance(load(path), dict)
        total = sum(len(list(refs(load(path)))) for path in ROOT.glob('*.schema.json'))
        self.assertEqual(total, EXPECTED_REFS)


if __name__ == '__main__':
    unittest.main()

