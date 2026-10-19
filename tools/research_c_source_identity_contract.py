#!/usr/bin/env python3
"""Refs #245: common source identity/provenance contract for C authoring.

C alias is NOT the source OVAL/A Object/State/Test/Variable ID. Original IDs
remain typed execution/provenance identities; every source binding is
required, injective and bounded. No automatic source matching, deduplication,
inference or best-effort migration. Shared by Apache + original OVAL Set.
"""
from __future__ import annotations
from hashlib import sha256
import json
import re

ALIASES=re.compile(r"[a-z][a-z0-9_-]{0,127}\Z")
MAX_BINDINGS=512

def source_digest(document):
    """Deterministic structural checksum. Not a signature or authentication."""
    try:
        raw=json.dumps(document,sort_keys=True,ensure_ascii=False,
                       allow_nan=False,separators=(",",":")).encode("utf-8")
    except (ValueError,TypeError,UnicodeError) as err:
        raise ValueError("source provenance cannot digest invalid typed graph") from err
    return sha256(raw).hexdigest()

def require_author_binding_catalog(author_mapping,provenance_mapping, *,
                                   label,source_id_field=None,
                                   min_entries=1,max_entries=MAX_BINDINGS):
    """Reject missing, duplicate, nontext and unbound authored identities.

    Provenance values are exact source ID strings, or typed source metadata
    records with a required source_id field. Callers separately validate the
    entire typed source metadata record.
    """
    if (not isinstance(author_mapping,dict) or
        not isinstance(provenance_mapping,dict) or
        type(label) is not str or not label or
        not min_entries<=len(author_mapping)<=max_entries or
        set(author_mapping)!=set(provenance_mapping)):
        raise ValueError("source identity binding catalog incomplete: "+str(label))
    ids=set()
    for alias,record in provenance_mapping.items():
        if type(alias) is not str or not ALIASES.fullmatch(alias):
            raise ValueError("unreviewed C source alias in "+label)
        if source_id_field is None:
            key=record
        elif isinstance(record,dict):
            key=record.get(source_id_field)
        else:
            key=None
        if type(key) is not str or not key.strip():
            raise ValueError("source identity missing from "+label)
        if key in ids:
            raise ValueError("source identity reused across aliases in "+label)
        ids.add(key)
    return {alias:(record if source_id_field is None
                   else record[source_id_field])
            for alias,record in provenance_mapping.items()}

def require_pinned_authoring(author,expected_sha256):
    if (type(expected_sha256) is not str or len(expected_sha256)!=64
        or not re.fullmatch(r"[0-9a-f]{64}",expected_sha256) or
        source_digest(author)!=expected_sha256):
        raise ValueError("source proof requires exactly original authoring content")
    return True
