#!/usr/bin/env python3
"""Check XSD passage reconciliation against actual proposed schema descriptions.

The committed extraction is a provenance snapshot. Re-harvesting against pinned
XSD checkouts verifies the source; this offline audit verifies complete statement
routing and ensures that no A/B prose is missing from its schema destination.
"""
from collections import Counter,defaultdict
from hashlib import sha256
import argparse,json
from pathlib import Path
import re
import generate_documentation as reference

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('docs/fidelity')
CLASS_DISPOSITION={'A':'retained','B':'adapted','C':'withheld','D':'withheld','E':'excluded'}


def encode(value):return json.dumps(value,indent=2,ensure_ascii=False)+'\n'


def audit(root=ROOT):
    source=json.loads((root/BASE/'source-documentation.json').read_text())
    statements=json.loads((root/BASE/'source-statements.json').read_text())['statements']
    rows=[json.loads(line) for line in (root/BASE/'crosswalk.jsonl').read_text().splitlines()]
    docs=reference.schemas(root)
    caps={c['capability']:c for c in source['capabilities']}
    expected={};actual=Counter();counts=defaultdict(Counter)
    for cap,c in caps.items():
        bindings=Counter(json.dumps(b,sort_keys=True) for b in c['documentation'])
        bydoc=Counter()
        for s in statements.values():bydoc[s['document']]+=1
        expected[cap]=sum(bydoc[b['documentation']] for b in c['documentation'])
    for sid,statement in statements.items():
        doc=source['documents'][statement['document']]
        if doc['text'][statement['start']:statement['end']]!=statement['text']:
            raise ValueError('Source statement span mismatch: '+sid)
    by_document=defaultdict(list)
    for statement in statements.values():by_document[statement['document']].append(statement)
    for docid,doc in source['documents'].items():
        ranges=sorted((s['start'],s['end']) for s in by_document[docid])
        position=0
        for start,end in ranges:
            if start<position or doc['text'][position:start].strip():
                raise ValueError('Source text omitted or overlapped: '+docid)
            position=end
        if doc['text'][position:].strip():raise ValueError('Source text omitted: '+docid)
    seen=set();semantic=[];shell=[]
    for row in rows:
        cap=row['capability'];sid=row['statement'];statement=statements[sid];doc=source['documents'][statement['document']]
        classification=row['classification']
        if classification not in CLASS_DISPOSITION or row['disposition']!=CLASS_DISPOSITION[classification]:
            raise ValueError('Invalid classification/disposition: '+sid)
        binding=json.dumps(row['binding'],sort_keys=True)
        identity=(cap,sid,binding)
        if identity in seen:raise ValueError('Duplicate reconciliation row: '+sid)
        seen.add(identity)
        if row['binding'] not in caps[cap]['documentation'] or row['binding']['documentation']!=statement['document']:
            raise ValueError('Wrong capability/source association: '+cap+':'+sid)
        actual[cap]+=1;counts[cap][classification]+=1
        if classification in ('A','B'):
            uri=row['destination'];fragment=row['destination_text'];value=reference.node(docs,uri)
            if value.get('description','')[row['destination_start']:row['destination_end']]!=fragment:
                raise ValueError('Lost applicable source passage: '+cap+':'+sid)
            if row['destination_pointer']!=uri+'/description':raise ValueError('Wrong destination pointer')
        elif row.get('destination') or row.get('destination_text'):
            raise ValueError('Withheld/excluded text promoted to native prose: '+cap+':'+sid)
        if classification in ('C','D'):
            semantic.append({'capability':cap,'statement':sid,'classification':classification,'reason':row['reason'],
                             'source_file':doc['file'],'source_commit':doc['commit'],'source_xpath':doc['xpath'],
                             'source_text':statement['text'],'source_version':doc['version']})
        if cap=='independent.shellcommand' and (row['binding']['direct'] or 'ShellCommand' in (row['binding'].get('declaration')or'')):
            shell.append({'statement':sid,'role':row['binding']['role'],'source_xpath':doc['xpath'],'source_text':statement['text'],
                          'classification':classification,'disposition':row['disposition'],'reason':row['reason'],
                          'destination':row.get('destination_pointer'),'native_text':row.get('destination_text')})
    for cap,total in expected.items():
        if actual[cap]!=total:raise ValueError('Unreconciled source passages: '+cap)
    capstats=[]
    for cap,c in sorted(caps.items()):
        count=counts[cap]
        capstats.append({'capability':cap,'source_version':c['source_version'],'outside_5123':c['outside_5123'],
            'documentation_passages':len({b['documentation'] for b in c['documentation']}),
            'statement_bindings':actual[cap],'retained':count['A'],'adapted':count['B'],'withheld':count['C']+count['D'],
            'excluded':count['E'],'classification_counts':dict(sorted(count.items())),
            'reconciliation_complete':actual[cap]==expected[cap],
            'runtime_equivalence':'not established'})
    total=Counter(r['classification'] for r in rows)
    coverage={'format':'scap-ng-documentation-fidelity-coverage-1','meaning':'Complete reconciliation means every extracted source statement has a checked disposition, not approved native runtime semantics.',
        'totals':{'capabilities':len(caps),'within_5123':sum(not c['outside_5123'] for c in caps.values()),
                  'outside_5123':sum(c['outside_5123'] for c in caps.values()),'unique_documentation_passages':len(source['documents']),
                  'unique_statements':len(statements),'capability_statement_bindings':len(rows),'retained':total['A'],
                  'adapted':total['B'],'withheld':total['C']+total['D'],'excluded':total['E'],
                  'classification_counts':dict(sorted(total.items())),'complete_source_reconciliations':len(capstats)},
        'capabilities':capstats}
    report='# Shellcommand source fidelity review\n\n'
    report+='Compared with the complete pinned Test/Object/State/Item annotations and the referenced ShellCommandBehaviors declarations. Source statements can require adaptation or withholding independently; native execution semantics are not inferred.\n\n'
    report+='[Before](shellcommand-before.md) · [Generated after](../reference/capabilities/independent.shellcommand.md) · [Exact crosswalk](crosswalk.jsonl) · [Semantic ledger](semantic-ledger.jsonl).\n\n'
    report+='| Source passage | Disposition | Destination / rationale |\n| --- | --- | --- |\n'
    for row in shell:
        text=row['source_text'].replace('|','\\|').replace('\n',' ')
        after=(row['native_text']or row['reason']).replace('|','\\|').replace('\n',' ')
        report+=f'| `{row["statement"]}` — {text} | {row["classification"]}: {row["disposition"]} | {after} |\n'
    outputs={BASE/'coverage.json':encode(coverage),BASE/'semantic-ledger.jsonl':''.join(json.dumps(r,sort_keys=True,ensure_ascii=False)+'\n'for r in semantic),
             BASE/'shellcommand-review.json':encode(shell),BASE/'SHELLCOMMAND-REVIEW.md':report}
    outputs[BASE/'manifest.json']=encode({'format':'scap-ng-documentation-fidelity-1','source_inputs':{str(BASE/name):sha256((root/BASE/name).read_bytes()).hexdigest() for name in ['source-documentation.json','source-statements.json','crosswalk.jsonl']},
        'derived':{str(p):sha256(text.encode()).hexdigest() for p,text in sorted(outputs.items())},
        'proposed_schemas':{str(p):sha256((root/p).read_bytes()).hexdigest() for _,p in docs.values()}})
    return outputs


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');a=p.parse_args();outputs=audit()
    for path,text in outputs.items():
        target=ROOT/path
        if a.check:
            if not target.exists()or target.read_text()!=text:raise SystemExit('Stale fidelity output: '+str(path))
        else:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
    print(encode(json.loads(outputs[BASE/'coverage.json'])['totals']).strip())


if __name__=='__main__':main()
