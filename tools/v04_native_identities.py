"""Native scope identities, never original external source IDs (#255/#268)."""
import re


def require_identity(identity, *, suffix=None, label='native identity'):
    if (not isinstance(identity, str) or len(identity) > 64 or
            re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identity) is None or
            (suffix is not None and not identity.endswith('-' + suffix))):
        raise ValueError(label + ': expected lower-case meaningful slug <=64 characters' +
                         (' ending in -' + suffix if suffix else ''))
    return identity


def assessment_identities(assessment):
    require_identity(assessment.get('id'), label='Assessment ID')
    for section, suffix in (('tests', 'test'), ('shared_objects', 'object'),
                            ('variables', 'variable'), ('inputs', 'input'), ('dependencies', None)):
        declarations = assessment.get(section, {})
        if not isinstance(declarations, dict):
            raise ValueError(section + ': expected native identity mapping')
        for identity in declarations:
            require_identity(identity, suffix=suffix, label=section + ' ID')
