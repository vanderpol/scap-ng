# Issues #14/#19 cross-repository semantic compatibility audit
This report audits the coordinated draft stack without merging PRs or changing converter behavior. It distinguishes verified conversion/schema behavior from intended semantics and runtime gaps. The machine-readable matrix is `docs/metadata/compatibility-audit.json`.
## Executive result
* Selector inventory reconciles to **141 total / 28 resolved / 113 unresolved**.
* The resolved selector contract shape is structurally tested, but direct tools execution is **blocked by the tools frozen snapshot pin** (145 current JSON files and 35 root schemas versus the tools expectation of 143 and 34).
* The accepted mapping update now emits `filepath`, `path`, and `filename` for all nine affected filesystem selectors; no aliases are introduced.
* All seven retained Variable forms are compared. `concat`, `regex_capture`, `merge`, and `unique` are structurally bounded in converter output; no evaluator was found, so Cartesian products, casts, ordering, regex execution, statuses, and runtime errors remain unverified.
## Pins and coordinated stack
* OVAL 5.12.3: `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`; XSD SHA-256 `06b79e8683d6b9dcaad3ab074a456588ed82c4edd2e8fff209def10aa0a366cc`.
* scap-ng audit base: `8f39cd1`.
* scap-ng-tools converter baseline: `1f4f74d`.
* Draft stack: [#15](https://github.com/vanderpol/scap-ng/pull/15), [#16](https://github.com/vanderpol/scap-ng/pull/16), [#17](https://github.com/vanderpol/scap-ng/pull/17), [#18](https://github.com/vanderpol/scap-ng/pull/18), and [#20](https://github.com/vanderpol/scap-ng/pull/20); Issue [#19](https://github.com/vanderpol/scap-ng/issues/19). None is merged by this work. The tools function-adapter comparison is [tools PR #16](https://github.com/vanderpol/scap-ng-tools/pull/16).
## Selector compatibility matrix

`Schema key` is the current resolved native selector name. `Converter key` is the key selected by `mapping.native.selector_map` in `v04_direct_converter.py` before schema validation. “Mapping/emission key match” is not runtime proof.

| Capability | Schema key | Operators / type | Null / enum | Converter key | Result |
|---|---|---|---|---|---|
| `linux.dpkginfo` | `name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `name` | structural key match |
| `linux.partition` | `mount_point` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `mount_point` | structural key match |
| `linux.selinuxboolean` | `name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `name` | structural key match |
| `linux.systemdunitdependency` | `unit` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `unit` | structural key match |
| `linux.systemdunitproperty` | `property` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `property` | structural key match |
| `linux.systemdunitproperty` | `unit` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `unit` | structural key match |
| `unix.file` | `filename` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `filename` | mapping/emission key match |
| `unix.file` | `filepath` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `filepath` | mapping/emission key match |
| `unix.file` | `path` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `path` | mapping/emission key match |
| `unix.interface` | `name` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `name` | structural key match |
| `unix.password` | `username` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `username` | structural key match |
| `unix.shadow` | `username` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `username` | structural key match |
| `windows.file` | `filename` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `filename` | mapping/emission key match |
| `windows.file` | `filepath` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `filepath` | mapping/emission key match |
| `windows.file` | `path` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `path` | mapping/emission key match |
| `windows.fileeffectiverights` | `filename` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | yes | `filename` | mapping/emission key match |
| `windows.fileeffectiverights` | `filepath` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `filepath` | mapping/emission key match |
| `windows.fileeffectiverights` | `path` | `equals, not_equal, case_insensitive_equals, case_insensitive_not_equal, matches_regex` / `string` | no | `path` | mapping/emission key match |
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
* The nine filesystem key differences are resolved in the canonical mapping candidate. Direct tools execution remains pending the separate tools snapshot/semantic-pack repin.
* Tools also fail closed on unproved cross-datatype Variable operands and have no runtime evaluator. These are converter qualification boundaries, not new schema semantics.
## Evidence and test results

- `python tools/generate_native_selector_schema.py --check`
- `python tools/generate_docs.py --check`
- `python -m unittest tests.test_compatibility_audit tests.test_schema_integrity tests.test_generated_documentation tests.test_variable_function_documentation -v (16 tests passed)`
- `python -m unittest discover -s tests -v (27 tests passed with declared dependencies installed)`
- Tools: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m unittest discover -s tests -v (14 tests run; 1 import error: missing referencing; 5 fixture-dependent suites skipped).
- Existing `tests/test_native_selector_contracts.py` is the positive/negative/boundary contract suite when optional Draft 2020-12 dependencies (`jsonschema` and `referencing`) are installed.
- No destructive commands, merges, converter edits, schema repins, or editor behavior changes were made.
## Acceptance artifacts

* Filesystem alternatives: `docs/evidence/issue21/filesystem-selector-alternatives/`. Candidate A validates; Candidate B and the pre-change tools emission remain rejected.
* Owner checklist and merge order: `docs/ISSUE14-19-OWNER-ACCEPTANCE-CHECKLIST.md`.
* Proposed multi-component `unique` shape remains owner-review only: additive `unique: [expression, ...]`; no grammar change was made.
* Current schema candidate digest after the approved mapping update: `0590d688edfe9f6bfcb0b3a849706dc7b2ce3e5eefbc9421c7fbb0caf0087a71`; final source commit and editor manifest remain pending tools repin/regeneration.

## Owner review queue

1. **GAP-SEL-01 (resolved)** — Owner-approved Candidate A names are now canonical in the three affected SCAP-NG mappings; converter output and selector contracts use filepath/path/filename for all nine selectors. **Decision:** No alias or rename; retain the approved OVAL names.
1. **GAP-VAR-01 (owner_review)** — unique is narrowed to one expression in active schema and converter while pinned OVAL UniqueFunctionType permits one or more components. **Decision:** Approve the narrowing or authorize a semantics-preserving multi-component representation.
1. **GAP-VAR-02 (qualification)** — No runtime proof for Cartesian products, cast execution, regex dialect/first-match behavior, unique ordering, merge sorting, missing values, statuses, or errors. **Decision:** Add evaluator/conformance vectors before claiming runtime parity.
1. **GAP-SNAP-01 (coordination)** — Tools snapshot pin is older than the current SCAP-NG stack. **Decision:** Repin tools only as a separately reviewed compatibility change; this audit does not alter the pin.

The key vocabulary decision is resolved to Candidate A. The `unique` arity, tools snapshot repin, and runtime conformance remain explicit review/qualification items; no grammar or runtime claims are added.
