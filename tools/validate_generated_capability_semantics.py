#!/usr/bin/env python3
# 0.2.0 reconciliation exact-head validation trigger: schema promotion complete; semantics unchanged.
# 0.2.0 freeze validation trigger: semantics unchanged; see transition freeze criteria.
# 0.2.0 final mainline reconciliation trigger: semantics unchanged; validates promoted schema/capability layout.
# 0.2.0 exact-head all-gates trigger: no semantic change.
# 0.2.0 post-layout-fix all-gates trigger: no semantic change.
# 0.2.0 post-registry-test-fix all-gates trigger: no semantic change.
"""Semantic validation that complements generated capability JSON Schemas.

JSON Schema handles structural/native vocabulary constraints. This module
handles source-backed cross-field and cross-reference rules that are clearer or
safer as semantic validation. Rules are intentionally narrow and capability
specific until proven reusable.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V03_MAPPING_DIR = ROOT / "schema" / "v0.3.0" / "capability-mappings" / "supported"


class CapabilitySemanticError(ValueError):
    pass


def _assessment_named_objects(assessment):
    """Return the named Object registry for the active Assessment version."""
    shared=assessment.get("shared_objects")
    if isinstance(shared,dict):
        return shared
    # Compatibility for frozen 0.2 and faithful/research pre-normalization trees.
    objects=assessment.get("objects")
    return objects if isinstance(objects,dict) else {}


def _is_variable_value(value):
    return (
        isinstance(value, dict)
        and set(value) == {"variable"}
        and isinstance(value.get("variable"), str)
        and bool(value["variable"])
    )


_STRING_LITERAL_DATATYPES = {
    "string",
    "binary",
    "version",
    "ipv4",
    "ipv6",
    "rpm_evr",
    "debian_evr",
    "fileset_revision",
    "ios_version",
}


def _native_literal_matches_datatype(value, datatype):
    """Return True when a literal uses the native JSON representation for datatype."""
    if _is_variable_value(value):
        return True
    if datatype == "boolean":
        return isinstance(value, bool)
    if datatype == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if datatype == "float":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False
        import math
        return math.isfinite(value)
    if datatype in _STRING_LITERAL_DATATYPES:
        return isinstance(value, str)
    # record literals are represented by structured predicate forms, never as
    # a scalar entity_value.
    return False


def _native_literal_or_collection_matches_datatype(value, datatype):
    if isinstance(value,list):
        return bool(value) and all(
            _native_literal_matches_datatype(item,datatype)
            for item in value
        )
    return _native_literal_matches_datatype(value,datatype)


def _iter_authored_predicates(node):
    """Yield scalar authored predicate dictionaries recursively."""
    if isinstance(node, dict):
        if {"value", "datatype"}.issubset(node):
            yield node
        for value in node.values():
            yield from _iter_authored_predicates(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_authored_predicates(value)


def validate_v02_native_literal_types(document):
    """Reject lexical/string stand-ins for typed native 0.2.0 literals."""
    assessment = document.get("assessment", document)
    specification = assessment.get("specification") or {}
    if specification.get("version") != "0.2.0":
        return []

    diagnostics = []
    for section in ("objects", "states"):
        for node_id, node in (assessment.get(section) or {}).items():
            for predicate in _iter_authored_predicates(node):
                value = predicate.get("value")
                datatype = predicate.get("datatype")
                if _is_variable_value(value):
                    continue
                if not _native_literal_matches_datatype(value, datatype):
                    diagnostics.append({
                        section[:-1]: node_id,
                        "code": "assessment.native_literal_datatype",
                        "datatype": datatype,
                        "value": value,
                        "message": (
                            "0.2.0 authored literals must use the native JSON "
                            "representation for their declared datatype"
                        ),
                    })
    return diagnostics


def validate_v03_native_literal_types(document):
    """Validate native 0.3 scalar/literal-collection JSON representations."""
    assessment=document.get("assessment",document)
    specification=assessment.get("specification") or {}
    if specification.get("version") != "0.3.0":
        return []

    diagnostics=[]
    for predicate in _iter_authored_predicates(assessment):
        value=predicate.get("value")
        datatype=predicate.get("datatype")
        if _is_variable_value(value):
            continue
        if not _native_literal_or_collection_matches_datatype(value,datatype):
            diagnostics.append({
                "code":"assessment.native_literal_datatype",
                "datatype":datatype,
                "value":value,
                "message":(
                    "0.3 authored literal scalars/collections must be non-empty "
                    "and every member must use the native JSON representation "
                    "for the declared datatype"
                ),
            })
    return diagnostics


EQUALITY_OPERATIONS={
    "equal", "equal_ci",
    "equals", "case_insensitive_equals",
}
EXACT_EQUALITY_OPERATIONS={"equal","equals"}
PATTERN_OPERATIONS={"match","pattern_match"}


FILE_SELECTION_CAPABILITIES={
    "unix.file",
    "file.hash",
    "windows.file",
    "windows.fileeffectiverights53",
    "independent.textfilecontent54",
    "independent.xmlfilecontent",
    "independent.yamlfilecontent",
    "linux.selinuxsecuritycontext",
}


def validate_file_selection_object(obj):
    """Return semantic diagnostics for native capabilities using file selection."""
    capability=obj.get("capability")
    if capability not in FILE_SELECTION_CAPABILITIES:
        return []

    diagnostics=[]
    select=obj.get("select") or {}
    traversal=obj.get("traversal")

    full_path=select.get("full_path")
    if full_path is not None and traversal is not None:
        diagnostics.append({
            "code":f"{capability}.full_path_no_traversal",
            "fields":["traversal"],
            "message":"full_path selection does not permit directory traversal",
        })

    directory=select.get("directory")
    directory_is_exact_binding=(
        isinstance(directory,dict)
        and set(directory)=={"from"}
        and isinstance(directory.get("from"),str)
    )
    if (
        isinstance(directory, dict)
        and not directory_is_exact_binding
        and directory.get("operation") not in EQUALITY_OPERATIONS
        and traversal is not None
    ):
        diagnostics.append({
            "code":f"{capability}.pattern_directory_no_traversal",
            "fields":["traversal"],
            "message":"non-equality directory selection cannot use traversal",
        })

    if capability == "independent.textfilecontent54":
        pattern=select.get("pattern")
        if isinstance(pattern,dict) and pattern.get("operation") not in PATTERN_OPERATIONS:
            diagnostics.append({
                "code":"independent.textfilecontent54.pattern_operation",
                "fields":["pattern"],
                "message":"textfilecontent54 pattern selector must use pattern-match semantics",
            })

    if capability == "independent.xmlfilecontent":
        xpath=select.get("xpath")
        if isinstance(xpath,dict) and xpath.get("operation") not in EXACT_EQUALITY_OPERATIONS:
            diagnostics.append({
                "code":"independent.xmlfilecontent.xpath_equal",
                "fields":["xpath"],
                "message":"xmlfilecontent xpath selector must use equal operation",
            })

    if capability == "independent.yamlfilecontent":
        for field in ("content","yamlpath"):
            value=select.get(field)
            if isinstance(value,dict) and value.get("operation") not in EXACT_EQUALITY_OPERATIONS:
                diagnostics.append({
                    "code":f"independent.yamlfilecontent.{field}_equal",
                    "fields":[field],
                    "message":f"yamlfilecontent {field} selector must use equal operation",
                })
        if "content" in select and traversal is not None:
            diagnostics.append({
                "code":"independent.yamlfilecontent.inline_content_no_traversal",
                "fields":["traversal"],
                "message":"inline YAML content selection cannot use file traversal",
            })

    if capability == "linux.selinuxsecuritycontext" and "pid" in select and traversal is not None:
        diagnostics.append({
            "code":"linux.selinuxsecuritycontext.pid_no_file_traversal",
            "fields":["traversal"],
            "message":"pid selection cannot use file traversal",
        })

    name=select.get("name", ...)
    if name is None:
        # null intentionally selects the directory itself.
        pass
    elif isinstance(name, dict):
        value=name.get("value")
        variable=_is_variable_value(value)
        pattern=name.get("operation") in PATTERN_OPERATIONS
        if value == "" and not (variable or pattern):
            diagnostics.append({
                "code":f"{capability}.name_empty",
                "fields":["name"],
                "message":"empty name requires a Variable reference or match semantics; use null to select the directory itself",
            })
        if (
            capability in {"windows.file","windows.fileeffectiverights53"}
            and isinstance(value, str)
            and not pattern
            and any(ch in value for ch in '\\/:*?>|<"')
        ):
            diagnostics.append({
                "code":f"{capability}.literal_name_characters",
                "fields":["name"],
                "message":"literal Windows file name contains path separator or reserved filename characters",
            })

    return diagnostics


def validate_unix_file_object(obj):
    """Backward-compatible focused helper for unix.file tests."""
    if obj.get("capability") != "unix.file":
        return []
    return validate_file_selection_object(obj)




def validate_equal_only_selectors(obj, capability, fields):
    if obj.get("capability") != capability:
        return []
    diagnostics=[]
    select=obj.get("select") or {}
    for field in fields:
        value=select.get(field)
        if isinstance(value,dict) and value.get("operation") not in EXACT_EQUALITY_OPERATIONS:
            diagnostics.append({
                "code":f"{capability}.{field}_equal",
                "fields":[field],
                "message":f"{capability} {field} selector must use equal operation",
            })
    return diagnostics


def validate_panos_config_object(obj):
    if obj.get("capability") != "panos.config":
        return []
    xpath=(obj.get("select") or {}).get("xpath")
    if isinstance(xpath,dict) and xpath.get("operation") not in EXACT_EQUALITY_OPERATIONS:
        return [{
            "code":"panos.config.xpath_equal",
            "fields":["xpath"],
            "message":"PAN-OS configuration xpath selector must use equal operation",
        }]
    return []


def validate_macos_pwpolicy512_object(obj):
    if obj.get("capability") != "macos.pwpolicy512":
        return []
    diagnostics=[]
    select=obj.get("select") or {}
    auth=select.get("authenticator", ...)
    password=select.get("authenticator_password", ...)
    if (auth is None) != (password is None):
        diagnostics.append({
            "code":"macos.pwpolicy512.auth_pair",
            "fields":["authenticator","authenticator_password"],
            "message":"authenticator and authenticator_password must both be null or both provide values",
        })
    for field in ("authenticator_password","directory_node","xpath"):
        value=select.get(field)
        if isinstance(value,dict) and value.get("operation") not in EXACT_EQUALITY_OPERATIONS:
            diagnostics.append({
                "code":f"macos.pwpolicy512.{field}_equal",
                "fields":[field],
                "message":f"{field} supports equality semantics only",
            })
    return diagnostics



def validate_windows_cmdlet_object(obj):
    if obj.get("capability") != "windows.cmdlet":
        return []
    diagnostics=[]
    collect=obj.get("collect") or {}
    module_id=collect.get("module_id")
    if isinstance(module_id,str):
        import uuid
        try:
            uuid.UUID(module_id.strip("{}"))
        except (ValueError, AttributeError):
            diagnostics.append({
                "code":"windows.cmdlet.module_guid",
                "fields":["module_id"],
                "message":"literal module_id must be a valid GUID representation",
            })
    selected=collect.get("select")
    if isinstance(selected,dict):
        fields=selected.get("fields") or {}
        if "*" in fields:
            diagnostics.append({
                "code":"windows.cmdlet.select_no_wildcard",
                "fields":["select"],
                "message":"cmdlet selected output fields must be explicit; '*' is not permitted",
            })
    return diagnostics



WINDOWS_NONNEGATIVE_STATE_FIELDS={
    "windows.lockoutpolicy":{"force_logoff","lockout_duration"},
}


def validate_windows_policy_state_ranges(test_id,test,states):
    fields=WINDOWS_NONNEGATIVE_STATE_FIELDS.get(test.get("capability"))
    if not fields:
        return []
    diagnostics=[]
    for field in fields:
        for state_id,payload in _literal_state_values(states,test.get("states"),field):
            value=payload.get("value")
            if isinstance(value,int) and not isinstance(value,bool) and value < 0:
                diagnostics.append({
                    "test":test_id,"state":state_id,
                    "code":f"{test.get('capability')}.nonnegative_time_values",
                    "field":field,"value":value,
                    "message":"literal policy time value must be non-negative",
                })
    return diagnostics


def _all_state_leaves(payload):
    """Visit every authored predicate, regardless of its Boolean placement."""
    if not isinstance(payload,dict):
        return
    if isinstance(payload.get("field"),str):
        yield payload
    for operator in ("all","any","one","odd"):
        children=payload.get(operator)
        if isinstance(children,list):
            for child in children:
                yield from _all_state_leaves(child)
    if isinstance(payload.get("not"),dict):
        yield from _all_state_leaves(payload["not"])


def _literal_state_values(states, state_ids, field):
    for state_id in state_ids or []:
        state=states.get(state_id)
        if not isinstance(state,dict):
            continue
        for payload in _all_state_leaves(state.get("state")):
            if payload.get("field") != field:
                continue
            value=payload.get("value")
            if isinstance(value,dict) and set(value) in ({"variable"},{"input"}):
                continue
            yield state_id,payload


def _conjunctive_state_leaves(payload):
    """Flatten only guaranteed ALL conjunctions; never assume ANY/ONE/ODD."""
    if not isinstance(payload,dict):
        return []
    if "field" in payload:
        return [payload]
    if set(payload)=={"all"} and isinstance(payload["all"],list):
        leaves=[]
        for child in payload["all"]:
            leaves.extend(_conjunctive_state_leaves(child))
        return leaves
    return []


def _validate_windows_registry_like_value_datatypes(test_id,test,states):
    if test.get("capability") not in {"windows.registry","windows.ntuser"}:
        return []

    groups=[]
    for state_id in test.get("states") or []:
        state=states.get(state_id)
        if isinstance(state,dict):
            leaves=[(state_id,leaf) for leaf in
                    _conjunctive_state_leaves(state.get("state"))]
            groups.append(leaves)

    # A Test can combine different States with ANY/ONE/ODD, which are
    # alternatives rather than guarantees. Cross-State narrowing is only
    # sound with explicit ALL; each State's own conjunction can still be
    # checked individually.
    check_groups=list(groups)
    if len(groups)>1 and test.get("states_match")=="all":
        check_groups.append([item for group in groups for item in group])

    diagnostics=[]
    for leaves in check_groups:
        exact_types={
            payload["value"]
            for _,payload in leaves
            if payload.get("field")=="type"
            and payload.get("operation") in EXACT_EQUALITY_OPERATIONS
            and isinstance(payload.get("value"),str)
        }
        if len(exact_types)>1:
            diagnostics.append({
                "test":test_id,
                "code":f"{test.get('capability')}.conflicting_registry_types",
                "registry_types":sorted(exact_types),
                "message":"Conjunctive State asserts incompatible registry types",
            })
            continue
        if len(exact_types)!=1:
            continue
        registry_type=next(iter(exact_types))
        allowed=REGISTRY_TYPE_VALUE_DATATYPES.get(registry_type)
        # A type-only assertion remains valid, but a value comparison cannot
        # silently claim type fidelity for an unmodelled Registry representation.
        if not allowed:
            for state_id,payload in leaves:
                if payload.get("field")=="value":
                    diagnostics.append({
                        "test":test_id,
                        "state":state_id,
                        "code":f"{test.get('capability')}.unsupported_type_value_encoding",
                        "registry_type":registry_type,
                        "message":"Registry type has no verified native value encoding; do not infer a datatype",
                    })
            continue
        for state_id,payload in leaves:
            if payload.get("field")!="value":
                continue
            value=payload.get("value")
            if isinstance(value,dict) and set(value) in ({"variable"},{"input"}):
                continue
            datatype=payload.get("datatype")
            if datatype not in allowed:
                diagnostics.append({
                    "test":test_id,
                    "state":state_id,
                    "code":f"{test.get('capability')}.value_type_datatype",
                    "registry_type":registry_type,
                    "datatype":datatype,
                    "allowed_datatypes":sorted(allowed),
                    "message":"registry value datatype is incompatible with exact asserted registry type",
                })
    # One mismatch per State/field even if both its local and test-wide ALL
    # conjunction lead to the same diagnostic.
    unique={}
    for finding in diagnostics:
        signature=(finding["code"],finding.get("state"),
                   finding.get("registry_type"),finding.get("datatype"),
                   tuple(finding.get("registry_types",())))
        unique[signature]=finding
    return list(unique.values())


def _valid_xml_date_literal(value):
    if not isinstance(value,str):
        return False
    import datetime as _dt
    try:
        _dt.date.fromisoformat(value)
        return len(value)==10
    except ValueError:
        return False


def validate_windows_wuaupdatesearcher_states(test_id,test,states):
    if test.get("capability") != "windows.wuaupdatesearcher":
        return []
    diagnostics=[]
    for state_id,payload in _literal_state_values(states,test.get("states"),"last_deployment_change_time"):
        value=payload.get("value")
        if not _valid_xml_date_literal(value):
            diagnostics.append({
                "test":test_id,
                "state":state_id,
                "code":"windows.wuaupdatesearcher.date_lexical_form",
                "value":value,
                "message":"last_deployment_change_time must preserve XML date lexical form YYYY-MM-DD",
            })
    return diagnostics


HIERARCHY_KEY_CAPABILITIES={
    "windows.registry",
    "windows.ntuser",
    "windows.regkeyeffectiverights53",
}


def validate_windows_registry_object(obj):
    """Return semantic diagnostics for registry-like Windows hierarchy Objects."""
    capability=obj.get("capability")
    if capability not in HIERARCHY_KEY_CAPABILITIES:
        return []

    diagnostics=[]
    select=obj.get("select") or {}
    key=select.get("key", ...)
    name=select.get("name", ...)

    if capability == "windows.registry" and key is None and name is not None:
        diagnostics.append({
            "code":"windows.registry.key_null_requires_name_null",
            "fields":["key","name"],
            "message":"name must be null when key is null",
        })

    if (
        isinstance(key,dict)
        and key.get("operation") not in EQUALITY_OPERATIONS
        and obj.get("traversal") is not None
    ):
        diagnostics.append({
            "code":f"{capability}.pattern_key_no_traversal",
            "fields":["traversal"],
            "message":"non-equality hierarchy key selection cannot use traversal",
        })

    return diagnostics


def _iter_set_filters(expression):
    """Yield State filters from a native recursive Set expression."""
    if not isinstance(expression, dict):
        return
    for operand in expression.get("operands") or []:
        if not isinstance(operand, dict):
            continue
        if isinstance(operand.get("object"), str):
            for flt in operand.get("filters") or []:
                if isinstance(flt, dict):
                    yield flt
        nested=operand.get("set")
        if isinstance(nested, dict):
            yield from _iter_set_filters(nested)


def _iter_set_object_refs(expression):
    """Yield Object IDs referenced by a native recursive Set expression."""
    if not isinstance(expression, dict):
        return
    for operand in expression.get("operands") or []:
        if not isinstance(operand, dict):
            continue
        object_id=operand.get("object")
        if isinstance(object_id,str):
            yield object_id
        nested=operand.get("set")
        if isinstance(nested,dict):
            yield from _iter_set_object_refs(nested)


EXECUTABLE_SEMANTIC_RULE_IDS={
    # Cross-reference capability checks are generic and recurse through Sets.
    # File-selection families share the same native semantic implementation.
    *{f"{cap}.full_path_no_traversal" for cap in FILE_SELECTION_CAPABILITIES},
    *{f"{cap}.pattern_directory_no_traversal" for cap in FILE_SELECTION_CAPABILITIES},
    *{f"{cap}.name_empty" for cap in FILE_SELECTION_CAPABILITIES},
    "independent.textfilecontent54.pattern_operation",
    "independent.xmlfilecontent.xpath_equal",
    "panos.config.xpath_equal",
    "macos.plist511.filepath_equal",
    "macos.plist511.xpath_equal",
    "macos.systemprofiler.xpath_equal",
    "independent.yamlfilecontent.content_equal",
    "independent.yamlfilecontent.yamlpath_equal",
    "independent.yamlfilecontent.inline_content_no_traversal",
    "linux.selinuxsecuritycontext.pid_no_file_traversal",
    "macos.pwpolicy512.auth_pair",
    "macos.pwpolicy512.password_equal",
    "macos.pwpolicy512.directory_node_equal",
    "macos.pwpolicy512.xpath_equal",
    "windows.cmdlet.module_guid",
    "windows.cmdlet.select_no_wildcard",
    "windows.file.literal_name_characters",
    "windows.fileeffectiverights53.literal_name_characters",
    "windows.registry.key_null_requires_name_null",
    "windows.registry.pattern_key_no_traversal",
    "windows.ntuser.pattern_key_no_traversal",
    "windows.regkeyeffectiverights53.pattern_key_no_traversal",
    "windows.registry.value_type_datatype",
    "windows.ntuser.value_type_datatype",
    "windows.lockoutpolicy.nonnegative_time_values",
    "windows.wuaupdatesearcher.date_lexical_form",
    "variable.value.source_exists",
    "windows.lockoutpolicy.singleton_source",
    "iosxe.version.singleton_source",
    "independent.family.singleton_source",
    "panos.version.singleton_source",
    "asa.version.singleton_source",
    "macos.profiles.singleton_source",
    "macos.systemsetup.singleton_source",
    "macos.filevault.singleton_source",
    "macos.firmwarepassword.singleton_source",
    "linux.apparmorstatus.singleton_source",
    "linux.sestatus.singleton_source",
    "unix.uname.singleton_source",
    "windows.passwordpolicy.singleton_source",
    "windows.auditeventpolicysubcategories.singleton_source",
    "macos.disabledservice.implicit_population",
    "macos.gatekeeper.implicit_source",
    "macos.softwareupdate.implicit_population",
}


def executable_rule_id_for_diagnostic(code):
    if code == "object.filter_state_capability":
        return code
    return code


STRUCTURAL_OR_IMPORT_SEMANTIC_RULE_IDS={
    "windows.wmi.query.structured_results",
    "independent.xmlfilecontent.materialized_item_creation",
    "windows.fileeffectiverights53.trustee_sid",
    "windows.regkeyeffectiverights53.deprecated_group_behaviors",
    # Enforced by generated schema structure or lossless importer materialization.
    "independent.yamlfilecontent.record_keys",
    "windows.cmdlet.record_fields",
    "windows.ntuser.materialized_collection_defaults",
    "windows.sid.materialized_behaviors",
    "windows.sid_sid.materialized_behaviors",
    "windows.wuaupdatesearcher.materialized_superseded_default",
    "windows.wuaupdatesearcher.source_path_repair",
    "independent.sql512.result_record",
    "independent.sql512.engine_filterability",
    "independent.unknown.fixed_result",
    "linux.rpmverifyfile.materialized_behaviors",
    "linux.rpmverifypackage.materialized_behaviors",
}

POLICY_SEMANTIC_RULE_IDS={
    "windows.userright.trustee_name_case",
    "independent.family.literal_vocabulary",
    "linux.dpkginfo.debian_evr",
    "unix.interface.type_literal",
    "unix.shadow.encrypt_method_literal",
    "windows.auditeventpolicysubcategories.supported_fields",
    # Normative deployment/authoring policy rather than document-shape or evaluator checks.
    "independent.shellcommand.trusted_content",
    "independent.shellcommand.not_generic_escape_hatch",
}

RUNTIME_SEMANTIC_RULE_IDS={
    "windows.wmi.query.source_fields",
    "linux.inetlisteningservers.protocol",
    "independent.environmentvariable58.null_pid",
    "linux.selinuxsecuritycontext.null_pid",
    "independent.shellcommand.pattern_semantics",
    "linux.partition.mount_options_complete",
    "linux.rpminfo.filepaths_collection",
    "linux.rpmverifypackage.skipped_results",
    "unix.symlink.canonical_resolution",
    "windows.passwordpolicy.source_ranges",
    # These require collection/evaluation behavior rather than static authored-content validation.
    "independent.xmlfilecontent.xpath_text_values",
}

def validate_declared_semantic_rules(mapping, implemented_rule_ids):
    """Report reviewed semantic rules that lack the caller's enforcement coverage."""
    declared={row.get("id") for row in mapping.get("semantic_validator_rules",[]) if row.get("id")}
    missing=sorted(declared-set(implemented_rule_ids))
    return missing


