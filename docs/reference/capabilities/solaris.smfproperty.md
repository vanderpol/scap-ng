# solaris.smfproperty

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/filters) |
| `service` | object | 0..1 | The SMF service on the system. | [/$defs/object/properties/service](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/service) |
| `instance` | object | 0..1 | The instance of an SMF service which represents a specific configuration of a service. | [/$defs/object/properties/instance](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/instance) |
| `property` | object | 0..1 | The name of the property associated with an SMF service. | [/$defs/object/properties/property](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/property) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `service` | array, object | 0..1 | The SMF service on the system. | [/$defs/meanings/properties/service](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/service) |
| `instance` | array, object | 0..1 | The instance of an SMF service which represents a specific configuration of a service. | [/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/instance) |
| `property` | array, object | 0..1 | The name of the property associated with an SMF service. | [/$defs/meanings/properties/property](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/property) |
| `fmri` | array, object | 0..1 | The Fault Management Resource Identifier (FMRI) of the SMF service which uniquely identifies the service on the system. | [/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/fmri) |
| `value` | array, object | 0..1 | The value of the property associated with an SMF service. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/value) |

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

[Local schema constraints](../advanced/solaris.smfproperty.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`service` | string | source-derived |
| Object.`instance` | string | source-derived |
| Object.`property` | string | source-derived |
| Item.`service` | string | source-derived |
| Item.`instance` | string | source-derived |
| Item.`property` | string | source-derived |
| Item.`fmri` | string | source-derived |
| Item.`value` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `solaris-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
