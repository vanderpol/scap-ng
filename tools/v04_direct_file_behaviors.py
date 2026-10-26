"""Bounded text-file acquisition behaviors, separate from matching predicates.

Only the approved nonrecursive Textfilecontent54 contract is enabled here.
Unknown traversal/view attributes fail closed rather than being discarded.
"""
from v04_direct_scap_source import attributes, ensure

BOOLEAN_DEFAULTS = {'ignore_case': False, 'multiline': True, 'singleline': False}
ITEM_CREATION = {'all_object_elements_fullfilled', 'filepath_exists'}
FILESYSTEMS = {'all': 'all', 'local': 'local', 'defined': 'same'}


def file_behaviors(element):
    """An optional original behaviors element -> explicit native parameters."""
    values = {} if element is None else element.attrib
    if element is not None:
        attributes(element, set(BOOLEAN_DEFAULTS) | {'item_creation', 'recurse_file_system'})
        ensure(not len(element) and not (element.text or '').strip(), 'behaviors must have no content')
    result = {}
    for name, default in BOOLEAN_DEFAULTS.items():
        value = values.get(name, 'true' if default else 'false')
        ensure(value in ('true', 'false', '1', '0'), 'invalid original behavior boolean: ' + name)
        result[name] = value in ('true', '1')
    creation = values.get('item_creation', 'all_object_elements_fullfilled')
    ensure(creation in ITEM_CREATION, 'unsupported item_creation')
    filesystem = values.get('recurse_file_system', 'all')
    ensure(filesystem in FILESYSTEMS, 'unsupported original filesystem scope')
    result.update(item_creation=creation, filesystem=FILESYSTEMS[filesystem])
    return result