def classify_declared_semantic_rules(mapping):
    """Return declared rule IDs grouped by their required enforcement layer.

    Capability-specific filter_state_capability declarations are implemented by
    the generic recursive Object/State capability validator.
    """
    declared={row.get("id") for row in mapping.get("semantic_validator_rules",[]) if row.get("id")}
    executable=set()
    for rule_id in declared:
        if rule_id.endswith(".filter_state_capability"):
            executable.add(rule_id)
        elif rule_id in EXECUTABLE_SEMANTIC_RULE_IDS:
            executable.add(rule_id)
    structural=declared & STRUCTURAL_OR_IMPORT_SEMANTIC_RULE_IDS
    runtime=declared & RUNTIME_SEMANTIC_RULE_IDS
    policy=declared & POLICY_SEMANTIC_RULE_IDS
    accounted=executable | structural | runtime | policy
    return {
        "executable":sorted(executable),
        "structural_or_import":sorted(structural),
        "runtime":sorted(runtime),
        "policy":sorted(policy),
        "unclassified":sorted(declared-accounted),
    }


SINGLETON_SOURCE_CAPABILITIES={
    "independent.family",
    "windows.lockoutpolicy",
    "windows.passwordpolicy",
    "windows.auditeventpolicysubcategories",
    "iosxe.version",
    "panos.version",
    "asa.version",
    "macos.profiles",
    "macos.systemsetup",
    "macos.filevault",
    "macos.firmwarepassword",
    "linux.apparmorstatus",
    "linux.sestatus",
    "unix.uname",
    "macos.disabledservice",
    "macos.gatekeeper",
    "macos.softwareupdate",
}

