# linux.kernelmodule

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `linux.kernelmodule` is used to check the loaded/loadability status for a given kernel module.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.kernelmodule.md) retain the validated encodings and any broader schema acceptance.

## Object

An example line of output from this command would look like: /lib/modules/3.10.0-693.21.1.el7.x86_64/kernel/sound/usb/line6/snd-usb-pod.ko.xz.

In this case, the module name would be "snd-usb-pod".

Another option is to parse the output of the "modprobe --showconfig" command.

An Object consists of a single module_name field that identifies the package being checked.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/object/properties/filters) |
| `module_name` | string | 0..1 | The name of the kernel module to collect. | [/$defs/object/properties/module_name](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/object/properties/module_name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item captures limited information, parsing the output of the "modprobe -n -v [module_name]" command.

Need a combo of "lsmod", "modprobe -n -v" and potentially searching ""

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `module_name` | string | 0..1 | The name of the kernel module for which information was collected | [/$defs/meanings/properties/module_name](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/meanings/properties/module_name) |
| `loaded` | boolean | 0..1 | True when the collected kernel module is currently loaded; false otherwise. | [/$defs/meanings/properties/loaded](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/meanings/properties/loaded) |
| `loadable` | boolean | 0..1 | True when the collected kernel module is allowed to be loaded; false otherwise. | [/$defs/meanings/properties/loadable](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/meanings/properties/loadable) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.kernelmodule.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
