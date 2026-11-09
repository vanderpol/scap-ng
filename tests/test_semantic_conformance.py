import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from check_semantic_conformance import check


class SemanticConformance(unittest.TestCase):
    def test_frozen_syntax_and_positive_negative_population_cases(self):
        result = check()
        self.assertEqual(result['schema_validated'], 15)
        self.assertEqual(result['actually_executed'], 0, 'syntax check must not claim evaluation')
        manifest = json.loads((ROOT / 'conformance/0.4/model-a/manifest.json').read_text())
        self.assertEqual({c['expected']['technical_outcome'] for c in manifest['cases']}, {'true', 'false'})

    def test_exact_compatibility_pointers(self):
        import hashlib
        matrix = json.loads((ROOT / 'docs/contracts/0.4-compatibility.json').read_text())
        self.assertEqual(set(matrix['classification_vocabulary']),
                         {'equivalent', 'intentionally_different', 'unsupported_by_RI', 'unresolved'})
        for row in matrix['native_sources']:
            raw = (ROOT / row['file']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), row['sha256'])
            value = json.loads(raw)
            for token in row['pointer'].strip('/').split('/'):
                token = token.replace('~1', '/').replace('~0', '~')
                value = value[int(token)] if isinstance(value, list) else value[token]
            self.assertEqual(value, row['source_annotation'])