NO_OBJECT_RULE_IDS={
    "macos.disabledservice":"macos.disabledservice.implicit_population",
    "macos.gatekeeper":"macos.gatekeeper.implicit_source",
    "macos.softwareupdate":"macos.softwareupdate.implicit_population",
}


def _no_object_rule_id(capability):
    return NO_OBJECT_RULE_IDS.get(capability, f"{capability}.singleton_source")


def _named_objects(assessment):
    """Return the named Object registry across faithful/research and canonical 0.3 forms."""
    shared=assessment.get("shared_objects")
    legacy=assessment.get("objects")
    if shared is not None and legacy is not None:
        raise ValueError("Assessment cannot contain both shared_objects and objects")
    return shared or legacy or {}


def validate_singleton_source_document(document):
    assessment=document.get("assessment",document)
    diagnostics=[]
    for test_id,test in (assessment.get("tests") or {}).items():
        capability=test.get("capability")
        if capability in SINGLETON_SOURCE_CAPABILITIES and "object" in test:
            diagnostics.append({
                "test":test_id,
                "code":_no_object_rule_id(capability),
                "fields":["object"],
                "message":"singleton-source capability Test must not reference an Object",
            })
    for object_id,obj in _named_objects(assessment).items():
        capability=obj.get("capability")
        if capability in SINGLETON_SOURCE_CAPABILITIES:
            diagnostics.append({
                "object":object_id,
                "code":_no_object_rule_id(capability),
                "message":"singleton-source capability must not define an Object",
            })
    return diagnostics




