# SCAP-NG 0.4 capability-specific native Object selectors

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Generated capability-specific selector overlay. Resolved entries close the operator vocabulary and value constraints; unresolved mappings are intentionally not guessed.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `selector_value_reference` | object | Definition | **Unresolved description** | [/$defs/selector_value_reference](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/selector_value_reference) |
| `linux_dpkginfo_name_selector` | object | Definition | OVAL 5.12.3 dpkginfo_object.name is an EntityObjectStringType. | [/$defs/linux_dpkginfo_name_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_name_selector) |
| `linux_partition_mount_point_selector` | object | Definition | The native contract uses the string selector vocabulary. | [/$defs/linux_partition_mount_point_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_partition_mount_point_selector) |
| `linux_selinuxboolean_name_selector` | object | Definition | OVAL 5.12.3 selinuxboolean_object.name is an EntityObjectStringType. | [/$defs/linux_selinuxboolean_name_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_name_selector) |
| `linux_systemdunitdependency_unit_selector` | object | Definition | OVAL 5.12.3 systemdunitdependency_object.unit is an EntityObjectStringType. | [/$defs/linux_systemdunitdependency_unit_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_unit_selector) |
| `linux_systemdunitproperty_unit_selector` | object | Definition | OVAL 5.12.3 systemdunitproperty_object.unit and property are EntityObjectStringType selectors. | [/$defs/linux_systemdunitproperty_unit_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_unit_selector) |
| `linux_systemdunitproperty_property_selector` | object | Definition | OVAL 5.12.3 systemdunitproperty_object.unit and property are EntityObjectStringType selectors. | [/$defs/linux_systemdunitproperty_property_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_property_selector) |
| `unix_file_filepath_selector` | object | Definition | OVAL 5.12.3 unix file_object selectors use EntityObjectStringType and retain all five string operations through the native crosswalk. filename null is the explicit directory-object form; empty string remains a string operand. | [/$defs/unix_file_filepath_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_filepath_selector) |
| `unix_file_path_selector` | object | Definition | OVAL 5.12.3 unix file_object selectors use EntityObjectStringType and retain all five string operations through the native crosswalk. filename null is the explicit directory-object form; empty string remains a string operand. | [/$defs/unix_file_path_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_path_selector) |
| `unix_file_filename_selector` | object | Definition | OVAL 5.12.3 unix file_object selectors use EntityObjectStringType and retain all five string operations through the native crosswalk. filename null is the explicit directory-object form; empty string remains a string operand. | [/$defs/unix_file_filename_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_filename_selector) |
| `unix_interface_name_selector` | object | Definition | OVAL 5.12.3 interface_object.name is an EntityObjectStringType. | [/$defs/unix_interface_name_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_interface_name_selector) |
| `unix_password_username_selector` | object | Definition | OVAL 5.12.3 password_object.username is an EntityObjectStringType. | [/$defs/unix_password_username_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_password_username_selector) |
| `unix_shadow_username_selector` | object | Definition | OVAL 5.12.3 shadow_object.username is an EntityObjectStringType. | [/$defs/unix_shadow_username_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_shadow_username_selector) |
| `windows_file_filepath_selector` | object | Definition | OVAL 5.12.3 Windows file_object selectors use EntityObjectStringType and retain all five string operations through the native crosswalk. filename null is the explicit directory-object form; empty string remains a string operand. | [/$defs/windows_file_filepath_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_filepath_selector) |
| `windows_file_path_selector` | object | Definition | OVAL 5.12.3 Windows file_object selectors use EntityObjectStringType and retain all five string operations through the native crosswalk. filename null is the explicit directory-object form; empty string remains a string operand. | [/$defs/windows_file_path_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_path_selector) |
| `windows_file_filename_selector` | object | Definition | OVAL 5.12.3 Windows file_object selectors use EntityObjectStringType and retain all five string operations through the native crosswalk. filename null is the explicit directory-object form; empty string remains a string operand. | [/$defs/windows_file_filename_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_filename_selector) |
| `windows_fileeffectiverights_filepath_selector` | object | Definition | OVAL 5.12.3 fileeffectiverights53_object selectors use EntityObjectStringType and retain all five string operations, including the source-limited non-equals trustee SID search. filename null selects the higher-level directory. | [/$defs/windows_fileeffectiverights_filepath_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_filepath_selector) |
| `windows_fileeffectiverights_path_selector` | object | Definition | OVAL 5.12.3 fileeffectiverights53_object selectors use EntityObjectStringType and retain all five string operations, including the source-limited non-equals trustee SID search. filename null selects the higher-level directory. | [/$defs/windows_fileeffectiverights_path_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_path_selector) |
| `windows_fileeffectiverights_filename_selector` | object | Definition | OVAL 5.12.3 fileeffectiverights53_object selectors use EntityObjectStringType and retain all five string operations, including the source-limited non-equals trustee SID search. filename null selects the higher-level directory. | [/$defs/windows_fileeffectiverights_filename_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_filename_selector) |
| `windows_fileeffectiverights_trustee_sid_selector` | object | Definition | OVAL 5.12.3 fileeffectiverights53_object selectors use EntityObjectStringType and retain all five string operations, including the source-limited non-equals trustee SID search. filename null selects the higher-level directory. | [/$defs/windows_fileeffectiverights_trustee_sid_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_trustee_sid_selector) |
| `windows_ntuser_key_selector` | object | Definition | OVAL 5.12.3 ntuser_object key and name use EntityObjectStringType with all five string operations. name null selects the higher-level key and empty string remains the default-value name. | [/$defs/windows_ntuser_key_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_key_selector) |
| `windows_ntuser_name_selector` | object | Definition | OVAL 5.12.3 ntuser_object key and name use EntityObjectStringType with all five string operations. name null selects the higher-level key and empty string remains the default-value name. | [/$defs/windows_ntuser_name_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_name_selector) |
| `windows_registry_hive_selector` | object | Definition | Hive names are canonical enum values. | [/$defs/windows_registry_hive_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_hive_selector) |
| `windows_registry_key_selector` | object | Definition | Registry key identity is case-insensitive. | [/$defs/windows_registry_key_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_key_selector) |
| `windows_registry_name_selector` | object | Definition | Registry value-name identity is case-insensitive. | [/$defs/windows_registry_name_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_name_selector) |
| `windows_regkeyeffectiverights_hive_selector` | object | Definition | OVAL 5.12.3 regkeyeffectiverights53_object uses the canonical registry-hive enum with equals only; key and trustee_sid retain all five EntityObjectStringType operations. key null selects the higher-level hive. | [/$defs/windows_regkeyeffectiverights_hive_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_hive_selector) |
| `windows_regkeyeffectiverights_key_selector` | object | Definition | OVAL 5.12.3 regkeyeffectiverights53_object uses the canonical registry-hive enum with equals only; key and trustee_sid retain all five EntityObjectStringType operations. key null selects the higher-level hive. | [/$defs/windows_regkeyeffectiverights_key_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_key_selector) |
| `windows_regkeyeffectiverights_trustee_sid_selector` | object | Definition | OVAL 5.12.3 regkeyeffectiverights53_object uses the canonical registry-hive enum with equals only; key and trustee_sid retain all five EntityObjectStringType operations. key null selects the higher-level hive. | [/$defs/windows_regkeyeffectiverights_trustee_sid_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_trustee_sid_selector) |
| `windows_service_service_name_selector` | object | Definition | OVAL 5.12.3 service_object.service_name is an EntityObjectStringType. | [/$defs/windows_service_service_name_selector](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_service_service_name_selector) |
| `linux_dpkginfo_object` | object, string | Definition | **Unresolved description** | [/$defs/linux_dpkginfo_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_object) |
| `linux_partition_object` | object, string | Definition | **Unresolved description** | [/$defs/linux_partition_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_partition_object) |
| `linux_selinuxboolean_object` | object, string | Definition | **Unresolved description** | [/$defs/linux_selinuxboolean_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_object) |
| `linux_systemdunitdependency_object` | object, string | Definition | **Unresolved description** | [/$defs/linux_systemdunitdependency_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_object) |
| `linux_systemdunitproperty_object` | object, string | Definition | **Unresolved description** | [/$defs/linux_systemdunitproperty_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object) |
| `unix_file_object` | object, string | Definition | Select filesystem entries and collect their metadata for comparison. | [/$defs/unix_file_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object) |
| `unix_interface_object` | object, string | Definition | **Unresolved description** | [/$defs/unix_interface_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_interface_object) |
| `unix_password_object` | object, string | Definition | **Unresolved description** | [/$defs/unix_password_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_password_object) |
| `unix_shadow_object` | object, string | Definition | **Unresolved description** | [/$defs/unix_shadow_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_shadow_object) |
| `windows_file_object` | object, string | Definition | **Unresolved description** | [/$defs/windows_file_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object) |
| `windows_fileeffectiverights_object` | object, string | Definition | **Unresolved description** | [/$defs/windows_fileeffectiverights_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object) |
| `windows_ntuser_object` | object, string | Definition | **Unresolved description** | [/$defs/windows_ntuser_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object) |
| `windows_registry_object` | object, string | Definition | **Unresolved description** | [/$defs/windows_registry_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object) |
| `windows_regkeyeffectiverights_object` | object, string | Definition | **Unresolved description** | [/$defs/windows_regkeyeffectiverights_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object) |
| `windows_service_object` | object, string | Definition | **Unresolved description** | [/$defs/windows_service_object](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_service_object) |

