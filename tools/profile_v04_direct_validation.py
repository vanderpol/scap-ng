#!/usr/bin/env python3
"""Profile the unchanged public validation gate; no timing assertions or schema edits."""
import argparse
import cProfile
import importlib.metadata
import io
import json
from pathlib import Path
import pstats
import sys
import time

from validate_native_json_schemas import build_validators, document_errors


def profile(authoring, samples):
    paths=sorted(authoring.rglob('*.json'))
    documents=[json.loads(p.read_text()) for p in paths]
    if not documents or samples<1:
        raise ValueError('nonempty JSON authoring directory and positive sample count required')
    validators=build_validators(Path(__file__).resolve().parents[1]/'schema/v0.4.0')
    def validate():
        for document in documents:
            kind,=document
            errors=list(document_errors(validators[kind+'.schema.json'],document))
            if errors:raise ValueError(str(errors))
    times=[]
    for _ in range(samples):
        started=time.perf_counter();validate();times.append(time.perf_counter()-started)
    profiler=cProfile.Profile();started=time.perf_counter();profiler.runcall(validate)
    profiled=time.perf_counter()-started
    stream=io.StringIO()
    pstats.Stats(profiler,stream=stream).strip_dirs().sort_stats('cumulative').print_stats(25)
    return {'python':sys.version,'jsonschema':importlib.metadata.version('jsonschema'),
            'documents':len(documents),'authoring_files':[str(p.relative_to(authoring)) for p in paths],
            'unprofiled_seconds':times,'profiled_seconds':profiled,'profile':stream.getvalue(),
            'method':'Same process, complete strict public document_errors gate each pass; source/schema unchanged; cProfile overhead separated; OS scheduling/caches uncontrolled.',
            'optimization':'No public validation optimization implemented. Nested oneOf/anyOf and unevaluatedProperties dominate; caching IO would not address the measured hotspot. Schema pruning, assumed-family fast paths and bypassing capability validation rejected.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('authoring',type=Path)
    parser.add_argument('--samples',type=int,default=3)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('output exists; refusing overwrite')
    result=profile(args.authoring,args.samples)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['profile'])


if __name__=='__main__':main()