def _load_v03_capability_mappings():
    mappings={}
    for path in sorted(V03_MAPPING_DIR.glob("*.json")):
        row=json.loads(path.read_text(encoding="utf-8"))
        capability=row.get("capability")
        if capability:
            mappings[capability]=row
    return mappings


def validate_v03_foreach(document):
    """Validate SCAP-NG 0.3 collection for_each, including chained lineage."""
    assessment=document.get("assessment",document)
    specification=assessment.get("specification") or {}
    if specification.get("version") != "0.3.0":
        return []

    objects=_assessment_named_objects(assessment)
    tests=assessment.get("tests") or {}
    mappings=_load_v03_capability_mappings()
    diagnostics=[]

    directly_tested={
        test.get("object")
        for test in tests.values()
        if isinstance(test,dict) and isinstance(test.get("object"),str)
    }

    bindings={}
    foreach_sources=set()
    for object_id,obj in objects.items():
        if not isinstance(obj,dict):
            continue
        foreach=obj.get("for_each")
        if isinstance(foreach,dict) and set(foreach)=={"item","in"}:
            bindings[object_id]=foreach
            if isinstance(foreach.get("in"),str):
                foreach_sources.add(foreach["in"])

    # One source edge per foreach Object yields a simple dependency graph.
    # Reject cycles before calculating inherited lexical lineage.
    reported_cycles=set()
    for start_id in sorted(bindings):
        order=[]
        index={}
        current=start_id
        while current in bindings:
            if current in index:
                cycle=tuple(order[index[current]:])
                key=tuple(sorted(cycle))
                if key not in reported_cycles:
                    reported_cycles.add(key)
                    diagnostics.append({
                        "object":start_id,
                        "code":"foreach.dependency_cycle",
                        "cycle":list(cycle),
                        "message":"foreach Object dependency graph must be acyclic",
                    })
                break
            index[current]=len(order)
            order.append(current)
            source_id=bindings[current].get("in")
            if not isinstance(source_id,str) or source_id not in objects:
                break
            current=source_id

    scope_cache={}
    alias_shadow_reported=set()

    def scope_for(object_id,trail=()):
        if object_id in scope_cache:
            return scope_cache[object_id]
        if object_id in trail:
            return {}
        foreach=bindings.get(object_id)
        if foreach is None:
            scope_cache[object_id]={}
            return {}
        source_id=foreach.get("in")
        source=objects.get(source_id)
        if not isinstance(source,dict):
            scope_cache[object_id]={}
            return {}
        inherited=scope_for(source_id,trail+(object_id,))
        alias=foreach.get("item")
        if not isinstance(alias,str):
            scope_cache[object_id]=dict(inherited)
            return scope_cache[object_id]
        if alias in inherited:
            key=(object_id,alias)
            if key not in alias_shadow_reported:
                alias_shadow_reported.add(key)
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.alias_shadow",
                    "alias":alias,
                    "message":"nested foreach item alias must not shadow an inherited lineage alias",
                })
        scope=dict(inherited)
        scope[alias]=source.get("capability")
        scope_cache[object_id]=scope
        return scope

    for object_id,obj in objects.items():
        if not isinstance(obj,dict):
            continue
        select=obj.get("select") or {}
        bound=[
            (field,spec.get("from"))
            for field,spec in select.items()
            if isinstance(spec,dict) and "from" in spec
        ]
        foreach=obj.get("for_each")

        if foreach is None:
            for field,_ in bound:
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.from_without_for_each",
                    "field":field,
                    "message":"A selector from binding requires Object-level for_each",
                })
            continue

        if not isinstance(foreach,dict) or set(foreach) != {"item","in"}:
            diagnostics.append({
                "object":object_id,
                "code":"foreach.binding_shape",
                "message":"for_each requires exactly item and in",
            })
            continue

        alias=foreach.get("item")
        source_id=foreach.get("in")
        if source_id == object_id:
            diagnostics.append({
                "object":object_id,
                "code":"foreach.self_source",
                "message":"for_each source Object must be distinct from target Object",
            })
            continue
        source=objects.get(source_id)
        if source is None:
            diagnostics.append({
                "object":object_id,
                "code":"foreach.source_missing",
                "source_object":source_id,
                "message":"for_each source references an unknown shared Object",
            })
            continue

        if not bound:
            diagnostics.append({
                "object":object_id,
                "code":"foreach.bound_selector_count",
                "count":0,
                "message":"for_each requires at least one selector bound from its visible lineage",
            })
            continue

        scope=scope_for(object_id)
        current_alias_used=False
        target_cap=obj.get("capability")
        target_map=mappings.get(target_cap)

        for target_field,from_ref in bound:
            if not isinstance(from_ref,str) or from_ref.count(".") != 1:
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.from_shape",
                    "field":target_field,
                    "message":"from must be <binding>.<source-field>",
                })
                continue
            ref_alias,source_field=from_ref.split(".",1)
            if ref_alias == alias:
                current_alias_used=True
            if ref_alias not in scope:
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.binding_alias",
                    "field":target_field,
                    "alias":ref_alias,
                    "visible_aliases":sorted(scope),
                    "message":"from binding alias must be the current foreach item or an inherited correlated lineage alias",
                })
                continue

            source_cap=scope.get(ref_alias)
            source_map=mappings.get(source_cap)
            if source_map is None or target_map is None:
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.capability_mapping_missing",
                    "source_capability":source_cap,
                    "target_capability":target_cap,
                    "message":"for_each requires reviewed 0.3 source and target capability mappings",
                })
                continue

            source_types=set(
                source_map.get("native",{}).get("field_datatypes",{}).get(source_field,[])
            )
            target_selector_names=set(
                target_map.get("native",{}).get("selector_map",{}).values()
            )
            target_types=set(
                target_map.get("native",{}).get("field_datatypes",{}).get(target_field,[])
            )
            if not source_types:
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.source_field_unknown",
                    "alias":ref_alias,
                    "field":source_field,
                    "message":"for_each source field is not a typed collected field of the bound capability",
                })
            if target_field not in target_selector_names or not target_types:
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.target_selector_unknown",
                    "field":target_field,
                    "message":"for_each target field is not a typed selector of the target capability",
                })
            compatible=sorted(source_types & target_types)
            if source_types and target_types and len(compatible) != 1:
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.datatype_compatibility",
                    "source_alias":ref_alias,
                    "source_datatypes":sorted(source_types),
                    "target_datatypes":sorted(target_types),
                    "compatible_datatypes":compatible,
                    "message":"for_each requires exactly one compatible source/target datatype per bound selector",
                })

        if not current_alias_used:
            diagnostics.append({
                "object":object_id,
                "code":"foreach.current_binding_unused",
                "alias":alias,
                "message":"for_each must bind at least one selector from its current item; ancestor-only bindings cannot justify an iteration level",
            })

        bound_fields={field for field,_ in bound}
        for field,spec in select.items():
            if field in bound_fields or not isinstance(spec,dict):
                continue
            if _is_variable_value(spec.get("value")):
                diagnostics.append({
                    "object":object_id,
                    "code":"foreach.additional_variable_selector",
                    "field":field,
                    "message":"for_each target Object cannot add an independent Variable selector",
                })

        if object_id not in directly_tested and object_id not in foreach_sources:
            diagnostics.append({
                "object":object_id,
                "code":"foreach.target_not_consumed",
                "message":"for_each Object must be directly tested or consumed as the named source of another for_each Object",
            })

    return diagnostics


