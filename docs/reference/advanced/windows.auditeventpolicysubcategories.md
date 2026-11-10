# windows.auditeventpolicysubcategories — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/credential_validation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/credential_validation) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/credential_validation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/credential_validation): Audit-policy setting for the events produced during the validation of a user's logon credentials.

Audit the events produced during the validation of a user's logon credentials.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce923f-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Logon: Audit Credential Validation

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/kerberos_authentication_service](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kerberos_authentication_service) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/kerberos_authentication_service](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kerberos_authentication_service): Audit-policy setting for the events produced by Kerberos authentication ticket-granting requests.

Audit the events produced by Kerberos authentication ticket-granting requests.

This state corresponds with the following GUID specified in ntsecapi.h: 0CCE9242-69AE-11D9-BED3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Logon: Audit Kerberos Authentication Service

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/kerberos_service_ticket_operations](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kerberos_service_ticket_operations) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/kerberos_service_ticket_operations](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kerberos_service_ticket_operations): Audit-policy setting for the events produced by Kerberos service ticket requests.

Audit the events produced by Kerberos service ticket requests.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9240-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Logon: Audit Kerberos Service Ticket Operations

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/other_account_logon_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_account_logon_events) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/other_account_logon_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_account_logon_events): Audit-policy setting for the events produced by changes to user accounts that are not covered by other events in the Account Logon category.

Audit the events produced by changes to user accounts that are not covered by other events in the Account Logon category.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9241-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Logon: Audit Other Account Logon Events

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/application_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/application_group_management) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/application_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/application_group_management): Audit-policy setting for the events produced by changes to application groups.

Audit the events produced by changes to application groups.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9239-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Management: Audit Application Group Management

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/computer_account_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/computer_account_management) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/computer_account_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/computer_account_management): Audit-policy setting for the events produced by changes to computer accounts.

Audit the events produced by changes to computer accounts.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9236-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Management: Audit Computer Account Management

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/distribution_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/distribution_group_management) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/distribution_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/distribution_group_management): Audit-policy setting for the events produced by changes to distribution groups.

Audit the events produced by changes to distribution groups.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9238-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Management: Audit Distribution Group Management

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/other_account_management_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_account_management_events) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/other_account_management_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_account_management_events): Audit-policy setting for the events produced by other user account changes that are not covered by other events in the Account Management category.

Audit the events produced by other user account changes that are not covered by other events in the Account Management category.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce923a-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Management: Audit Other Account Management Events

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/security_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_group_management) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/security_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_group_management): Audit-policy setting for the events produced by changes to security groups.

Audit the events produced by changes to security groups.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9237-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Management: Audit Security Group Management

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/user_account_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/user_account_management) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/user_account_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/user_account_management): Audit-policy setting for the events produced by changes to user accounts.

Audit the events produced by changes to user accounts.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9235-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Account Management: Audit User Account Management

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/dpapi_activity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/dpapi_activity) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/dpapi_activity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/dpapi_activity): Audit-policy setting for the events produced when requests are made to the Data Protection application interface.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce922d-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Detailed Tracking: Audit DPAPI Activity

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/process_creation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/process_creation) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/process_creation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/process_creation): Audit-policy setting for the events produced when a process is created or starts.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce922b-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Detailed Tracking: Audit Process Creation

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/process_termination](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/process_termination) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/process_termination](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/process_termination): Audit-policy setting for the events produced when a process ends.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce922c-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Detailed Tracking: Audit Process Termination

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/rpc_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/rpc_events) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/rpc_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/rpc_events): Audit-policy setting for the events produced by inbound remote procedure call connections.

Audit the events produced by inbound remote procedure call connections.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce922e-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Detailed Tracking: Audit RPC Events

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory_service_access](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_access) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/directory_service_access](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_access): Audit-policy setting for the events produced when an Active Directory Domain Services object is accessed.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce923b-69ae-11d9-bed3-505054503030.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory_service_changes](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_changes) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/directory_service_changes](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_changes): Audit-policy setting for the events produced when changes are made to Active Directory Domain Services objects.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce923c-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: DS Access: Audit Directory Service Changes

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory_service_replication](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_replication) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/directory_service_replication](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_replication): Audit-policy setting for the events produced when two Active Directory Domain Services domain controllers are replicated.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce923d-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: DS Access: Audit Directory Service Access

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/detailed_directory_service_replication](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/detailed_directory_service_replication) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/detailed_directory_service_replication](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/detailed_directory_service_replication): Audit-policy setting for the events produced by detailed Active Directory Domain Services replication between domain controllers.

