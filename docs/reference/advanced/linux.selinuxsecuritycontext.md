# linux.selinuxsecuritycontext — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/full_path) | {} | source-derived |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/full_path): Absolute path for a file on the machine.

`full_path` specifies the absolute path for a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/directory) | {} | source-derived |

[/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/directory): Directory component of the absolute path to a file on the machine.

`directory` specifies the directory component of the absolute path to a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/name) | {} | source-derived |
| [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/pid) | {} | source-derived |

[/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/pid): The process ID of the process.

This is the process ID of the process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/user) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/user): SELinux user component of the security context.

`user` specifies the SELinux user that either created the file or started the process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/role](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/role) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/role](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/role): SELinux role component of the security context.

`role` specifies the types that a process may transition to (domain transitions).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/type) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/type): SELinux type or process domain component of the security context.

`type` specifies the domain in which the file is accessible or the domain in which a process executes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/low_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/low_sensitivity) | {} | source-derived |

[/$defs/meanings/properties/low_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/low_sensitivity): Current sensitivity of a file or process.

`low_sensitivity` specifies the current sensitivity of a file or process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/low_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/low_category) | {} | source-derived |

[/$defs/meanings/properties/low_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/low_category): Set of categories associated with the low sensitivity.

`low_category` specifies the set of categories associated with the low sensitivity.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/high_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/high_sensitivity) | {} | source-derived |

[/$defs/meanings/properties/high_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/high_sensitivity): Maximum range for a file or the clearance for a process.

`high_sensitivity` specifies the maximum range for a file or the clearance for a process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/high_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/high_category) | {} | source-derived |

[/$defs/meanings/properties/high_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/high_category): Set of categories associated with the high sensitivity.

`high_category` specifies the set of categories associated with the high sensitivity.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/rawlow_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawlow_sensitivity) | {} | source-derived |

[/$defs/meanings/properties/rawlow_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawlow_sensitivity): Current sensitivity of a file or process but in its raw context.

`rawlow_sensitivity` specifies the current sensitivity of a file or process but in its raw context.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/rawlow_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawlow_category) | {} | source-derived |

[/$defs/meanings/properties/rawlow_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawlow_category): Set of categories associated with the low sensitivity but in its raw context.

`rawlow_category` specifies the set of categories associated with the low sensitivity but in its raw context.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/rawhigh_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawhigh_sensitivity) | {} | source-derived |

[/$defs/meanings/properties/rawhigh_sensitivity](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawhigh_sensitivity): Maximum range for a file or the clearance for a process but in its raw context.

`rawhigh_sensitivity` specifies the maximum range for a file or the clearance for a process but in its raw context.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/rawhigh_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawhigh_category) | {} | source-derived |

[/$defs/meanings/properties/rawhigh_category](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/meanings/properties/rawhigh_category): Set of categories associated with the high sensitivity but in its raw context.

`rawhigh_category` specifies the set of categories associated with the high sensitivity but in its raw context.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/full_path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/directory](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/directory) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/name): Name of a file to evaluate.

`name` specifies the name of a file to evaluate.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/pid) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/object/properties/pid): Process ID of the process.

`pid` is the process ID of the process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/item): This item describes the SELinux security context of a file or process on the local system.

This item follows the SELinux security context structure: user:role:type:low_sensitivity[:low_category]- high_sensitivity [:high_category].

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/linux.selinuxsecuritycontext.schema.json#/$defs/require): This includes SELinux security context's user, type role, low sensitivity, low category, high sensitivity, high category, raw low sensitivity, raw low category, raw high sensitivity, and raw high category.

This state follows the SELinux security context structure: user:role:type:low_sensitivity[:low_category]- high_sensitivity [:high_category].

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
