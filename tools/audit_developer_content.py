#!/usr/bin/env python3
"""Audit the pinned historical 65-stream preview without editing or upgrading it."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_SHA = 'a01ea589501bf8a53e5df68e50ca9478f19543d2bd3844546667fde743c28d8c'
CAPABILITIES = ('independent.shellcommand', 'windows.registry', 'unix.file', 'windows.file',
                'windows.service', 'linux.rpminfo', 'linux.partition', 'independent.textfilecontent')
OUTPUT = ROOT / 'docs/metadata/developer-guide-content-audit.json'
LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)


def audit(archive, originals):
    if sha256(archive.read_bytes()).hexdigest() != ARCHIVE_SHA:
        raise ValueError('Historical corpus pin mismatch')
    counts = {cap: Counter() for cap in CAPABILITIES}
    objects = {cap: Counter() for cap in CAPABILITIES}
    samples = {cap: {} for cap in CAPABILITIES}
    automated = manual = 0
    with ZipFile(archive) as corpus:
        names = sorted(corpus.namelist())
        for name in names:
            if '/assessments/' not in name or not name.endswith('.yaml'):
                continue
            raw = corpus.read(name)
            document = yaml.load(raw, Loader=LOADER)['assessment']
            if document.get('mode') != 'automated':
                manual += 1
                continue
            automated += 1
            for test_id, test in sorted(document['tests'].items()):
                original_capability = test.get('capability')
                cap = {'independent.textfilecontent54': 'independent.textfilecontent'}.get(original_capability, original_capability)
                if cap not in counts:
                    continue
                count = counts[cap]
                count['tests'] += 1
                count['source_capability=' + original_capability] += 1
                obj = test.get('object', {})
                if not isinstance(obj, dict):
                    count['non_inline_objects'] += 1
                    continue
                objects[cap].update(obj.keys())
                for key in ('traversal', 'filesystem', 'pattern', 'error_if_exit_status_not_0', 'error_if_stderr_exists'):
                    if key in obj:
                        value = json.dumps(obj[key], sort_keys=True, separators=(',', ':'))
                        count[key + '=' + value] += 1
                stream = name.split('/local/')[1].split('/')[0]
                sample = dict(member=name, yaml_sha256=sha256(raw).hexdigest(), assessment=document['id'],
                              test=test_id, object=obj, require=test.get('require'), stream=stream)
                # Stable shortest literal example plus a traversal example where present.
                key = 'traversal' if 'traversal' in obj else 'bounded_example'
                size = len(json.dumps(sample['object']))
                previous = samples[cap].get(key)
                if previous is None or size < len(json.dumps(previous['object'])):
                    samples[cap][key] = sample
        results = {}
        for cap in CAPABILITIES:
            mapping = json.loads((ROOT / 'schema/capability-mappings/supported' / (cap + '.json')).read_text())
            examples = list(samples[cap].values())
            for sample in examples:
                trace_name = 'scap-ng-normalized-review/records/streams/' + sample['stream'] + '.source-trace.json'
                trace = json.loads(corpus.read(trace_name))
                rule = next(r for r in trace['rules'] if r.get('assessment') == sample['assessment'])
                source_name = trace['source_member'].replace('.xml', '.zip')
                source_zip = originals / source_name
                if sha256(source_zip.read_bytes()).hexdigest() != trace['source_zip_sha256']:
                    raise ValueError('Original signed source pin mismatch: ' + source_name)
                with ZipFile(source_zip) as source:
                    xml_bytes = source.read(trace['source_member'])
                if sha256(xml_bytes).hexdigest() != trace['source_xml_sha256']:
                    raise ValueError('Original XML pin mismatch')
                xml = ET.fromstring(xml_bytes)
                dependencies = set(rule['dependencies'])
                wanted = {mapping['source'].get(kind) for kind in ('test', 'object', 'state')}
                component = next((node for node in xml.iter() if node.get('id') == rule['component']), xml)
                nodes = [node for node in component.iter() if node.get('id') in dependencies and
                         node.tag.rsplit('}', 1)[-1] in wanted]
                sample['source'] = dict(zip=source_name, zip_sha256=trace['source_zip_sha256'],
                                        xml_sha256=trace['source_xml_sha256'], rule=rule['source_rule'],
                                        definition=rule['definition'], component=rule['component'],
                                        scope='Same Rule dependency closure; not a per-Test equivalence proof.',
                                        nodes=[dict(id=node.get('id'), kind=node.tag.rsplit('}', 1)[-1],
                                                    attributes=dict(sorted(node.attrib.items())),
                                                    fields=[dict(name=child.tag.rsplit('}', 1)[-1],
                                                                 attributes=dict(sorted(child.attrib.items())),
                                                                 text=(child.text or '').strip()) for child in node
                                                            if child.tag.rsplit('}', 1)[-1] not in ('notes',)])
                                               for node in nodes])
            results[cap] = dict(counts=dict(sorted(counts[cap].items())),
                                object_keys=dict(sorted(objects[cap].items())), examples=examples)
    return dict(format='scap-ng/developer-content-audit/1', archive_sha256=ARCHIVE_SHA,
                evidence_commit='7dc17f0982cdb5b17281f8f8e4373dbd87f86f58',
                archive_path='runs/v04-library/2026-10-30-all65-normalized-review-ff69d46b3/scap-ng-v04-normalized-library-review.zip',
                original_repository='https://github.com/niwc-atlantic/scap-content-library',
                original_commit='8c8e5dff860af6b1290ee9273a282db24278f8d5', original_directory='Archive/2026_Q3',
                qualification='Historical grammar preview; no current grammar upgrade, compilation or scanner equivalence claim.',
                automated_assessments=automated, non_automated_assessments_excluded=manual,
                capabilities=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('originals', type=Path, help='Pinned NIWC Archive/2026_Q3 directory')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = json.dumps(audit(args.archive, args.originals), indent=2, sort_keys=True) + '\n'
    if args.check:
        if OUTPUT.read_bytes() != result.encode():
            raise SystemExit('Developer content audit drifted')
        print('Pinned converted-content and original-source audit matches')
    else:
        OUTPUT.write_text(result, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
