import copy
import itertools
from pathlib import Path
import random
import unittest
from lxml import etree
import yaml
from requirements import Value, Item, Population, compile_spec, evaluate, permission_mask, combine
from audit_coverage import parse, interval_coverage, evaluate as audit_evaluate, SYSCALLS, MAX_AUID

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent


def example(name):
    return yaml.safe_load((HERE/'examples'/f'{name}.yaml').read_text())


def files(modes, status='complete'):
    return Population([Item(str(i), {'permissions': Value(mode)}) for i, mode in enumerate(modes)], status)


def zone(key, *, signed=True, integrated=False, rr=('RRSIG', 'DNSKEY', 'NSEC3'), status='complete'):
    return Item(key, {'signed': Value(signed), 'integrated': Value(integrated),
                     'records': Population([Item(str(i), {'type': Value(t)}) for i,t in enumerate(rr)], status)})


def directives(values, status='complete'):
    return Population([Item(str(i), {'name': Value(name), 'value': Value(value)})
                       for i,(name,value) in enumerate(values)], status)


def installation(key, main=(('KeepAlive', 'On'), ('MaxKeepAliveRequests',100)), loaded=()):
    return Item(key, {'main': directives(main), 'loaded': directives(loaded)})


def audit_lines(*, grouped=True):
    return [f'-a always,exit -F arch={arch} -S {names} {actor} -k perm_mod'
            for arch in ('b32','b64')
            for actor in ('-F auid=0','-F auid>=1000 -F auid!=unset')
            for names in ([','.join(SYSCALLS)] if grouped else list(SYSCALLS))]


class Permissions(unittest.TestCase):
    def test_all_4096_modes_against_original_xml_boolean_state(self):
        xml = etree.parse(str(STUDY/'evidence/rhel_9/SV-257889/source-oval.xml'))
        state = next(s for s in xml.find('{*}states') if s.find('{*}suid') is not None)
        source_bits = {'suid':0o4000,'sgid':0o2000,'sticky':0o1000,'gwrite':0o20,
                       'gexec':0o10,'oread':0o4,'owrite':0o2,'oexec':0o1}
        self.assertEqual({etree.QName(e).localname for e in state}, set(source_bits))
        self.assertTrue(all(e.text == 'false' and e.get('operation','equals') == 'equals' for e in state))
        doc = example('home-files')
        for mode in range(0o10000):
            # Independent oracle directly evaluates each pinned State entity.
            source = all(not bool(mode & source_bits[etree.QName(e).localname]) for e in state)
            result = evaluate(doc, {'user-files': files([mode]), 'root-files': files([mode])})
            self.assertEqual(result['result'], 'true' if source else 'false', oct(mode))

    def test_0604_is_not_more_restrictive_than_0740(self):
        result=evaluate(example('home-files'), {'user-files': files([0o604]), 'root-files': files([0o700])})
        self.assertEqual(result['result'],'false')
        failure=next(f for f in result['findings'] if f['result']=='false')
        self.assertEqual(failure['detail']['forbidden'], ['other.read'])

    def test_source_root_and_user_empty_distinction(self):
        doc=example('home-files')
        self.assertEqual(evaluate(doc, {'user-files':files([]),'root-files':files([0o700])})['result'],'true')
        self.assertEqual(evaluate(doc, {'user-files':files([0o700]),'root-files':files([])})['result'],'false')

    def test_incomplete_error_unknown_and_decisive_bad_mode(self):
        doc=example('home-files')
        for status, expected in [('incomplete','unknown'),('not_collected','unknown'),('error','error')]:
            self.assertEqual(evaluate(doc, {'user-files': files([0o700],status), 'root-files':files([0o700])})['result'],expected)
            self.assertEqual(evaluate(doc, {'user-files':files([0o777],status),'root-files':files([0o700])})['result'],'false')
        row=Item('u', {'permissions':Value(status='unknown')})
        self.assertEqual(evaluate(doc, {'user-files':Population([row]),'root-files':files([0o700])})['result'],'unknown')

    def test_special_bits_and_invalid_modes_remain_visible(self):
        doc=example('home-files')
        for mode in (0o4700,0o2700,0o1700):
            self.assertEqual(evaluate(doc, {'user-files':files([mode]),'root-files':files([0o700])})['result'],'false')
        for mode in (True, -1, 0o10000, '0740'):
            self.assertEqual(evaluate(doc, {'user-files':files([mode]),'root-files':files([0o700])})['result'],'error')


