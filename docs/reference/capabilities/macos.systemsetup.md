# macos.systemsetup

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `macos.systemsetup` is used to check systemsetup properties.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.systemsetup.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is a singleton used to access system setup information.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item represents system setup information.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `timezone` | string | 0..1 | The name of the time zone. | [/$defs/meanings/properties/timezone](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/timezone) |
| `usingnetworktime` | boolean | 0..1 | Whether the machine is using network time. | [/$defs/meanings/properties/usingnetworktime](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/usingnetworktime) |
| `networktimeserver` | string | 0..1 | The network time server. | [/$defs/meanings/properties/networktimeserver](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/networktimeserver) |
| `computersleep` | integer | 0..1 | The computer sleep inactivity timer, or 0 for never. | [/$defs/meanings/properties/computersleep](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/computersleep) |
| `displaysleep` | integer | 0..1 | The display sleep inactivity timer, or 0 for never. | [/$defs/meanings/properties/displaysleep](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/displaysleep) |
| `harddisksleep` | integer | 0..1 | The hard disk sleep inactivity timer, or 0 for never. | [/$defs/meanings/properties/harddisksleep](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/harddisksleep) |
| `wakeonmodem` | boolean | 0..1 | Whether the computer will wake up if the modem is accessed. | [/$defs/meanings/properties/wakeonmodem](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/wakeonmodem) |
| `wakeonnetworkaccess` | boolean | 0..1 | Whether the computer will wake up if the network is accessed. | [/$defs/meanings/properties/wakeonnetworkaccess](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/wakeonnetworkaccess) |
| `restartfreeze` | boolean | 0..1 | Whether the computer will restart after freezing. | [/$defs/meanings/properties/restartfreeze](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/restartfreeze) |
| `allowpowerbuttontosleepcomputer` | boolean | 0..1 | Whether the power button can be used to cause the computer to sleep. | [/$defs/meanings/properties/allowpowerbuttontosleepcomputer](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/allowpowerbuttontosleepcomputer) |
| `restartpowerfailure` | boolean | 0..1 | Whether the computer will restart after a power failure. | [/$defs/meanings/properties/restartpowerfailure](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/restartpowerfailure) |
| `remotelogin` | boolean | 0..1 | Whether remote logins are allowed. | [/$defs/meanings/properties/remotelogin](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/remotelogin) |
| `remoteappleevents` | boolean | 0..1 | Whether remote Apple events are enabled. | [/$defs/meanings/properties/remoteappleevents](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/remoteappleevents) |
| `computername` | string | 0..1 | The computer's name. | [/$defs/meanings/properties/computername](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/computername) |
| `localsubnetname` | string | 0..1 | The name of the local subnet. | [/$defs/meanings/properties/localsubnetname](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/localsubnetname) |
| `startupdisk` | string | 0..1 | The startup disk. | [/$defs/meanings/properties/startupdisk](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/startupdisk) |
| `waitforstartupafterpowerfailure` | integer | 0..1 | The number of seconds the computer waits to start up after a power failure. | [/$defs/meanings/properties/waitforstartupafterpowerfailure](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/waitforstartupafterpowerfailure) |
| `disablekeyboardwhenenclosurelockisengaged` | boolean | 0..1 | Whether the keyboard is locked when the closure lock is engaged. | [/$defs/meanings/properties/disablekeyboardwhenenclosurelockisengaged](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/disablekeyboardwhenenclosurelockisengaged) |
| `kernelbootarchitecturesetting` | string | 0..1 | The kernel boot architecture setting. | [/$defs/meanings/properties/kernelbootarchitecturesetting](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/kernelbootarchitecturesetting) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields makes it possible to make assertions about system setup settings.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.systemsetup.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
