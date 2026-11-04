# Issues #14/#19 cross-repository semantic compatibility audit
This report audits the coordinated draft stack without merging PRs or changing converter behavior. It distinguishes verified conversion/schema behavior from intended semantics and runtime gaps. The machine-readable matrix is `docs/metadata/compatibility-audit.json`.
## Executive result
* Selector inventory reconciles to **141 total / 28 resolved / 113 unresolved**.
* The resolved selector contract shape and direct tools compatibility are now **verified** against the accepted Candidate-A snapshot (145 JSON files, 35 roots, 658 references).
* The converter mapping and native emission now use the owner-approved OVAL names `filepath`, `path`, and `filename` for all nine filesystem selector contracts. The source crosswalk may still mention OVAL XML acquisition names such as `full_path`, `directory`, and `name`; those source names are not native aliases.
* All seven retained Variable forms are compared. `concat`, `regex_capture`, `merge`, and `unique` are structurally bounded in converter output; no evaluator was found, so Cartesian products, casts, ordering, regex execution, statuses, and runtime errors remain unverified.
## Pins and coordinated stack
* OVAL 5.12.3: `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`; XSD SHA-256 `06b79e8683d6b9dcaad3ab074a456588ed82c4edd2e8fff209def10aa0a366cc`.
* scap-ng audit base: `8f39cd1`.
* scap-ng-tools converter baseline: `1f4f74d`.
* Tools compatibility candidate: `scap-ng-tools@3e69cd822fcd961f4d9492c9f9ea48f18693742f` ([draft #22](https://github.com/vanderpol/scap-ng-tools/pull/22)).
* Draft stack: [#15](https://github.com/vanderpol/scap-ng/pull/15), [#16](https://github.com/vanderpol/scap-ng/pull/16), [#17](https://github.com/vanderpol/scap-ng/pull/17), [#18](https://github.com/vanderpol/scap-ng/pull/18), and [#20](https://github.com/vanderpol/scap-ng/pull/20); Issue [#19](https://github.com/vanderpol/scap-ng/issues/19). None is merged by this work. The tools function-adapter comparison is [tools PR #16](https://github.com/vanderpol/scap-ng-tools/pull/16).
## Selector compatibility matrix

`Schema key` is the current resolved native selector name. `Converter key` is the key selected by `mapping.native.selector_map` in `v04_direct_converter.py` before schema validation. “Verified native key match” proves emitted YAML vocabulary and schema acceptance; it is not scanner/runtime proof.

| Capability | Schema key | Operators / type | Null / enum | Converter key | Result |
|---|---|---|---|---|---|
| `linux.dpkginfo` | `name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `name` | structural key match |
| `linux.partition` | `mount_point` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `mount_point` | structural key match |
| `linux.selinuxboolean` | `name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `name` | structural key match |
| `linux.systemdunitdependency` | `unit` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `unit` | structural key match |
| `linux.systemdunitproperty` | `property` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `property` | structural key match |
| `linux.systemdunitproperty` | `unit` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `unit` | structural key match |
| `unix.file` | `filename` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `filename` | verified native key match |
| `unix.file` | `filepath` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `filepath` | verified native key match |
| `unix.file` | `path` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `path` | verified native key match |
| `unix.interface` | `name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `name` | structural key match |
| `unix.password` | `username` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `username` | structural key match |
| `unix.shadow` | `username` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `username` | structural key match |
| `windows.file` | `filename` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `filename` | verified native key match |
| `windows.file` | `filepath` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `filepath` | verified native key match |
| `windows.file` | `path` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `path` | verified native key match |
| `windows.fileeffectiverights` | `filename` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `filename` | verified native key match |
| `windows.fileeffectiverights` | `filepath` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `filepath` | verified native key match |
| `windows.fileeffectiverights` | `path` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `path` | verified native key match |
| `windows.fileeffectiverights` | `trustee_sid` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `trustee_sid` | structural key match |
| `windows.ntuser` | `key` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `key` | structural key match |
| `windows.ntuser` | `name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `name` | structural key match |
| `windows.registry` | `hive` | `equals` / `string` | no; classes_root, current_config, current_user, current_user_local_settings, local_machine, users | `hive` | structural key match |
| `windows.registry` | `key` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `key` | structural key match |
| `windows.registry` | `name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `name` | structural key match |
| `windows.regkeyeffectiverights` | `hive` | `equals` / `string` | no; classes_root, current_config, current_user, current_user_local_settings, local_machine, users | `hive` | structural key match |
| `windows.regkeyeffectiverights` | `key` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `key` | structural key match |
| `windows.regkeyeffectiverights` | `trustee_sid` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `trustee_sid` | structural key match |
| `windows.service` | `service_name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `service_name` | structural key match |

All selector rows use source path pins recorded in the mapping files. The operator crosswalk is `equals → equals`, `not equal → not_equal`, `case insensitive equals → case_insensitive_equals`, `case insensitive not equal → case_insensitive_not_equal`, and `pattern match → matches_regex`. The converter preserves explicit case and regex operation tokens where it emits a predicate; the closed registry hive is normalized to canonical `equals` with a recorded selector equivalence.
## Retained Variable expression forms

| Form | Converter/schema finding | Verification boundary |
|---|---|---|
| `literal` | Converter emits typed literal components and constant literal arrays; no value execution. | **verified structural subset**; no runtime execution claim. |
| `variable` | Converter emits named Variable references and preserves variable declarations. | **verified structural subset**; no runtime execution claim. |
| `values` | object_component emits a collected Object-field projection; field resolution is validated, not executed. | **verified structural subset**; no runtime execution claim. |
| `concat` | Converter requires at least two children and preserves child order; no Cartesian product is evaluated. | **verified structural subset**; no runtime execution claim. |
| `regex_capture` | Converter requires one child and a pattern and emits the pattern unchanged; regex matching is not executed. | **verified structural subset**; no runtime execution claim. |
| `unique` | Converter and active schema accept one expression; pinned OVAL UniqueFunctionType permits one or more components. | **owner review required oval arity gap**; no runtime execution claim. |
| `merge` | Converter requires one child and materializes delimiter/sort/order defaults; no sorting or join is executed. | **verified structural subset**; no runtime execution claim. |

`unique` is the only explicitly identified source-arity gap: the active native grammar and converter require one child, while pinned OVAL permits one or more components. This is retained as an owner decision, not widened here. `merge` is a native composition rather than a claim of an identically named OVAL function.
## Semantic axes

| Axis | Verified | Status |
|---|---|---|
| `cartesian_product` | No evaluator found. Converter explicitly does not evaluate products and refuses an unproved constant-array function boundary. | **unverified runtime** |
| `datatype_casting` | Literal parsing, native datatype mapping, same-datatype variable operands, and narrow local lexical string-to-integer/float validation are implemented; runtime cast behavior is absent. | **partial conversion only** |
| `value_ordering` | Converter preserves expression child order and emits merge sort/order; it does not execute merge or prove provider ordering. | **emission only** |
| `missing_values_and_status` | Conversion comments and failure checks preserve boundaries, but no runtime population/status engine exists in either repository. | **unverified runtime** |
| `error_propagation` | Converter fails closed on malformed/unsupported source structures; evaluator error propagation is not implemented. | **conversion fail closed runtime unverified** |
| `regex_and_case` | Selector operation crosswalk emits matches_regex and explicit case operators; regex_capture pattern is copied unchanged; no regex engine execution was found. | **crosswalk verified runtime unverified** |

The pinned XSD supplies the source type/function declarations, not an evaluator. No implementation in either repository establishes runtime Cartesian-product cardinality, cast failure behavior, regex dialect, merge ordering, missing-value status propagation, or error/result equivalence.
## Restrictions and compatibility risks

* Resolved selector restrictions are field-specific string operators, explicit enum values for registry hives, and nullable higher-level selectors. Existing schema tests cover positive, negative, boundary, list/Variable, nullability, unknown key, and legacy `pattern_match` cases.
* The nine filesystem selector mismatches are resolved in the coordinated candidate: the converter emits the canonical native keys and the direct YAML/schema regression tests validate them. Pre-change `full_path`/`directory`/`name` output remains recorded only as migration evidence and is not accepted as a native alias.
* Tools also fail closed on unproved cross-datatype Variable operands and have no runtime evaluator. These are converter qualification boundaries, not new schema semantics.
## Evidence and test results

- `python tools/generate_native_selector_schema.py --check`
- `python tools/generate_docs.py --check`
- `python -m unittest tests.test_compatibility_audit tests.test_schema_integrity tests.test_generated_documentation tests.test_variable_function_documentation -v (16 tests passed)`
- `python -m unittest discover -s tests -v (27 tests passed with declared dependencies installed)`
- Tools: SCAP_NG_SCHEMA_ROOT=<accepted mapping candidate> PYTHONPATH=src python -m unittest discover -s tests -v: 18 passed, 4 fixture-dependent suites skipped; filesystem compatibility tests passed.
- Existing `tests/test_native_selector_contracts.py` is the positive/negative/boundary contract suite when optional Draft 2020-12 dependencies (`jsonschema` and `referencing`) are installed.
- No destructive commands, merges, converter edits, schema repins, or editor behavior changes were made.
## Acceptance artifacts

* Filesystem alternatives: `docs/evidence/issue21/filesystem-selector-alternatives/`. Candidate A validates; Candidate B and the pre-change tools emission remain rejected.
* Owner checklist and merge order: `docs/ISSUE14-19-OWNER-ACCEPTANCE-CHECKLIST.md`.
* Proposed multi-component `unique` shape remains owner-review only: additive `unique: [expression, ...]`; no grammar change was made.
* Verified candidate pins: schema source commit `5a13698933c88ca1e271d635b9bee39af75bc027`, schema digest `0a8c5a5840b5a17839db87decf034544286baf56383f52de71795862cca20593`, tools semantic pack `5e3aa7a017cbce86cb724679fd1a3ce15e1ff63def48f09b61a3f83f3484fb92`, and editor-pack manifest `305dbd0b77729c69f3bc5d40232b0b3fbc5a32646310678f61ff2ae304831a5f` over 236 resources.

## Owner review queue

1. **GAP-SEL-01 (resolved)** — Owner-approved Candidate A names are now canonical in the three affected SCAP-NG mappings; converter output and selector contracts use filepath/path/filename for all nine selectors. **Decision:** No alias or rename; retain the approved OVAL names.
1. **GAP-VAR-01 (owner_review)** — unique is narrowed to one expression in active schema and converter while pinned OVAL UniqueFunctionType permits one or more components. **Decision:** Approve the narrowing or authorize a semantics-preserving multi-component representation.
1. **GAP-VAR-02 (qualification)** — No runtime proof for Cartesian products, cast execution, regex dialect/first-match behavior, unique ordering, merge sorting, missing values, statuses, or errors. **Decision:** Add evaluator/conformance vectors before claiming runtime parity.
1. **GAP-SNAP-01 (resolved)** — The tools snapshot and semantic pack now verify against the accepted Candidate-A SCAP-NG schema; editor-pack regeneration also passed with 236 resources. **Decision:** Keep the exact source/digest/pack pins and update the separate tools PR.

The key vocabulary and snapshot gate are resolved for this candidate. Preserve the approved 0.4.0 schema; the `unique` arity and runtime conformance gaps remain explicit owner-review/qualification items.
