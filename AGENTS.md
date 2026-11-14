# Semantic implementation requirement

## Active owner handoff — 2026-11-14

The only active pre-alpha schema is **SCAP-NG 0.4.1** in flat `schema/`. Historical 0.4.0 is available through Git/archive, **not** a concurrent active grammar. Read [#66](https://github.com/vanderpol/scap-ng/issues/66) and draft [PR #65](https://github.com/vanderpol/scap-ng/pull/65) at pinned `aece827964c785be77b088c3c61255a2d07fd9a9` (Assessment family `578315d1e00bd39449ed597ed3d39555384276bd36198a54ca0b1e3c17e72829`); verify current status before changes. A draft PR is not merged main. Update docs, metadata, examples, semantic pack and all consumer pins coherently on change.

**Prioritize runtime-enabling core features, not further editorial studies.** The shared native evaluator must support Object/Set/Filter semantics, typed Variables and expressions (literal, variable, values, concat, regex_capture only under approved PCRE2 profile, unique, merge, recursive count), input guards, Require scalar/field/item operators and cardinality, Boolean and/or/one/xor, status/completeness, Evaluate, applicability and Results. Native `one` is exactly one and `xor` is odd parity. No redundant Variable declaration datatype, implicit numeric-string casts, fabricated Items, or incomplete-population pass. Confirm active `foreach` and `else_if` contracts from actual current schema before asserting support. Schema-valid is not runnable equivalence.

**Authoring/scanner documentation:** concise table-first, schema-derived selectors/fields/operators, field-level hover descriptions, readable pass/fail Assessment examples, registry recursive selection and variable-backed key/name where permitted, shellcommand stdout/stderr and privileged-execution caveats, all statuses and held features. OVAL is a compatibility source, never mandatory reading for native implementers. Preserve source Rule/Assessment identity, actual shared applicability/CPE references, profiles enabled by default with disable/re-enable, manual/OCIL alternatives.

**OVAL Self-Assertion source conformance is a required breadth inventory, not deep proof:** pin `OVAL-Community/SCAP-Self-Assertion@e3538595c5083b9c34d937a81d319234df9bbfaa` under `SCAP_1.4/OVAL_Test_Content/`. Map original XML hash, Definition/Test/Object/State/Variable IDs, source checks and expected-result authority to native schema pointers and feature gaps. Sample witnesses are cursory; separate source witness, independent expected result, conversion, schema admission, native/OVAL execution, security/scale qualification. Tools PR #62 reports 144 XML/168 Definitions/803 Tests in its specific source scope, NOT the older 76/462 partial scope; recount per platform/directory. Source Test 180 is independently expected true but production RI still holds regex. Missing feature families and edge cases require supplemental tests.

Cross-repo responsibilities: `scap-ng` owns normative language, `scap-ng-tools` conversion, `scap-ng-ri` evaluator/planner/collectors/storage, `scap-ng-vscode` YAML-preserving editing. Coordinate small linked draft PRs without touching other repositories' code or silently changing approved semantics. Agents should proceed autonomously on clear requirements, escalating only normative/security/irreversible owner decisions. Quantify functioning native features/gatherers and independent behavior, not just passing test totals.


For every RI capability implemented or modified, the same development increment must include:

1. Research of pinned OVAL 5.12.3 evaluation rules and edge cases.
2. Mapping to the exact canonical SCAP-NG 0.4 schema, distinguishing equivalent, intentionally different, unsupported and unresolved behavior.
3. Standalone normative native documentation in this repository; OVAL must not be required reading for implementers.
4. Executable conformance fixtures with positive and negative cases, and passing RI regressions.
5. An OVAL-to-native compatibility matrix with source pointers and exact schema pins.
6. A clear separation between language requirements and RI implementation limitations.

No language behavior is complete without these four deliverables: normative documentation, compatibility mapping, executable conformance tests and passing RI regressions. Coordinate separate linked draft PRs; preserve frozen schemas and all semantic holds. Escalate genuine specification conflicts. Do not merge or promote unapproved semantics. Store implementation/performance limits separately from language requirements.


### Execution authority and incomplete evidence (permanent)

- Normative SCAP-NG contracts must distinguish acquisition status, logical Object completeness, population completeness, evidence completeness, privilege context, visibility/namespace scope, evidence trust, and evaluation outcome. A successful syscall or returned Item is not a completeness guarantee.
- Root, restricted namespace, missing, denied, partial, symlink, mount-boundary, include, and kernel-visibility behavior must be explicitly specified or held; container/namespace root must not be described as host-wide authority.
- Apparent passes that require complete population evidence must not be asserted without sufficient completeness. Observed decisive failures may remain failures only where unseen evidence cannot reverse the condition.
- Any normative change in these areas requires coordinated frozen-schema/result review, standalone canonical documentation understandable without OVAL, pinned OVAL 5.12.3 compatibility research, positive/negative conformance fixtures, and linked RI regression tests. AGENTS.md does not approve new language or schema semantics; unresolved decisions belong in an owner-review document.