Audit the events produced by detailed Active Directory Domain Services replication between domain controllers.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce923e-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: DS Access: Audit Detailed Directory Service Replication

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/account_lockout](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/account_lockout) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/account_lockout](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/account_lockout): Audit-policy setting for the events produced by a failed attempt to log onto a locked out account.

Audit the events produced by a failed attempt to log onto a locked out account.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9217-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit Account Lockout

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipsec_extended_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_extended_mode) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/ipsec_extended_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_extended_mode): Audit-policy setting for the events produced by Internet Key Exchange and Authenticated Internet protocol during Extended Mode negotiations.

Audit the events produced by Internet Key Exchange and Authenticated Internet protocol during Extended Mode negotiations.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce921a-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit IPsec Extended Mode

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipsec_main_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_main_mode) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/ipsec_main_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_main_mode): Audit-policy setting for the events produced by Internet Key Exchange and Authenticated Internet protocol during Main Mode negotiations.

Audit the events produced by Internet Key Exchange and Authenticated Internet protocol during Main Mode negotiations.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9218-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logof/Logoff: Audit IPsec Main Mode

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipsec_quick_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_quick_mode) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/ipsec_quick_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_quick_mode): Audit-policy setting for the events produced by Internet Key Exchange and Authenticated Internet protocol during Quick Mode negotiations.

Audit the events produced by Internet Key Exchange and Authenticated Internet protocol during Quick Mode negotiations.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9219-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit IPsec Quick Mode

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/logoff](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logoff) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/logoff](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logoff): Audit-policy setting for the events produced by closing a logon session.

Audit the events produced by closing a logon session.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9216-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit Logoff

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/logon](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logon) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/logon](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logon): Audit-policy setting for the events produced by attempts to log onto a user account.

Audit the events produced by attempts to log onto a user account.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9215-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit Logon

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/network_policy_server](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/network_policy_server) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/network_policy_server](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/network_policy_server): Audit-policy setting for the events produced by RADIUS and Network Access Protection user access requests.

Audit the events produced by RADIUS and Network Access Protection user access requests.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9243-69ae-11d9-bed3-505054503030.This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit Network Policy Server

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/other_logon_logoff_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_logon_logoff_events) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/other_logon_logoff_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_logon_logoff_events): Audit-policy setting for the events produced by other logon/logoff based events that are not covered in the Logon/Logoff category.

Audit the events produced by other logon/logoff based events that are not covered in the Logon/Logoff category.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce921c-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit Other Logon/Logoff Events

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/special_logon](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/special_logon) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/special_logon](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/special_logon): Audit-policy setting for the events produced by special logons.

Audit the events produced by special logons.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce921b-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit Special Logon

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/logon_claims](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logon_claims) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/logon_claims](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logon_claims): Audit-policy setting for user and device claims information in the user's logon token.

Audit user and device claims information in the user's logon token.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9247-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Logon/Logoff: Audit User / Device Claims

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/application_generated](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/application_generated) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/application_generated](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/application_generated): Audit-policy setting for the events produced by applications that use the Windows Auditing API.

Audit the events produced by applications that use the Windows Auditing API.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9222-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit Application Generated

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/certification_services](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/certification_services) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/certification_services](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/certification_services): Audit-policy setting for the events produced by operations on Active Directory Certificate Services.

Audit the events produced by operations on Active Directory Certificate Services.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9221-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit Certification Services

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/detailed_file_share](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/detailed_file_share) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/detailed_file_share](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/detailed_file_share): Audit-policy setting for the events produced by attempts to access files and folders on a shared folder.

Audit the events produced by attempts to access files and folders on a shared folder.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9244-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit Detailed File Share

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_share](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/file_share) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/file_share](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/file_share): Audit-policy setting for the events produced by attempts to access a shared folder.

