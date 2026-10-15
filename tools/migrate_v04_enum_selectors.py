#!/usr/bin/env python3
"""Research-only, lossless source migration for OVAL enum-valued Object selectors.

Reviewed OVAL mappings sometimes encode a selector field as a *literal enum
value*, e.g. windows.registry select.hive: local_machine. The 0.4 single
authored grammar instead uses select.hive: {equals: local_machine}.

This function NEVER guesses a comparator: literal conversion is permitted ONLY
when a value is in the reviewed selector_value_enums. The exceptional constant
full-enum Windows selector uses OVAL's documented implicit var_check=all.
The inverse transformation is structurally exact; typed dynamic/regex or
collection inputs are left unchanged for their respective source rules.
"""
from copy import deepcopy


def _certified_constant_enum(document, variable_id, allowed):
    """Constrain the research rewrite to one fully known, unique enum domain.

    This is a structural source proof, not a claim that 0.4 live scanner or
    OVAL object var_check semantics have been independently verified.
    """
    if not isinstance(variable_id,str) or not isinstance(allowed,list) or not allowed:
        return None
    assessment=document.get("assessment",document)
    variables=assessment.get("variables",{}) if isinstance(assessment,dict) else {}
    variable=variables.get(variable_id) if isinstance(variables,dict) else None
    if not isinstance(variable,dict):
        return None
    if variable.get("kind")!="constant" or variable.get("datatype")!="string":
        return None
    expression=variable.get("expression")
    if not isinstance(expression,dict) or set(expression)!={"literal"}:
        return None
    values=expression["literal"]
    if not isinstance(values,list) or not values:
        return None
    if any(not isinstance(v,str) for v in values):
        return None
    if len(values)!=len(set(values)) or len(allowed)!=len(set(allowed)):
        return None
    if len(values)!=len(allowed) or set(values)!=set(allowed):
        return None
    return values


def migrate(document, supported_mappings):
    out=deepcopy(document)
    changes=[]
    def walk(node,path,cap):
        if isinstance(node,list):
            for i,value in enumerate(node):
                walk(value,path+[i],cap)
            return
        if not isinstance(node,dict):return
        curcap=node.get("capability",cap)
        if not isinstance(curcap,str):curcap=cap
        select=node.get("select")
        if isinstance(select,dict) and curcap in supported_mappings:
            enums=supported_mappings[curcap].get("native",{}).get("selector_value_enums",{})
            for field,allowed in enums.items():
                if field not in select:continue
                val=select[field]
                if isinstance(val,str):
                    if val not in allowed:
                        raise ValueError(
                            f"Non-enumerated selector value {curcap}.{field}={val!r}; "
                            "refuse to infer equality or coerce it"
                        )
                    select[field]={"equals":val}
                    changes.append({"path":path+["select",field],"source_value":val,
                                    "capability":curcap,"field":field,
                                    "classification":"source_exact_literal_enum"})
                elif isinstance(val,dict) and set(val)=={"variable"}:
                    # This source has an explicit, named, constant Variable.
                    # Do NOT rewrite arbitrary variable references or infer
                    # value_match from an unexamined dynamic value population.
                    values=_certified_constant_enum(out,val["variable"],allowed)
                    if values is not None:
                        # Source OVAL omits var_check, whose documented
                        # OVAL 5.12.3 effective value is ALL. Do NOT silently
                        # substitute ONE, even if it seems more useful for
                        # the author's likely intent. Keep a reversible
                        # source identity record; scanner parity is separate.
                        new={"equals":list(values),"datatype":"string",
                             "value_match":"all"}
                        select[field]=new
                        changes.append({
                            "path":path+["select",field],
                            "source_value":deepcopy(val),
                            "target_value":deepcopy(new),
                            "capability":curcap,"field":field,
                            "classification":"constant_full_enum_implicit_all_source_exact",
                            "source_var_check":"all",
                            "source_var_check_provenance":"OVAL 5.12.3 documented implicit default",
                            "literal_count":len(values),
                        })
        for key,val in node.items():
            walk(val,path+[key],curcap)
    walk(out,[],None)
    return out,changes


def restore(document,changes):
    out=deepcopy(document)
    for note in reversed(changes):
        target=out
        for key in note["path"][:-1]:
            target=target[key]
        field=note["path"][-1]
        expected=note.get("target_value",{"equals":note["source_value"]})
        if target[field]!=expected:
            raise ValueError(f"Enum migration source proof mismatch at {note['path']}")
        target[field]=note["source_value"]
    return out