class Dns(unittest.TestCase):
    def test_256_two_zone_truth_cases_against_direct_intent_formula(self):
        doc=example('dns')
        for bits in itertools.product((False,True),repeat=8):
            rows=[zone(str(i),signed=bits[i*4],rr=[t for j,t in enumerate(('RRSIG','DNSKEY','NSEC3'),1) if bits[i*4+j]]) for i in range(2)]
            self.assertEqual(evaluate(doc,{'zones':Population(rows)})['result'], 'true' if all(bits) else 'false')

    def test_original_server_wide_empty_and_integrated_exception(self):
        doc=example('dns')
        self.assertEqual(evaluate(doc,{'zones':Population([])})['result'],'true')
        self.assertEqual(evaluate(doc,{'zones':Population([zone('one',integrated=True,signed=False,rr=())])})['result'],'true')
        # Mixed population still evaluates integrated zones; no per-zone skip.
        mixed=Population([zone('one',integrated=True,signed=False,rr=()),zone('two')])
        self.assertEqual(evaluate(doc,{'zones':mixed})['result'],'false')

    def test_rr_types_cannot_be_borrowed_from_other_zones(self):
        rows=[zone(str(i),rr=(t,)) for i,t in enumerate(('RRSIG','DNSKEY','NSEC3'))]
        self.assertEqual(evaluate(example('dns'),{'zones':Population(rows)})['result'],'false')

    def test_duplicates_do_not_replace_missing_type(self):
        row=zone('one',rr=('RRSIG','RRSIG','DNSKEY'))
        self.assertEqual(evaluate(example('dns'),{'zones':Population([row])})['result'],'false')

    def test_partial_zone_inventory_cannot_prove_all_zones(self):
        doc=example('dns')
        for rows in ([],[zone('one')],[zone('one',integrated=True)]):
            self.assertEqual(evaluate(doc,{'zones':Population(rows,'incomplete')})['result'],'unknown')

    def test_positive_record_witnesses_and_unproven_absence(self):
        doc=example('dns')
        self.assertEqual(evaluate(doc,{'zones':Population([zone('one',status='incomplete')])})['result'],'true')
        self.assertEqual(evaluate(doc,{'zones':Population([zone('one',rr=('RRSIG',),status='incomplete')])})['result'],'unknown')
        for status,result in [('error','error'),('not_collected','unknown')]:
            self.assertEqual(evaluate(doc,{'zones':Population([zone('one',status=status)])})['result'],result)

    def test_unknown_record_type_is_not_an_empty_success(self):
        row=zone('one',rr=('RRSIG','DNSKEY'))
        row.fields['records'].items.append(Item('u',{'type':Value(status='unknown')}))
        self.assertEqual(evaluate(example('dns'),{'zones':Population([row])})['result'],'unknown')

    def test_known_bad_zone_dominates_other_unknown(self):
        row=zone('bad',signed=False,status='error')
        self.assertEqual(evaluate(example('dns'),{'zones':Population([row],'incomplete')})['result'],'false')


