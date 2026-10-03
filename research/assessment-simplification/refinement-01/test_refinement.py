import copy
import itertools
import json
from pathlib import Path
import unittest
from lxml import etree
import yaml
from jsonschema import Draft202012Validator
from oval_result_truth_tables import aggregate_operator, evaluate_collected_object_test
from table_expansion import expand
from source_contracts import project_xml, project_native, assert_source_and_tree, assert_and_tree
from dns_records import decode, evaluate
from apache_occurrences import collect
from build_protocol_schema import schema

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]


def table(rid):
    return yaml.safe_load((HERE/'tables'/f'{rid}.yaml').read_text())


def envelope(keys=('one',), integrated=False):
    return {'format': 'research.dns-rr.v1', 'snapshot_id': 'test-snapshot',
            'inventory': {'status': 'complete', 'keys': list(keys)},
            'zones': [{'key': key, 'integrated': integrated, 'signed': True,
                       'rr': {t: {'status': 'complete', 'count': 1} for t in ('RRSIG','DNSKEY','NSEC3')}} for key in keys]}


def snapshot(text='', status='complete'):
    return {'status': status, 'text': text}


class TableTests(unittest.TestCase):
    def test_full_source_contracts_not_just_patterns(self):
        for rid in ('SV-258179','SV-258236'):
            path = STUDY/'evidence/rhel_9'/rid/'source-oval.xml'
            graph = json.loads((path.parent/'graph.json').read_text())
            ids = assert_source_and_tree(path, graph['closures'][0]['seed']['name'])
            source = dict(project_xml(path))
            doc = expand(table(rid))
            generated = project_native(doc)
            self.assertEqual([source[k] for k in ids], [v for _,v in generated])
            self.assertEqual(len(ids), len(assert_and_tree(doc)))

    def test_pinned_default_is_at_least_one_exists(self):
        schema = etree.parse(str(ROOT/'third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd'))
        attrs = schema.xpath("//*[local-name()='complexType' and @name='TestType']/*[local-name()='attribute' and @name='check_existence']")
        self.assertEqual(len(attrs), 1)
        self.assertEqual(attrs[0].get('default'), 'at_least_one_exists')
        audit = expand(table('SV-258179'))['assessment']['tests']
        self.assertEqual(sum(t['existence']=='some' for t in audit.values()), 8)

    def test_duplicate_predicates_retain_distinct_identity(self):
        doc = expand(table('SV-258179'))['assessment']
        contracts = project_native({'assessment':doc})
        self.assertEqual(len(contracts),24)
        self.assertEqual(len({json.dumps(c,sort_keys=True) for _,c in contracts}),22)
        self.assertEqual(len(set(doc['tests'])),24)

    def test_duplicate_ids_runtime_inputs_and_unknown_fields_rejected(self):
        for mutate in (
            lambda t: t['rows'].append(copy.deepcopy(t['rows'][0])),
            lambda t: t.update(organizational_input={'syscall':'other'}),
            lambda t: t['rows'][0].update(command='find /'),
            lambda t: t['rows'][0].update(syscall='$(anything)'),
            lambda t: t['templates'].update({'pattern-template-1':'${runtime_input}'}),
        ):
            t = table('SV-258179'); mutate(t)
            with self.assertRaises((ValueError,KeyError)): expand(t)

    def test_row_reordering_retains_named_contracts(self):
        t = table('SV-258179'); first=dict(project_native(expand(t)))
        t['rows'].reverse()
        self.assertEqual(first,dict(project_native(expand(t))))

    def test_unknown_defaults_and_malformed_publisher_shapes_rejected(self):
        for mutate in (
            lambda t:t['defaults'].update(command='echo hidden'),
            lambda t:t['defaults'].update(collect={'ignore_case':True}),
            lambda t:t['defaults'].update(instance={'value':'2'}),
            lambda t:t['rows'][0].pop('syscall'),
            lambda t:t.update(rows={'runtime':'selection'}),
            lambda t:t['rows'].append(None),
        ):
            t=table('SV-258179');mutate(t)
            with self.assertRaises(ValueError):expand(t)

    def test_all_collection_flags_and_state_results_per_source_row(self):
        flags = ('complete','incomplete','error','does not exist','not collected','not applicable')
        outcomes = ('true','false','error','unknown','not evaluated','not applicable')
        for rid in ('SV-258179','SV-258236'):
            xml = STUDY/'evidence/rhel_9'/rid/'source-oval.xml'
            src = sorted((c for _,c in project_xml(xml)), key=lambda c:json.dumps(c,sort_keys=True))
            dst = sorted((c for _,c in project_native(expand(table(rid)))), key=lambda c:json.dumps(c,sort_keys=True))
            for source, proposal in zip(src,dst,strict=True):
                for flag, count, result in itertools.product(flags,(0,1,2),outcomes):
                    if source['states'] and count == 0 and flag == 'incomplete':
                        # The inherited helper requires at least one supplied State
                        # result. Do not fabricate an Item to test empty partial collection.
                        continue
                    def evaluate_contract(c):
                        states = bool(c['states'])
                        return evaluate_collected_object_test(flag,
                            existence={'all':'all_exist','some':'at_least_one_exists'}[c['existence']],
                            check=c['match'], has_state=states, exists=count,
                            item_results=[result]*max(count,1) if states else None)
                    self.assertEqual(evaluate_contract(source),evaluate_contract(proposal))

    def test_flatten_and_preserves_six_state_aggregation(self):
        domain = ('true','false','error','unknown','not evaluated','not applicable')
        for a,b,c in itertools.product(domain,repeat=3):
            nested=aggregate_operator('AND',[aggregate_operator('AND',[a,b]),c])
            self.assertEqual(nested,aggregate_operator('AND',[a,b,c]))

    def test_one_global_population_hides_missing_required_backend(self):
        self.assertEqual(evaluate_collected_object_test('complete',existence='at_least_one_exists',exists=11,
            has_state=True,item_results=['true']*11),'true')
        per_row=['true']*11+[evaluate_collected_object_test('does not exist',existence='at_least_one_exists',has_state=True)]
        self.assertEqual(aggregate_operator('AND',per_row),'false')

    def test_anomaly_repair_changes_source_contract(self):
        t=table('SV-258179')
        r=next(r for r in t['rows'] if r['id']=='audit-64-bit-invocations-lsetxattr-system-call-by-root-user')
        self.assertEqual(r['arch'],'b32')
        prior=dict(project_native(expand(t)))
        r['arch']='b64'
        self.assertNotEqual(prior,dict(project_native(expand(t))))


