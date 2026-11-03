"""Independently justify binary32 vector expectations with exact rationals."""
from decimal import Decimal
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def magnitude(bits):
    exponent, fraction = bits >> 23, bits & 0x7fffff
    return Fraction(fraction if exponent == 0 else fraction + 2**23) * Fraction(2)**(
        -149 if exponent == 0 else exponent - 150)


class Binary32Contract(unittest.TestCase):
    def test_scope_is_finite_expected_and_existing_schema_family_is_untouched(self):
        raw = (ROOT/'docs/metadata/binary32-comparison-contract.json').read_bytes()
        contract = json.loads(raw)
        self.assertEqual(contract['format'], 'scap-ng-0.4.0-binary32-comparisons/1')
        self.assertEqual(contract['owner_direction']['date'], '2026-11-03')
        self.assertEqual(len(contract['operations']), 6)
        self.assertIn('blocked', contract['expected']['nonfinite'])
        checksum = sha256()
        for path in sorted((ROOT/'schema').rglob('*.json')):
            checksum.update(path.relative_to(ROOT/'schema').as_posix().encode() + b'\0')
            checksum.update(path.read_bytes())
        self.assertEqual(checksum.hexdigest(), 'f19246c60814f7768a5564cd335675b4c2c6ae721ebd6a464ee9a6f17185e0a3')

    def test_vectors_use_exact_nearest_even_intervals_without_host_float_casts(self):
        rows = json.loads((ROOT/'tests/fixtures/binary32-vectors.json').read_text())
        self.assertEqual(len(rows), 19)
        for row in rows:
            text, bits = row['lexical'], int(row['bits'], 16)
            if text in ('INF', '-INF', 'NaN'):
                continue
            value = Decimal(text)
            self.assertEqual(int(value.is_signed()), bits >> 31)
            value = value.copy_abs()
            absolute = bits & 0x7fffffff
            if value.adjusted() > 100:
                self.assertEqual(absolute, 0x7f800000)
                continue
            if value.adjusted() < -100:
                self.assertEqual(absolute, 0)
                continue
            exact = Fraction(value)
            if absolute == 0x7f800000:
                self.assertGreaterEqual(exact, 2**128 - 2**103)
                continue
            represented = magnitude(absolute)
            if absolute == 0:
                self.assertLessEqual(exact, Fraction(1, 2**150))
                continue
            lower = (magnitude(absolute - 1) + represented) / 2
            upper = (represented + (magnitude(absolute + 1) if absolute < 0x7f7fffff else 2**128)) / 2
            self.assertGreaterEqual(exact, lower)
            self.assertLessEqual(exact, upper)
            if exact in (lower, upper):
                self.assertEqual(absolute & 1, 0, 'nearest-even tie')


if __name__ == '__main__':
    unittest.main()
