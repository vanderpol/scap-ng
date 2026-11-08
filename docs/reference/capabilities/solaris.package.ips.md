# solaris.package.ips

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/filters) |
| `publisher` | object | 0..1 | The person, group of persons, or organization that is the source of the package. | [/$defs/object/properties/publisher](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/publisher) |
| `name` | object | 0..1 | The full hierarchical name of the package which is separated by forward slash characters. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/name) |
| `version` | object | 0..1 | The version of the package which consists of the component version, build version, and branch version. | [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/version) |
| `timestamp` | object | 0..1 | The timestamp when the package was published in the ISO-8601 basic format (YYYYMMDDTHHMMSSZ). | [/$defs/object/properties/timestamp](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/timestamp) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `publisher` | array, object | 0..1 | The person, group of persons, or organization that is the source of the package. | [/$defs/meanings/properties/publisher](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/publisher) |
| `name` | array, object | 0..1 | The full hierarchical name of the package which is separated by forward slash characters. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/name) |
| `version` | array, object | 0..1 | The version of the package which consists of the component version, build version, and branch version. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/version) |
| `timestamp` | array, object | 0..1 | The timestamp when the package was published in the ISO-8601 basic format (YYYYMMDDTHHMMSSZ). | [/$defs/meanings/properties/timestamp](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/timestamp) |
| `fmri` | array, object | 0..1 | The Fault Management Resource Identifier (FMRI) of the package which uniquely identifies the package on the system. | [/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/fmri) |
| `summary` | array, object | 0..1 | A summary of what the package provides. | [/$defs/meanings/properties/summary](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/summary) |
| `description` | array, object | 0..1 | A description of what the package provides. | [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/description) |
| `category` | array, object | 0..1 | The category of the package. | [/$defs/meanings/properties/category](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/category) |
| `updates_available` | array, object | 0..1 | A boolean value indicating whether or not updates are available for this package. | [/$defs/meanings/properties/updates_available](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/updates_available) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

### Condition logic

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |

### Item existence requirement

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Existence only; there is no satisfaction operation without a comparison. | [/$defs/item_presence_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/item_presence_requirement/properties/item_requirement) |


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/solaris.package.ips.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`publisher` | string | source-derived |
| Object.`name` | string | source-derived |
| Object.`version` | version | source-derived |
| Object.`timestamp` | string | source-derived |
| Item.`publisher` | string | source-derived |
| Item.`name` | string | source-derived |
| Item.`version` | version | source-derived |
| Item.`timestamp` | string | source-derived |
| Item.`fmri` | string | source-derived |
| Item.`summary` | string | source-derived |
| Item.`description` | string | source-derived |
| Item.`category` | string | source-derived |
| Item.`updates_available` | boolean | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `solaris-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
