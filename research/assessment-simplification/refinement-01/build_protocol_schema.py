"""Disposable protocol schema for the isolated DNS adapter experiment."""
import json
from pathlib import Path


def closed(properties, **extra):
    return {'type': 'object', 'properties': properties, 'required': list(properties),
            'additionalProperties': False, **extra}


def schema():
    text = {'type': 'string', 'minLength': 1}
    observation = {'oneOf': [
        closed({'status': {'enum': ['complete','incomplete']}, 'count': {'type': 'integer', 'minimum': 0}}),
        closed({'status': {'enum': ['error','not_collected']}})]}
    doc = closed({
        'format': {'const': 'research.dns-rr.v1'}, 'snapshot_id': text,
        'inventory': closed({'status': {'enum': ['complete','incomplete','error','not_collected']},
                            'keys': {'type': 'array', 'uniqueItems': True, 'items': text}}),
        'zones': {'type': 'array', 'items': closed({
            'key': text, 'integrated': {'type': 'boolean'}, 'signed': {'type': 'boolean'},
            'rr': closed({t: observation for t in ('RRSIG','DNSKEY','NSEC3')})})}
    })
    return {'$schema': 'https://json-schema.org/draft/2020-12/schema',
            'title': 'EXPERIMENTAL DNS query envelope; not SCAP-NG normative schema',
            'description': 'Key membership, key uniqueness across rows and scope completeness require the decoder. No policy Boolean from the collector.', **doc}


if __name__ == '__main__':
    Path(__file__).with_name('dns-envelope.schema.json').write_text(json.dumps(schema(),indent=2)+'\n')
