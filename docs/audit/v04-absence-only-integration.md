# Canonical absence-only integration — #251 / #248

Base: `4e14a715e5f06c669a3640d0963b864de8a3085a` (`main`).
This is the owner-authorized converter/upgrader integration, separate from the
[schema-only review packet](v04-absence-only-schema-review.md). It does not change
0.3.x, the normative specification, editor, scanner or Item-level `all_exist`.

## Exact candidate retrieval and schema review

The latest #251 coordination comment supplied the complete git-format patch for
local commit `5ecc215981788e78bf11e209232cf2be1ac87414`, which was not published as
a Git commit. Extracted its raw fenced block and restored the terminal blank line
omitted by rendered Markdown. The resulting complete patch is exactly 24,438
bytes and matches the published SHA-256:
`5386eff5bc29a223ba3225ff4bb3f618ff3b5bae5dd1255fac9393af0999ead6`.
The base matched, the checkout was clean, `git apply --check` passed, and exactly
five declared paths were applied. The schema blob is unchanged from the candidate:
`725bba3c6588368a91c9d8dc4fbae8ca2462b524`.

Reviewed the full packet, all schema changes and positive/negative tests. The
owner-selected field form is exactly `unlabeled: {values_found: none}`; the record
form is exactly `record: {records_found: none}`. Neither accepts comparisons,
matching counts, datatype, redaction flags or member predicates. A local absence
overrides inherited comparison requirements. Shared absence/matching pairs are
invalid. `values_matching: none` with existing values and a comparison remains a
separate accepted concept. No alternate syntax or alias was invented.

OVAL 5.12.3 `EntityStateSimpleBaseType` and `EntityStateComplexBaseType` both define
`check_existence`, including `none_exist`. The record type extends the latter.
Record-member omission is different: `EntityStateFieldType` requires an error
when an expected member is missing. The existing reference test confirms that
case remains `error`; it is not reinterpreted as confirmed record absence.

## Source-backed before/after and losslessness

### Actual DNS source

Original pinned NIWC source:
`research/assessment-simplification/evidence/ms_windows_server_dns/SV-259345/source-oval.xml`,
SHA-256 `44411063be71910f348a31059b69338f3c83a68db4082cafeac198ff440f04d2`.
Definition `oval:navy.navwar.niwcatlantic.scc.windows:def:259345` uses States
`oval:navy.navwar.niwcatlantic.scc.windows:ste:25934502` and
`oval:navy.navwar.niwcatlantic.scc.windows:ste:25934503`, each containing exactly:

```xml
<independent-def:stdout_line check_existence="none_exist"/>
```

Both have no text, comparator attribute, member nodes or variable reference.
The old XML lowering materialized missing text as an empty scalar. The following
**before** fragment is a legacy migration intermediate, not canonical authoring:

```yaml
stdout_line: {datatype: string, equals: '', require: none_exist}
```

Actual canonical **after**, also retained in compiled Test operands:

```yaml
stdout_line: {values_found: none}
```

The explicit legacy `none_exist` source token controls this migration. It does
not repair invalid canonical input. Only no comparison or the missing-text
`equals: ''`/default-string artifact is accepted. Other comparisons or attributes
reject rather than disappear. Original lexical input and its digest remain in
the source ledger; inverse replay verifies exact source reconstruction.

A controlled variant of the same original XML changes one field to explicit
`check_existence="at_least_one_exists"`, `operation="equals"`, with empty text.
The resulting comparison stays intact through YAML and compiled JSON:

```yaml
stdout_line: {datatype: string, equals: '', values_found: one_or_more, values_matching: every}
```

The other original absence field still becomes `{values_found: none}`. Empty
value comparison and confirmed absence therefore do not collapse into each other.

### Original Gatekeeper and controlled record source

The exact Gatekeeper source is pinned at Self-Assertion revision
`e3538595c5083b9c34d937a81d319234df9bbfaa`, path
`SCAP_1.4/OVAL_Test_Content/macos/macos-def_gatekeeper_test.xml`,
SHA-256 `a76301de534a71f84fc498108c59b065551b9ec933db1b0a8e8582e835b2eebf`.
Test `oval:navy.navwar.niwcatlantic.scc:tst:1` and its State combine enabled=true
with `<unlabeled check_existence="none_exist"/>`. Its proof CLI now emits canonical
content, validates both schema contracts, and independently reconstructs the
original OVAL semantic graph and passes the original macOS XSD. The new native
form is `unlabeled: {values_found: none}`, including under inherited scopes.

