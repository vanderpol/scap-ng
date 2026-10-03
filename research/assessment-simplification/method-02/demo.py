"""Print explainable failures from four new-method synthetic observations."""
import json
from pathlib import Path
import yaml
from requirements import Value, Item, Population, evaluate
from audit_coverage import evaluate as audit_evaluate, SYSCALLS

HERE = Path(__file__).resolve().parent


def main():
    examples = {n: yaml.safe_load((HERE/'examples'/f'{n}.yaml').read_text())
                for n in ('home-files','dns','apache','audit')}
    permission = evaluate(examples['home-files'], {
        'user-files': Population([Item('/home/alice/.profile', {'permissions': Value(0o604)})]),
        'root-files': Population([Item('/root/.profile', {'permissions': Value(0o700)})])})
    zone = Item('example.test', {'integrated': Value(False), 'signed': Value(True),
            'records': Population([Item('sig', {'type': Value('RRSIG')}), Item('key', {'type': Value('DNSKEY')})])})
    dns = evaluate(examples['dns'], {'zones': Population([zone])})
    directive = lambda key,name,value: Item(key, {'name':Value(name),'value':Value(value)})
    apache = evaluate(examples['apache'], {'installations': Population([Item('httpd-one', {
        'main': Population([directive('conf:1','KeepAlive','Off'),directive('conf:2','KeepAlive','On'),directive('conf:3','MaxKeepAliveRequests',100)]),
        'loaded': Population([])})])})
    lines = [f'-a always,exit -F arch={arch} -S {",".join(SYSCALLS)} {actor}'
             for arch in ('b32','b64') for actor in ('-F auid=0','-F auid>=1000 -F auid!=unset')]
    lines[2] = lines[2].replace(',lsetxattr','')
    audit = audit_evaluate(examples['audit'], lines)
    report = {'kind': 'synthetic method experiments, not target scans',
              'cases': {'permissions': permission, 'dns': dns, 'apache': apache, 'audit': audit},
              'explanations': [
                  '/home/alice/.profile allows other.read, which is outside the stated permission allowance.',
                  'example.test has RRSIG and DNSKEY records but is missing NSEC3.',
                  'httpd-one explicitly declares KeepAlive Off at conf:1; a later On does not satisfy an all-occurrence requirement.',
                  'Loaded b64 rules do not cover lsetxattr for audit user ID 0.']}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
