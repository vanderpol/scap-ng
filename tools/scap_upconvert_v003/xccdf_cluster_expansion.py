#!/usr/bin/env python3
"""Order-preserving XCCDF cluster-id expansion for migration.

This module operates on ordered Profile operations before any lossy dictionary
projection. It intentionally normalizes cluster indirection away.
"""
from __future__ import annotations


class ClusterExpansionError(RuntimeError):
    pass


RULE_GROUP_OPS = {"select", "refine-rule"}
VALUE_OPS = {"set-value", "set-complex-value", "refine-value"}


def _compatible(operation_type, member_kind):
    if operation_type in RULE_GROUP_OPS:
        return member_kind in {"rule", "group"}
    if operation_type in VALUE_OPS:
        return member_kind == "value"
    raise ClusterExpansionError(f"unsupported Profile operation type: {operation_type}")


def expand_cluster_operations(operations, clusters, direct_ids):
    """Expand ordered Profile operations that target XCCDF cluster-id values.

    operations: ordered mappings containing at least type and idref.
    clusters: mapping cluster-id -> ordered member mappings with id and kind.
    direct_ids: set of concrete XCCDF item ids.

    Returns a new ordered list. Cluster members are emitted in their supplied
    source order at the exact position of the source Profile operation.
    """
    direct_ids = set(direct_ids)
    out = []

    for source_index, op in enumerate(operations):
        op_type = op["type"]
        target = op["idref"]
        is_direct = target in direct_ids
        is_cluster = target in clusters

        if is_direct and is_cluster:
            raise ClusterExpansionError(
                f"ambiguous XCCDF Profile idref {target!r}: matches both item id and cluster-id"
            )

        if is_direct or not is_cluster:
            row = dict(op)
            row.setdefault("source_index", source_index)
            out.append(row)
            continue

        members = [
            member for member in clusters[target]
            if _compatible(op_type, member["kind"])
        ]
        if not members:
            raise ClusterExpansionError(
                f"cluster {target!r} has no members compatible with {op_type}"
            )

        for member in members:
            row = dict(op)
            row["idref"] = member["id"]
            row["source_index"] = source_index
            row["expanded_from_cluster"] = target
            row["cluster_member_kind"] = member["kind"]
            out.append(row)

    return out
