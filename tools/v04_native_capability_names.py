"""Approved native identity migration only (Decision 5; #255/#268).

Original OVAL QNames/IDs and frozen proof pins are unchanged. This table is
identity data, not converter logic. Current native validators reject old names.
"""
RENAMES = {'independent.environmentvariable58': 'independent.environmentvariable', 'independent.sql512': 'independent.sql', 'independent.textfilecontent54': 'independent.textfilecontent', 'macos.nvram512': 'macos.nvram', 'macos.plist511': 'macos.plist', 'macos.pwpolicy512': 'macos.pwpolicy', 'solaris.package511': 'solaris.package.ips', 'unix.process58': 'unix.process', 'windows.fileeffectiverights53': 'windows.fileeffectiverights', 'windows.regkeyeffectiverights53': 'windows.regkeyeffectiverights', 'windows.user_sid55': 'windows.user_sid'}


def canonical_capability(name):
    return RENAMES.get(name, name) if isinstance(name, str) else name


def archival_witness_identities(value):
    """Decode only capability identities; literal expected text is untouched."""
    if isinstance(value, dict):
        return {key: canonical_capability(child) if key == 'capability' and isinstance(child, str)
                else archival_witness_identities(child) for key, child in value.items()}
    if isinstance(value, list):
        return [archival_witness_identities(child) for child in value]
    return value


def rename_native_identities(value, *, reverse=False):
    """Explicit archival/contract identity projection; never native validation."""
    mapping = {v: k for k, v in RENAMES.items()} if reverse else RENAMES
    def visit(node):
        if isinstance(node, str):
            for old, new in mapping.items():
                node = node.replace(old, new)
            return node
        if isinstance(node, dict):
            return {visit(k): visit(v) for k, v in node.items()}
        if isinstance(node, list):
            return [visit(v) for v in node]
        return node
    return visit(value)
