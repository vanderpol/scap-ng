# windows.auditeventpolicysubcategories

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `credential_validation` | array, object | 0..1 | Audit-policy setting for the events produced during the validation of a user's logon credentials. | [/$defs/meanings/properties/credential_validation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/credential_validation) |
| `kerberos_authentication_service` | array, object | 0..1 | Audit-policy setting for the events produced by Kerberos authentication ticket-granting requests. | [/$defs/meanings/properties/kerberos_authentication_service](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kerberos_authentication_service) |
| `kerberos_service_ticket_operations` | array, object | 0..1 | Audit-policy setting for the events produced by Kerberos service ticket requests. | [/$defs/meanings/properties/kerberos_service_ticket_operations](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kerberos_service_ticket_operations) |
| `other_account_logon_events` | array, object | 0..1 | Audit-policy setting for the events produced by changes to user accounts that are not covered by other events in the Account Logon category. | [/$defs/meanings/properties/other_account_logon_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_account_logon_events) |
| `application_group_management` | array, object | 0..1 | Audit-policy setting for the events produced by changes to application groups. | [/$defs/meanings/properties/application_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/application_group_management) |
| `computer_account_management` | array, object | 0..1 | Audit-policy setting for the events produced by changes to computer accounts. | [/$defs/meanings/properties/computer_account_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/computer_account_management) |
| `distribution_group_management` | array, object | 0..1 | Audit-policy setting for the events produced by changes to distribution groups. | [/$defs/meanings/properties/distribution_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/distribution_group_management) |
| `other_account_management_events` | array, object | 0..1 | Audit-policy setting for the events produced by other user account changes that are not covered by other events in the Account Management category. | [/$defs/meanings/properties/other_account_management_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_account_management_events) |
| `security_group_management` | array, object | 0..1 | Audit-policy setting for the events produced by changes to security groups. | [/$defs/meanings/properties/security_group_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_group_management) |
| `user_account_management` | array, object | 0..1 | Audit-policy setting for the events produced by changes to user accounts. | [/$defs/meanings/properties/user_account_management](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/user_account_management) |
| `dpapi_activity` | array, object | 0..1 | Audit-policy setting for the events produced when requests are made to the Data Protection application interface. | [/$defs/meanings/properties/dpapi_activity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/dpapi_activity) |
| `process_creation` | array, object | 0..1 | Audit-policy setting for the events produced when a process is created or starts. | [/$defs/meanings/properties/process_creation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/process_creation) |
| `process_termination` | array, object | 0..1 | Audit-policy setting for the events produced when a process ends. | [/$defs/meanings/properties/process_termination](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/process_termination) |
| `rpc_events` | array, object | 0..1 | Audit-policy setting for the events produced by inbound remote procedure call connections. | [/$defs/meanings/properties/rpc_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/rpc_events) |
| `directory_service_access` | array, object | 0..1 | Audit-policy setting for the events produced when an Active Directory Domain Services object is accessed. | [/$defs/meanings/properties/directory_service_access](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_access) |
| `directory_service_changes` | array, object | 0..1 | Audit-policy setting for the events produced when changes are made to Active Directory Domain Services objects. | [/$defs/meanings/properties/directory_service_changes](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_changes) |
| `directory_service_replication` | array, object | 0..1 | Audit-policy setting for the events produced when two Active Directory Domain Services domain controllers are replicated. | [/$defs/meanings/properties/directory_service_replication](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/directory_service_replication) |
| `detailed_directory_service_replication` | array, object | 0..1 | Audit-policy setting for the events produced by detailed Active Directory Domain Services replication between domain controllers. | [/$defs/meanings/properties/detailed_directory_service_replication](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/detailed_directory_service_replication) |
| `account_lockout` | array, object | 0..1 | Audit-policy setting for the events produced by a failed attempt to log onto a locked out account. | [/$defs/meanings/properties/account_lockout](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/account_lockout) |
| `ipsec_extended_mode` | array, object | 0..1 | Audit-policy setting for the events produced by Internet Key Exchange and Authenticated Internet protocol during Extended Mode negotiations. | [/$defs/meanings/properties/ipsec_extended_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_extended_mode) |
| `ipsec_main_mode` | array, object | 0..1 | Audit-policy setting for the events produced by Internet Key Exchange and Authenticated Internet protocol during Main Mode negotiations. | [/$defs/meanings/properties/ipsec_main_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_main_mode) |
| `ipsec_quick_mode` | array, object | 0..1 | Audit-policy setting for the events produced by Internet Key Exchange and Authenticated Internet protocol during Quick Mode negotiations. | [/$defs/meanings/properties/ipsec_quick_mode](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_quick_mode) |
| `logoff` | array, object | 0..1 | Audit-policy setting for the events produced by closing a logon session. | [/$defs/meanings/properties/logoff](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logoff) |
| `logon` | array, object | 0..1 | Audit-policy setting for the events produced by attempts to log onto a user account. | [/$defs/meanings/properties/logon](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logon) |
| `network_policy_server` | array, object | 0..1 | Audit-policy setting for the events produced by RADIUS and Network Access Protection user access requests. | [/$defs/meanings/properties/network_policy_server](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/network_policy_server) |
| `other_logon_logoff_events` | array, object | 0..1 | Audit-policy setting for the events produced by other logon/logoff based events that are not covered in the Logon/Logoff category. | [/$defs/meanings/properties/other_logon_logoff_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_logon_logoff_events) |
| `special_logon` | array, object | 0..1 | Audit-policy setting for the events produced by special logons. | [/$defs/meanings/properties/special_logon](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/special_logon) |
| `logon_claims` | array, object | 0..1 | Audit-policy setting for user and device claims information in the user's logon token. | [/$defs/meanings/properties/logon_claims](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/logon_claims) |
| `application_generated` | array, object | 0..1 | Audit-policy setting for the events produced by applications that use the Windows Auditing API. | [/$defs/meanings/properties/application_generated](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/application_generated) |
| `certification_services` | array, object | 0..1 | Audit-policy setting for the events produced by operations on Active Directory Certificate Services. | [/$defs/meanings/properties/certification_services](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/certification_services) |
| `detailed_file_share` | array, object | 0..1 | Audit-policy setting for the events produced by attempts to access files and folders on a shared folder. | [/$defs/meanings/properties/detailed_file_share](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/detailed_file_share) |
| `file_share` | array, object | 0..1 | Audit-policy setting for the events produced by attempts to access a shared folder. | [/$defs/meanings/properties/file_share](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/file_share) |
| `file_system` | array, object | 0..1 | Audit-policy setting for the events produced user attempts to access file system objects. | [/$defs/meanings/properties/file_system](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/file_system) |
| `filtering_platform_connection` | array, object | 0..1 | Audit-policy setting for the events produced by connections that are allowed or blocked by Windows Filtering Platform. | [/$defs/meanings/properties/filtering_platform_connection](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_connection) |
| `filtering_platform_packet_drop` | array, object | 0..1 | Audit-policy setting for the events produced by packets that are dropped by Windows Filtering Platform. | [/$defs/meanings/properties/filtering_platform_packet_drop](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_packet_drop) |
| `handle_manipulation` | array, object | 0..1 | Audit-policy setting for the events produced when a handle is opened or closed. | [/$defs/meanings/properties/handle_manipulation](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/handle_manipulation) |
| `kernel_object` | array, object | 0..1 | Audit-policy setting for the events produced by attempts to access the system kernel. | [/$defs/meanings/properties/kernel_object](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/kernel_object) |
| `other_object_access_events` | array, object | 0..1 | Audit-policy setting for the events produced by the management of Task Scheduler jobs or COM+ objects. | [/$defs/meanings/properties/other_object_access_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_object_access_events) |
| `registry` | array, object | 0..1 | Audit-policy setting for the events produced by attempts to access registry objects. | [/$defs/meanings/properties/registry](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/registry) |
| `sam` | array, object | 0..1 | Audit-policy setting for the events produced by attempts to access Security Accounts Manager objects. | [/$defs/meanings/properties/sam](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/sam) |
| `removable_storage` | array, object | 0..1 | Audit-policy setting for events that indicate file object access attemps to removable storage. | [/$defs/meanings/properties/removable_storage](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/removable_storage) |
| `central_access_policy_staging` | array, object | 0..1 | Audit-policy setting for events that indicate permission granted or denied by a proposed policy differs from the current central access policy on an object. | [/$defs/meanings/properties/central_access_policy_staging](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/central_access_policy_staging) |
| `audit_policy_change` | array, object | 0..1 | Audit-policy setting for the events produced by changes in security audit policy settings. | [/$defs/meanings/properties/audit_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/audit_policy_change) |
| `authentication_policy_change` | array, object | 0..1 | Audit-policy setting for the events produced by changes to the authentication policy. | [/$defs/meanings/properties/authentication_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/authentication_policy_change) |
| `authorization_policy_change` | array, object | 0..1 | Audit-policy setting for the events produced by changes to the authorization policy. | [/$defs/meanings/properties/authorization_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/authorization_policy_change) |
| `filtering_platform_policy_change` | array, object | 0..1 | Audit-policy setting for the events produced by changes to the Windows Filtering Platform. | [/$defs/meanings/properties/filtering_platform_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/filtering_platform_policy_change) |
| `mpssvc_rule_level_policy_change` | array, object | 0..1 | Audit-policy setting for the events produced by changes to policy rules used by the Windows Firewall. | [/$defs/meanings/properties/mpssvc_rule_level_policy_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/mpssvc_rule_level_policy_change) |
| `other_policy_change_events` | array, object | 0..1 | Audit-policy setting for the events produced by other security policy changes that are not covered other events in the Policy Change category. | [/$defs/meanings/properties/other_policy_change_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_policy_change_events) |
| `non_sensitive_privilege_use` | array, object | 0..1 | Audit-policy setting for the events produced by the use of non-sensitive privileges. | [/$defs/meanings/properties/non_sensitive_privilege_use](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/non_sensitive_privilege_use) |
| `other_privilege_use_events` | array, object | 0..1 | Audit-policy setting for other privilege-use events. | [/$defs/meanings/properties/other_privilege_use_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_privilege_use_events) |
| `sensitive_privilege_use` | array, object | 0..1 | Audit-policy setting for the events produced by the use of sensitive privileges. | [/$defs/meanings/properties/sensitive_privilege_use](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/sensitive_privilege_use) |
| `ipsec_driver` | array, object | 0..1 | Audit-policy setting for the events produced by the IPsec filter driver. | [/$defs/meanings/properties/ipsec_driver](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/ipsec_driver) |
| `other_system_events` | array, object | 0..1 | Audit-policy setting for the events produced by the startup and shutdown, security policy processing, and cryptography key file and migration operations of the Windows Firewall. | [/$defs/meanings/properties/other_system_events](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/other_system_events) |
| `security_state_change` | array, object | 0..1 | Audit-policy setting for the events produced by changes in the security state. | [/$defs/meanings/properties/security_state_change](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_state_change) |
| `security_system_extension` | array, object | 0..1 | Audit-policy setting for the events produced by the security system extensions or services. | [/$defs/meanings/properties/security_system_extension](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/security_system_extension) |
| `system_integrity` | array, object | 0..1 | Audit-policy setting for the events that indicate that the integrity security subsystem has been violated. | [/$defs/meanings/properties/system_integrity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/system_integrity) |
| `group_membership` | array, object | 0..1 | Audit-policy setting for the group membership of a token for an associated log on. | [/$defs/meanings/properties/group_membership](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/group_membership) |
| `pnp_activity` | array, object | 0..1 | Audit-policy setting for events generated by plug and play (PNP). | [/$defs/meanings/properties/pnp_activity](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/pnp_activity) |
| `user_device_claims` | array, object | 0..1 | Audit-policy setting for the user and device claims that are present in the token of an associated logon. | [/$defs/meanings/properties/user_device_claims](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/user_device_claims) |
| `audit_detailedtracking_tokenrightadjusted` | array, object | 0..1 | Audit-policy setting for when token privileges are enabled or disabled for a specific account’s token. | [/$defs/meanings/properties/audit_detailedtracking_tokenrightadjusted](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json#/$defs/meanings/properties/audit_detailedtracking_tokenrightadjusted) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |


Validation shape: [/$defs/canonical_all_items_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.auditeventpolicysubcategories.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`credential_validation` | string | source-derived |
| Item.`kerberos_authentication_service` | string | source-derived |
| Item.`kerberos_service_ticket_operations` | string | source-derived |
| Item.`other_account_logon_events` | string | source-derived |
| Item.`application_group_management` | string | source-derived |
| Item.`computer_account_management` | string | source-derived |
| Item.`distribution_group_management` | string | source-derived |
| Item.`other_account_management_events` | string | source-derived |
| Item.`security_group_management` | string | source-derived |
| Item.`user_account_management` | string | source-derived |
| Item.`dpapi_activity` | string | source-derived |
| Item.`process_creation` | string | source-derived |
| Item.`process_termination` | string | source-derived |
| Item.`rpc_events` | string | source-derived |
| Item.`directory_service_access` | string | source-derived |
| Item.`directory_service_changes` | string | source-derived |
| Item.`directory_service_replication` | string | source-derived |
| Item.`detailed_directory_service_replication` | string | source-derived |
| Item.`account_lockout` | string | source-derived |
| Item.`ipsec_extended_mode` | string | source-derived |
| Item.`ipsec_main_mode` | string | source-derived |
| Item.`ipsec_quick_mode` | string | source-derived |
| Item.`logoff` | string | source-derived |
| Item.`logon` | string | source-derived |
| Item.`network_policy_server` | string | source-derived |
| Item.`other_logon_logoff_events` | string | source-derived |
| Item.`special_logon` | string | source-derived |
| Item.`logon_claims` | string | source-derived |
| Item.`application_generated` | string | source-derived |
| Item.`certification_services` | string | source-derived |
| Item.`detailed_file_share` | string | source-derived |
| Item.`file_share` | string | source-derived |
| Item.`file_system` | string | source-derived |
| Item.`filtering_platform_connection` | string | source-derived |
| Item.`filtering_platform_packet_drop` | string | source-derived |
| Item.`handle_manipulation` | string | source-derived |
| Item.`kernel_object` | string | source-derived |
| Item.`other_object_access_events` | string | source-derived |
| Item.`registry` | string | source-derived |
| Item.`sam` | string | source-derived |
| Item.`removable_storage` | string | source-derived |
| Item.`central_access_policy_staging` | string | source-derived |
| Item.`audit_policy_change` | string | source-derived |
| Item.`authentication_policy_change` | string | source-derived |
| Item.`authorization_policy_change` | string | source-derived |
| Item.`filtering_platform_policy_change` | string | source-derived |
| Item.`mpssvc_rule_level_policy_change` | string | source-derived |
| Item.`other_policy_change_events` | string | source-derived |
| Item.`non_sensitive_privilege_use` | string | source-derived |
| Item.`other_privilege_use_events` | string | source-derived |
| Item.`sensitive_privilege_use` | string | source-derived |
| Item.`ipsec_driver` | string | source-derived |
| Item.`other_system_events` | string | source-derived |
| Item.`security_state_change` | string | source-derived |
| Item.`security_system_extension` | string | source-derived |
| Item.`system_integrity` | string | source-derived |
| Item.`group_membership` | string | source-derived |
| Item.`pnp_activity` | string | source-derived |
| Item.`user_device_claims` | string | source-derived |
| Item.`audit_detailedtracking_tokenrightadjusted` | string | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.auditeventpolicysubcategories.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
