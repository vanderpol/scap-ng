#!/usr/bin/env python3
"""Semantic validation that complements generated capability JSON Schemas.

JSON Schema handles structural/native vocabulary constraints. This module
handles source-backed cross-field and cross-reference rules that are clearer or
safer as semantic validation. Rules are intentionally narrow and capability
specific until proven reusable.
"""
from __future__ import annotations


class CapabilitySemanticError(ValueError):
    pass


def _is_variable_value(value):
    return (
        isinstance(value, dict)
        and set(value) == {"variable"}
        and isinstance(value.get("variable"), str)
        and bool(value["variable"])
    )


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
    if (
        isinstance(directory, dict)
        and directory.get("operation") != "equal"
        and traversal is not None
    ):
        diagnostics.append({
            "code":f"{capability}.pattern_directory_no_traversal",
            "fields":["traversal"],
            "message":"non-equality directory selection cannot use traversal",
        })

    if capability == "independent.textfilecontent54":
        pattern=select.get("pattern")
        if isinstance(pattern,dict) and pattern.get("operation") != "match":
            diagnostics.append({
                "code":"independent.textfilecontent54.pattern_operation",
                "fields":["pattern"],
                "message":"textfilecontent54 pattern selector must use match operation",
            })

    if capability == "independent.xmlfilecontent":
        xpath=select.get("xpath")
        if isinstance(xpath,dict) and xpath.get("operation") != "equal":
            diagnostics.append({
                "code":"independent.xmlfilecontent.xpath_equal",
                "fields":["xpath"],
                "message":"xmlfilecontent xpath selector must use equal operation",
            })

    if capability == "independent.yamlfilecontent":
        for field in ("content","yamlpath"):
            value=select.get(field)
            if isinstance(value,dict) and value.get("operation") != "equal":
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
        pattern=name.get("operation") == "match"
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
        if isinstance(value,dict) and value.get("operation") != "equal":
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
    if isinstance(xpath,dict) and xpath.get("operation") != "equal":
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
        if isinstance(value,dict) and value.get("operation") != "equal":
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


def _literal_state_values(states, state_ids, field):
    for state_id in state_ids or []:
        state=states.get(state_id)
        if not isinstance(state,dict):
            continue
        payload=state.get("state") or {}
        if payload.get("field") != field:
            continue
        value=payload.get("value")
        if isinstance(value,dict) and set(value)=={"variable"}:
            continue
        yield state_id,payload


def _validate_windows_registry_like_value_datatypes(test_id,test,states):
    if test.get("capability") not in {"windows.registry","windows.ntuser"}:
        return []
    referenced=[
        states.get(state_id)
        for state_id in (test.get("states") or [])
        if isinstance(states.get(state_id),dict)
    ]
    exact_types=[]
    for state in referenced:
        payload=state.get("state") or {}
        if (
            payload.get("field")=="type"
            and payload.get("operation")=="equal"
            and isinstance(payload.get("value"),str)
        ):
            exact_types.append(payload["value"])
    if len(set(exact_types)) != 1:
        return []
    registry_type=exact_types[0]
    allowed=REGISTRY_TYPE_VALUE_DATATYPES.get(registry_type)
    if not allowed:
        return []
    diagnostics=[]
    for state_id,payload in _literal_state_values(states,test.get("states"),"value"):
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
    return diagnostics


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
        and key.get("operation") != "equal"
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
    for object_id,obj in (assessment.get("objects") or {}).items():
        capability=obj.get("capability")
        if capability in SINGLETON_SOURCE_CAPABILITIES:
            diagnostics.append({
                "object":object_id,
                "code":_no_object_rule_id(capability),
                "message":"singleton-source capability must not define an Object",
            })
    return diagnostics


def validate_assessment_capability_semantics(document):
    """Validate current native Assessment cross-node capability semantics."""
    assessment=document.get("assessment",document)
    diagnostics=[]

    objects=assessment.get("objects") or {}
    variables=assessment.get("variables") or {}
    states=assessment.get("states") or {}
    tests=assessment.get("tests") or {}

    for object_id,obj in objects.items():
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

        for referenced_object_id in _iter_set_object_refs(obj.get("set")):
            referenced_object=objects.get(referenced_object_id)
            if referenced_object is None:
                diagnostics.append({
                    "object":object_id,
                    "code":"object.set_object_missing",
                    "referenced_object":referenced_object_id,
                    "message":"Set references an unknown Object",
                })
            elif referenced_object.get("capability") != obj.get("capability"):
                diagnostics.append({
                    "object":object_id,
                    "code":"object.set_object_capability",
                    "referenced_object":referenced_object_id,
                    "message":"Set Object capability must match parent Object capability",
                })

        for flt in _iter_set_filters(obj.get("set")):
            state_id=flt.get("state")
            state=states.get(state_id)
            if state is None:
                diagnostics.append({
                    "object":object_id,
                    "code":"object.filter_state_missing",
                    "state":state_id,
                    "message":"Object filter references an unknown State",
                })
                continue
            if state.get("capability") != obj.get("capability"):
                diagnostics.append({
                    "object":object_id,
                    "code":"object.filter_state_capability",
                    "state":state_id,
                    "message":"Object filter State capability must match Object capability",
                })

    for test_id,test in tests.items():
        if "object" in test:
            object_id=test.get("object")
            obj=objects.get(object_id)
            if obj is None:
                diagnostics.append({
                    "test":test_id,
                    "code":"test.object_missing",
                    "object":object_id,
                    "message":"Test references an unknown Object",
                })
            elif obj.get("capability") != test.get("capability"):
                diagnostics.append({
                    "test":test_id,
                    "code":"test.object_capability",
                    "object":object_id,
                    "message":"Test and Object capabilities must match",
                })

        if "variable" in test:
            variable_id=test.get("variable")
            if variable_id not in variables:
                diagnostics.append({
                    "test":test_id,
                    "code":"variable.value.source_exists" if test.get("capability")=="variable.value" else "test.variable_missing",
                    "variable":variable_id,
                    "message":"Test references an unknown Variable",
                })

        for state_id in test.get("states") or []:
            state=states.get(state_id)
            if state is None:
                diagnostics.append({
                    "test":test_id,
                    "code":"test.state_missing",
                    "state":state_id,
                    "message":"Test references an unknown State",
                })
            elif state.get("capability") != test.get("capability"):
                diagnostics.append({
                    "test":test_id,
                    "code":"test.state_capability",
                    "state":state_id,
                    "message":"Test and State capabilities must match",
                })

        diagnostics.extend(
            _validate_windows_registry_like_value_datatypes(test_id,test,states)
        )
        diagnostics.extend(
            validate_windows_wuaupdatesearcher_states(test_id,test,states)
        )
        diagnostics.extend(
            validate_windows_policy_state_ranges(test_id,test,states)
        )

    diagnostics.extend(validate_singleton_source_document(document))
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
