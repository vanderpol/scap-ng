# Existing SCAP 1.4 and shellcommand options come first

**Owner clarification, 2026-10-03; research direction, not a schema change.**
The goal is an easier equally accurate compliance check. Existing shellcommand
is a valid final answer when appropriate. Moving content constrained by SCAP 1.3
to capabilities available in SCAP 1.4 can remove complexity without inventing
assessment-language features. Novelty is not a success criterion.

## Source evidence

At receiving commit `809fffb5a5a4e23842b41819c9a2b264747be900`, all five original
NIWC ZIP hashes were rechecked against their pins. Their actual data-streams all
declare `scap-version="1.4"`. Seven of twelve selected closures already use
`shellcommand_test`: Apache KeepAlive/cookie, Windows FTP/registry and all three
DNS cases. RHEL audit/home/crypto and Windows AD rights retain OVAL 5.11 generator
declarations; that does not make their enclosing enhanced package SCAP 1.3.
[Inventory](evidence/existing-capabilities-inventory.json) records Test types,
generator versions, original XML hashes and package data-stream attributes.

These are **NIWC-enhanced** sources. They do not establish the version of every
DISA publication or quantify savings over original DISA 1.3 content. Compare
paired original/enhanced versions of the same requirement, including wording,
applicability, scope and error/results, before attributing savings to the upgrade.
A version upgrade enables a rewrite; it does not automatically rewrite content.

The pinned OVAL 5.12.3 independent schema defines `shellcommand_test`. Current NG
already has the reviewed `independent.shellcommand` mapping, with explicit
interpreter, command, optional line pattern and error flags. OVAL's source contract
describes a command/one-liner, excluding external script files and embedded multiline
scripts. The earlier `dns-query.ps1` is an acquisition sketch, not by itself a
directly usable OVAL shellcommand Object.

## Compare existing solutions before new features

Research SHOULD first attempt the simplest accurate existing collector/SCAP 1.4
method, including focused shellcommand queries. A requirement-facing compiler MAY
hide repetition. New providers/runtime operations SHOULD require a demonstrated
semantic or practical gap. Compare author readability, execution cost and portability.

| Case | Existing option to investigate | Evidence still needed |
| --- | --- | --- |
| Crypto policy | `update-crypto-policies --show` / `--check` through existing shellcommand and native States | Exact required FIPS targets/type coverage and installed utility behavior. Consistency with DEFAULT is not FIPS compliance; compare original twelve checks and manual intent separately. |
| DNS | Fixed publisher PowerShell administrative queries through shellcommand, ordinary States/Variables | Per-zone/interface keys, selection/exceptions, query failures, empty results, duration boundaries and module versions. A custom DNS capability is not presumed necessary. |
| Audit | Focused `auditctl -l` collection through shellcommand | Loaded/persisted differences, ordering, global audit state and correct configured coverage evaluation. A query collector does not prove event auditing. |
| Apache | Focused service queries exposing the required observations | Explicit occurrences, main/loaded groups and presence semantics. Effective last-value output/syntax success does not prove the source check. Native scanning retains includes/traversal. |
| Files | Existing native file selection/comparison, with optional authoring abbreviations | Account scope, Sets/Filters, traversal/mount/link/status behavior; these remain native acquisition. |

A fixed command MAY compute a domain fact when its complete semantics and errors
are reviewable and target-tested. That need not become a new standard operation.
Ordinary observations plus native Tests/States are preferable where they preserve
useful evidence. The typed DNS/configuration providers from method-02 remain
**alternatives**, not prerequisites. Even a validated audit coverage algorithm
could live in a publisher command if that proves simpler and sufficiently portable.

Original constraints remain: shellcommand SHALL NOT become the universal primary
method; filesystem traversal/broad scanning SHALL remain native; Organizational
Input SHALL be constrained and SHALL NOT inject commands or choose Tests. Effectively
deprecated Tests SHALL NOT be revived by command wrappers or upgrades.

This checkpoint inspected sources/schemas; no content commands or target scans
ran, and unrelated semantic suites were not repeated. No upgrade savings or
scanner equivalence is claimed. Reproduce the inventory with lxml and the pinned
cache (the cache's five ZIPs are hash-verified before inspection):

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/scap-ng/bin/python research/assessment-simplification/transform-03/inspect_existing_capabilities.py --source-cache /workspace/scratch/simplification-sources
```

Provenance: **Inherited** pinned NIWC source/package and reviewed mapping/schema;
**Common** inventory script and comparison; **Evidence/Audit** verified hashes,
declarations, counts and limitations. Pins remain in parent dossiers and
refinement-01 source-reproduction. No target data, external implementation or
legacy serialization was added to executable native content.