Record fixture: original `windows/win-def_wmi57_object_test.xml` at that same pin,
SHA-256 `ac9a8bc062d9a261624eefc963da7cc3e190be96519da5369054d1bde8a52cdb`.
The original bytes and provenance are retained under
`tests/fixtures/v04-absence-only/`. No published record-absence case was found in
the pinned OVAL test-content tree. The test therefore explicitly constructs a
controlled variant: replace a WMI State's record member predicates with
`<result datatype="record" check_existence="none_exist"/>`. This variant is not
claimed as original published content. It passes the pinned Windows OVAL XSD,
the maintained original-source lowering/reconstruction comparison, current schema
validation and native bundle compilation.

Before (old lowering cannot recognize an empty record member list):

```yaml
result: {datatype: record, equals: '', require: none_exist}
```

After:

```yaml
result: {record: {records_found: none}}
```

Record absence with nonempty member predicates rejects. Inverse provenance retains
the exact original intermediate. The typed source-IR scope index now accepts the
absence-only record without inventing matching counts or member obligations.
The native compiler already preserves the complete requirement AST; no runtime
result kernel or compiler evaluation semantics were changed.

## Regression repairs and verification

The schema-only candidate independently reproduced the two reported failures in
`test_field_and_record_quantifier_cross_products` and
`test_windows_dns_variables_and_filters`. Both now pass. Every cross-product case
is still exercised: absence with a synthetic nonempty comparison/member predicate
must explicitly reject, rather than silently dropping it. Valid comparison pairs
still round-trip; dedicated source-backed absence positives replace no assertions.

New integration tests cover original Gatekeeper and DNS, inherited scopes,
present empty strings, controlled record absence, invalid matcher/comparator/
attribute combinations, source inverse ledgers and actual compiled JSON operands.
All test/generated 0.4 output is canonical; legacy State structures remain only
explicit migration inputs/internal source intermediates, never authored aliases.

OVAL reference-algebra checks retain confirmed `does_not_exist` → true,
existing → false, error → error, and not-collected → unknown, including mixed
absence/error and absence/not-collected evidence. These are source-reference
checks, not a scanner execution. Missing record member remains error. No generic
empty observation is assumed to prove successful collection or field absence.

| Validation | Result |
| --- | --- |
| Focused schema/converter/upgrader/compiler/source and flattening suites | **252 tests passed, no skips** |
| Executable all-Items grammar assertions | 3 positive, 6 negative cardinality cases plus inherited-scope and legacy-rejection checks passed |
| Supported capability schema-generation census | **100/100**, zero failures; 694 predicates, 140 selectors, four record capabilities |
| Original Gatekeeper proof CLI | Schema, generated capability, YAML/JSON, independent OVAL root semantic graph and macOS XSD passed; source/native mutations rejected |
| Unchanged main broad runner | 3037 tests; 2 failures, 127 errors, 26 skips |
| Integrated candidate broad runner | 3045 tests; 1 failure, 127 errors, 26 skips |
| Broad failure-identity comparison | **Zero new**, 128 unchanged occurrences; prior Gatekeeper absence positive resolved |

The 128 historical research/reference failures remain visible. No tests were
removed, skipped, demoted or marked expected failures. Eight new schema/source
regression methods account for the broad test-count increase. The independent
Item-level `all_exist` negative regression remains passing and unresolved by design.

## Exact commands and publication

Python 3.12.14; workflow-pinned PyYAML 6.0.3, lxml 6.1.1, jsonschema 4.25.1;
observed cryptography 50.0.2. Existing external AppArmor/environmentvariable58/uname
and Gatekeeper source bindings point to Self-Assertion XML at the pin above.
IOS/IOS XE line-source bindings are supplied for focused tests, but not the broad
runner, matching its workflow. Run from the repository root with the existing
`PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003`:

