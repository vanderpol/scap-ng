# OVAL 6.0 VMware ESX design workstream — Issue #86

**Status: proposed SCAP-NG 0.5.0 content.** This directory is deliberately
outside the active SCAP-NG 0.4.1 schema, manifest, and conformance suite. It
must not be promoted or used to change the 0.4.1 pin without a later canonical
schema decision.

## Exact source pin

The inventory is generated directly from the official
`OVAL-Community/OVAL` tag `v6.0` at commit
`5afcf590fb5d334687bfdc47f98716424cdb7f3d`:

| Source | Namespace | SHA-256 |
| --- | --- | --- |
| `esx-definitions-schema.xsd` | `urn:oval:v6:definitions:esx` | `b3288d02e6f0021fc48ca86f1e794b616e5f8d337dabfa45207666f0f87ff3f7` |
| `esx-system-characteristics-schema.xsd` | `urn:oval:v6:system-characteristics:esx` | `a8780d4469c7786e27c3808b1976f09e9c34cba584955b053c23876110f9fb46` |

The XSD snapshots and OVAL terms are retained under `source/`. No official
`v6.0.1` tag was available in the public OVAL repository at design time; this
workstream does not substitute moving `master` or claim 6.0.1 coverage. A
6.0.1 pin is a promotion blocker.

Run:

```sh
python proposed/issue86-esx-oval6/tools/generate_inventory.py
```

The generated inventory contains every XSD-defined ESX Test/Object/State/Item
family, direct fields, cardinalities, documentation, enumerations, and source
constraints. Current derived counts are **20 families**, **20 Tests**, **20
Objects**, **20 States**, **20 Items**, **30 Object fields**, **75 State
fields**, **75 Item fields**, **19 enumeration definitions**, and **440 explicit
field/cardinality constraints**.

## Generic crosswalk

`capability-crosswalk.json` maps every family to a generic proposed capability
`esx.<family>`:

- Test → `Assessment.tests.<id>`;
- Object → Test `object` selectors;
- State → Test `require.fields` and explicit Item/field cardinalities;
- Item → typed evidence `items[].fields`.

This is a representation proposal, not a canonical 0.5.0 schema. Converter
mapping, semantic evaluation, editor support, and RI collection are separately
marked as gaps. OVAL 5.12.3 ESX-specific `patch56_test`, `patch_test`,
`version_test`, and `visdkmanagedobject_test` are deprecated source constructs:
they must be rejected with `deprecated_source_construct`, never version-aliased
or upgraded by name.

## Examples and evidence

`assessments/host-advancedsetting.assessment.yaml` and
`assessments/host-service.assessment.yaml` are proposed YAML examples covering
representative DISA ESXi requirements. They use generic capabilities and keep
`object` before `require` in every Test. Fixtures are deterministic (fixed
clock, locale, ordering, typed values, explicit selector-preserving negative
variants). Expected results are independently derived from the fixtures and
XSD-derived Item/State requirements; they do not come from an RI.

`stig/representative-requirements.json` pins representative DISA-derived ESXi
6.5 requirements and source hashes. It is explicitly not current ESXi 8
qualification. Before promotion, pin the current DISA ESXi STIG artifact and
review each mapping. STIG IDs are provenance only; no collector may branch on
IDs.

## govmomi / RI handoff

`GOVMOMI-COLLECTION.md` documents generic native-Go collection requirements,
managed-object/property areas, privileges, completeness, status propagation,
and the bounded RI #202 handoff. It does not implement govmomi execution. The
portable Assessment/fixture/expected tuple remains implementation-independent;
real `vcsim` or ESXi receipts belong to `scap-ng-ri`.

## Explicit non-claims

This workstream does not alter `schema/`, `conformance/manifest.json`, the
0.4.1 family digest, active 0.4.1 mappings, or RI behavior. It does not claim
schema validity against an unapproved 0.5.0 schema, converter parity, native
collector support, current DISA coverage, or scanner qualification.
