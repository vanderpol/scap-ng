#!/usr/bin/env python3
"""#237: normalize independently collected WMI SELECT query snapshots.

Offline research adapter only. Does NOT invoke CIM/WMI/PowerShell or attest
that the query executed, that Windows access was complete, or that the OVAL
WMI Item schema agrees with the projection. Preserve query identity verbatim.
"""
from __future__ import annotations

PROVIDER="windows.wmi.query"
VERSION="offline-query-snapshot-v0.1"
FLAGS={"complete","incomplete","error","not collected","not applicable"}


def normalize(snapshot, *, namespace, query):
    from research_b_source_wmi_lowering import validate_wmi_query
    validate_wmi_query(namespace,query)
    using={"namespace":namespace,"query":query}
    def bad(reason):
        return {"provider":PROVIDER,"version":VERSION,"using":using,
                "status":"error","items":[],"diagnostics":[{"reason":reason}]}
    if not isinstance(snapshot,dict) or set(snapshot)!={"using","status","rows"}:
        return bad("snapshot_missing_or_unexpected_fields")
    if snapshot["using"] != using:
        return bad("acquisition_query_identity_mismatch")
    status=snapshot["status"]
    rows=snapshot["rows"]
    if not isinstance(status,str) or status not in FLAGS or not isinstance(rows,list):
        return bad("unsupported_collection_status_or_rows")
    if status not in {"complete","incomplete"} and rows:
        return bad("terminal_status_with_unverified_rows")
    items=[]
    for i,row in enumerate(rows):
        if not isinstance(row,dict) or not row or any(
            not isinstance(name,str) or not name or not isinstance(value,(str,int,bool))
            for name,value in row.items()
        ):
            return bad("unsupported_or_malformed_WMI_result_row")
        # WMI Items can have richer identity than this stable row index.
        # This projection is only safe for existence counts in a fixture.
        items.append({"id":f"wmi-query-row:{i}","fields":dict(row)})
    return {"provider":PROVIDER,"version":VERSION,"using":using,
            "status":status,"items":items,"diagnostics":[]}