## `/$defs/linux_dpkginfo_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/linux_dpkginfo_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/linux_dpkginfo_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/linux_dpkginfo_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_object/oneOf/1/properties/set) |
| `name` | object | 0..1 | OVAL 5.12.3 dpkginfo_object.name is an EntityObjectStringType. | [/$defs/linux_dpkginfo_object/oneOf/1/properties/name](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_object/oneOf/1/properties/name) |

## `/$defs/linux_partition_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/linux_partition_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/linux_partition_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/linux_partition_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1/properties/set) |
| `mount_point` | object | 0..1 | The native contract uses the string selector vocabulary. | [/$defs/linux_partition_object/oneOf/1/properties/mount_point](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1/properties/mount_point) |

## `/$defs/linux_selinuxboolean_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/linux_selinuxboolean_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/linux_selinuxboolean_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/linux_selinuxboolean_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_object/oneOf/1/properties/set) |
| `name` | object | 0..1 | OVAL 5.12.3 selinuxboolean_object.name is an EntityObjectStringType. | [/$defs/linux_selinuxboolean_object/oneOf/1/properties/name](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_object/oneOf/1/properties/name) |

## `/$defs/linux_systemdunitdependency_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/linux_systemdunitdependency_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/linux_systemdunitdependency_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/linux_systemdunitdependency_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_object/oneOf/1/properties/set) |
| `unit` | object | 0..1 | OVAL 5.12.3 systemdunitdependency_object.unit is an EntityObjectStringType. | [/$defs/linux_systemdunitdependency_object/oneOf/1/properties/unit](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_object/oneOf/1/properties/unit) |

