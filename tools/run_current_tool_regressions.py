#!/usr/bin/env python3
"""Run current 0.4 regressions or the explicitly pinned historical research set.

Historical 0.2 schemas are preserved under schema/v0.2.0. Their Board-pilot
conversion and sample-reproduction tests are deliberately excluded from active
0.3 CI. Shared SCAP 1.4 / OVAL semantic regressions are still included.
"""
from __future__ import annotations

import sys
import unittest
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ARCHIVED_CONTENT_MODULES = frozenset({
    "test_board_conversion_v02",
    "test_board_samples_v02",
    # 0.4-A's preapproval draft-vs-research boundary is historical: its
    # assumption that scoped field requirements and and/or are unapproved
    # contradicts the 2026-10-21 canonical 0.4.0 owner decision.
    # Keep the tests in repository as history, not current 0.4 CI.
    "test_v04_a_grammar_boundary",
})


def iter_tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from iter_tests(item)
        else:
            yield item


def select_tests(directory, manifest):
    suite = unittest.TestLoader().discover(str(directory), pattern="test_*.py")
    all_tests = list(iter_tests(suite))
    maintained = [t for t in all_tests if t.__class__.__module__ not in ARCHIVED_CONTENT_MODULES]
    research_ids = set()
    for row in manifest['historical']:
        source = directory / (row['module'] + '.py')
        if hashlib.sha256(source.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Historical test source changed; review CI routing: ' + row['module'])
        found = {t.id() for t in maintained if t.__class__.__module__ == row['module']}
        if found != set(row['test_ids']):
            raise ValueError('Historical test selection changed: ' + row['module'])
        research_ids.update(found)
    current = [t for t in maintained if t.id() not in research_ids]
    research = [t for t in maintained if t.id() in research_ids]
    before = set(manifest['pre_split_selected_ids'])
    after = {t.id() for t in maintained}
    if before - after:
        raise ValueError('Pre-split test identities disappeared: ' + str(sorted(before - after)))
    if len(current) + len(research) != len(maintained):
        raise ValueError('CI partition is not exhaustive')
    return current, research, {
        'current_ids': sorted(t.id() for t in current),
        'historical_ids': sorted(research_ids),
        'pre_split_missing_ids': sorted(before - after),
        'new_current_ids': sorted(after - before),
        'pre_existing_archived_modules': sorted(ARCHIVED_CONTENT_MODULES),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--partition', choices=('current', 'historical', 'all'), default='current')
    parser.add_argument('--source-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--report', type=Path)
    parser.add_argument('--list-only', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).resolve().parents[1] /
                           'tests/ci/historical-research.json').read_text())
    directory = args.source_root.resolve() / 'tools'
    if args.partition == 'historical':
        revision = subprocess.check_output(['git', '-C', str(args.source_root),
                                            'rev-parse', 'HEAD'], text=True).strip()
        if revision != manifest['source_ref']:
            raise ValueError('Historical execution requires pinned source ref ' + manifest['source_ref'])
        subprocess.run(['git', '-C', str(args.source_root), 'diff', '--exit-code',
                        'HEAD', '--', 'tools', 'schema', 'tests'], check=True)
    sys.path.insert(0, str(directory))
    current, research, selection = select_tests(directory, manifest)
    selected = {'current': current, 'historical': research, 'all': current + research}[args.partition]
    print(f"Selected {args.partition}: {len(selected)}; current {len(current)}; historical {len(research)}",
          file=sys.stderr)
    report = {'partition': args.partition, 'research_source_ref': manifest['source_ref'],
              'selection': selection}
    if args.list_only:
        report['selected_ids'] = sorted(t.id() for t in selected)
        result = None
    else:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
        report.update(tests=result.testsRun, failures=len(result.failures), errors=len(result.errors),
                      skips=len(result.skipped), successful=result.wasSuccessful(),
                      skipped_tests=[{'id': str(t), 'reason': reason} for t, reason in result.skipped],
                      diagnostics=[{'kind': kind, 'id': str(t), 'traceback': tb}
                                   for kind, rows in (('failure', result.failures), ('error', result.errors))
                                   for t, tb in rows])
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    if result is None:
        return 0
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
