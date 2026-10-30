#!/usr/bin/env python3
"""Deterministic read-only ZIP packaging of an accepted #263 v2 layout.

All authoring YAML and durability sidecars are preserved verbatim. Package
hashes and payload inventory are emitted beside the ZIP, never inside source.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import zipfile


PREFIX='scap-ng-0.4.0-human-readable-review/'


def package(root, dest):
    root=Path(root).resolve();dest=Path(dest).resolve()
    receipt=json.loads((root/'metadata/reflow-receipt.json').read_text())
    if receipt['status']!='PASS' or receipt['format']!='scap-ng-native-human-library-v2/1':
        raise ValueError('only a completed validated v2 export can be packaged')
    manifest_target=dest.parent/(dest.name+'.manifest.json')
    if dest.exists() or manifest_target.exists() or dest.is_relative_to(root):
        raise ValueError('ZIP target must be new and outside source')
    inventory=[]
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('symlink is not eligible for portable review ZIP')
        if not path.is_file():
            continue
        relative=path.relative_to(root).as_posix()
        raw=path.read_bytes()
        inventory.append({'path':relative,'bytes':len(raw),
                          'sha256':sha256(raw).hexdigest()})
    if sum(x['path'].startswith('authoring/') and x['path'].endswith('.yaml')
           for x in inventory)!=receipt['native_yaml']:
        raise ValueError('packaging lost native authoring files')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as out:
        for item in inventory:
            info=zipfile.ZipInfo(PREFIX+item['path'],date_time=(1980,1,1,0,0,0))
            info.external_attr=0o100644<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            out.writestr(info,(root/item['path']).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(dest) as check:
        if check.testzip() is not None:
            raise ValueError('published ZIP failed CRC integrity check')
    answer={'format':'scap-ng-human-library-package/1','file':dest.name,
            'sha256':sha256(dest.read_bytes()).hexdigest(),
            'bytes':dest.stat().st_size,
            'native_yaml':receipt['native_yaml'],
            'compiled_program_hashes_unchanged':receipt['compiled_program_hashes_unchanged'],
            'accepted_proofs_unchanged':receipt['accepted_static_proofs_unchanged'],
            'payload_inventory':inventory}
    with manifest_target.open('x') as out:
        out.write(json.dumps(answer,indent=2)+'\n')
    return {key:value for key,value in answer.items() if key!='payload_inventory'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('--output',required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(package(args.root,args.output),sort_keys=True))


if __name__=='__main__':
    main()