## `/$defs/linux_systemdunitproperty_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/linux_systemdunitproperty_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/linux_systemdunitproperty_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/linux_systemdunitproperty_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1/properties/set) |
| `unit` | object | 0..1 | OVAL 5.12.3 systemdunitproperty_object.unit and property are EntityObjectStringType selectors. | [/$defs/linux_systemdunitproperty_object/oneOf/1/properties/unit](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1/properties/unit) |
| `property` | object | 0..1 | OVAL 5.12.3 systemdunitproperty_object.unit and property are EntityObjectStringType selectors. | [/$defs/linux_systemdunitproperty_object/oneOf/1/properties/property](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1/properties/property) |

## `/$defs/unix_file_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/unix_file_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/unix_file_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/unix_file_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/set) |
| `filepath` | object | 0..1 | Full path of the selected entry. | [/$defs/unix_file_object/oneOf/1/properties/filepath](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filepath) |
| `path` | object | 0..1 | Directory containing the selected entry. | [/$defs/unix_file_object/oneOf/1/properties/path](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/path) |
| `filename` | null, object | 0..1 | Entry name within the selected directory; null selects the directory itself. | [/$defs/unix_file_object/oneOf/1/properties/filename](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filename) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/unix_file_object/oneOf/1/properties/filesystem](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filesystem) |
| `traversal` | object | 0..1 | Controls recursive searching through directories and symbolic links. | [/$defs/unix_file_object/oneOf/1/properties/traversal](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/traversal) |

## `/$defs/unix_interface_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/unix_interface_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/unix_interface_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/unix_interface_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1/properties/set) |
| `name` | object | 0..1 | OVAL 5.12.3 interface_object.name is an EntityObjectStringType. | [/$defs/unix_interface_object/oneOf/1/properties/name](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1/properties/name) |

## `/$defs/unix_password_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/unix_password_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_password_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/unix_password_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_password_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/unix_password_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_password_object/oneOf/1/properties/set) |
| `username` | object | 0..1 | OVAL 5.12.3 password_object.username is an EntityObjectStringType. | [/$defs/unix_password_object/oneOf/1/properties/username](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_password_object/oneOf/1/properties/username) |

## `/$defs/unix_shadow_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/unix_shadow_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/unix_shadow_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/unix_shadow_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1/properties/set) |
| `username` | object | 0..1 | OVAL 5.12.3 shadow_object.username is an EntityObjectStringType. | [/$defs/unix_shadow_object/oneOf/1/properties/username](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1/properties/username) |

## `/$defs/windows_file_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/windows_file_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/windows_file_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/windows_file_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/set) |
| `filepath` | object | 0..1 | OVAL 5.12.3 Windows file_object selectors use EntityObjectStringType and retain all five string operations through the native crosswalk. filename null is the explicit directory-object form; empty string remains a string operand. | [/$defs/windows_file_object/oneOf/1/properties/filepath](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/filepath) |
| `path` | object | 0..1 | OVAL 5.12.3 Windows file_object selectors use EntityObjectStringType and retain all five string operations through the native crosswalk. filename null is the explicit directory-object form; empty string remains a string operand. | [/$defs/windows_file_object/oneOf/1/properties/path](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/path) |
| `filename` | null, object | 0..1 | **Unresolved description** | [/$defs/windows_file_object/oneOf/1/properties/filename](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/filename) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/windows_file_object/oneOf/1/properties/filesystem](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/filesystem) |
| `traversal` | object | 0..1 | Windows file traversal. | [/$defs/windows_file_object/oneOf/1/properties/traversal](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/traversal) |

