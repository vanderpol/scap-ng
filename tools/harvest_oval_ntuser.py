#!/usr/bin/env python3
"""Inventory pinned OVAL ntuser annotations without copying their licensed prose.

Run against the XSD files from the historical research checkout; the published
staging repository intentionally does not vendor the complete research corpus.
"""

import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


XSD = '{http://www.w3.org/2001/XMLSchema}'
SOURCE_DIR = 'third_party/scap-1.4-schemas/oval_5.12.3'
UPSTREAM = 'https://github.com/OVAL-Community/OVAL/blob/v5.12.3/oval-schemas/'
EXPECTED_NODES = ('ntuser_test', 'ntuser_object', 'ntuser_state', 'ntuser_item')


def normalized_annotations(element):
    annotations = element.findall(f'./{XSD}annotation/{XSD}documentation')
    return [re.sub(r'\s+', ' ', ''.join(node.itertext())).strip()
            for node in annotations]


def record_annotations(element):
    annotations = normalized_annotations(element)
    canonical = '\n'.join(annotations).encode('utf-8')
    return {
        'annotation_count': len(annotations),
        'normalized_characters': sum(len(part) for part in annotations),
        'normalized_sha256': sha256(canonical).hexdigest(),
    }


def file_identity(path):
    content = path.read_bytes()
    git_header = f'blob {len(content)}\0'.encode('ascii')
    return {
        'source_path': f'{SOURCE_DIR}/{path.name}',
        'upstream_url': UPSTREAM + path.name,
        'sha256': sha256(content).hexdigest(),
        'git_blob_sha1': sha1(git_header + content).hexdigest(),
    }


def harvest(definitions, characteristics):
    roots = {
        'definitions': ET.parse(definitions).getroot(),
        'system_characteristics': ET.parse(characteristics).getroot(),
    }
    nodes = {}
    for name in EXPECTED_NODES:
        kind = 'system_characteristics' if name == 'ntuser_item' else 'definitions'
        root = roots[kind]
        matches = [el for el in root.iter(f'{XSD}element')
                   if el.get('name') == name]
        if len(matches) != 1:
            raise ValueError(f'{name}: expected one XSD element, got {len(matches)}')
        element = matches[0]
        children = {}
        for child in element.findall(f'.//{XSD}sequence/{XSD}element'):
            field = child.get('name')
            if field and field != name:
                children[field] = record_annotations(child)
        nodes[name] = {
            'source': kind,
            'xsd_element': name,
            **record_annotations(element),
            'fields': dict(sorted(children.items())),
        }
    return {
        'format': 'scap-ng/legacy-oval-ntuser-annotation-audit/1',
        'provenance_status': 'source_verified_semantics_not_adopted',
        'license_notice': 'OVAL XSD source includes a Government License/Disclaimer requiring reproduction when the XSD is copied or modified. This audit carries hashes, counts and pointers, not the XSD documentation text.',
        'files': {
            'definitions': file_identity(definitions),
            'system_characteristics': file_identity(characteristics),
        },
        'nodes': nodes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--definitions', type=Path, required=True)
    parser.add_argument('--system-characteristics', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    payload = harvest(args.definitions, args.system_characteristics)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n',
                           encoding='utf-8')
    print(f'Audited {len(payload["nodes"])} OVAL elements; source bytes not copied')


if __name__ == '__main__':
    main()