Audit the events produced by attempts to access a shared folder.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9224-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit File Share

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_system](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/file_system) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/file_system](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/file_system): Audit-policy setting for the events produced user attempts to access file system objects.

Audit the events produced user attempts to access file system objects.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce921d-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit File System

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/filtering_platform_connection](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_connection) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/filtering_platform_connection](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_connection): Audit-policy setting for the events produced by connections that are allowed or blocked by Windows Filtering Platform.

Audit the events produced by connections that are allowed or blocked by Windows Filtering Platform.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9226-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit Filtering Platform Connection

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/filtering_platform_packet_drop](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_packet_drop) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/filtering_platform_packet_drop](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_packet_drop): Audit-policy setting for the events produced by packets that are dropped by Windows Filtering Platform.

Audit the events produced by packets that are dropped by Windows Filtering Platform.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9225-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit Filtering Platform Packet Drop

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/handle_manipulation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/handle_manipulation) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/handle_manipulation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/handle_manipulation): Audit-policy setting for the events produced when a handle is opened or closed.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9223-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Handle Manipulation

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/kernel_object](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kernel_object) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/kernel_object](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kernel_object): Audit-policy setting for the events produced by attempts to access the system kernel.

Audit the events produced by attempts to access the system kernel.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce921f-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Kernel Object

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/other_object_access_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_object_access_events) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/other_object_access_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_object_access_events): Audit-policy setting for the events produced by the management of Task Scheduler jobs or COM+ objects.

Audit the events produced by the management of Task Scheduler jobs or COM+ objects.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9227-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Other Object Access Events

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/registry](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/registry) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/registry](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/registry): Audit-policy setting for the events produced by attempts to access registry objects.

Audit the events produced by attempts to access registry objects.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce921e-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit Registry

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/sam](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/sam) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/sam](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/sam): Audit-policy setting for the events produced by attempts to access Security Accounts Manager objects.

Audit the events produced by attempts to access Security Accounts Manager objects.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9220-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit SAM

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/removable_storage](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/removable_storage) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/removable_storage](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/removable_storage): Audit-policy setting for events that indicate file object access attemps to removable storage.

Audit events that indicate file object access attempts to removable storage.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9245-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Audit Removable Storage

Audit events that indicate file object access attemps to removable storage.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/central_access_policy_staging](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/central_access_policy_staging) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/central_access_policy_staging](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/central_access_policy_staging): Audit-policy setting for events that indicate permission granted or denied by a proposed policy differs from the current central access policy on an object.

Audit events that indicate permission granted or denied by a proposed policy differs from the current central access policy on an object.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9246-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Object Access: Central Access Policy Staging

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/audit_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/audit_policy_change) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/audit_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/audit_policy_change): Audit-policy setting for the events produced by changes in security audit policy settings.

Audit the events produced by changes in security audit policy settings.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce922f-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Policy Change: Audit Audit Policy Change

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/authentication_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/authentication_policy_change) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/authentication_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/authentication_policy_change): Audit-policy setting for the events produced by changes to the authentication policy.

Audit the events produced by changes to the authentication policy.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9230-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Policy Change: Audit Authentication Policy Change

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/authorization_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/authorization_policy_change) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/authorization_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/authorization_policy_change): Audit-policy setting for the events produced by changes to the authorization policy.

Audit the events produced by changes to the authorization policy.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9231-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Policy Change: Audit Authorization Policy Change

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/filtering_platform_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_policy_change) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/filtering_platform_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_policy_change): Audit-policy setting for the events produced by changes to the Windows Filtering Platform.

Audit the events produced by changes to the Windows Filtering Platform.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9233-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Policy Change: Audit Filtering Platform Policy Change

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/mpssvc_rule_level_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/mpssvc_rule_level_policy_change) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/mpssvc_rule_level_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/mpssvc_rule_level_policy_change): Audit-policy setting for the events produced by changes to policy rules used by the Windows Firewall.

Audit the events produced by changes to policy rules used by the Windows Firewall.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9232-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Policy Change: Audit MPSSVC Rule-Level Policy Change

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/other_policy_change_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_policy_change_events) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/other_policy_change_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_policy_change_events): Audit-policy setting for the events produced by other security policy changes that are not covered other events in the Policy Change category.