```bash
python -m unittest -v \
  test_v04_schema_draft test_v04_clear_cardinality_schema test_v04_all_items_schema \
  test_v04_field_requirement_schema test_v04_object_selector_language \
  test_v04_field_requirement_conversion test_v04_canonical_source_ir \
  test_v04_source_schema_registry test_v04_canonical_requirement_oracle \
  test_v04_native_bundle_compiler test_v04_approved_pipeline \
  test_v04_absence_only_integration test_v04_scalar_none_exist_source \
  test_scap_converter_core test_scap_converter_core_object_presence \
  test_scap_converter_core_multistate test_scap_converter_core_apparmorstatus \
  test_scap_converter_core_environment_uname test_oval_result_truth_tables \
  test_generate_capability_schema_v04 test_v04_flat_object_authoring \
  test_flatten_v04_object_schema test_audit_v04_flat_object_names
python tools/test_generate_capability_schema_v04_corpus.py --output /tmp/absence-generation.json
python tools/prove_v04_oval_macos_gatekeeper_source.py \
  --source tests/fixtures/v04-absence-only/macos-def_gatekeeper_test.xml \
  --schema-root schema/v0.4.0 \
  --xsd-root third_party/scap-1.4-schemas/oval_5.12.3 --output /tmp/gatekeeper-absence-proof
python tools/run_current_tool_regressions.py
```

The source integration fixtures are self-contained for CI. The schema workflow
now runs the new source-backed integration test and Gatekeeper regression.
Published directly to `main` with a normal, non-forced push:

- Schema-only candidate: [7ff986ce04c2ea8c128d2c39f7f9ff90cc707e19](https://github.com/vanderpol/scap-ng/commit/7ff986ce04c2ea8c128d2c39f7f9ff90cc707e19).
- Converter/upgrader integration, source proofs, fixtures and regressions:
  [8d4774f4e9ef75d628ed9d832a6c634ba2591bcf](https://github.com/vanderpol/scap-ng/commit/8d4774f4e9ef75d628ed9d832a6c634ba2591bcf).

Terminal hosted results for the integration SHA, observed 2026-10-24:

| Workflow | Result |
| --- | --- |
| [0.4 draft schema](https://github.com/vanderpol/scap-ng/actions/runs/40121214869) | Passed, including the new source-backed absence integration tests |
| [Shared converter core](https://github.com/vanderpol/scap-ng/actions/runs/40121214715) | Passed |
| [Original Gatekeeper source roundtrip](https://github.com/vanderpol/scap-ng/actions/runs/40121214762) | Passed |
| [Capability schema generation](https://github.com/vanderpol/scap-ng/actions/runs/40121214800) | Passed |
| [Current-design contracts](https://github.com/vanderpol/scap-ng/actions/runs/40121214684) | Passed |
| [Canonical authoring fast checks](https://github.com/vanderpol/scap-ng/actions/runs/40121214753) | Passed |
| [Markdown audit](https://github.com/vanderpol/scap-ng/actions/runs/40121214752) | Passed |
| [Commit issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40121214785) | Passed |
| [Rebaseline smoke](https://github.com/vanderpol/scap-ng/actions/runs/40121214750) | Failed; not a green release gate |

The local pinned-dependency broad comparison above establishes zero new failing
test identities and one resolved absence regression. The hosted rebaseline
conclusion is reported separately; its failure is not suppressed or interpreted
as success. Historical classification and recommended release-scope follow-up
remain in the [maintained regression report](v04-maintained-ci-stabilization.md).
This task does not change their gating status.

Issue-write access in this environment previously returned the exact error
`Post "https://api.github.com/graphql": Forbidden`; it was not retried in a loop.
This committed report is the durable GitHub handoff fallback.

No unresolved semantic choice was made for the supported source cases. Unsupported
nonempty comparisons/member predicates remain explicitly blocked pending original
source proof. No 65-benchmark execution, 0.3.x edit, normative-specification change,
Item-level population decision or scanner-runtime-equivalence claim was made.

Issues: [#251](https://github.com/vanderpol/scap-ng/issues/251),
[#248](https://github.com/vanderpol/scap-ng/issues/248).
