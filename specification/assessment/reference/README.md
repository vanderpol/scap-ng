# Assessment author and assessor reference

**Status:** documentation foundation for the pre-alpha working design; 0.2.0
remains a partial draft. This catalog is incomplete and is not a released
conformance specification.

An Assessment describes how to determine technical truth. A Rule determines
how that truth affects its policy result. Start with [shared assessment
behavior](shared-behavior.md), then read the reference for the capability used
by each Test, Object, or State.

| Capability | What it checks | Source and result versions | Reference |
| --- | --- | --- | --- |
| `unix.file` | Unix file identity, ownership, mode bits, times, size, and ACL presence | 0.1.0 base; draft 0.2.0 result names/reporting | [Unix files](unix.file.md) |
| `variable.value` | Values produced by a named Variable | 0.1.0 base; draft 0.2.0 expressions/reporting | [Variable values](variable.value.md) |
| `esx.host_service` | Named ESXi host service configuration/running state | Draft 0.2.0 addition | [Host services](esx.host_service.md) |
| `esx.host_advancedsetting` | Named ESXi host setting with typed repeated values | Draft 0.2.0 addition | [Host settings](esx.host_advancedsetting.md) |
| `esx.host_account` | Named host accounts and shell access | Draft 0.2.0 addition | [Host accounts](esx.host_account.md) |
| `esx.host_vib` | Installed VIB metadata and acceptance category | Draft 0.2.0 addition | [Installed VIBs](esx.host_vib.md) |

## Where requirements live

The intended publication is one versioned SCAP-NG reference containing shared
semantics and capability-specific contracts. Vendors should be able to implement
NG from that reference without reconstructing its requirements from OVAL XSDs.
Pinned OVAL sources remain migration/provenance evidence and support review of
inherited behavior.

Today, these documents explain and link existing contracts. Shared evaluation
rules remain maintained in [Assessment evaluation semantics](../../../research/iterations/003/design/assessment-evaluation-semantics.md).
Accepted 0.3 collection iteration is documented in
[Collection `for_each`](../foreach.md).
Native structural mappings remain in [the capability mapping catalog](../../../schema/v0.1.0/capability-mappings/README.md).
The [0.2.0 schema guide](../../../schema/v0.2.0/README.md) owns the current draft
expression/result slice. This first documentation pass does not move or replace
those authorities.

One maintained source for each requirement is the goal. A future reviewed
catalog may combine structured capability definitions, field documentation,
and links to shared normative rules, then generate JSON Schemas and the
published reference. YAML is a proposed source serialization for that catalog;
the existing JSON mappings are still the generator input. Neither the catalog
consolidation nor documentation generation pipeline is implemented here.

Useful field explanations, titles, and examples SHOULD be carried into generated
JSON Schema annotations. A schema annotation alone SHALL NOT be the only home
for collection, comparison, applicability, or result-propagation requirements
that schema validation cannot enforce. Generated publication must identify the
exact specification/catalog revision and avoid independently edited copies of
the same requirement.

## How references are written

Use [the capability reference template](capability-template.md). Explain every
native selector, comparable field, and result-only field, including units,
cardinality, absence/error behavior, meaningful constraints, and collection
prerequisites. Adapt useful OVAL documentation to NG semantics; preserve source
pins and identify intentional differences or unresolved interpretations.

Examples link to maintained content and independently explained expectations.
Distinguish structural validity, semantic graph validity, synthetic observation
consistency, migration equivalence, and actual target execution. A callback-based
conditional fixture does not prove a collector or State comparator.

The [capability coverage inventory](../../../docs/audit/capability-coverage-2026-10-03/README.md)
records the wider catalog and its gaps. These initial references do not
complete documentation of the 100 mapped capabilities or the 22 new OVAL 6.0
Tests. Two new ESXi host mappings have synthetic cases; the other 20 new Tests
still need implementation. Expansion is tracked in GitHub #128/#131 alongside
0.2.0 stabilization.

## Provenance

Owner direction, 2026-10-03: begin foundational Markdown while finalizing 0.2.0;
establish the format and complete examples before bounded Codex catalog
expansion. [Reference source ledger](sources.json) pins the inspected NG
checkpoint, source XSDs, mappings, semantic documents, and test evidence.
Classification: **Common** explanatory organization; **Adapted** OVAL-derived
field meanings; **Evidence/Audit** implementation and coverage statements.