Audit the events produced by other security policy changes that are not covered other events in the Policy Change category.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9234-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Policy Change: Audit Other Policy Change Events

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/non_sensitive_privilege_use](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/non_sensitive_privilege_use) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/non_sensitive_privilege_use](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/non_sensitive_privilege_use): Audit-policy setting for the events produced by the use of non-sensitive privileges.

Audit the events produced by the use of non-sensitive privileges.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9229-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Privilege Use: Audit Non Sensitive Privilege Use

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/other_privilege_use_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_privilege_use_events) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/other_privilege_use_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_privilege_use_events): Audit-policy setting for other privilege-use events.

This is currently not used and has been reserved by Microsoft for use in the future.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce922a-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Privilege Use: Audit Other Privilege Use Events

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/sensitive_privilege_use](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/sensitive_privilege_use) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/sensitive_privilege_use](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/sensitive_privilege_use): Audit-policy setting for the events produced by the use of sensitive privileges.

Audit the events produced by the use of sensitive privileges.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9228-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: Privilege Use: Audit Sensitive Privilege Use

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipsec_driver](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_driver) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/ipsec_driver](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_driver): Audit-policy setting for the events produced by the IPsec filter driver.

Audit the events produced by the IPsec filter driver.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9213-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: System: Audit IPsec Driver

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/other_system_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_system_events) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/other_system_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_system_events): Audit-policy setting for the events produced by the startup and shutdown, security policy processing, and cryptography key file and migration operations of the Windows Firewall.

Audit the events produced by the startup and shutdown, security policy processing, and cryptography key file and migration operations of the Windows Firewall.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9214-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: System: Audit Other System Events

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/security_state_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_state_change) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/security_state_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_state_change): Audit-policy setting for the events produced by changes in the security state.

Audit the events produced by changes in the security state.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9210-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: System: Audit Security State Change

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/security_system_extension](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_system_extension) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/security_system_extension](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_system_extension): Audit-policy setting for the events produced by the security system extensions or services.

Audit the events produced by the security system extensions or services.

This state corresponds with the following GUID specified in ntsecapi.h: cce9211-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: System: Audit Security System Extension

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/system_integrity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/system_integrity) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/system_integrity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/system_integrity): Audit-policy setting for the events that indicate that the integrity security subsystem has been violated.

Audit the events that indicate that the integrity security subsystem has been violated.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9212-69ae-11d9-bed3-505054503030.

This state corresponds with the following Advanced Audit Policy: System: Audit System Integrity

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/group_membership](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/group_membership) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/group_membership](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/group_membership): Audit-policy setting for the group membership of a token for an associated log on.

This subcategory audits the group membership of a token for an associated log on.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9249-69ae-11d9-bed3-505054503030.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/pnp_activity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/pnp_activity) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/pnp_activity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/pnp_activity): Audit-policy setting for events generated by plug and play (PNP).

This subcategory audits events generated by plug and play (PNP).

This state corresponds with the following GUID specified in ntsecapi.h: 0cce9248-69ae-11d9-bed3-505054503030.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/user_device_claims](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/user_device_claims) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/user_device_claims](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/user_device_claims): Audit-policy setting for the user and device claims that are present in the token of an associated logon.

This subcategory audits the user and device claims that are present in the token of an associated logon.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/audit_detailedtracking_tokenrightadjusted](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/audit_detailedtracking_tokenrightadjusted) | {"declared_values_not_new_validation_restrictions": ["AUDIT_FAILURE", "AUDIT_NONE", "AUDIT_SUCCESS", "AUDIT_SUCCESS_FAILURE"]} | source-derived |

[/$defs/meanings/properties/audit_detailedtracking_tokenrightadjusted](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/audit_detailedtracking_tokenrightadjusted): Audit-policy setting for when token privileges are enabled or disabled for a specific account’s token.

This state corresponds with the following GUID specified in ntsecapi.h: 0cce924a-69ae-11d9-bed3-505054503030.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/object): The Object is used by an audit event policy subcategories test to define those objects to evaluate based on a specified state.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/item): These settings are used to specify which system and network events are monitored.

It is important to note that these audit event policy settings are specific to certain versions of Windows.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
