#!/usr/bin/env python3
"""Read-only census of 0.4 Test cardinality compaction opportunities (#264).

This scans *current native YAML*, for which OVAL State boundaries may not be
recoverable. It ONLY measures Test-level inherited field requirements; a
source-backed future converter may also fold single-State scalar AND fields.
No files, proof statuses, or compiled programs are changed by this command.
"""

import argparse
from collections import Counter
from pathlib import Path

import yaml

from v04_human_authoring_compact import compact_test_requirement


def audit(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError('authoring root not found: ' + str(root))
    totals = Counter()
    samples = []
    by_stream = Counter()
    for path in sorted(root.rglob('*.yaml')):
        if not '/assessments/automated/' in '/' + path.relative_to(root).as_posix():
            continue
        if path.is_symlink():
            raise ValueError('symlink is not a trusted native Assessment: ' + str(path))
        document = yaml.safe_load(path.read_text(encoding='utf-8'))
        if not isinstance(document, dict) or 'assessment' not in document:
            continue
        totals['assessment_files'] += 1
        tests = document['assessment'].get('tests') or {}
        for test_id, test in tests.items():
            totals['tests'] += 1
            source = test.get('require')
            candidate, edit = compact_test_requirement(source)
            if not edit:
                continue
            totals['tests_eligible'] += 1
            stream = path.relative_to(root).parts[0]
            by_stream[stream] += 1
            old = len(yaml.safe_dump(source, sort_keys=False).splitlines())
            new = len(yaml.safe_dump(candidate, sort_keys=False).splitlines())
            totals['yaml_lines_removed_estimate'] += max(0, old - new)
            if len(samples) < 8:
                samples.append({'file': path.relative_to(root).as_posix(),
                                'test': test_id, 'lines_before': old, 'lines_after': new})
    return {'status': 'READ_ONLY', 'source': str(root), 'counts': dict(totals),
            'eligible_stig_count': len(by_stream),
            'top_stigs': by_stream.most_common(12), 'samples': samples,
            'not_measured': 'single-State AND folding requires source-OVAL provenance',
            'proof_status_unchanged': 'no native files edited; not a revalidation'}


def main():
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--authoring-root', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(audit(args.authoring_root), indent=2))


if __name__ == '__main__':
    main()
