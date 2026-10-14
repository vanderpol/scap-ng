#!/usr/bin/env python3
"""Remove redundant 'default' Assessment aliases without changing Rule meaning."""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path
import yaml

CHOICE_LINE = re.compile(r'^    ([a-zA-Z0-9_-]+):[ \t]*$', re.M)
DEFAULT = re.compile(r'^(?P<indent>  )default_assessment_choice:[ \t]*default[ \t]*$', re.M)


def rewrite_rule(source: bytes, name: str):
    original = yaml.safe_load(source)
    rule = original.get('rule') if isinstance(original, dict) else None
    if not isinstance(rule, dict):
        raise ValueError(f'{name}: not a native Rule')
    choices = rule['assessment_choices']
    if 'default' not in choices:
        if rule.get('default_assessment_choice') not in choices:
            raise ValueError(f'{name}: invalid publisher default')
        return source, None
    legacy = choices['default']
    aliases = [n for n, v in choices.items() if n != 'default' and v == legacy]
    if not aliases:
        raise ValueError(f'{name}: `default` has unique meaning; cannot discard it')
    selected = next((k for k in ('automated', 'manual') if k in aliases), aliases[0])
    if rule.get('default_assessment_choice') != 'default':
        raise ValueError(f'{name}: `default` alias exists but is not the selected default')
    body = source.decode('utf-8')
    start = re.search(r'^  assessment_choices:[ \t]*$', body, re.M)
    if not start:
        raise ValueError(f'{name}: missing choice section')
    section_start = body.find('\n', start.end()) + 1
    section_end_match = re.search(r'^  [a-zA-Z_][\w-]*:', body[section_start:], re.M)
    if not section_end_match:
        raise ValueError(f'{name}: unable to locate end of choices')
    section_end = section_start + section_end_match.start()
    block = body[section_start:section_end]
    matches = list(CHOICE_LINE.finditer(block))
    defaults = [(idx, m) for idx, m in enumerate(matches) if m.group(1) == 'default']
    if len(defaults) != 1:
        raise ValueError(f'{name}: source default YAML block is missing or ambiguous')
    idx, match = defaults[0]
    end = matches[idx + 1].start() if idx + 1 < len(matches) else len(block)
    block = block[:match.start()] + block[end:]
    body = body[:section_start] + block + body[section_end:]
    body, replaced = DEFAULT.subn('  default_assessment_choice: ' + selected, body)
    if replaced != 1:
        raise ValueError(f'{name}: missing exactly one default_assessment_choice')
    out = body.encode('utf-8')
    parsed = yaml.safe_load(out)
    expected = copy.deepcopy(original)
    expected['rule']['assessment_choices'].pop('default')
    expected['rule']['default_assessment_choice'] = selected
    if parsed != expected:
        raise ValueError(f'{name}: unexpected semantic YAML change')
    return out, selected


def curate(source_zip: Path, output_zip: Path, expected_rules: int | None = None):
    output_zip.parent.mkdir(parents=True,exist_ok=True)
    counts = Counter()
    original_assessments = {}
    seen = set()
    entries = {}
    with zipfile.ZipFile(source_zip) as archive:
        if archive.testzip():
            raise ValueError('Invalid source CRC')
        for member in archive.infolist():
            if member.is_dir():
                continue
            name = member.filename
            if name in seen:
                raise ValueError(f'Duplicate ZIP member {name}')
            seen.add(name)
            contents = archive.read(name)
            if '/assessments/' in name and name.endswith('.yaml'):
                original_assessments[name] = contents
            if name.endswith('.rule.yaml'):
                contents, selected = rewrite_rule(contents, name)
                counts['rules'] += 1
                if selected is not None:
                    counts['aliases_removed'] += 1
                    counts['default_'+selected] += 1
            entries[name] = contents
    if expected_rules is not None and counts['rules'] != expected_rules:
        raise ValueError(f'Expected {expected_rules} Rules, got {counts["rules"]}')
    if counts['rules'] != counts['aliases_removed']:
        raise ValueError(f'Found {counts["rules"] - counts["aliases_removed"]} Rules still missing new format')
    with zipfile.ZipFile(output_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, contents in sorted(entries.items()):
            member = zipfile.ZipInfo(name, (1980,1,1,0,0,0))
            member.compress_type = zipfile.ZIP_DEFLATED
            member.external_attr = (0o100644 & 0xffff) << 16
            archive.writestr(member, contents, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(output_zip) as output:
        if output.testzip():
            raise ValueError('Output ZIP CRC failed')
        if len(output.namelist()) != len(entries):
            raise ValueError('Output file count changed')
        for name in original_assessments:
            if output.read(name) != original_assessments[name]:
                raise ValueError(f'Assessment bytes changed: {name}')
        for name in entries:
            if output.read(name) != entries[name]:
                raise ValueError(f'Output bytes differ for {name}')
    return {'rules':counts['rules'], 'removed_aliases':counts['aliases_removed'],
        'publisher_defaults':{key[8:]:count for key,count in counts.items() if key.startswith('default_')},
        'assessments_unmodified':len(original_assessments),'sha256':hashlib.sha256(output_zip.read_bytes()).hexdigest()}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('source',type=Path)
    p.add_argument('destination',type=Path)
    p.add_argument('--expected-rules',type=int,default=None)
    args=p.parse_args()
    print(json.dumps(curate(args.source,args.destination,args.expected_rules),indent=2))


if __name__=='__main__':
    main()
