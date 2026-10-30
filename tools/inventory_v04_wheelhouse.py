#!/usr/bin/env python3
"""Inspect original offline wheels and retain dependency/license metadata."""
import argparse
from email.parser import BytesParser
from hashlib import sha256
import json
from pathlib import Path
import re
import zipfile


def inventory(wheelhouse, lock):
    expected={}
    for line in lock.read_text().splitlines():
        if not line or line.startswith('#'):continue
        match=re.fullmatch(r'(\S+)==(\S+) --hash=sha256:([0-9a-f]{64})',line)
        if not match:raise ValueError('unsupported/non-pinned dependency lock line')
        name,version,digest=match.groups();expected[name.lower().replace('_','-')]=(version,digest)
    records=[]
    for path in sorted(wheelhouse.glob('*.whl')):
        raw=path.read_bytes();digest=sha256(raw).hexdigest()
        with zipfile.ZipFile(path) as wheel:
            names=[n for n in wheel.namelist() if n.endswith('.dist-info/METADATA')]
            if len(names)!=1:raise ValueError('ambiguous wheel metadata')
            metadata=BytesParser().parsebytes(wheel.read(names[0]))
            name=metadata['Name'];version=metadata['Version']
            if expected.pop(name.lower().replace('_','-'),None)!=(version,digest):
                raise ValueError('wheel does not match pinned lock: '+path.name)
            licenses=[{'path':n,'sha256':sha256(wheel.read(n)).hexdigest(),'bytes':len(wheel.read(n))}
                for n in wheel.namelist() if not n.endswith('/') and
                ('.dist-info/licenses/' in n or Path(n).name.lower().startswith(('license','copying','notice')))]
            records.append({'file':path.name,'bytes':len(raw),'sha256':digest,'name':name,'version':version,
                'license':metadata.get('License'),'license_expression':metadata.get('License-Expression'),
                'license_classifiers':[v for v in metadata.get_all('Classifier',[]) if v.startswith('License ::')],
                'license_notices':licenses})
    if expected:raise ValueError('missing locked wheels: '+str(sorted(expected)))
    return {'status':'PASS','lock_sha256':sha256(lock.read_bytes()).hexdigest(),
            'platform':'Linux x86_64 CPython 3.12','packages':records,
            'project_license':'UNDECLARED; owner decision required before final licensed release'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wheelhouse',type=Path,required=True)
    parser.add_argument('--lock',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.write_text(json.dumps(inventory(args.wheelhouse,args.lock),indent=2)+'\n')
