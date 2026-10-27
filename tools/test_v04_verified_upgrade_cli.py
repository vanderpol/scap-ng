"""Public verified upgrade emits a proved subset and preserves failed source work."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from v04_direct_scap_source import SourceModel
from verify_v04_direct_scope import accept_source

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tests/fixtures/v04-direct-prototype/server2025-signed.zip'
PIN = '2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0'


class VerifiedUpgradeCLITests(unittest.TestCase):
    def test_public_cli_proves_compiles_and_excludes_invalid_source_without_overwrite(self):
        source = SourceModel(SOURCE, PIN)
        rules = [next(i for i in source.rules if '_SV-' + n + 'r' in i) for n in ('278139', '278080', '278031')]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'upgrade'
            command = [sys.executable, str(ROOT / 'tools/v04_direct_converter.py'), str(SOURCE),
                       '--sha256', PIN, '--verify', '--output', str(output)]
            for rule in rules:
                command += ['--rule', rule]
            environment = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            result = subprocess.run(command, capture_output=True, text=True, env=environment)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((output / 'acceptance.json').read_text())
            self.assertEqual(report['outcomes'], {'NOT_SELECTED': 288, 'PROVED': 2, 'BLOCKED': 1})
            self.assertEqual(len(report['cases']), 291)
            self.assertEqual(len(report['programs']), 2)
            self.assertEqual(report['package_consumer']['status'], 'INDEPENDENT_PACKAGE_CONSUMER_PASS')
            self.assertFalse(report['package_consumer']['scanner_evaluated'])
            blocked = next(c for c in report['cases'] if c['rule'] == rules[2])
            self.assertIn('invalid', blocked['diagnostic'])
            self.assertTrue(blocked['dependencies'])
            self.assertEqual(report['source']['sha256'], PIN)
            self.assertTrue((output / 'source-trace.json').is_file())
            self.assertTrue((output / 'coverage.md').is_file())
            snapshot = {p.relative_to(output): sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file()}
            again = subprocess.run(command, capture_output=True, text=True, env=environment)
            self.assertNotEqual(again.returncode, 0)
            self.assertIn('refusing overwrite', again.stderr)
            self.assertEqual(snapshot, {p.relative_to(output): sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file()})

    def test_bad_pin_or_unknown_selection_never_creates_an_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'upgrade'
            for pin, selection in (('0' * 64, None), (PIN, ['unknown'])):
                with self.subTest(pin=pin), self.assertRaises(ValueError):
                    accept_source(SOURCE, pin, output, rule_ids=selection)
                self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
