# solaris.package.ips

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `solaris.package.ips` provides support for checking the metadata of packages installed using the Solaris Image Packaging System.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/solaris.package.ips.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `solaris.package.ips` to identify the set of packages to check on a system.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/filters) |
| `publisher` | string | 0..1 | The person, group of persons, or organization that is the source of the package. | [/$defs/object/properties/publisher](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/publisher) |
| `name` | string | 0..1 | The full hierarchical name of the package which is separated by forward slash characters. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/name) |
| `version` | version | 0..1 | The version of the package which consists of the component version, build version, and branch version. | [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/version) |
| `timestamp` | string | 0..1 | The timestamp when the package was published in the ISO-8601 basic format (YYYYMMDDTHHMMSSZ). | [/$defs/object/properties/timestamp](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/object/properties/timestamp) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores system state information associated with IPS packages installed on a Solaris system.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `publisher` | string | 0..1 | The person, group of persons, or organization that is the source of the package. | [/$defs/meanings/properties/publisher](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/publisher) |
| `name` | string | 0..1 | The full hierarchical name of the package which is separated by forward slash characters. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/name) |
| `version` | version | 0..1 | The version of the package which consists of the component version, build version, and branch version. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/version) |
| `timestamp` | string | 0..1 | The timestamp when the package was published in the ISO-8601 basic format (YYYYMMDDTHHMMSSZ). | [/$defs/meanings/properties/timestamp](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/timestamp) |
| `fmri` | string | 0..1 | The Fault Management Resource Identifier (FMRI) of the package which uniquely identifies the package on the system. | [/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/fmri) |
| `summary` | string | 0..1 | A summary of what the package provides. | [/$defs/meanings/properties/summary](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/summary) |
| `description` | string | 0..1 | A description of what the package provides. | [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/description) |
| `category` | string | 0..1 | The category of the package. | [/$defs/meanings/properties/category](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/category) |
| `updates_available` | boolean | 0..1 | A boolean value indicating whether or not updates are available for this package. | [/$defs/meanings/properties/updates_available](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json#/$defs/meanings/properties/updates_available) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/solaris.package.ips.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/solaris.package.ips.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `solaris-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
