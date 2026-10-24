"""Routing invariants: preserve dated jobs and mandatory current assertions (#251)."""
from hashlib import sha256
import json
from pathlib import Path
import unittest

import yaml

from run_current_tool_regressions import ARCHIVED_CONTENT_MODULES, iter_tests

ROOT = Path(__file__).resolve().parents[1]


def workflow(path):
    return yaml.safe_load((ROOT / path).read_text())


class WorkflowReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ROOT / 'tests/ci/legacy-workflows.json').read_text())

    def test_all_seven_replays_manual_pinned_and_original_commands_preserved(self):
        self.assertEqual(len(self.manifest['workflows']), 7)
        for row in self.manifest['workflows']:
            with self.subTest(workflow=row['workflow']):
                w = workflow(row['workflow'])
                self.assertEqual(set(w.get('on', w.get(True))), {'workflow_dispatch'})
                self.assertIs(w.get('on', w.get(True))['workflow_dispatch']['inputs']
                              ['allow_historical']['default'], False)
                self.assertTrue(w['name'].startswith('Historical manual'))
                self.assertEqual(row['original_source_ref'],
                                 '2de578c088291558f44d0c7a505ad149dea5fc76')
                runs = []
                for job in w['jobs'].values():
                    self.assertNotIn('continue-on-error', job)
                    self.assertIn('inputs.allow_historical', job['if'])
                    own = next(s for s in job['steps']
                               if s.get('uses', '').startswith('actions/checkout'))
                    self.assertEqual(own['with']['ref'], row['original_source_ref'])
                    uploads = [s for s in job['steps'] if s.get('uses', '').startswith('actions/upload-artifact')]
                    self.assertTrue(uploads)
                    self.assertTrue(all(s.get('if') == 'always()' for s in uploads))
                    for step in job['steps']:
                        self.assertNotIn('continue-on-error', step)
                        if 'run' in step:
                            runs.append(step['run'])
                self.assertEqual([sha256(s.encode()).hexdigest() for s in runs],
                                 row['historical_run_sha256'])
                # Only a floating dependency installation was pinned; assertions
                # and historical downloads/converters remain byte-for-byte.
                original_view = [s.replace('PyYAML==6.0.3 jsonschema==4.25.1',
                                           'PyYAML==6.0.3 jsonschema')
                                 if row['workflow'].endswith('deep-validation.yml') else s
                                 for s in runs]
                self.assertEqual([sha256(s.encode()).hexdigest() for s in original_view],
                                 row['original_run_sha256'])

    def test_production_assertion_methods_are_not_in_historical_partition(self):
        routing = json.loads((ROOT / 'tests/ci/historical-research.json').read_text())
        historical = {t for r in routing['historical'] for t in r['test_ids']}
        modules = {m for r in self.manifest['workflows'] for m in r['mandatory_modules']}
        count = 0
        for module in sorted(modules):
            self.assertNotIn(module, ARCHIVED_CONTENT_MODULES)
            suite = unittest.defaultTestLoader.loadTestsFromName(module)
            tests = list(iter_tests(suite))
            self.assertTrue(tests, module)
            self.assertFalse(any(type(t).__name__ == '_FailedTest' for t in tests), module)
            self.assertFalse({t.id() for t in tests} & historical, module)
            count += len(tests)
        self.assertGreater(count, 60)

    def test_mandatory_runner_and_three_original_source_bindings_remain_live(self):
        w = workflow('.github/workflows/rebaseline-smoke.yml')
        triggers = w.get('on', w.get(True))
        self.assertIn('.github/workflows/**', triggers['push']['paths'])
        job = w['jobs']['smoke']
        run = next(s for s in job['steps'] if s.get('name') == 'Run maintained tool regressions')
        self.assertIn('python tools/run_current_tool_regressions.py', run['run'])
        self.assertNotIn('--partition historical', run['run'])
        self.assertNotIn('--list-only', run['run'])
        for key in ('SCAP_NG_FAMILY_SOURCE_XML', 'SCAP_NG_IOS_GLOBAL_SOURCE_XML',
                    'SCAP_NG_IOSXE_GLOBAL_SOURCE_XML'):
            self.assertIn(key, run['env'])
        source = next(s for s in job['steps'] if s.get('with', {}).get('repository') ==
                      'OVAL-Community/SCAP-Self-Assertion')
        self.assertEqual(source['with']['ref'], 'e3538595c5083b9c34d937a81d319234df9bbfaa')


if __name__ == '__main__':
    unittest.main()