def _iter_inline_object_uses(node,path=()):
    """Yield (path, Object payload) for consumer-local explicit object fields."""
    if isinstance(node,dict):
        for key,value in node.items():
            child_path=path+(key,)
            if key=="object" and isinstance(value,dict) and isinstance(value.get("capability"),str):
                yield child_path,value
            yield from _iter_inline_object_uses(value,child_path)
    elif isinstance(node,list):
        for index,value in enumerate(node):
            yield from _iter_inline_object_uses(value,path+(index,))


def _validate_object_payload(object_id,obj,objects,states,diagnostics):
    """Apply capability and Set/Filter semantics to one named or inline Object."""
    if not isinstance(obj,dict):
        return
    for row in validate_file_selection_object(obj):
        diagnostics.append({"object":object_id,**row})
    for row in validate_windows_registry_object(obj):
        diagnostics.append({"object":object_id,**row})
    for row in validate_macos_pwpolicy512_object(obj):
        diagnostics.append({"object":object_id,**row})
    for row in validate_windows_cmdlet_object(obj):
        diagnostics.append({"object":object_id,**row})
    for row in validate_panos_config_object(obj):
        diagnostics.append({"object":object_id,**row})
    for row in validate_equal_only_selectors(obj,"macos.plist511",("full_path","xpath")):
        diagnostics.append({"object":object_id,**row})
    for row in validate_equal_only_selectors(obj,"macos.systemprofiler",("xpath",)):
        diagnostics.append({"object":object_id,**row})

    def walk_set(expression):
        if not isinstance(expression,dict):
            return
        for index,operand in enumerate(expression.get("operands") or []):
            if not isinstance(operand,dict):
                continue
            used=operand.get("object")
            if isinstance(used,str):
                referenced=objects.get(used)
                if referenced is None:
                    diagnostics.append({
                        "object":object_id,
                        "code":"object.set_object_missing",
                        "referenced_object":used,
                        "message":"Set references an unknown shared Object",
                    })
                elif referenced.get("capability") != obj.get("capability"):
                    diagnostics.append({
                        "object":object_id,
                        "code":"object.set_object_capability",
                        "referenced_object":used,
                        "message":"Set Object capability must match parent Object capability",
                    })
            elif isinstance(used,dict):
                if used.get("capability") != obj.get("capability"):
                    diagnostics.append({
                        "object":object_id,
                        "code":"object.inline_set_object_capability",
                        "operand_index":index,
                        "message":"Inline Set Object capability must match parent Object capability",
                    })
                _validate_object_payload(
                    f"{object_id}.set[{index}]",used,objects,states,diagnostics
                )

            for fidx,flt in enumerate(operand.get("filters") or []):
                if not isinstance(flt,dict):
                    continue
                state_use=flt.get("state")
                if isinstance(state_use,str):
                    state=states.get(state_use)
                    if state is None:
                        diagnostics.append({
                            "object":object_id,
                            "code":"object.filter_state_missing",
                            "state":state_use,
                            "message":"Object filter references an unknown State",
                        })
                    elif state.get("capability") != obj.get("capability"):
                        diagnostics.append({
                            "object":object_id,
                            "code":"object.filter_state_capability",
                            "state":state_use,
                            "message":"Object filter State capability must match Object capability",
                        })
                elif isinstance(state_use,dict):
                    if state_use.get("capability") != obj.get("capability"):
                        diagnostics.append({
                            "object":object_id,
                            "code":"object.inline_filter_state_capability",
                            "filter_index":fidx,
                            "message":"Inline filter State capability must match Object capability",
                        })

            nested=operand.get("set")
            if isinstance(nested,dict):
                walk_set(nested)

    walk_set(obj.get("set"))


