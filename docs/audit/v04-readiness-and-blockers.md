# 0.4.0 readiness and blockers — 2026-10-24 (#251)

**Not release-ready.** Audit pinned to `main` at
[`56397063033971110f79442ab8c51928d486d961`](https://github.com/vanderpol/scap-ng/commit/56397063033971110f79442ab8c51928d486d961),
as requested in the [coordination handoff](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6388106562).
Fetched `origin/main`; it matched that SHA and the checkout was clean. Completed
absence integration was reviewed, not reimplemented. No schema, production
converter/compiler, normative specification, editor, scanner or gate changed.
The only executable addition is a bounded, non-gating acceptance audit command.

## Actual acceptance evidence

[Machine-readable results](v04-readiness-acceptance-results.json) contain original
source paths/hashes, every original Test ID, executed CLI commands, verification
results and generated-artifact SHA-256 values. All inputs are the existing pinned
NIWC production XML fixtures, not archived generated authoring. The maintained
source-backed converter reuses mature parsing/lowering internally; its output
crosses the **current** 0.4 schema and native compiler.

| Production source | Original Definition | Tests | Result |
| --- | --- | ---: | --- |
| RHEL 9 `SV-257889` | `oval:mil.disa.stig.defs:def:230325` | 2 | PASS: Filters, permissions, Variables |
| Windows Server 2025 `SV-278001` | `oval:navy.navwar.niwcatlantic.scc.windows:def:278001` | 5 | PASS: records, shared Objects |
| Windows Server DNS `SV-259345` | `oval:navy.navwar.niwcatlantic.scc.windows:def:259345` | 5 | PASS: Variables, Filters, confirmed field absence |
| Windows 11 `SV-253254` | `oval:mil.disa.stig.defs:def:253254` | 1 | PASS: Enterprise/EnterpriseS complete-State OR |

**Four CLI cases, 13 compiled Tests, zero failures.** Each ran the public
converter subprocess, rendered canonical YAML and JSON, independently parsed and
compiled both formats with schema validation enabled, required identical bundle
bytes, then independently verified the resulting `.scapng`. Each bundle contains
three documents and one program. Actual compiled `require` operands equal the
converted authoring requirements. Artifact hashes are for this exact execution;
no generated payload or large log is committed.

**Important boundary:** the integration harness supplies a synthetic minimal
Benchmark/Rule wrapper around each real converted Assessment. This proves
Assessment conversion and closed-graph compilation; it does not prove original
XCCDF Benchmark/Rule migration, full package coverage or a six-STIG rebaseline.
The existing pipeline tests independently verify original OVAL semantic-root
reconstruction and source/upgrade inverse proofs. These are static source proofs.

Fresh existing regression runs:

- `test_v04_approved_pipeline` + `test_v04_native_bundle_compiler`:
  **18 tests passed, zero failures/errors/skips**. Includes the four production
  samples, rejection of the reserved population mapping, damaged/stale programs,
  changed operands, graph/reference/version failures and tampered bundles.
- `test_v04_public_cli_smoke` + `test_v04_native_bundle_signing`:
  **six tests passed, zero failures/errors/skips**. Public CLI source-package and
  dual-archive modes pass; five ephemeral-certificate CMS tests reject wrong/no
  trust, wrong keys and tampering. Those signing tests explicitly bypass schema
  validation on their miniature fixture. They are **not** signed, fully validated
  production-sample acceptance or production publisher authentication.

All four audited production bundles are unsigned: `signature_verified: false`.
Native signing/explicit-trust verification exists in
`tools/v04_native_bundle_signing.py`; an absent signing implementation is therefore
not the blocker. Independently managed publisher identity/trust/release policy
and a signed current-production end-to-end acceptance gate are not established
by this audit. Every bundle reports `scanner_evaluated: false`. No live collector,
scanner runtime, generic six-state equivalence or Board ratification is claimed.

## Reproduce the bounded run

From the repository root, Python 3.12.14 with PyYAML 6.0.3, lxml 6.1.1,
jsonschema 4.25.1 and cryptography 50.0.2 was used. OpenSSL must be available
for CMS tests. These are the observed exact versions, not a new dependency lock
or a claim that every hosted workflow has identical pins.

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003
export SCAP_NG_251_OUTPUT_DIR=/tmp/v04-readiness/source-proof
python -m unittest -v test_v04_approved_pipeline test_v04_native_bundle_compiler
python -m unittest -v test_v04_public_cli_smoke test_v04_native_bundle_signing
python tools/audit_v04_readiness_acceptance.py --output-dir /tmp/v04-readiness/cli
```

The local `python` executable was
`/workspace/.onboarding/rebaseline-venv/bin/python`. The committed audit command
records the checked-out HEAD and active Assessment schema digest; run it from the
named audit base plus this audit-only addition to reproduce the audited toolchain.
Its subprocesses use the same Python. It creates files only under its requested
output directory. It does not sign, dispatch CI or select a source corpus.

## Stale documentation versus current implementation

This is a findings list, **not an edit or waiver of release criteria**. Dated
historical proofs retain their original scope; they are not silently promoted.

| Surface | Stale or overbroad wording | Actual status at the audit SHA |
| --- | --- | --- |
| [Finalization gates](../../review/current/0.4.0-FINALIZATION-GATES.md), Gate 1 and later historical entries | `require.items/all_items_must`; legacy `all/any/odd` acceptance | Current Test uses structured `items_found` and, for conditions, `items_satisfying` with `fields/and/or/one/xor`. Presence-only uses `items_found`. Deprecated forms fail closed. Old 4,001-document evidence is against an earlier schema. |
| Same, Gate 4 | Executable `.scapng` compilation still unimplemented | Current native compiler emits and verifies Test/result programs for the bounded accepted subset. Full source/capability and scanner coverage remain unproven. Do not mark Gate 4 complete from these samples. |
| Same, Gatekeeper dated entry | `{require: none_exist}` positive native syntax | Integrated canonical field absence is `{values_found: none}`; record absence is `{record: {records_found: none}}`. No comparator/matcher or unrelated attributes are permitted on those forms. Existing-value `values_matching: none` is separate. |
| [Schema README](../../schema/v0.4.0/README.md), opening status | Absence-only still pending owner diff review; converter migration subsequent | #251's coordination review acknowledges the implemented source-backed integration. Scanner proof remains outstanding. The reviewed schema bytes are unchanged by this audit. |
| Same, cardinality description | Source `all_exist` and `at_least_one_exists` both map to `items_found: one_or_more` | This is not a general lossless equivalence. The retained mixed-population counterexample below requires an owner decision; do not use this prose to authorize a converter mapping. |
| Same, implementation status | Executable compilation broadly outstanding | Bounded current-schema compilation now passes; signatures, intended source coverage and runtime evidence have separate status. |
| [Current design](../../research/iterations/003/design/CURRENT-DESIGN.md), version/vocabulary | Active 0.3 line, first-class States and old placement guidance | [Toolchain contract](../releases/TOOLCHAIN-RELEASES.md) identifies active 0.4 output; current Test schema and #251 are authoritative for this task. Preserve useful version-neutral source semantics, not the older authored dialect. |
| [Developer runbook](../developer/CONVERTER-COMPILER-RUNBOOK.md), direct-State subsection | Exactly one scalar State, no multiple State fields | Registry multi-State AND/OR is already source-attested in `scap_converter_core.py` and [its report](v04-registry-multistate-stabilization.md). Other adapter boundaries still apply. |
| Historical source-preview/signature evidence | Earlier six-STIG packages or source-only CMS proof could be read as current signed executable release evidence | Neither is a current-schema whole-package acceptance or production trust proof. Current typed compilation, signing test, runtime and human acceptance remain distinct. |

No finalization-gate status, grammar, normative text, published asset or owner
decision was rewritten. Proposed documentation reconciliation should retain
dated historical evidence and link current reviewed results, without weakening
the original pass criteria.

## Remaining regression inventory and real production boundaries

Reuse the completed broad run rather than repeating 3,045 tests for a read-only
audit. `563970630` differs from tested integration SHA `8d4774f4e` only in its
report: `git diff 563970630 8d4774f4e -- tools schema tests` is empty.
The [absence integration report](v04-absence-only-integration.md) records
**3,045 tests / one failure / 127 errors / 26 skips**, zero newly failing IDs.

The [current exact-identity classification](v04-readiness-regression-classification.json)
joins all 128 failing occurrences against the prior maintained inventory:

- **126 historical research-dialect occurrences:** removed scalar enum catalogs
  (120), removed candidate schema definitions (five), and one old native-C
  compatibility-manifest/export-count expectation. This includes
  `test_v04_field_requirement_schema_candidate.CanonicalGrammarCandidateTests`
  `setUpClass` and four `test_validate_v04_fields_condition_preview` research
  candidate cases; filenames alone do not make those current grammar tests.
- **Two historical fixture/reference errors:**
  `test_research_c_unified_complex_windows.ComplexWindowsUnifiedCompiler.test_one_frontend_still_compiles_a_schema_valid_native_A_test_set`
  and
  `test_research_c_windows_shared_native.WindowsNativeCompilation.test_compiled_native_04_a_states_pass_base_schema`
  (exact unittest identities are preserved in the JSON). Their historical
  validators lack a resource registry; fixing lookup alone would leave their
  dialect mismatch unresolved.
- **Zero current production failing identities in that recorded inventory.**
  This is not zero production coverage gaps. The Gatekeeper absence positive is
  now resolved; the earlier inventory's boundary entry is historical, not a
  remaining blocker. All research cases still execute in the maintained gate;
  none was skipped, suppressed, demoted or removed.

The genuine reserved production boundary remains pinned RHEL 9 `SV-258179`,
SHA-256 `463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9`,
Definition `oval:mil.disa.stig.defs:def:230413`, Test
`oval:mil.disa.stig.ind:tst:23041300` with `check_existence="all_exist"`.
The existing passing negative test
`ApprovedPipelineTests.test_real_all_exist_source_requires_owner_population_decision`
demonstrates a complete population of one existing and one nonexistent member:
OVAL `all_exist` is **false**, `at_least_one_exists` is **true**. The upgrade's
source-equivalence assertion rejects; this audit does not resolve that meaning.
The public core also rejects that Definition; freshly observed exact error:

```text
ValueError: Direct Object/Test original OVAL source proof: multi-Test requires 2-15 direct Object Tests without State/Variable
```

That public diagnostic is an adapter-shape restriction, not proof that the core
diagnosed the population distinction. The independent source-backed negative is
the semantic evidence. Unsupported intended-release source gaps require explicit
coverage disposition; four passing samples cannot settle the whole denominator.

## Minimum sequence to release readiness; stop at owner decisions

1. **Jack decides historical regression scope:** keep these research dialects as
   mandatory current release requirements and authorize migration, or approve
   separately pinned research CI. Until then the maintained gate remains red;
   no gating change is made here.
2. **Jack decides the source-backed Item population boundary** and intended
   release source coverage. Preserve the `all_exist` counterexample; never replace
   its source meaning silently. Resolve/explicitly disposition actual unsupported
   sources before claiming their coverage.
3. After those decisions, reconcile stale readiness/runbook wording against the
   reviewed current grammar, complete targeted approved coverage fixes and
   re-run positive/negative gates. A whole six-STIG regeneration is a separate
   authorized checkpoint, not part of this task.
4. Complete intended release-package closure/compilation and signing/trust
   acceptance, clean-extract toolchain/dependency reproducibility, version-correct
   normative docs/examples and human review. Maintain exact SHA evidence.
5. Obtain capability/collector/scanner acceptance and the other retained release
   criteria, including Studio compatibility if required by the owner. These need
   their own work authorizations; no runtime parity follows from this packet.

Stop here at the reserved decisions. Existing exact integration-SHA hosted
results are linked in the [integration report](v04-absence-only-integration.md):
eight passing workflows and red rebaseline. No manual workflow, full six-STIG or
65-benchmark execution was launched. Issue-comment access was previously denied
with `Post "https://api.github.com/graphql": Forbidden`; the coordination comment
explicitly preserves the committed-report fallback. No repeated issue-write
attempt or scheduling claim is made.
