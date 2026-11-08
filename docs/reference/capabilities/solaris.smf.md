# solaris.smf

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `solaris.smf` is used to check service management facility controlled services including traditional unix rc level start/kill scrips and inetd daemon services.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/solaris.smf.md) retain the validated encodings and any broader schema acceptance.

## Object

An Object consists of a fmri field that represents the Fault Management Resource Identifier (FMRI) which uniquely identifies a service.

The Object is used by `solaris.smf` to define the specific service instance to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/object/properties/filters) |
| `fmri` | string | 0..1 | The FMRI (Fault Managed Resource Identifier) field is used to identify system objects for which advanced fault and resource management capabilities are provided. | [/$defs/object/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/object/properties/fmri) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item is used to hold information related to service management facility controlled services

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `fmri` | string | 0..1 | The FMRI (Fault Managed Resource Identifier) field describes a possible identifier associated with a service. | [/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/fmri) |
| `service_name` | string | 0..1 | Usually an abbreviated form of the FMRI. | [/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/service_name) |
| `service_state` | string | 0..1 | Possible state that the service may be in. | [/$defs/meanings/properties/service_state](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/service_state) |
| `protocol` | string | 0..1 | Possible protocol supported by the service. | [/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/protocol) |
| `server_executable` | string | 0..1 | The field server_executable is a string representing the listening daemon on the server side. | [/$defs/meanings/properties/server_executable](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/server_executable) |
| `server_arguements` | string | 0..1 | The server_arguments field describes possible parameters that are passed to the service. | [/$defs/meanings/properties/server_arguements](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/server_arguements) |
| `exec_as_user` | string | 0..1 | String pulled from svcprop in the following format: inetd_start/user astring root | [/$defs/meanings/properties/exec_as_user](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/exec_as_user) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different information associated with a specific smf controlled service.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/solaris.smf.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `solaris-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
