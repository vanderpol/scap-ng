#!/usr/bin/env python3
"""Offline provenance inventory for reviewed OVAL 5.12.3 pilot documentation.

Pass the oval-schemas directory from the pinned public checkout. No XSD prose
is redistributed. This audits lineage, not native or scanner equivalence.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

XSD = '{http://www.w3.org/2001/XMLSchema}'
PIN = '2f140ee5c5dd1ed9606fcd5afc301f6baeb48706'
OUTPUT = Path(__file__).resolve().parents[1] / 'docs/metadata/developer-guide-oval-audit.json'
CAPABILITIES = {'windows': 'registry', 'unix': 'file', 'independent': 'shellcommand'}


def harvest(source):
    files, nodes = {}, {}
    for family, capability in sorted(CAPABILITIES.items()):
        for category in ('definitions', 'system-characteristics'):
            filename = f'{family}-{category}-schema.xsd'
            content = (source / filename).read_bytes()
            files[filename] = dict(sha256=sha256(content).hexdigest(),
                                  git_blob_sha1=sha1(f'blob {len(content)}\0'.encode() + content).hexdigest(),
                                  url=f'https://github.com/OVAL-Community/OVAL/blob/{PIN}/oval-schemas/{filename}')
            root = ET.fromstring(content)
            expected = ([capability + suffix for suffix in ('_test', '_object', '_state')]
                        if category == 'definitions' else [capability + '_item'])
            if category == 'definitions':
                expected.append({'windows': 'RegistryBehaviors', 'unix': 'FileBehaviors',
                                 'independent': 'ShellCommandBehaviors'}[family])
            for name in expected:
                matches = [node for node in root if node.get('name') == name]
                if len(matches) != 1:
                    raise ValueError(f'{filename}: expected exactly one {name}')
                node = matches[0]
                annotations = [' '.join(''.join(part.itertext()).split())
                               for part in node.iter(XSD + 'documentation')]
                nodes[f'{family}.{capability}/{name}'] = dict(
                    file=filename,
                    xpath=f'/xsd:schema/xsd:{node.tag.split("}")[-1]}[@name="{name}"]',
                    annotation_count=len(annotations),
                    normalized_characters=sum(map(len, annotations)),
                    normalized_sha256=sha256('\n'.join(annotations).encode()).hexdigest())
    return dict(format='scap-ng/developer-guide-oval-audit/1', upstream_commit=PIN,
                upstream_tag='v5.12.3', status='legacy_research_not_native_contract',
                normalization='Document-order descendant xsd:documentation text; whitespace collapsed; LF joined, UTF-8.',
                files=files, nodes=nodes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Pinned OVAL oval-schemas directory')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    value = json.dumps(harvest(args.source), indent=2) + '\n'
    if args.check:
        if OUTPUT.read_bytes() != value.encode():
            raise SystemExit('OVAL developer provenance inventory drifted')
        print('OVAL developer provenance inventory matches (6 files, 15 nodes)')
    else:
        OUTPUT.write_text(value, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
