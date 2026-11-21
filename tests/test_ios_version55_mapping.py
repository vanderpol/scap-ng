"""Source-backed contract witness for the nondeprecated IOS version55 mapping."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IOSVersion55MappingTests(unittest.TestCase):
    def test_mapping_preserves_source_test_object_state_and_fields(self):
        mapping = json.loads((ROOT / 'schema/capability-mappings/supported/ios.version55.json').read_text())
        self.assertEqual(mapping['capability'], 'ios.version55')
        self.assertEqual(mapping['source']['test'], 'version55_test')
        self.assertEqual(mapping['source']['object'], 'version55_object')
        self.assertEqual(mapping['source']['state'], 'version55_state')
        self.assertEqual(mapping['source']['item'], 'version_item')
        self.assertEqual(set(mapping['native']['state_field_map']), {
            'major_version', 'minor_version', 'release', 'train_identifier',
            'rebuild', 'subrebuild', 'mainline_rebuild', 'version_string',
        })
        self.assertEqual(mapping['native']['field_datatypes']['major_version'], ['integer'])
        self.assertEqual(mapping['native']['field_datatypes']['version_string'], ['string'])



if __name__ == '__main__':
    unittest.main()
