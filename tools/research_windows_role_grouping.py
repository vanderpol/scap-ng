#!/usr/bin/env python3
"""#235: synthetic Windows DomainRole whole-State grouping experiment.

Based on the source fixture for Windows 11 SV-253495:
member alternative = ALL DomainRole records equal '1' OR ALL equal '3'.
standalone alternative = ALL records equal '0' OR ALL equal '2'.
The nesting and OR of WHOLE alternatives must not be simplified to
per-value membership. NOT a real WMI collector or full OVAL six-state engine.
"""
from __future__ import annotations
from research_requirements_first_evidence import PASS,FAIL,ERROR,UNKNOWN

ALLOWED_STATUSES={"complete","incomplete","error","not collected"}
ROLE_NAME={
  "0":"standalone_workstation",
  "1":"member_workstation",
  "2":"standalone_server",
  "3":"member_server",
  "4":"backup_domain_controller",
  "5":"primary_domain_controller"
}

def _or(results):
    if PASS in results:return PASS
    if ERROR in results:return ERROR
    if UNKNOWN in results:return UNKNOWN
    return FAIL

def _all(results):
    if FAIL in results:return FAIL
    if ERROR in results:return ERROR
    if UNKNOWN in results:return UNKNOWN
    return PASS

def one_whole_state(root, expected_role):
    status=root.get("status")
    if status not in ALLOWED_STATUSES:raise ValueError("invalid nested record status")
    if status=="error":return ERROR
    if status=="not collected":return UNKNOWN
    records=root.get("records",[])
    if not isinstance(records,list):raise ValueError("records must be list")
    if not records:return FAIL if status=="complete" else UNKNOWN
    results=[]
    for record in records:
        if not isinstance(record,dict):raise ValueError("invalid record")
        if record.get("status")=="error":
            results.append(ERROR)
        elif record.get("status")=="unknown":
            results.append(UNKNOWN)
        elif "domainrole" not in record:
            # Original record-state expected field is absent: the pinned
            # OVAL EntityStateFieldType reference reports Error.
            results.append(ERROR)
        else:
            role=record["domainrole"]
            if not isinstance(role,str):
                raise ValueError("source DomainRole field must be an exact string, no coercion")
            results.append(PASS if role==expected_role else FAIL)
    result=_all(results)
    return UNKNOWN if status=="incomplete" and result==PASS else result

def role_alternative(root,allowed_roles):
    """OR between complete homogeneous State alternatives, NOT set membership."""
    if not isinstance(allowed_roles,(tuple,list)) or not allowed_roles:
        raise ValueError("need distinct whole-State alternatives")
    return _or([one_whole_state(root,role) for role in allowed_roles])

def test_root_population(evidence,allowed_roles):
    """Root Items are separate groups; require >=1 root and ALL root Items match."""
    status=evidence.get("status")
    if status not in ALLOWED_STATUSES:raise ValueError("invalid root collection status")
    if status=="error":return ERROR
    if status=="not collected":return UNKNOWN
    items=evidence.get("items",[])
    if not isinstance(items,list):raise ValueError("items must be list")
    if not items:return FAIL if status=="complete" else UNKNOWN
    identities=set()
    answers=[]
    for item in items:
        ident=item.get("id")
        if not isinstance(ident,str) or not ident or ident in identities:
            return ERROR
        identities.add(ident)
        answers.append(role_alternative(item,allowed_roles))
    result=_all(answers)
    return UNKNOWN if status=="incomplete" and result==PASS else result

def normalized_fact_for_item(root):
    """Expose source-independent role facts without discarding grouping evidence.

    Provider promises NO conversion of [1,3] to a single native member role.
    Actual implementation would attach original typed nested records/provenance.
    """
    member=role_alternative(root,("1","3"))
    standalone=role_alternative(root,("0","2"))
    roles=root.get("records",[])
    complete=root.get("status")=="complete"
    known=[r.get("domainrole") for r in roles if isinstance(r,dict)]
    same=complete and bool(roles) and len(known)==len(roles) and len(set(known))==1
    if same:
        named=ROLE_NAME.get(known[0],"other")
    elif complete and roles and all("domainrole" in r for r in roles):
        named="mixed_records"
    elif not roles and complete:
        named="no_records"
    else:
        named="unresolved"
    return {
      "role_name":named,
      "domain_joined_member":member,
      "standalone":standalone,
      "source_record_count":len(roles),
      "source_record_status":root.get("status"),
    }
