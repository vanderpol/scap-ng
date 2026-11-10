# windows.userright — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/userright](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/userright) | {"declared_values_not_new_validation_restrictions": ["SE_ASSIGNPRIMARYTOKEN_NAME", "SE_AUDIT_NAME", "SE_BACKUP_NAME", "SE_CHANGE_NOTIFY_NAME", "SE_CREATE_GLOBAL_NAME", "SE_CREATE_PAGEFILE_NAME", "SE_CREATE_PERMANENT_NAME", "SE_CREATE_SYMBOLIC_LINK_NAME", "SE_CREATE_TOKEN_NAME", "SE_DEBUG_NAME", "SE_ENABLE_DELEGATION_NAME", "SE_IMPERSONATE_NAME", "SE_INC_BASE_PRIORITY_NAME", "SE_INCREASE_QUOTA_NAME", "SE_INC_WORKING_SET_NAME", "SE_LOAD_DRIVER_NAME", "SE_LOCK_MEMORY_NAME", "SE_MACHINE_ACCOUNT_NAME", "SE_MANAGE_VOLUME_NAME", "SE_PROF_SINGLE_PROCESS_NAME", "SE_RELABEL_NAME", "SE_REMOTE_SHUTDOWN_NAME", "SE_RESTORE_NAME", "SE_SECURITY_NAME", "SE_SHUTDOWN_NAME", "SE_SYNC_AGENT_NAME", "SE_SYSTEM_ENVIRONMENT_NAME", "SE_SYSTEM_PROFILE_NAME", "SE_SYSTEMTIME_NAME", "SE_TAKE_OWNERSHIP_NAME", "SE_TCB_NAME", "SE_TIME_ZONE_NAME", "SE_TRUSTED_CREDMAN_ACCESS_NAME", "SE_UNDOCK_NAME", "SE_UNSOLICITED_INPUT_NAME", "SE_BATCH_LOGON_NAME", "SE_DENY_BATCH_LOGON_NAME", "SE_DENY_INTERACTIVE_LOGON_NAME", "SE_DENY_NETWORK_LOGON_NAME", "SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME", "SE_DENY_SERVICE_LOGON_NAME", "SE_INTERACTIVE_LOGON_NAME", "SE_NETWORK_LOGON_NAME", "SE_REMOTE_INTERACTIVE_LOGON_NAME", "SE_SERVICE_LOGON_NAME"]} | source-derived |

[/$defs/meanings/properties/userright](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/userright): Name of a particular user right/privilege.

`userright` holds a string that represents the name of a particular user right/privilege.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/trustee_name) | {} | source-derived |

[/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/trustee_name): Unique name associated with the SID that has been granted the specified user right/privilege.

`trustee_name` is the unique name associated with the SID that has been granted the specified user right/privilege.

In Windows, trustee names are case-insensitive.

As a result, it is recommended that the case-insensitive operations are used for this field.

For local trustee names use: "computer name\trustee name".

For built-in accounts on the system, use the trustee name without a domain.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/trustee_sid) | {} | source-derived |

[/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/meanings/properties/trustee_sid): SID that has been granted the specified user right/privilege.

`trustee_sid` identifies the SID that has been granted the specified user right/privilege.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/userright](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/object/properties/userright) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"], "declared_values_not_new_validation_restrictions": ["SE_ASSIGNPRIMARYTOKEN_NAME", "SE_AUDIT_NAME", "SE_BACKUP_NAME", "SE_CHANGE_NOTIFY_NAME", "SE_CREATE_GLOBAL_NAME", "SE_CREATE_PAGEFILE_NAME", "SE_CREATE_PERMANENT_NAME", "SE_CREATE_SYMBOLIC_LINK_NAME", "SE_CREATE_TOKEN_NAME", "SE_DEBUG_NAME", "SE_ENABLE_DELEGATION_NAME", "SE_IMPERSONATE_NAME", "SE_INC_BASE_PRIORITY_NAME", "SE_INCREASE_QUOTA_NAME", "SE_INC_WORKING_SET_NAME", "SE_LOAD_DRIVER_NAME", "SE_LOCK_MEMORY_NAME", "SE_MACHINE_ACCOUNT_NAME", "SE_MANAGE_VOLUME_NAME", "SE_PROF_SINGLE_PROCESS_NAME", "SE_RELABEL_NAME", "SE_REMOTE_SHUTDOWN_NAME", "SE_RESTORE_NAME", "SE_SECURITY_NAME", "SE_SHUTDOWN_NAME", "SE_SYNC_AGENT_NAME", "SE_SYSTEM_ENVIRONMENT_NAME", "SE_SYSTEM_PROFILE_NAME", "SE_SYSTEMTIME_NAME", "SE_TAKE_OWNERSHIP_NAME", "SE_TCB_NAME", "SE_TIME_ZONE_NAME", "SE_TRUSTED_CREDMAN_ACCESS_NAME", "SE_UNDOCK_NAME", "SE_UNSOLICITED_INPUT_NAME", "SE_BATCH_LOGON_NAME", "SE_DENY_BATCH_LOGON_NAME", "SE_DENY_INTERACTIVE_LOGON_NAME", "SE_DENY_NETWORK_LOGON_NAME", "SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME", "SE_DENY_SERVICE_LOGON_NAME", "SE_INTERACTIVE_LOGON_NAME", "SE_NETWORK_LOGON_NAME", "SE_REMOTE_INTERACTIVE_LOGON_NAME", "SE_SERVICE_LOGON_NAME"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.userright.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
