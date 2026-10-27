"""Bounded text-file acquisition behaviors, separate from matching predicates.

Only the approved nonrecursive Textfilecontent54 contract is enabled here.
Unknown traversal/view attributes fail closed rather than being discarded.
"""
from v04_direct_scap_source import UnsupportedSource, attributes, ensure

BOOLEAN_DEFAULTS = {'ignore_case': False, 'multiline': True, 'singleline': False}
ITEM_CREATION = {'all_object_elements_fullfilled', 'filepath_exists'}
FILESYSTEMS = {'all': 'all', 'local': 'local', 'defined': 'same'}


def traversal_behaviors(element, acquisition, *, windows=False):
    """Translate shared FileBehaviors without changing a selector's meaning.

    OVAL defaults recursion to none. Downward traversal applies only to an
    equality path selector, never a full filepath. Deprecated upward recursion
    and unimplemented platform-view controls remain explicit blockers.
    """
    values = {} if element is None else element.attrib
    if element is not None:
        attributes(element, {'max_depth', 'recurse', 'recurse_direction', 'recurse_file_system'})
        ensure(not len(element) and not (element.text or '').strip(), 'behaviors must have no content')
    try:
        depth = int(values.get('max_depth', '-1'))
    except ValueError as error:
        raise UnsupportedSource('invalid original max_depth') from error
    ensure(depth >= -1, 'original max_depth must be -1 or nonnegative')
    direction = values.get('recurse_direction', 'none')
    ensure(direction in ('none', 'down'), 'unsupported/deprecated recursion direction')
    options = ({'directories': 'directories', 'junctions': 'junctions',
                'junctions and directories': 'junctions_and_directories'} if windows else
               {'directories': 'directories', 'symlinks': 'symlinks',
                'symlinks and directories': 'symlinks_and_directories'})
    recurse = values.get('recurse', 'directories' if windows else 'symlinks and directories')
    ensure(recurse in options, 'unsupported/deprecated original recurse value')
    scope = values.get('recurse_file_system', 'all')
    ensure(scope in FILESYSTEMS, 'unsupported original filesystem scope')
    result = {'filesystem': FILESYSTEMS[scope]}
    directory = acquisition.get('directory')
    if direction == 'down' and 'full_path' not in acquisition and isinstance(directory, dict) and 'equals' in directory:
        result['traversal'] = {'max_depth': None if depth == -1 else depth, 'recurse': options[recurse]}
    return result


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
