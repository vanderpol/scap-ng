"""Growing source coverage must retain every previously pinned original byte."""
from pathlib import Path
import tempfile
import unittest

from verify_v04_unix_password import run, verify_case_floor


class OriginalCaseRetentionTests(unittest.TestCase):
    def test_additional_proofs_are_allowed_but_missing_or_changed_originals_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected, actual = root / 'expected', root / 'actual'
            expected.mkdir()
            actual.mkdir()
            original = '{"original_source": "pinned", "version": 1}\n'
            (expected / 'original.json').write_text(original)
            (actual / 'original.json').write_text(original)
            (actual / 'newly-proved.json').write_text('{"original_source": "additional"}\n')
            self.assertEqual(verify_case_floor(expected, actual), {'retained': 1, 'additional': 1})
            (actual / 'original.json').write_text(original.replace('1', '2'))
            with self.assertRaisesRegex(ValueError, 'lost or changed'):
                verify_case_floor(expected, actual)
            (actual / 'original.json').unlink()
            with self.assertRaisesRegex(ValueError, 'lost or changed'):
                verify_case_floor(expected, actual)

    def test_empty_baseline_cannot_create_a_vacuous_success(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, 'baseline is empty'):
                verify_case_floor(root, root)

    def test_existing_fixture_directory_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixtures = root / 'preserved'
            fixtures.mkdir()
            original = fixtures / 'original.json'
            original.write_text('preserve these bytes')
            with self.assertRaisesRegex(ValueError, 'refusing overwrite'):
                run(root, root / 'output', fixtures=fixtures)
            self.assertEqual(original.read_text(), 'preserve these bytes')
            self.assertFalse((root / 'output').exists())


if __name__ == '__main__':
    unittest.main()
