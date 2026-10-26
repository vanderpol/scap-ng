"""Source field contracts for two approved current-system policy acquisitions.

Input is one original State entity plus its versioned capability mapping; output
is a copy with the original OVAL typed-entity default made explicit. No source
tree is changed. The independent proof reader derives these defaults separately
from the original XSD, rather than importing this conversion helper.
"""
from copy import deepcopy

from v04_direct_scap_source import UnsupportedSource, ensure, local_name

POLICIES = frozenset({'windows.passwordpolicy', 'windows.lockoutpolicy'})
NONNEGATIVE = {'windows.passwordpolicy': {'max_passwd_age'},
               'windows.lockoutpolicy': {'force_logoff', 'lockout_duration'}}


def policy_entity(element, mapping):
    """Check source types/ranges, preserving Variable checks for evaluation."""
    if mapping['capability'] not in POLICIES:
        return element
    field = local_name(element)
    types = mapping['native']['field_datatypes'].get(field)
    ensure(types in (['integer'], ['boolean']), 'unsupported policy field datatype')
    datatype = 'int' if types == ['integer'] else 'boolean'
    ensure(element.get('datatype', datatype) == datatype, 'policy field source datatype mismatch')
    result = deepcopy(element)
    result.set('datatype', datatype)
    if field in NONNEGATIVE[mapping['capability']] and not element.get('var_ref'):
        try:
            value = int(element.text or '')
        except ValueError as error:
            raise UnsupportedSource('policy field requires an integer literal') from error
        ensure(value >= 0, 'policy source literal must be nonnegative')
    return result
