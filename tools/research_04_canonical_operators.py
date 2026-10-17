#!/usr/bin/env python3
"""Research #235: existing SCAP-NG field operators, no English-first aliases.

Layered over independently source-inverting consistent-quantifiers experiment.
Preserves collection/Item/State/record cardinalities and literal values.
Research only: not an adopted 0.4 language or scanner-execution proof.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile
import yaml
from jsonschema import Draft202012Validator
from research_english_first_04_complex import FIELD_OPS, FIELD_MODES
from research_04_fixed_require_editor import PINNED, SAMPLES, to_fixed, from_fixed
from research_04_flat_require import flat_doc, source_doc
from research_04_consistent_quantifiers import (
    document_to_consistent, document_to_flat, schema_for_consistent,
)

# Derived from the importer itself. Only obsolete operators are renamed;
# regex, bitwise, greater_than, less_than and literals are untouched.
FRIENDLY_TO_SOURCE = {friendly: original for original, friendly in FIELD_OPS.items()
                      if friendly != original}
PREFIXES = {''}
for mode in FIELD_MODES.values():
    if mode not in ('ordinary','no_values_exist'):
        PREFIXES.add({'some_values_':'at_least_one_value_',
                      'when_present_some_values_':'when_present_at_least_one_value_'}
                     .get(mode, mode))
# The 0.4 auditor-candidate translator modernizes those specific two prefixes.
ALIASES = {prefix + alias: prefix + original
           for prefix in PREFIXES for alias, original in FRIENDLY_TO_SOURCE.items()}
INVERSE = {native: alias for alias, native in ALIASES.items()}
assert len(INVERSE)==len(ALIASES), 'operator alias collision'

# These are metadata/wrappers, not comparison operations. A comparison key
# is a sole key of a leaf, and its value may be scalar, list or typed operand.
# Schema additionally forbids alias names at arbitrary nested depths inside
# author-facing `require`, including the numeric-comparison aliases.

def change_comparators(node, *, forward: bool, counts: Counter | None = None):
    mapping = ALIASES if forward else INVERSE
    if isinstance(node,list):
        return [change_comparators(x,forward=forward,counts=counts) for x in node]
    if not isinstance(node,dict):
        return deepcopy(node)
    if len(node)==1:
        key, val = next(iter(node.items()))
        if key in mapping:
            if counts is not None:
                counts['operator_aliases_removed']+=1
                counts['operator_'+key+'_to_'+mapping[key]]+=1
            return {mapping[key]:deepcopy(val)}
    return {k:change_comparators(v,forward=forward,counts=counts) for k,v in node.items()}


def require_to_canonical(require, counts=None):
    if not isinstance(require,dict) or 'items' not in require:
        raise ValueError('missing items in authoring requirement')
    result=deepcopy(require)
    for k,v in require.items():
        if k not in ('items','match'):
            result[k]=change_comparators(v,forward=True,counts=counts)
    # Distinct source predicates which accidentally collapse into one spelling
    # are not silently accepted as authoring equivalence.
    if require_from_canonical(result)!=require:
        raise ValueError('non-invertible comparison operator alias')
    return result


def require_from_canonical(require):
    if not isinstance(require,dict) or 'items' not in require:
        raise ValueError('missing items in authoring requirement')
    result=deepcopy(require)
    for k,v in require.items():
        if k not in ('items','match'):
            result[k]=change_comparators(v,forward=False)
    return result


def to_canonical_document(consistent,counts=None):
    out=deepcopy(consistent)
    for check in out['checks'].values():
        check['require']=require_to_canonical(check['require'],counts)
    return out


def from_canonical_document(doc):
    out=deepcopy(doc)
    for check in out['checks'].values():
        check['require']=require_from_canonical(check['require'])
    return out


def schema_for_canonical(base):
    schema=schema_for_consistent(base)
    schema['$id']='https://scap-ng.dev/research/english-first-04/canonical-operators.schema.json'
    schema['title']='RESEARCH: existing 0.4 comparison operators and consistent quantifiers'
    # Recursive guard validates every YAML object key inside require clauses;
    # no `is`, `is_not`, or aliases may silently coexist with `equals`, etc.
    # This is an additional research-level negative guard and not intended as
    # the final capability-specific completion grammar.
    schema['$defs']['noEnglishOperatorAliases']={
      'if':{'type':'object'},
      'then':{
        'propertyNames':{'not':{'enum':sorted(ALIASES)}},
        'additionalProperties':{'$ref':'#/$defs/noEnglishOperatorAliases'},
      },
      'else':{
        'if':{'type':'array'},
        'then':{'items':{'$ref':'#/$defs/noEnglishOperatorAliases'}}
      },
    }
    old=schema['$defs']['requirement']
    schema['$defs']['requirement']={'allOf':[old,{'$ref':'#/$defs/noEnglishOperatorAliases'}]}
    Draft202012Validator.check_schema(schema)
    return schema


def proof(archive,base_schema,out_dir):
    digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest!=PINNED:raise ValueError('six-STIG baseline SHA256 changed')
    base=json.loads(Path(base_schema).read_text())
    schema=schema_for_canonical(base)
    validator=Draft202012Validator(schema)
    counts=Counter();failed=[];chosen={}
    with zipfile.ZipFile(archive) as z:
        for path in sorted(z.namelist()):
            if not(path.startswith('authoring/') and '/assessments/' in path and path.endswith('.yaml')):
                continue
            original=(yaml.safe_load(z.read(path)) or {}).get('assessment') or {}
            if original.get('mode')!='automated' or not isinstance(original.get('tests'),dict) or not original['tests']:
                continue
            counts['assessments']+=1
            counts['tests']+=len(original['tests'])
            try:
                fixed=to_fixed(original)
                flat=flat_doc(fixed)
                consistent=document_to_consistent(flat)
                canonical=to_canonical_document(consistent,counts)
                error=next(validator.iter_errors(canonical),None)
                if error:raise ValueError('canonical editor schema: '+error.message[:260])
                inverted=from_canonical_document(canonical)
                if inverted!=consistent or document_to_flat(inverted)!=flat or from_fixed(source_doc(flat))!=original:
                    raise ValueError('source dictionary not exactly invertible')
                counts['exact_assessments']+=1
                counts['exact_tests']+=len(original['tests'])
                if path in SAMPLES.values():
                    label=next(n for n,p in SAMPLES.items() if p==path)
                    chosen[label]=canonical
                bad=deepcopy(canonical)
                ck=next(iter(bad['checks'].values()))
                ck['require']['condition']={'domainrole':{'is':'1'}}
                if validator.is_valid(bad):raise ValueError('schema accepted obsolete condition/alias')
                counts['invalid_wrapper_rejected']+=1
            except (ValueError,AssertionError,KeyError,TypeError) as e:
                failed.append({'path':path,'error':str(e)[:350]})
    if (counts['assessments'],counts['tests'])!=(872,1375):
        raise ValueError('source count drift')
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    (out/'canonical-operators.editor.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
    for name,doc in chosen.items():
        (out/(name+'.canonical.research.yaml')).write_text(
           '# RESEARCH ONLY — not normative 0.4, runtime/evidence parity not proven\n'
           +yaml.safe_dump(doc,sort_keys=False,allow_unicode=True,width=110))
    result={'source_sha256':digest,'counts':dict(counts),'failures':failed,
            'samples':sorted(chosen),'operator_map':FRIENDLY_TO_SOURCE,
            'compatibility':'All original source item, State and record requirements preserved'}
    (out/'report.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    (out/'report.md').write_text(markdown_report(result))
    return result


def markdown_report(result):
    c=result['counts']
    rows=sorted(((key.replace('operator_','',1),value) for key,value in c.items()
                 if key.startswith('operator_') and key!='operator_aliases_removed'),
                key=lambda x:(-x[1],x[0]))
    lines=['# Existing SCAP-NG comparison operators — six-STIG proof','',
      '**Research only; this is not the adopted 0.4 schema or scanner semantics proof.**','',
      f"- **{c['exact_assessments']}/{c['assessments']}** complete automated Assessments, **{c['exact_tests']}/{c['tests']}** named Tests exactly inverted.",
      f"- Replaced **{c['operator_aliases_removed']}** English-first comparison aliases with existing SCAP-NG operators.",
      f"- Reject old-condition mutations in **{c['invalid_wrapper_rejected']}** source-backed Assessments.",
      '- Item, matching, record, field and State quantifiers unchanged from the prior experiment.',
      '- 201 importer-legacy all_exist Tests remain explicit and unchanged.','',
      '## Windows 11 role query (real SV-253495)','',
      '```yaml', 'require:', '  items: at_least_one', '  match: all', '  states:', '    or:',
      '      - result:', '          records: at_least_one', '          match: all', '          domainrole: {equals: "1"}',
      '      - result:', '          records: at_least_one', '          match: all', '          domainrole: {equals: "3"}', '```','',
      '## Source-derived comparison conversions','',
      '| Previous operator alias → existing operator | Instances |', '| --- | ---: |']
    lines.extend(f'| `{k}` | {v} |' for k,v in rows)
    lines.extend(['', '## Limits', '',
      '- Exact dictionary round-trip is not independent proof of OVAL scanner/runtime/evidence equivalence.',
      '- Structural predicates and value-matching cardinalities are unchanged; genuine boolean values (`false`/`true`) remain data.',
      '- The remaining source-shape exception must not be repaired speculatively.', '',
      '## Rejected source Assessments', ''])
    lines.extend(f"- `{x['path']}`: {x['error']}" for x in result['failures'])
    lines.extend(['','## Full source-backed examples','','See the neighboring `*.canonical.research.yaml` files.',''])
    return '\n'.join(lines)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--archive',required=True)
    p.add_argument('--base-schema',required=True)
    p.add_argument('--out',required=True)
    args=p.parse_args()
    print(json.dumps(proof(args.archive,args.base_schema,args.out),indent=2)[:4500])