class Apache(unittest.TestCase):
    def test_independent_direct_predicates_36_same_installation_cases(self):
        doc=example('apache')
        for keep,limit,extra in itertools.product((None,'On','Off'),(None,0,99,100,101,1000),(False,True)):
            main=[]
            if keep is not None: main.append(('KeepAlive',keep))
            if limit is not None: main.append(('MaxKeepAliveRequests',limit))
            if extra: main.append(('KeepAlive','Off'))
            expected=keep == 'On' and limit is not None and limit >= 100 and not extra
            self.assertEqual(evaluate(doc,{'installations':Population([installation('one',main)])})['result'],'true' if expected else 'false')

    def test_default_does_not_prove_explicit_presence(self):
        self.assertEqual(evaluate(example('apache'),{'installations':Population([installation('one',())])})['result'],'false')

    def test_favorable_second_installation_does_not_repair_first(self):
        rows=[installation('bad',(('KeepAlive','On'),)),installation('good')]
        self.assertEqual(evaluate(example('apache'),{'installations':Population(rows)})['result'],'false')

    def test_loaded_group_is_optional_but_bad_occurrences_fail(self):
        doc=example('apache')
        self.assertEqual(evaluate(doc,{'installations':Population([installation('one')])})['result'],'true')
        self.assertEqual(evaluate(doc,{'installations':Population([installation('one',loaded=(('KeepAlive','Off'),))])})['result'],'false')

    def test_unreadable_group_and_unknown_selector_not_discarded(self):
        doc=example('apache');row=installation('one');row.fields['loaded'].status='error'
        self.assertEqual(evaluate(doc,{'installations':Population([row])})['result'],'error')
        row=installation('one');row.fields['loaded']=Population([Item('u',{'name':Value(status='unknown'),'value':Value('Off')})])
        self.assertEqual(evaluate(doc,{'installations':Population([row])})['result'],'unknown')

    def test_multiple_repeated_conflicting_values_keep_order_independent_all_policy(self):
        row=installation('one',(('KeepAlive','Off'),('KeepAlive','On'),('MaxKeepAliveRequests',100)))
        result=evaluate(example('apache'),{'installations':Population([row])})
        self.assertEqual(result['result'],'false')
        failure=next(f for f in result['findings'] if f['result']=='false')
        self.assertEqual(failure['detail']['settings'][0]['occurrences'][0], {'occurrence':'0','result':'false'})


class Audit(unittest.TestCase):
    def test_grouped_and_separate_rules_cover_same_24_obligations(self):
        spec=example('audit')
        for grouped in (False,True):
            result=audit_evaluate(spec,audit_lines(grouped=grouped))
            self.assertEqual(result['result'],'true')
            self.assertEqual(len(result['coverage']),24)

    def test_equivalent_rule_field_order_and_sentinel_spellings(self):
        for unset in ('unset','-1',str(MAX_AUID)):
            # Auid filter order may vary; architecture must stay before -S.
            rules=[line.replace(' -F auid>=1000 -F auid!=unset',' -F auid!=unset -F auid>=1000') for line in audit_lines()]
            rules=[r.replace('unset',unset) for r in rules]
            self.assertEqual(audit_evaluate(example('audit'),rules)['result'],'true')

    def test_missing_one_root_b64_syscall_is_not_covered(self):
        lines=audit_lines();lines[2]=lines[2].replace(',lsetxattr','')
        result=audit_evaluate(example('audit'),lines)
        self.assertEqual(result['result'],'false')
        self.assertTrue(any(r['architecture']=='b64' and r['syscall']=='lsetxattr' and r['actor']=='root-logins' and r['gaps'] for r in result['coverage']))

    def test_comment_and_prior_never_rule_remove_coverage(self):
        lines=audit_lines();lines[0]='# '+lines[0]
        self.assertEqual(audit_evaluate(example('audit'),lines)['result'],'false')
        lines=['-a never,exit -F arch=b64 -S lsetxattr -F auid=0']+audit_lines()
        self.assertEqual(audit_evaluate(example('audit'),lines)['result'],'false')
        # First matching always rule wins in this restricted model.
        self.assertEqual(audit_evaluate(example('audit'),audit_lines()+lines[:1])['result'],'true')

    def test_symbolic_actor_scope_cannot_be_proven_by_one_user(self):
        narrow=[line.replace('auid>=1000','auid=1000') for line in audit_lines()]
        self.assertEqual(audit_evaluate(example('audit'),narrow)['result'],'false')

    def test_two_disjoint_rules_can_cover_one_actor_range(self):
        lines=[]
        for line in audit_lines():
            if 'auid>=1000' in line:
                lines.extend([line+' -F auid<=1999',line.replace('auid>=1000','auid>=2000')])
            else:lines.append(line)
        self.assertEqual(audit_evaluate(example('audit'),lines)['result'],'true')

    def test_partition_against_independent_exhaustive_small_domain_oracle(self):
        rng=random.Random(1729)
        for _ in range(500):
            definitions=[(rng.choice(('always','never')),rng.choice(('=','!=','>=','<=','>','<')),rng.randrange(16))
                         for _ in range(rng.randrange(1,7))]
            lines=[f'-a {action},exit -F arch=b32 -S setxattr -F auid{op}{value}' for action,op,value in definitions]
            actual=interval_coverage(parse(lines),'b32','setxattr',0,15)['result']
            decisions=[]
            for uid in range(16):
                action=None
                for effect,op,val in definitions:
                    yes=(uid==val if op=='=' else uid!=val if op=='!=' else uid>=val if op=='>='
                         else uid<=val if op=='<=' else uid>val if op=='>' else uid<val)
                    if yes: action=effect;break
                decisions.append(action=='always')
            self.assertEqual(actual,'true' if all(decisions) else 'false')

    def test_extra_filters_numeric_calls_and_budgets_do_not_pass(self):
        for extra in (' -F success=1',' -F uid=0',' -F auid>4294967296'):
            self.assertEqual(audit_evaluate(example('audit'),[r+extra for r in audit_lines()])['result'],'unknown')
        # > max is well-formed but unsatisfiable, not unsupported syntax.
        self.assertEqual(audit_evaluate(example('audit'),[r+' -F auid>4294967295' for r in audit_lines()])['result'],'false')
        self.assertEqual(audit_evaluate(example('audit'),['-a always,exit -F arch=b64 -S 188'])['result'],'unknown')
        self.assertEqual(audit_evaluate(example('audit'),['-a always,exit -S setxattr -F arch=b64'])['result'],'unknown')
        self.assertEqual(audit_evaluate(example('audit'),audit_lines(),maximum_cells=0)['result'],'error')

    def test_source_mismatch_and_partial_order_cannot_prove_coverage(self):
        with self.assertRaises(ValueError):audit_evaluate(example('audit'),audit_lines(),source='persisted')
        for status,result in [('incomplete','unknown'),('not_collected','unknown'),('error','error')]:
            self.assertEqual(audit_evaluate(example('audit'),audit_lines(),status=status)['result'],result)


