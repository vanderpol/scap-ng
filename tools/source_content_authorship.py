#!/usr/bin/env python3
"""Non-normative helper for future SCAP-NG content-authorship migration research.

This does not emit 0.2.0 source fields. It exists to make the proposed 0.3.0
source-Definition attribution rules deterministic and testable.
"""
from __future__ import annotations


def author_from_oval_definition_id(definition_id: str | None) -> str | None:
    """Return a conservative author attribution from a source OVAL Definition ID.

    Unknown namespaces intentionally return None rather than guessing from the
    repository, converter, package filename, or current maintainer.
    """
    value = (definition_id or "").strip().lower()
    if not value:
        return None
    if "disa" in value:
        return "DISA"
    if "navwar" in value or "niwc" in value:
        return "NIWC"
    return None
