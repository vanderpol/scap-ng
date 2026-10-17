# Can the 201 Test-level `all_exist` requirements be simplified?

**Research evidence only; no adopted 0.4 authoring or result schema.**

Pinned 2026-10-15 r3 six-STIG source; imported source Tests stay unchanged.

| Classification | Tests | Meaning |
| --- | ---: | --- |
| `all_exist` Tests audited | 201 | Six-STIG distinct named Tests |
| State-free | 127 | Check only Item presence |
| State-bearing | 74 | Also evaluate Item State conditions |
| Equivalent under **complete**, existing-root-Item-only collection | 201 | Same presence and State results, including error/unknown **State results** |
| Also equivalent on modeled **incomplete** collection under existing-only Items | 127 | **State-free only**; no decisive State comparison |
| Cases needing incomplete-scan policy | 74 | State-bearing; at-least-one may yield decisive failure whereas all-exist remains unknown |

## What the reference actually proves

- Existing Items alone give identical existence outcomes for `all_exist` and `at_least_one_exists` in a complete collection.
- Empty and missing collections are handled through collection flags/zero Items, not fabricated Item identities.
- The two choices differ in OVAL's generic tables with a mixed Item-status collection: a real Item plus error/not-collected/does-not-exist Item.
- **Banning fabricated does-not-exist Items resolves only one of those differences.** Failures must be represented without corrupting the six result outcomes.
- The local generic reference treats incomplete State-bearing scans specially; normalizing them without a new native semantic contract changes results.

## Generic result counterexamples

### incomplete:all

- existing=1, State outcomes=['false']: all_exist→`unknown`, at_least_one→`false`
- existing=2, State outcomes=['true', 'false']: all_exist→`unknown`, at_least_one→`false`

### incomplete:none satisfy

- existing=1, State outcomes=['true']: all_exist→`unknown`, at_least_one→`false`
- existing=2, State outcomes=['true', 'true']: all_exist→`unknown`, at_least_one→`false`

## Example source-folder distribution

The shared folder is reused across benchmarks and is not a seventh STIG.

| Folder | Presence only | All State matches | No State matches |
| --- | ---: | ---: | ---: |
| ms_windows_11 | 0 | 10 | 0 |
| ms_windows_server_2025 | 0 | 3 | 0 |
| oracle_linux_9 | 10 | 3 | 0 |
| rhel_9 | 18 | 4 | 0 |
| shared | 99 | 53 | 1 |

## Remaining owner-facing design choices

1. Decide whether all native root Items must have `exists` status, with missing/unreadable/not-collected represented through collection or field results; preserve all the required six-state outcomes.
2. For State-bearing source `all_exist` Tests, decide what native tests do on incomplete observations. Preserve existing OVAL meaning in the importer until differential parity is demonstrated.
3. Represent mandatory expected identities separately from `all *collected* Items` (e.g., every listed audit-tool path must exist versus every found path must match).
4. Retain a source-exact compatibility path or a precise conversion blocker for OVAL partial missing Items, with actual original XML/source provenance.

## Provenance and boundaries

- Test results are computed by the checked-in OVAL 5.12.3 generic model, not a scanner.
- Complete flags with root Items limited to exists give equal behavior for all 201, not general migration parity.
- State-free (127) cases agree on the modeled complete/incomplete/error/not-collected flags, under the existing-only Item restriction.
- State-bearing (74) may differ when incomplete scans contain a decisive per-Item failure; preserving original source results remains required.
- Mixed root Item statuses error and not_collected remain a difference unless native schema defines their representation in collection/field status.
- A native test cannot infer that every *named selector value* exists from all observed Items matching.
- No automatic OVAL XML rewriting, STIG normalization, or schema decisions were made.
