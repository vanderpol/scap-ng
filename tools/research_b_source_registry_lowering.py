#!/usr/bin/env python3
"""#237: fail-closed SCAP-NG 0.3 -> B fixture IR registry-source lowerer.

Only direct single-Test, one literal HKLM registry value and one literal State comparison or a bounded type/value AND on the same Item. The source's unspecified Windows registry view is retained
as an explicitly UNRESOLVED compatibility question, not set to 64-bit.
Source 0.3 YAML is not original SCAP 1.4 OVAL XML: no parity claim.
"""
from __future__ import annotations


def lower_source_registry_assessment(source):
    if not isinstance(source,dict) or set(source)!={"assessment"}:
        raise ValueError("one converted registry Assessment document required")
    a=source["assessment"]
    allowed={"assessment_title","class","evaluate","id","mode","purpose",
             "specification","tests","version"}
    if not isinstance(a,dict) or a.get("mode")!="automated" or set(a)-allowed:
        raise ValueError("unsupported source Assessment dependencies")
    tests=a.get("tests")
    if not isinstance(tests,dict) or len(tests)!=1:
        raise ValueError("one direct registry Test required")
    tid,t=next(iter(tests.items()))
    if not isinstance(tid,str) or not tid or a.get("evaluate")!={"test":tid}:
        raise ValueError("direct literal registry Test reference required")
    if not isinstance(t,dict) or set(t)!={
        "capability","existence","match","object","reported_elements",
        "states","test_title"}:
        raise ValueError("unsupported registry Test semantics")
    if t["capability"]!="windows.registry" or t["existence"]!="one_or_more" or (
        t["match"] not in {"all","one","one_or_more"}) or (
        t["reported_elements"]!="all"):
        raise ValueError("unsupported source registry Test existence/matching")
    states=t["states"]
    if not isinstance(states,list) or len(states)!=1 or not isinstance(states[0],dict):
        raise ValueError("one source registry State entry required")

    def lower_field(state):
        if not isinstance(state,dict) or set(state)!={
            "existence","field","match","operation","value"}:
            raise ValueError("unsupported registry State child/cardinality")
        if state["existence"]!="one_or_more" or state["match"]!="all" or (
                state["operation"]!="equals"):
            raise ValueError("registry State child requires literal equality and source entity cardinality")
        field=state["field"]
        value=state["value"]
        if field=="value":
            if type(value) not in (int,str) or (
                    type(value) is int and not -(2**63)<=value<(2**63)):
                raise ValueError("registry State value requires a typed scalar literal")
        elif field=="type":
            if type(value) is not str or value not in {"dword","qword","string"}:
                raise ValueError("registry State type requires a recognized source type")
        else:
            raise ValueError("unsupported registry source State field")
        return {"field":field,"operation":"equals","expected":value,
                "entity_existence":"at_least_one_exists","entity_check":"all"}

    state=states[0]
    if set(state)=={"all"}:
        all_states=state["all"]
        if not isinstance(all_states,list) or len(all_states)!=2:
            raise ValueError("bounded registry source AND requires two child fields")
        children=[lower_field(child) for child in all_states]
        if {c["field"] for c in children}!={"type","value"}:
            raise ValueError("registry State AND requires type and value on same Item")
        normalized_state={"all":children}
    else:
        normalized_state=lower_field(state)
        if normalized_state["field"]!="value":
            raise ValueError("standalone registry pilot only supports value State")
    obj=t["object"]
    if not isinstance(obj,dict) or set(obj)!={"capability","object_title","select"} or (
        obj["capability"]!="windows.registry"):
        raise ValueError("unsupported registry source Object set/behaviors")
    selector=obj["select"]
    if not isinstance(selector,dict) or set(selector)!={"hive","key","name"}:
        raise ValueError("source registry Object has unsupported or explicit view metadata")
    if selector["hive"]!="local_machine":
        raise ValueError("only literal HKLM source is supported")
    def exact(value,field):
        if (not isinstance(value,dict) or set(value)!={"operation","value"} or
            value["operation"]!="equals" or type(value["value"]) is not str
            or not value["value"]):
            raise ValueError(field+" requires exact literal equality")
        return value["value"]
    key=exact(selector["key"],"key");name=exact(selector["name"],"name")
    return {
        "kind":"compat_oval_registry_view_invariant",
        "source_assessment_id":a["id"],
        "source_test_id":tid,
        "provider":"windows.registry_source_views",
        "using":{"hive":"HKLM","key":key,"name":name},
        "source_view":"unspecified_requires_xml_parity",
        "existence":"at_least_one_exists",
        "check":{"all":"all","one":"only one","one_or_more":"at least one"}[t["match"]],
        "state":normalized_state,
    }