## `/$defs/windows_fileeffectiverights_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/set) |
| `filepath` | object | 0..1 | OVAL 5.12.3 fileeffectiverights53_object selectors use EntityObjectStringType and retain all five string operations, including the source-limited non-equals trustee SID search. filename null selects the higher-level directory. | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filepath](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filepath) |
| `path` | object | 0..1 | OVAL 5.12.3 fileeffectiverights53_object selectors use EntityObjectStringType and retain all five string operations, including the source-limited non-equals trustee SID search. filename null selects the higher-level directory. | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/path](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/path) |
| `filename` | null, object | 0..1 | **Unresolved description** | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filename](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filename) |
| `trustee_sid` | object | 0..1 | OVAL 5.12.3 fileeffectiverights53_object selectors use EntityObjectStringType and retain all five string operations, including the source-limited non-equals trustee SID search. filename null selects the higher-level directory. | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/trustee_sid](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/trustee_sid) |
| `filesystem` | string | 0..1 | Filesystem scope: all, local, or the starting filesystem (same). | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filesystem](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filesystem) |
| `traversal` | object | 0..1 | Windows file traversal. | [/$defs/windows_fileeffectiverights_object/oneOf/1/properties/traversal](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/traversal) |

## `/$defs/windows_ntuser_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/windows_ntuser_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/windows_ntuser_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/windows_ntuser_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/set) |
| `key` | object | 0..1 | OVAL 5.12.3 ntuser_object key and name use EntityObjectStringType with all five string operations. name null selects the higher-level key and empty string remains the default-value name. | [/$defs/windows_ntuser_object/oneOf/1/properties/key](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/key) |
| `name` | null, object | 0..1 | **Unresolved description** | [/$defs/windows_ntuser_object/oneOf/1/properties/name](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/name) |
| `include_default` | boolean | 0..1 | **Unresolved description** | [/$defs/windows_ntuser_object/oneOf/1/properties/include_default](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/include_default) |
| `item_creation` | string | 0..1 | **Unresolved description** | [/$defs/windows_ntuser_object/oneOf/1/properties/item_creation](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/item_creation) |

## `/$defs/windows_registry_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/windows_registry_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/windows_registry_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/windows_registry_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/set) |
| `hive` | object | 0..1 | Hive names are canonical enum values. | [/$defs/windows_registry_object/oneOf/1/properties/hive](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/hive) |
| `key` | null, object | 0..1 | **Unresolved description** | [/$defs/windows_registry_object/oneOf/1/properties/key](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/key) |
| `name` | null, object | 0..1 | **Unresolved description** | [/$defs/windows_registry_object/oneOf/1/properties/name](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/name) |

## `/$defs/windows_regkeyeffectiverights_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/set) |
| `hive` | object | 0..1 | OVAL 5.12.3 regkeyeffectiverights53_object uses the canonical registry-hive enum with equals only; key and trustee_sid retain all five EntityObjectStringType operations. key null selects the higher-level hive. | [/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/hive](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/hive) |
| `key` | null, object | 0..1 | **Unresolved description** | [/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/key](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/key) |
| `trustee_sid` | object | 0..1 | OVAL 5.12.3 regkeyeffectiverights53_object uses the canonical registry-hive enum with equals only; key and trustee_sid retain all five EntityObjectStringType operations. key null selects the higher-level hive. | [/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/trustee_sid](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/trustee_sid) |

## `/$defs/windows_service_object/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Capability responsible for collecting or interpreting this resource. | [/$defs/windows_service_object/oneOf/1/properties/capability](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_service_object/oneOf/1/properties/capability) |
| `filters` | array | 0..1 | Post-collection inclusion or exclusion filters applied to observed Items. | [/$defs/windows_service_object/oneOf/1/properties/filters](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_service_object/oneOf/1/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/windows_service_object/oneOf/1/properties/set](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_service_object/oneOf/1/properties/set) |
| `service_name` | object | 0..1 | OVAL 5.12.3 service_object.service_name is an EntityObjectStringType. | [/$defs/windows_service_object/oneOf/1/properties/service_name](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_service_object/oneOf/1/properties/service_name) |

## Advanced constraints

[Local constraints](../advanced/native-selector.md) and [complete JSON Schema](../../../proposed-schema/documentation/native-selector.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
