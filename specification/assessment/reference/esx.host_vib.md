# ESXi installed VIB software — `esx.host_vib`

**Status:** draft 0.2.0 native contract with synthetic observations. This is not
a live VMware collector, signature verifier, or complete comparator.

## Object and acquisition

Target one identified ESXi host. The Object requires nonnull string predicate
`select.vib_name`, selecting installed vSphere Installation Bundle metadata.
The source illustrates `Get-EsxCli` software VIB listing; NG does not mandate
that backend or arbitrary shell execution. Collect the installed VIB population
in the target context. A denied/failed query is collection error, not successful
absence. Preserve distinct observations instead of collapsing by equal names.
Named Objects and compatible States use [shared behavior](shared-behavior.md).

## State and Item field reference

All fields are scalar per Item and available for comparison.

| Native field | Datatype | Meaning | Source field |
| --- | --- | --- | --- |
| `vib_name` | string | Installed VIB name. | `vib_name` |
| `acceptance_level` | string | Observed trust category from installed VIB metadata. | `acceptance_level` |
| `creation_date` | string | Observed creation-date text, without assumed format/timezone. | `creation_date` |
| `vendor` | string | Observed VIB vendor. | `vendor` |
| `version` | string | Observed VIB version; source explicitly declares string. | `version` |

Present collected values SHALL be JSON strings. Acceptance category literals
are case-sensitive: `VMwareCertified`, `VMwareAccepted`, `PartnerSupported`,
`CommunitySupported`, `Unknown`. Both State and observed Item enforce this list.
`Unknown` is an observed category: comparing it with `VMwareCertified` using
equality yields false, not the technical outcome `unknown`.

The categories respectively describe VMware-created/tested/signed software,
partner-created software tested/signed by VMware, software tested/signed by a
certified partner, community software not tested by those parties, and an
unknown category. This field is reported metadata, not independent cryptographic
verification. It SHALL NOT be treated as a new ordinal datatype.

The source State allows an empty XML value as a Variable-reference placeholder.
NG references Variables directly; an empty category literal is rejected, while
a typed Variable reference is permitted. A producer SHALL distinguish a missing,
unavailable, erroneous, or redacted value using the shared entity contract,
not the `Unknown` category. Runtime Variable resolution must respect the category
constraint; structural acceptance of a reference alone does not prove that.
Version and creation-date strings are not silently upgraded to ordered version
or date/time datatypes. Other non-equality operation boundaries require their
own comparator evidence.

## Tests, reporting and examples

[Standalone examples and oracle](../../../tests/esx-host-0.2.0/README.md)
require `VMwareCertified` for synthetic `fixture-vib`. That category matches;
`CommunitySupported` and `Unknown` fail. Reporting retains required VIB identity
and the compared category; default all retains other available metadata.
Redaction and unavailable values may omit payloads without violating enums.
These are synthetic equality/status cases, not acquisition or signature evidence.

## Provenance and gaps

[Mapping](../../../schema/v0.2.0/capability-mappings/experimental/esx.host_vib.json)
adapts `host_vib_test/object/state/item` and the named acceptance-level types
from the [pinned new-Test source](../../../third_party/oval-6.0-new-tests/README.md).
The explicit Item enum/type overlay is confined to reviewed mapping inputs;
stable 0.1.0 generated contracts are unchanged. Classification: Adapted fields,
types and categories; Inherited exact licensed source; Common native guidance;
Evidence/Audit synthetic expectations and source checks.

Live host/backend/version/privilege evidence, Variable resolution, pattern and
non-equality comparator boundaries, and vendor conformance remain in #128/#131.
