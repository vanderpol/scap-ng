"""Independent source facts for approved Windows nullable/NTUSER acquisition."""
from functools import lru_cache
from pathlib import Path
import xml.etree.ElementTree as ET

from v04_source_package_semantics import keys, need, literal, source_hierarchy

ROOT = Path(__file__).resolve().parents[1]
X = '{http://www.w3.org/2001/XMLSchema}'
NIL = '{http://www.w3.org/2001/XMLSchema-instance}nil'
NULLABLE_FIELDS = {
    'windows.ntuser': {'name': 'string'},
    'windows.appcmdlistconfig': {'identifier': 'string'},
    'windows.fileeffectiverights': {'filename': 'string'},
    'independent.environmentvariable': {'pid': 'int'},
}


def nil_selector(node, capability, name):
    """Preserve acquisition nil; never treat it as an empty string predicate."""
    datatype = NULLABLE_FIELDS.get(capability, {}).get(name)
    keys(node, {NIL, 'datatype'}, 'nil acquisition selector')
    need(datatype is not None and node.get(NIL) in ('true', '1')
         and node.get('datatype', 'string') == datatype
         and not len(node) and not (node.text or '').strip(),
         'nil selector outside bounded proof')
    return None


@lru_cache(maxsize=1)
def ntuser_defaults():
    """Pin the original defaults; do not import converter behavior routes."""
    schema = ET.parse(ROOT / 'third_party/scap-1.4-schemas/oval_5.12.3/windows-definitions-schema.xsd').getroot()
    node = schema.find(X + "complexType[@name='NTUserBehaviors']")
    need(node is not None, 'missing original NTUSER behavior contract')
    defaults = {n.get('name'): n.get('default') for n in node.findall(X + 'attribute')}
    need(defaults == {'include_default': 'false', 'max_depth': '-1',
                     'recurse_direction': 'none', 'windows_view': '64_bit',
                     'item_creation': 'key_and_name_exist'}, 'original NTUSER defaults changed')
    choices = node.find(X + "attribute[@name='item_creation']")
    need({n.get('value') for n in choices.findall('.//' + X + 'enumeration')} ==
         {'key_and_name_exist', 'every_ntuser'}, 'original NTUSER item creation changed')
    # Explicit deprecated windows_view/upward recursion remain unsupported.
    # The native mapping intentionally has no windows_view authoring field.
    return defaults


def ntuser_behaviors(node, key):
    defaults = ntuser_defaults()
    if node is not None:
        keys(node, {'include_default', 'item_creation', 'max_depth', 'recurse_direction'},
             'NTUSER behaviors')
        need(not len(node) and not (node.text or '').strip(), 'nonempty NTUSER behaviors')
    attributes = {} if node is None else node.attrib
    include = attributes.get('include_default', defaults['include_default'])
    creation = attributes.get('item_creation', defaults['item_creation'])
    need(creation in ('key_and_name_exist', 'every_ntuser'), 'unknown original NTUSER item creation')
    traversal = ET.Element('behaviors', {k: v for k, v in attributes.items()
                                       if k in ('max_depth', 'recurse_direction')})
    return {'include_default': literal('boolean', include)['value'],
            'item_creation': creation, **source_hierarchy(traversal, key)}
