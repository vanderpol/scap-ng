#!/usr/bin/env python3
"""Deterministic XCCDF 1.2 check-content resolution for SCAP-NG migration.

This helper models build-time migration semantics only. It does not fetch
network resources itself; callers provide a resolver over a closed/pinned
source set.
"""
from __future__ import annotations


class CheckContentResolutionError(RuntimeError):
    pass


def resolve_check_content(alternatives, embedded_content, resolver):
    """Resolve ordered XCCDF check-content-ref alternatives.

    alternatives: iterable of mappings with required href and optional name.
    embedded_content: embedded check-content payload or None.
    resolver: callable(href, name) -> payload or None. Returning None or
      raising FileNotFoundError/LookupError means this alternative did not
      resolve and the next source alternative is attempted.

    Returns a dict containing selected payload plus deterministic migration
    evidence for all alternatives actually attempted.
    """
    attempts = []
    for index, ref in enumerate(alternatives):
        href = ref["href"]
        name = ref.get("name")
        try:
            payload = resolver(href, name)
        except (FileNotFoundError, LookupError) as exc:
            attempts.append({
                "index": index,
                "href": href,
                "name": name,
                "resolved": False,
                "error": str(exc),
            })
            continue

        if payload is None:
            attempts.append({
                "index": index,
                "href": href,
                "name": name,
                "resolved": False,
                "error": None,
            })
            continue

        attempts.append({
            "index": index,
            "href": href,
            "name": name,
            "resolved": True,
            "error": None,
        })
        return {
            "source": "check-content-ref",
            "selected_index": index,
            "href": href,
            "name": name,
            "content": payload,
            "attempts": attempts,
        }

    if embedded_content is not None:
        return {
            "source": "check-content",
            "selected_index": None,
            "href": None,
            "name": None,
            "content": embedded_content,
            "attempts": attempts,
        }

    raise CheckContentResolutionError(
        "no XCCDF check-content-ref resolved and no embedded check-content is available"
    )
