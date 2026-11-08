# macos.systemsetup

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `timezone` | array, object | 0..1 | The name of the time zone. | [/$defs/meanings/properties/timezone](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/timezone) |
| `usingnetworktime` | array, object | 0..1 | Whether the machine is using network time. | [/$defs/meanings/properties/usingnetworktime](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/usingnetworktime) |
| `networktimeserver` | array, object | 0..1 | The network time server. | [/$defs/meanings/properties/networktimeserver](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/networktimeserver) |
| `computersleep` | array, object | 0..1 | The computer sleep inactivity timer, or 0 for never. | [/$defs/meanings/properties/computersleep](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/computersleep) |
| `displaysleep` | array, object | 0..1 | The display sleep inactivity timer, or 0 for never. | [/$defs/meanings/properties/displaysleep](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/displaysleep) |
| `harddisksleep` | array, object | 0..1 | The hard disk sleep inactivity timer, or 0 for never. | [/$defs/meanings/properties/harddisksleep](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/harddisksleep) |
| `wakeonmodem` | array, object | 0..1 | Whether the computer will wake up if the modem is accessed. | [/$defs/meanings/properties/wakeonmodem](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/wakeonmodem) |
| `wakeonnetworkaccess` | array, object | 0..1 | Whether the computer will wake up if the network is accessed. | [/$defs/meanings/properties/wakeonnetworkaccess](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/wakeonnetworkaccess) |
| `restartfreeze` | array, object | 0..1 | Whether the computer will restart after freezing. | [/$defs/meanings/properties/restartfreeze](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/restartfreeze) |
| `allowpowerbuttontosleepcomputer` | array, object | 0..1 | Whether the power button can be used to cause the computer to sleep. | [/$defs/meanings/properties/allowpowerbuttontosleepcomputer](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/allowpowerbuttontosleepcomputer) |
| `restartpowerfailure` | array, object | 0..1 | Whether the computer will restart after a power failure. | [/$defs/meanings/properties/restartpowerfailure](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/restartpowerfailure) |
| `remotelogin` | array, object | 0..1 | Whether remote logins are allowed. | [/$defs/meanings/properties/remotelogin](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/remotelogin) |
| `remoteappleevents` | array, object | 0..1 | Whether remote Apple events are enabled. | [/$defs/meanings/properties/remoteappleevents](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/remoteappleevents) |
| `computername` | array, object | 0..1 | The computer's name. | [/$defs/meanings/properties/computername](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/computername) |
| `localsubnetname` | array, object | 0..1 | The name of the local subnet. | [/$defs/meanings/properties/localsubnetname](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/localsubnetname) |
| `startupdisk` | array, object | 0..1 | The startup disk. | [/$defs/meanings/properties/startupdisk](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/startupdisk) |
| `waitforstartupafterpowerfailure` | array, object | 0..1 | The number of seconds the computer waits to start up after a power failure. | [/$defs/meanings/properties/waitforstartupafterpowerfailure](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/waitforstartupafterpowerfailure) |
| `disablekeyboardwhenenclosurelockisengaged` | array, object | 0..1 | Whether the keyboard is locked when the closure lock is engaged. | [/$defs/meanings/properties/disablekeyboardwhenenclosurelockisengaged](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/disablekeyboardwhenenclosurelockisengaged) |
| `kernelbootarchitecturesetting` | array, object | 0..1 | The kernel boot architecture setting. | [/$defs/meanings/properties/kernelbootarchitecturesetting](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json#/$defs/meanings/properties/kernelbootarchitecturesetting) |

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

[Local schema constraints](../advanced/macos.systemsetup.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`timezone` | string | source-derived |
| Item.`usingnetworktime` | boolean | source-derived |
| Item.`networktimeserver` | string | source-derived |
| Item.`computersleep` | integer | source-derived |
| Item.`displaysleep` | integer | source-derived |
| Item.`harddisksleep` | integer | source-derived |
| Item.`wakeonmodem` | boolean | source-derived |
| Item.`wakeonnetworkaccess` | boolean | source-derived |
| Item.`restartfreeze` | boolean | source-derived |
| Item.`allowpowerbuttontosleepcomputer` | boolean | source-derived |
| Item.`restartpowerfailure` | boolean | source-derived |
| Item.`remotelogin` | boolean | source-derived |
| Item.`remoteappleevents` | boolean | source-derived |
| Item.`computername` | string | source-derived |
| Item.`localsubnetname` | string | source-derived |
| Item.`startupdisk` | string | source-derived |
| Item.`waitforstartupafterpowerfailure` | integer | source-derived |
| Item.`disablekeyboardwhenenclosurelockisengaged` | boolean | source-derived |
| Item.`kernelbootarchitecturesetting` | string | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.systemsetup.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
