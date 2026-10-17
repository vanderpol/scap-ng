#!/usr/bin/env python3
"""Research #235: normalized structured Windows DNS zone/key fixture evidence.

NOT a Windows DNS collector, PowerShell execution, scanner, or source-equivalent
SCAP 1.4 conversion. The caller supplies raw-ish structured Get-DnsServerZone
and Get-DnsServerSigningKey fixture records, with independent completion flags.
Missing fields, duplicate identities and uncorrelatable keys are reported as
INCOMPLETE, never silently treated as compliant or absent.
"""
from __future__ import annotations

PROVIDER="windows.dns.zone_signing_evidence"
VERSION="0.1.0"
ZONE_KEYS=("ZoneName","ZoneType","IsAutoCreated","IsReverseLookupZone","IsDsIntegrated","IsSigned")
KEY_KEYS=("KeyId","ZoneName","KeyType","Days","Hours")
SKIP_TYPES={"Forwarder"}
SKIP_ZONES={"trustanchors"}
KEY_TYPES={"ZoneSigningKey","KeySigningKey"}

def normalize(zones:list[dict], keys:list[dict], *,
              zones_status="complete", keys_status="complete"):
    if zones_status not in {"complete","incomplete","error","not collected"}:
        raise ValueError("bad zone collection status")
    if keys_status not in {"complete","incomplete","error","not collected"}:
        raise ValueError("bad key collection status")
    if not isinstance(zones,list) or not isinstance(keys,list):
        raise ValueError("zone and key rows must be lists")
    diagnostics=[]
    def note(why,**details):
        diagnostics.append({"reason":why,**details})
    by_identity={}
    output=[]
    for i,zone in enumerate(zones):
        if not isinstance(zone,dict):
            note("invalid_zone",row=i)
            continue
        if not set(ZONE_KEYS)<=set(zone):
            note("zone_fields_missing",row=i,
                 fields=sorted(set(ZONE_KEYS)-set(zone)))
            continue
        name=zone["ZoneName"]
        if not isinstance(name,str) or not name:
            note("zone_name_invalid",row=i)
            continue
        if any(not isinstance(zone[x],bool)
               for x in ("IsAutoCreated","IsReverseLookupZone","IsDsIntegrated","IsSigned")):
            note("zone_boolean_type_invalid",row=i)
            continue
        if not isinstance(zone["ZoneType"],str):
            note("zone_type_invalid",row=i)
            continue
        if zone["ZoneType"] in SKIP_TYPES or name.casefold() in SKIP_ZONES or zone["IsAutoCreated"]:
            continue
        ident=name.casefold()
        if ident in by_identity:
            note("duplicate_zone_identity",zone=name,row=i)
            continue
        item={
            "id":ident,
            "name":name,
            "direction":"reverse" if zone["IsReverseLookupZone"] else "forward",
            "directory_integration":zone["IsDsIntegrated"],
            "signed":zone["IsSigned"],
            "key_signing_keys":[],
            "zone_signing_keys":[],
        }
        by_identity[ident]=item
        output.append(item)

    seen_keys=set()
    for i,key in enumerate(keys):
        if not isinstance(key,dict):
            note("invalid_key",row=i);continue
        if not set(KEY_KEYS)<=set(key):
            note("key_fields_missing",row=i,fields=sorted(set(KEY_KEYS)-set(key)))
            continue
        zone_name=key["ZoneName"]
        key_id=key["KeyId"]
        if not isinstance(zone_name,str) or not zone_name or not isinstance(key_id,str) or not key_id:
            note("key_identity_invalid",row=i);continue
        parent=by_identity.get(zone_name.casefold())
        if not parent:
            # A key may belong to a zone intentionally filtered out, but
            # this minimal provider cannot safely assume it is irrelevant
            # without an explicit collection filter contract.
            note("key_parent_not_in_normalized_zones",row=i,zone=zone_name)
            continue
        kind=key["KeyType"]
        if kind not in KEY_TYPES:
            # Original source filters key types; other key kinds are excluded.
            continue
        ident=(parent["id"],key_id)
        if ident in seen_keys:
            note("duplicate_signing_key_identity",row=i,zone=zone_name,key_id=key_id)
            continue
        seen_keys.add(ident)
        days,hours=key["Days"],key["Hours"]
        if any(not isinstance(x,int) or isinstance(x,bool) for x in (days,hours)) or days<0 or not 0<=hours<24:
            note("key_validity_typed_duration_invalid",row=i,zone=zone_name)
            continue
        key_item={
            "id":key_id,
            "zone_id":parent["id"],
            "kind":kind,
            "validity_hours":days*24+hours,
            "source_days":days,
            "source_hours":hours,
        }
        field="zone_signing_keys" if kind=="ZoneSigningKey" else "key_signing_keys"
        parent[field].append(key_item)

    if zones_status=="error" or keys_status=="error":
        status="error"
    elif zones_status!="complete" or keys_status!="complete" or diagnostics:
        status="incomplete"
    else:status="complete"

    return {"provider":PROVIDER,"version":VERSION,"status":status,
            "zone_source_status":zones_status,"key_source_status":keys_status,
            "zones":output,"diagnostics":diagnostics,
            "zone_count":len(output),
            "forward_zone_count":sum(1 for z in output if z["direction"]=="forward")}
