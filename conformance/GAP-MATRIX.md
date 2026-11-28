# Issue #87 specification-to-test-content coverage

The corpus targets canonical SCAP-NG 0.4.1 at
`cc5eac4bfd89f2f5a5df30b7ecc1be59527c5876`. Use the
[suite index](suite-index.json) to acquire the Assessment, fixture and expected
outcome at the same repository revision. `bash conformance/check.sh` checks
source pins, inventory, corpus content and independent local oracles. Consumer
receipts live in the [qualification ledger](qualification/coverage.json).

`for_each` is deferred to 0.5.0 consideration. Deprecated OVAL 5.12.3 ESX
Tests are excluded. The four experimental OVAL 6.0-derived ESXi capabilities
have a separate suite and accounting.

## Counts and scope

| Measure | Before | Current |
| --- | ---: | ---: |
| Active mapped capabilities with an authored native baseline | 101/101 | 101/101 |
| Experimental capabilities with an authored native baseline | 4/4 | 4/4 |
| Mapped fields with a typed structural witness across both cohorts | 718/718 | 718/718 |
| Active mapped field/datatype pairs with a value in indexed fixtures | 619/910 | 622/910 |
| Experimental field/datatype pairs with a value in the baseline fixture | 17/28 | 17/28 |
| Reachable enum and const values matched by active native documents | 143/850 | 170/850 |
| Reachable enum and const values without any scoped match | 678/850 | 658/850 |
| Active mapped capabilities with OVAL 5.12.3 source Tests | 99/101 | 101/101 |
| OVAL Self-Assertion XML Definitions / Tests, including archived members | 167 / 799 | 196 / 828 |
| Dedicated exact scalar-equality boundary Test leaves | 0 | 10 |
| Targeted function boundary Test leaves with known populations | 0 | 11 |
| Linked automated Result and Item-report fixtures over the same supplied evidence | 0 | 1 |

The OVAL baseline is the pinned upstream Self-Assertion corpus. Native
comparison counts use merged baseline `b5b99e997450741a0444ec7b631e71fe2d49b001`.
Schema matching counts exact locations visited during validation, including
sibling branches that can fail a different constraint. Draft transport and
experimental matches are recorded separately and can overlap active matches.
Typed fixture counts record a value labeled with the mapped datatype. The current
count adds the exact-equality and Result evidence suites. These counts carry no assertion about field-specific behavior or acquisition.

## Remaining content and specification decisions

