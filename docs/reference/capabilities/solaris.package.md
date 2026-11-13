# solaris.package

Proposed documentation; frozen 0.4.1 validation is unchanged.

The package test is used to check information associated with different SVR4 packages installed on the system.

Image Packaging System (IPS) packages are not supported by this test.

The information used by this test is modeled after the /usr/bin/pkginfo command.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/solaris.package.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a package test to define the SVR4 packages to be evaluated.

A package object consists of a single pkginst field that identifies the package to be used.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/object/properties/filters) |
| `pkginst` | string | 0..1 | String that represents a package designation by its instance. | [/$defs/object/properties/pkginst](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/object/properties/pkginst) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item holds information about installed SVR4 packages.

Output of /usr/bin/pkginfo.

See pkginfo(1).

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `pkginst` | string | 0..1 | String that represents a package designation by its instance. | [/$defs/meanings/properties/pkginst](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/pkginst) |
| `name` | string | 0..1 | Text string that specifies a full package name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/name) |
| `category` | string | 0..1 | String in the form of a comma-separated list of categories under which a package may be displayed. | [/$defs/meanings/properties/category](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/category) |
| `version` | string | 0..1 | Text string that specifies the current version associated with the software package. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/version) |
| `vendor` | string | 0..1 | String used to identify the vendor that holds the software copyright (maximum length of 256 ASCII characters). | [/$defs/meanings/properties/vendor](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/vendor) |
| `description` | string | 0..1 | String that represents a more in-depth description of a package. | [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/description) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different information associated with SVR4 packages installed on the system.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/solaris.package.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `solaris-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