class DnsTests(unittest.TestCase):
    def test_experimental_protocol_schema_rejects_error_count_and_coercion(self):
        doc=schema();Draft202012Validator.check_schema(doc)
        v=Draft202012Validator(doc)
        example=envelope()
        self.assertTrue(v.is_valid(example))
        example['zones'][0]['rr']['NSEC3']={'status':'error','count':0}
        self.assertFalse(v.is_valid(example))
        example=envelope();example['zones'][0]['rr']['NSEC3']['count']=True
        self.assertFalse(v.is_valid(example))
        # Local JSON shape cannot enforce key membership; decoder handles it.
        example=envelope();example['zones'][0]['key']='undeclared'
        self.assertTrue(v.is_valid(example))
        with self.assertRaises(ValueError):decode(json.dumps(example))

    def test_two_zone_predicates_exhaustive(self):
        for bits in itertools.product((False,True),repeat=8):
            doc=envelope(('one','two'))
            for i,z in enumerate(doc['zones']):
                z['signed']=bits[i*4]
                for offset,rr in enumerate(('RRSIG','DNSKEY','NSEC3'),1):
                    z['rr'][rr]['count']=int(bits[i*4+offset])
            self.assertEqual(evaluate(decode(json.dumps(doc))), 'true' if all(bits) else 'false')

    def test_complete_empty_and_all_integrated_exceptions(self):
        self.assertEqual(evaluate(decode(json.dumps(envelope(())))),'true')
        doc=envelope(('one','two'),True)
        doc['zones'][0]['rr']['NSEC3']={'status':'error'}
        self.assertEqual(evaluate(decode(json.dumps(doc))),'true')
        doc['zones'][1]['integrated']=False
        self.assertEqual(evaluate(decode(json.dumps(doc))),'error')

    def test_partial_inventory_never_proves_good(self):
        for keys in ((),('one',)):
            doc=envelope(keys);doc['inventory']['status']='incomplete'
            self.assertEqual(evaluate(decode(json.dumps(doc))),'unknown')
        doc=envelope();doc['inventory']['status']='error'
        self.assertEqual(evaluate(decode(json.dumps(doc))),'error')

    def test_per_type_error_unknown_and_decisive_violation(self):
        for status,outcome in [('error','error'),('not_collected','unknown'),('incomplete','unknown')]:
            doc=envelope();obs={'status':status}
            if status=='incomplete':obs['count']=1
            doc['zones'][0]['rr']['NSEC3']=obs
            self.assertEqual(evaluate(decode(json.dumps(doc))),outcome)
            doc['zones'][0]['signed']=False
            self.assertEqual(evaluate(decode(json.dumps(doc))),'false')

    def test_missing_key_complete_error_partial_unknown(self):
        doc=envelope(('one','two'));doc['zones'].pop()
        self.assertEqual(evaluate(decode(json.dumps(doc))),'error')
        doc['inventory']['status']='incomplete'
        self.assertEqual(evaluate(decode(json.dumps(doc))),'unknown')

    def test_malformed_and_duplicate_records_rejected(self):
        for mutate in (
            lambda d:d['zones'].append(copy.deepcopy(d['zones'][0])),
            lambda d:d['zones'][0]['rr']['NSEC3'].update(count=True),
            lambda d:d['zones'][0]['rr']['NSEC3'].update(count=-1),
            lambda d:d['zones'][0]['rr'].pop('NSEC3'),
            lambda d:d['zones'][0].update(integrated='false'),
            lambda d:d['zones'][0]['rr'].update(NSEC3={'status':'error','count':0}),
        ):
            doc=envelope();mutate(doc)
            with self.assertRaises(ValueError):decode(json.dumps(doc))
        with self.assertRaises(ValueError):decode('{"format":"x","format":"y"}')

    def test_nonzero_timeout_truncation_and_output_limits(self):
        data=json.dumps(envelope())
        for kwargs in ({'exit_code':1},{'timed_out':True},{'maximum_bytes':3}):
            with self.assertRaises(ValueError):decode(data,**kwargs)
        with self.assertRaises(ValueError):decode(data[:-5])

    def test_wrong_json_container_types_are_protocol_errors(self):
        with self.assertRaises(ValueError):decode('[]')
        for mutate in (
            lambda d:d.update(inventory=None),
            lambda d:d['zones'].append(None),
            lambda d:d['zones'][0].update(key=[]),
            lambda d:d['zones'][0].update(rr=None),
            lambda d:d['zones'][0]['rr'].update(NSEC3=None),
        ):
            doc=envelope();mutate(doc)
            with self.assertRaises(ValueError):decode(json.dumps(doc))

    def test_unrelated_favorable_records_cannot_cover_one_zone(self):
        doc=envelope(('one','two','three'))
        for i,z in enumerate(doc['zones']):
            for j,rr in enumerate(('RRSIG','DNSKEY','NSEC3')):z['rr'][rr]['count']=int(i==j)
        self.assertTrue(all(any(z['rr'][rr]['count'] for z in doc['zones']) for rr in ('RRSIG','DNSKEY','NSEC3')))
        self.assertEqual(evaluate(decode(json.dumps(doc))),'false')


