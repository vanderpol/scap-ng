# linux.kernelmodule — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/module_name](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/meanings/properties/module_name) | {} | source-derived |
| [/$defs/meanings/properties/loaded](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/meanings/properties/loaded) | {} | source-derived |
| [/$defs/meanings/properties/loadable](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/meanings/properties/loadable) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/object): An example line of output from this command would look like: /lib/modules/3.10.0-693.21.1.el7.x86_64/kernel/sound/usb/line6/snd-usb-pod.ko.xz.

In this case, the module name would be "snd-usb-pod".

Another option is to parse the output of the "modprobe --showconfig" command.

An Object consists of a single module_name field that identifies the package being checked.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/module_name](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/object/properties/module_name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/module_name](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/object/properties/module_name): The name of the kernel module to collect.

This is the name of the kernel module to collect.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/item): The Item captures limited information, parsing the output of the "modprobe -n -v [module_name]" command.

Need a combo of "lsmod", "modprobe -n -v" and potentially searching ""

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.kernelmodule.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
