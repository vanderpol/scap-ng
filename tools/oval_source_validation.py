"""Original OVAL XSD/Schematron validation with node-scoped diagnostics.

No conversion or source repair. The embedded Schematron extraction follows the
already-tested version-neutral algorithm in validate_embedded_schematron; this
module imports no historical conversion pipeline. Original assertions are copied
unchanged. Failed assertions and deprecation reports remain distinct.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from lxml import etree as E, isoschematron

OVAL = 'http://oval.mitre.org/XMLSchema/oval-definitions-5'
SCH = 'http://purl.oclc.org/dsdl/schematron'
SVRL = 'http://purl.oclc.org/dsdl/svrl'
XS = 'http://www.w3.org/2001/XMLSchema'


def embedded_schematron(paths):
    """Collect namespace declarations first, retaining every original pattern."""
    schema = E.Element('{' + SCH + '}schema', nsmap={'sch': SCH}, queryBinding='xslt')
    sources = [E.parse(str(p)) for p in paths]
    namespaces = {}
    for source in sources:
        for node in source.iter('{' + SCH + '}ns'):
            prefix, uri = node.get('prefix'), node.get('uri')
            if prefix in namespaces and namespaces[prefix] != uri:
                raise ValueError('Schematron namespace conflict: ' + prefix)
            if prefix not in namespaces:
                E.SubElement(schema, '{' + SCH + '}ns', prefix=prefix, uri=uri)
                namespaces[prefix] = uri
    for source in sources:
        for node in source.iter('{' + SCH + '}pattern'):
            pattern = deepcopy(node)
            pattern.set('id', 'source-' + str(len(schema)) + '-' + (node.get('id') or 'unnamed'))
            schema.append(pattern)
    return schema, namespaces


def source_id(document, location, namespaces):
    """Attribute a child/attribute diagnostic to its nearest declared OVAL node.

    Unattributable errors remain component-wide. They must never disappear merely
    because the reporting XPath could not be resolved by the local evaluator.
    """
    try:
        matches = document.xpath(location, namespaces=namespaces)
    except E.XPathError:
        return None
    if not matches:
        return None
    node = matches[0]
    if not isinstance(node, E._Element):
        node = node.getparent() if hasattr(node, 'getparent') else None
    while node is not None:
        if node.get('id'):
            return node.get('id')
        node = node.getparent()
    return None


class SourceValidator:
    """Compile pinned schemas once per source namespace combination."""
    def __init__(self, schema_directory):
        self.directory = Path(schema_directory).resolve()
        self.cache = {}

    def schemas(self, families):
        families = tuple(sorted(families))
        if families not in self.cache:
            paths = [self.directory / name for name in ('oval-common-schema.xsd', 'oval-definitions-schema.xsd')]
            paths += [self.directory / (family + '-definitions-schema.xsd') for family in families]
            umbrella = E.Element('{' + XS + '}schema', nsmap={'xs': XS})
            for path in paths[1:]:
                original = E.parse(str(path))
                E.SubElement(umbrella, '{' + XS + '}import', namespace=original.getroot().get('targetNamespace'),
                             schemaLocation=path.as_uri())
            schema, namespaces = embedded_schematron(paths)
            self.cache[families] = (E.XMLSchema(umbrella),
                isoschematron.Schematron(schema, store_report=True), namespaces,
                {p.name: sha256(p.read_bytes()).hexdigest() for p in paths})
        return self.cache[families]

    def validate(self, original):
        document = E.ElementTree(deepcopy(original))
        families = {E.QName(n).namespace.split('#')[1] for n in original.iter()
                    if isinstance(n.tag, str) and (E.QName(n).namespace or '').startswith(OVAL + '#')}
        xsd, schematron, namespaces, hashes = self.schemas(families)
        namespaces = {**{k: v for k, v in original.nsmap.items() if k}, **namespaces}
        issues = []
        xsd.validate(document)
        for error in xsd.error_log:
            issues.append({'validator': 'XSD', 'kind': 'invalid', 'message': error.message,
                           'location': error.path, 'source_id': source_id(document, error.path, namespaces)
                           if error.path else None})
        schematron.validate(document)
        for node in schematron.validation_report.iter():
            if node.tag not in ('{' + SVRL + '}failed-assert', '{' + SVRL + '}successful-report'):
                continue
            message = ' '.join(''.join(node.itertext()).split())
            kind = ('invalid' if node.tag.endswith('failed-assert') else
                    'deprecated' if 'DEPRECATED' in message.upper() else 'report')
            location = node.get('location')
            issues.append({'validator': 'Schematron', 'kind': kind, 'message': message,
                           'test': node.get('test'), 'location': location,
                           'source_id': source_id(document, location, namespaces) if location else None})
        return {'status': 'INVALID' if any(i['kind'] == 'invalid' for i in issues) else 'VALID',
                'schema_sha256': hashes, 'issues': issues}