def validate_assessment_capability_semantics(document):
    """Validate current native Assessment cross-node capability semantics."""
    assessment=document.get("assessment",document)
    diagnostics=[]

    objects=_named_objects(assessment)
    variables=assessment.get("variables") or {}
    states=assessment.get("states") or {}
    tests=assessment.get("tests") or {}

    for object_id,obj in objects.items():
        _validate_object_payload(object_id,obj,objects,states,diagnostics)

    # Variable-local and other consumer-local Object payloads remain typed
    # Objects even though they no longer have Assessment-scoped IDs.
    for variable_id,variable in variables.items():
        for path,obj in _iter_inline_object_uses(variable,("variables",variable_id)):
            _validate_object_payload(
                f"{variable_id}:"+"/".join(map(str,path)),obj,objects,states,diagnostics
            )

    for test_id,test in tests.items():
        effective_states=dict(states)
        effective_test=dict(test)
        effective_state_ids=[]

        if "object" in test:
            object_use=test.get("object")
            if isinstance(object_use,str):
                obj=objects.get(object_use)
                if obj is None:
                    diagnostics.append({
                        "test":test_id,
                        "code":"test.object_missing",
                        "object":object_use,
                        "message":"Test references an unknown shared Object",
                    })
                elif obj.get("capability") != test.get("capability"):
                    diagnostics.append({
                        "test":test_id,
                        "code":"test.object_capability",
                        "object":object_use,
                        "message":"Test and Object capabilities must match",
                    })
            elif isinstance(object_use,dict):
                if object_use.get("capability") != test.get("capability"):
                    diagnostics.append({
                        "test":test_id,
                        "code":"test.inline_object_capability",
                        "message":"Test and inline Object capabilities must match",
                    })
                _validate_object_payload(
                    f"{test_id}.object",object_use,objects,states,diagnostics
                )

        if "variable" in test:
            variable_id=test.get("variable")
            if variable_id not in variables:
                diagnostics.append({
                    "test":test_id,
                    "code":"variable.value.source_exists" if test.get("capability")=="variable.value" else "test.variable_missing",
                    "variable":variable_id,
                    "message":"Test references an unknown Variable",
                })

        for index,state_use in enumerate(test.get("states") or []):
            if isinstance(state_use,str):
                state=states.get(state_use)
                effective_state_ids.append(state_use)
                if state is None:
                    diagnostics.append({
                        "test":test_id,
                        "code":"test.state_missing",
                        "state":state_use,
                        "message":"Test references an unknown State",
                    })
                elif state.get("capability") != test.get("capability"):
                    diagnostics.append({
                        "test":test_id,
                        "code":"test.state_capability",
                        "state":state_use,
                        "message":"Test and State capabilities must match",
                    })
            elif isinstance(state_use,dict):
                synthetic=f"__inline_state_{index}"
                effective_states[synthetic]=state_use
                effective_state_ids.append(synthetic)
                if state_use.get("capability") != test.get("capability"):
                    diagnostics.append({
                        "test":test_id,
                        "code":"test.inline_state_capability",
                        "state_index":index,
                        "message":"Test and inline State capabilities must match",
                    })

        effective_test["states"]=effective_state_ids
        diagnostics.extend(
            _validate_windows_registry_like_value_datatypes(
                test_id,effective_test,effective_states
            )
        )
        diagnostics.extend(
            validate_windows_wuaupdatesearcher_states(
                test_id,effective_test,effective_states
            )
        )
        diagnostics.extend(
            validate_windows_policy_state_ranges(
                test_id,effective_test,effective_states
            )
        )

    diagnostics.extend(validate_singleton_source_document(document))
    diagnostics.extend(validate_v02_native_literal_types(document))
    diagnostics.extend(validate_v03_native_literal_types(document))
    diagnostics.extend(validate_v03_foreach(document))
    return diagnostics


REGISTRY_TYPE_VALUE_DATATYPES={
    "binary":{"binary"},
    "dword":{"integer"},
    "dword_big_endian":{"integer"},
    "qword":{"integer"},
    "expand_string":{"string"},
    "link":{"string"},
    "multi_string":{"string"},
    "string":{"string","version"},
}


def assert_assessment_capability_semantics(document):
    diagnostics=validate_assessment_capability_semantics(document)
    if diagnostics:
        raise CapabilitySemanticError(
            "capability semantic validation failed: " + repr(diagnostics)
        )
    return document
