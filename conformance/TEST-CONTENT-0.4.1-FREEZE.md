# SCAP-NG 0.4.1 Test Content Freeze

**Status:** authoring and independent-oracle freeze candidate; scanner execution is
not claimed.  This receipt is for canonical `vanderpol/scap-ng` Issue #87 and
Studio qualification Issue #94.  It does not alter the 0.4.1 language or the
RI #196 execution boundary.

## Exact source and generated receipts

| Artifact | Value |
|---|---|
| Schema version | `0.4.1` |
| Canonical schema commit | `d1ab0283e09369c2c734d3b8f93b65007441cf07` |
| Schema-family SHA-256 | `1755c893712ef30334dc7ecadc88e5abf387c2d60a75211bc2445b7cefa2e7d4` |
| `conformance/manifest.json` SHA-256 | `a72fb77f2dcf3c932e84676acb97bc84d34cce9fbc5f0333d2ecf57c481a9a3b` |
| `conformance/schema-coverage.json` SHA-256 | `3580316a790d2e87a6df2e5a30f544091ec5a9deb4db55f24c6a36207599a2a7` |
| `conformance/coverage-audit.json` SHA-256 | `f948448ed597a30b72abeeb247deb6cc87a8207b860414a5788b17a763800621` |
| RI handoff SHA-256 | `245fa6b689ce70c36f8c5cdd261502456af3f11881b9ae01997a1033d92ba09d` |
| Editor metadata pack | 238 resources; manifest SHA-256 `9a531bcaaf6555b50689f4ceee06fb604c7013b3ee0b544b3af9e6b9dc7ac6e1` |

The generator was rerun from the checked-out schema and was byte-identical.
The manifest and audit are source-derived; declared inventory numbers are not
used as proof of witness execution.

## Completion matrix

| Area | Authoring/portable evidence | Qualification state |
|---|---|---|
| Capability mappings | 105 mappings: 101 supported, 4 experimental ESX | 101 active admitted; ESX remains explicitly excluded |
| Capability fields | 718/718 authored and positive-fixture witnessed | structural + typed fixture witness |
| Comparison operators | 67/67 | schema-valid typed positive witnesses; runtime unqualified |
| Selector alternatives | 94/94 | source-derived alternatives with matching fixture witnesses |
| Cardinalities | `none`, `exactly_one`, `one_or_more`, `zero_or_more`, `every` | schema and portable boundary witnesses |
| Logical Evaluate | `and`, `or`, `one`, `xor`, canonical `not`, double negation | false leaves remain visible; status outcomes are not negated into success |
| Variable expressions | 16 schema alternatives: `literal`, `variable`, 14 named functions including `begin`, `end`, `input`, and `values` | all branches authored in `core-variable-functions`; expected values independently derived |
| Variable/Input interactions | aliases, ordered duplicate values, required/absent/empty/over-cardinality/out-of-range Input | portable authoring/oracle witnesses; collector and graph execution unqualified |
| Set/Filter | include/exclude, union/intersection/difference, one-operand and nested Set, logical predicate, empty collected population | portable native witness; collector/status propagation unqualified |
| Exceptional outcomes | FALSE, UNKNOWN, ERROR, NOT_APPLICABLE, NOT_EVALUATED, disabled/profile | explicit typed fixtures and expected reasons; precedence/runtime unqualified |
| Enum/constraint authoring | 142 enum nodes, 11,327 constraint nodes inventoried; invalid authoring vectors reject representative boundaries | complete inventory; not a claim that every constraint combination is runtime-executed |
| Semantic-validator rules | 180 total: 60 semantic, 19 structural, 4 authoring-rejected, 81 source-only/native-equivalence, 16 RI not-run | every rule has an explicit disposition; no silent completion |
| Deterministic replay | 840 expanded capability vectors, 104 multi-value cases, fixed clock/locale/order and hashes | reproducible portable corpus |
| Editor consumption | Exact d1ab pack; 158 corpus Assessment files opened/modelled, 152 active and 6 ESX excluded | source-preservation qualification; no scanner claim |

The 81 `filter_state_capability` identities are preserved as
`source-only-native-equivalence`.  They refer to legacy OVAL State-reference
terminology; native 0.4.1 uses inline `state_filter` predicates in Set/Object
expressions.  They share the independently justified `core-set-filters`
witness and are not silently relabeled as 81 native semantic passes.

## Reproducible gates

Run from the repository root with the pinned `.venv`:

```sh
.venv/bin/python conformance/tools/generate.py
.venv/bin/python conformance/tools/runner.py validate
.venv/bin/python conformance/tools/runner.py coverage
.venv/bin/python -m unittest tests.test_issue87_conformance -v
.venv/bin/python -m unittest tests.test_model_a_oracle -v
```

The freeze checkpoint produced:

- `validated 105 capability Assessments and 13 core Assessment`;
- `schema_validated: true`, `base_vectors_per_capability: 7`, and
  `expanded_capability_vectors_total: 840`;
- Issue #87 focused discovery: **27 tests passed** on this freeze branch;
- full canonical repository discovery: **240 tests passed**;
- deterministic regeneration: **byte-identical**;
- editor `npm test`: **206 tests passed**; exact d1ab integration: **34 passed**;
  offline verification: **VERIFIED**; host acceptance: **passed** with zero
  probe failures (one known Red Hat YAML cross-resource `$ref` warning remains
  visible).

The editor-side exact-pin corpus smoke opened/modelled **158/158** files
with **0 model failures**. Six files (four direct ESX Assessments and two
aggregate Assessments containing ESX capabilities) are explicitly experimental
and excluded. Eighteen files are intentional invalid-authoring rejection
vectors. The **134 admitted, non-experimental Assessments** passed an additional
source-preservation lifecycle check: 134/134 no-op save, same-value edit,
reopen/parse, and undo. This is editor source/open qualification, not evidence
that a scanner collected any fixture.

## Explicit holds and ownership boundary

The corpus is frozen for schema-valid authoring and independent portable
expected results.  It does **not** certify platform collectors, permissions,
status precedence under live acquisition, scale/concurrency, or cross-scanner
agreement.  The 16 `not_run` semantic rules and their exact Assessment,
fixture, expected-result, and adapter requirements remain in
`0.4/execution-boundaries/RI-196-HANDOFF.json`; RI #196 must produce receipts
that pass `receipt.schema.json` and `tools/oracle.py`.

No production converter, scanner, or canonical schema change is included in
this freeze.  Any later normative ambiguity must add a pinned counterexample,
independent expected-result justification, and a regression test before the
freeze is amended.