class Language(unittest.TestCase):
    def test_compile_all_three_examples(self):
        for name in ('home-files','dns','apache'):compile_spec(example(name))

    def test_typos_inputs_shadowing_deprecated_and_ambiguous_predicates_rejected(self):
        for mutate in (
            lambda d:d.update(organizational_inputs={'command':'anything'}),
            lambda d:d['objects']['zones'].update(command='find /'),
            lambda d:d['objects']['zones'].update(capability='windows.accesstoken'),
            lambda d:d['tests']['DNSSEC records']['require'].update(signd={'equals':True}),
            lambda d:d['tests']['DNSSEC records'].update(empty='automatic'),
            lambda d:d['tests']['DNSSEC records'].update(**{'as':'zones'}),
            lambda d:d['tests']['DNSSEC records']['require']['signed'].update(at_least=1),
        ):
            d=example('dns');mutate(d)
            with self.assertRaises(ValueError):compile_spec(d)

    def test_exception_does_not_hide_invalid_unexecuted_requirement(self):
        d=example('dns');d['tests']['DNSSEC records']['require']['typo']={'equals':True}
        with self.assertRaises(ValueError):evaluate(d,{'zones':Population([])})

    def test_duplicate_parent_identity_and_bad_field_types_fail(self):
        d=example('dns')
        self.assertEqual(evaluate(d,{'zones':Population([zone('same'),zone('same')])})['result'],'error')
        row=zone('one');row.fields['signed']=Value(1)
        self.assertEqual(evaluate(d,{'zones':Population([row])})['result'],'error')

    def test_malformed_and_duplicate_relationship_items_cannot_supply_witnesses(self):
        d=example('dns');row=zone('one')
        row.fields['records'].items[1].key='0'
        self.assertEqual(evaluate(d,{'zones':Population([row])})['result'],'error')
        self.assertEqual(evaluate(d,{'zones':Population([None])})['result'],'error')
        self.assertEqual(evaluate(d,{'zones':Population([], 'invented')})['result'],'error')

    def test_comparison_results_are_not_coerced_or_unknown_names_accepted(self):
        with self.assertRaises(ValueError):combine('all',['not applicable'])
        with self.assertRaises(ValueError):combine('mystery',['true'])
        self.assertEqual(combine('all',['false','unknown','error']),'false')
        self.assertEqual(combine('any',['true','unknown','error']),'true')


if __name__ == '__main__':
    unittest.main()