| Surface | Coverage and exact follow-up |
| --- | --- |
| Capabilities and datatypes | The [machine matrix](content-coverage.json) identifies missing indexed datatype evidence by mapping and field. Reconcile those rows against targeted suites before authoring further comparisons. For example, `windows.registry.value` has supplied integer evidence in the [paired fixtures](0.4/supplied-evidence.json) beyond the generic baseline, but binary/version examples require a separate review of operand encodings and applicability. |
| Selectors and schema constraints | The [audit](coverage-audit.json) records 94 selector alternatives and 718 mapped fields across both scopes. The [source inventory](schema-coverage.json) lists all 1,620 property groups and 11,346 constraint occurrences. Complete positive, rejection and cross-property boundary coverage remains open. The [enum and const ledger](qualification/schema-value-occurrences.json) gives every reachable unmatched value and its exact pointer. |
| Comparisons and cardinality | The common authoring suite covers 67 field operations, including the active regex spelling. The [exact equality suite](exact-equality/expected.json) adds native integer precision, negative and zero, empty and whitespace, Unicode identity and case boundaries. The [Model A oracle](0.4/model-a/manifest.json) establishes nonempty cardinality, and the [ONE/XOR suite](logical-cardinality/expected.json) distinguishes known Boolean folds. Primitive datatype operations, field-specific operator constraints, and cross-status folds still require independently justified cases. |
| Variables and functions | [Core witnesses](expected/core-variable-functions.json) cover the 14 active operations, with alias/constant and ordered output controls. [Merge](variable-merge/expected.json), [time difference](variable-time-difference/expected.json) and [external Input](variable-external-input/expected.json) add source-specific expected outcomes. [Function boundaries](function-boundaries/expected.json) cover Cartesian multiply and concat, ordered component flattening, literal-delimiter empty parts, substring bounds, and first and empty captures. Complete parameter, datatype, empty and exceptional combinations remain open. General empty-population reduction and Variable cardinality semantics are under review in [#135](https://github.com/vanderpol/scap-ng/pull/135) and [#136](https://github.com/vanderpol/scap-ng/pull/136). |
| Shared Objects, Sets and Filters | [Core Set/Filter witnesses](expected/core-set-filters.json) establish ordered overlap, nesting, single-operand and include/exclude behavior. The mapping audit links 81 repeated source rules to the shared native Filter rather than counting the same behavior 81 times. Field-specific predicate restrictions and combinations of partial acquisition and filters remain open. |
| Conditional and applicability | [Ordered guards](conditional-replay/expected.json) cover branch ordering, indeterminate guards and fallback. [Applicability](expected/core-applicability.json) covers the common dependency handoff. Add native combinations of guard, applicability and shared dependencies across scopes, including provenance of reused and excluded invocations. |
| Manual, Inputs, Profiles and Tailoring | [Manual lifecycle](manual-lifecycle/expected.json) exercises the six authored answer choices, missing and stale answers, and direct/imported/delegated provenance. [Content package](content-package/sources.json) and [Input guards](expected/core-input-guards.json) cover basic rollout and absent/empty/boundary bindings. Profile inheritance and selection conflicts, Tailoring/Organizational Input precedence, and policy-to-Result interactions still need an explicit occurrence and behavior audit. |
| Results and evidence | [Result evidence](result-evidence/expected.json) links collection and Variable audit records, field uses, Test-local Items and a projected Item report. It includes all six Collection and seven Variable status tokens as schema controls. [Result package](result-package/expected.json) adds cross-target references, disabled versus invoked distinction, and exact bytes for unsigned draft transport. Broader materialization, projection domain, and completeness/counter combinations remain open. The [contract decision ledger](../docs/DOCUMENTATION-CONTRACT-DECISIONS.md#item-materialization-and-projection) records the unresolved projection authority and count definitions. |
| OVAL 5.12.3 Self-Assertion | [Supplement](oval-self-assertion/expected.json) covers UNIX and Windows YAML file-content and SQLite SQL512. Eight [boundary cases](oval-self-assertion/yaml-boundaries/expected.json) add empty, missing, malformed and unreadable cases across both platforms. The [source ledger](oval-source-coverage.json) lists source Tests outside adopted mappings and keeps the original XML identities. Investigate additional source edge cases in already represented families. UNIX Set/Filter source parity remains open in [#132](https://github.com/vanderpol/scap-ng/issues/132). |
| OVAL 6.0 ESXi | [Experimental expected cases](experimental/esxi/expected.json) and the source ledger distinguish the 4 experimental and 16 proposed source Tests. Keep the 16 proposals outside active 0.4.1. Track the partial DISA evidence and conflicting timeout direction in [#86](https://github.com/vanderpol/scap-ng/issues/86), and experimental selector isolation in [#133](https://github.com/vanderpol/scap-ng/issues/133). |

The [unresolved operational contracts](../docs/contracts/0.4-semantic-holds.md)
document questions that affect independent expectations, including mixed
datatype casts and six-state reduction. Existing structural and independently
derivable outcome cases can be authored while those decisions are pending.

## Consumer discrepancies and historical failures

- SQL512 conversion is tracked in [Tools #127](https://github.com/vanderpol/scap-ng-tools/issues/127), and source evidence datatype ambiguity in [Tools #128](https://github.com/vanderpol/scap-ng-tools/issues/128).
- RI tracks native replay in [#196](https://github.com/vanderpol/scap-ng-ri/issues/196), ESXi in [#202](https://github.com/vanderpol/scap-ng-ri/issues/202), YAML acquisition in [#305](https://github.com/vanderpol/scap-ng-ri/issues/305), and guard trace discrepancies in [#309](https://github.com/vanderpol/scap-ng-ri/issues/309). Runtime, scale, performance and backend qualification belong to RI.
- Studio extension-host checks are tracked in [Studio #75](https://github.com/vanderpol/scap-ng-vscode/issues/75). The [sample audit](qualification/studio-sample-audit.json) records the sample scope examined. The same canonical fixture revisions can be consumed by Tools, RI and Studio.
- The reproducible stale documentation-fidelity manifest was repaired. The six historical failures reported for Issue #87 could not be recovered as an exact list from the available logs. Current local gate results and the archived [qualification ledger](qualification/README.md) provide the reproducible record.
