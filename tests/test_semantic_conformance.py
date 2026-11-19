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

    def test_existing_four_capability_catalog(self):
        result = check(supplied_evidence=True)
        self.assertEqual(result['schema_validated'], 23)
        self.assertEqual(result['actually_executed'], 0)

    def test_newer_historical_receipt_tracks_actual_git_bytes(self):
        """Every later frozen hash must resolve at its stated source commit."""
        import hashlib
        import subprocess

        receipt = json.loads((ROOT / 'conformance/0.4/frozen-schema-sha256.json').read_text())
        self.assertEqual(len(receipt['files']), 145)
        for path, expected in receipt['files'].items():
            with self.subTest(path=path):
                self.assertTrue(path.startswith('schema/'))
                original = subprocess.run(
                    ['git', 'show', receipt['commit'] + ':' + path],
                    cwd=ROOT, check=True, capture_output=True, timeout=15).stdout
                self.assertEqual(hashlib.sha256(original).hexdigest(), expected)

    def test_archived_receipt_and_original_source_mutations_fail_closed(self):
        """An immutable Git receipt or original schema mutation must be rejected."""
        import subprocess
        from unittest.mock import patch
        import check_semantic_conformance as checker

        real_run = subprocess.run
        for suffix, expected in (
                (':conformance/0.4/frozen-schema-sha256.json',
                 'historical conformance receipt digest mismatch'),
                (':schema/applicability.schema.json',
                 'historical conformance source digest mismatch')):
            with self.subTest(suffix=suffix):
                def mutate(argv, *args, **kwargs):
                    result = real_run(argv, *args, **kwargs)
                    if len(argv) >= 3 and argv[1] == 'show' and argv[2].endswith(suffix):
                        return subprocess.CompletedProcess(
                            argv, result.returncode, result.stdout + b' ', result.stderr)
                    return result

                with patch.object(checker.subprocess, 'run', side_effect=mutate):
                    with self.assertRaisesRegex(ValueError, expected):
                        checker.check()

    def test_case_sensitive_evidence_members(self):
        from copy import deepcopy
        import yaml
        from jsonschema import Draft202012Validator
        from referencing import Registry, Resource
        cases=json.loads((ROOT/'conformance/0.4/evidence-member-negatives.json').read_text())
        fixture=yaml.safe_load((ROOT/cases['fixture']).read_text())
        schemas=[json.loads(p.read_text()) for p in (ROOT/'schema').glob('*.schema.json')]
        registry=Registry().with_resources((s['$id'],Resource.from_contents(s)) for s in schemas)
        schema=next(s for s in schemas if s['$id'].endswith('/collected-item.schema.json'))
        validator=Draft202012Validator(schema,registry=registry)
        validator.validate(fixture['collected_items'][0])
        for case in cases['cases']:
            changed=deepcopy(fixture);node=changed
            for part in case['object_pointer'].strip('/').split('/'):
                node=node[int(part)] if isinstance(node,list) else node[part]
            node[case['invalid_spelling']]=node.pop(case['member'])
            self.assertTrue(list(validator.iter_errors(changed['collected_items'][0])),case['id'])
