"""Acceptance cannot lose a source-proved Rule or silently change its program."""
from copy import deepcopy
import unittest

from verify_v04_direct_scope import verify_proof_floor


class DirectScopeAcceptanceTests(unittest.TestCase):
    def test_retains_proofs_and_allows_additional_proved_rules(self):
        baseline = {'source_sha256': 'original', 'rules': {
            'rule-1': {'assessment': 'assessment-1', 'program_sha256': 'program-1'}}}
        evidence = {'source': {'sha256': 'original'}, 'cases': [
            {'rule': 'rule-1', 'outcome': 'PROVED', 'assessment': 'assessment-1'},
            {'rule': 'rule-2', 'outcome': 'PROVED', 'assessment': 'assessment-2'}],
            'programs': [{'assessment': 'assessment-1', 'program_sha256': 'program-1'},
                         {'assessment': 'assessment-2', 'program_sha256': 'program-2'}]}
        verify_proof_floor('example', evidence, baseline)
        for mutation in ('lost proof', 'changed program', 'changed source'):
            wrong = deepcopy(evidence)
            if mutation == 'lost proof':
                wrong['cases'][0]['outcome'] = 'UNVERIFIABLE'
            elif mutation == 'changed program':
                wrong['programs'][0]['program_sha256'] = 'different'
            else:
                wrong['source']['sha256'] = 'different'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                verify_proof_floor('example', wrong, baseline)


if __name__ == '__main__':
    unittest.main()