class ApacheTests(unittest.TestCase):
    def test_nested_literal_includes_preserve_order_space_and_context(self):
        files={'/main':snapshot('KeepAlive On\nInclude "conf/space name.conf"\nMaxKeepAliveRequests 100'),
               '/srv/httpd/conf/space name.conf':snapshot('<VirtualHost *:443>\nSession On\nInclude /cookie\n</VirtualHost>'),
               '/cookie':snapshot('SessionCookieName "session;HttpOnly;Secure"')}
        result=collect(files,'/main')
        self.assertEqual(result['status'],'complete')
        self.assertEqual([r['directive'] for r in result['rows']],['KeepAlive','Session','SessionCookieName','MaxKeepAliveRequests'])
        self.assertEqual(result['rows'][2]['context'],[['VirtualHost',('*:443',)]])
        self.assertEqual(result['rows'][2]['arguments'],['session;HttpOnly;Secure'])

    def test_repeated_includes_are_distinct_occurrences(self):
        result=collect({'/main':snapshot('Include /child\nInclude /child'),'/child':snapshot('KeepAlive Off')},'/main')
        self.assertEqual(len(result['rows']),2)
        self.assertNotEqual(result['rows'][0]['occurrence'],result['rows'][1]['occurrence'])

    def test_optional_absence_requires_native_absence_evidence(self):
        result=collect({'/main':snapshot('IncludeOptional /missing')},'/main')
        self.assertEqual(result['status'],'error')
        files={'/main':snapshot('IncludeOptional /missing'),'/missing':snapshot(status='does_not_exist')}
        self.assertEqual(collect(files,'/main')['status'],'complete')

    def test_optional_unreadable_is_not_absence(self):
        files={'/main':snapshot('IncludeOptional /hidden'),'/hidden':snapshot(status='error')}
        self.assertEqual(collect(files,'/main')['status'],'error')

    def test_cycles_limits_and_unsupported_grammar_are_explicit(self):
        cases=[({'/main':snapshot('Include /main')},{}),
               ({'/main':snapshot('Include /child'),'/child':snapshot('KeepAlive On')},{'maximum_files':1}),
               ({'/main':snapshot('Include conf/*.conf')},{}),
               ({'/main':snapshot('<IfModule ssl_module>\nKeepAlive On\n</IfModule>')},{})]
        for files,kwargs in cases:
            result=collect(files,'/main',**kwargs)
            self.assertEqual(result['status'],'error')
            self.assertTrue(result['diagnostics'])

    def test_no_effective_defaults_or_override_collapse(self):
        self.assertEqual(collect({'/main':snapshot('')},'/main')['rows'],[])
        rows=collect({'/main':snapshot('KeepAlive Off\nKeepAlive On')},'/main')['rows']
        self.assertEqual([r['arguments'] for r in rows],[['Off'],['On']])

    def test_unimplemented_expansion_and_bad_section_quotes_are_errors(self):
        for text in ('Include ${ROOT}/conf', 'KeepAlive On'+chr(92), '<Directory "unterminated>'):
            result=collect({'/main':snapshot(text)},'/main')
            self.assertEqual(result['status'],'error')
            self.assertTrue(result['diagnostics'])

    def test_installations_keep_separate_native_file_universes(self):
        one=collect({'/one/main':snapshot('DocumentRoot /one/www')},'/one/main',installation='one')
        two=collect({'/two/main':snapshot('DocumentRoot /two/www')},'/two/main',installation='two')
        self.assertEqual([(r['installation'],r['arguments'][0]) for r in one['rows']+two['rows']],
                         [('one','/one/www'),('two','/two/www')])

    def test_changed_server_root_cannot_resolve_include_against_old_root(self):
        files={'/main':snapshot('ServerRoot /other\nInclude conf/httpd.conf'),
               '/srv/httpd/conf/httpd.conf':snapshot('KeepAlive On'),
               '/other/conf/httpd.conf':snapshot('KeepAlive Off')}
        result=collect(files,'/main')
        self.assertEqual(result['status'],'error')
        self.assertFalse(any(r['directive']=='KeepAlive' for r in result['rows']))


if __name__ == '__main__':
    unittest.main()
