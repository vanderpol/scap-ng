# SCAP-NG 0.4.0 owner decisions — authoritative authoring contract

**Recorded:** 2026-10-31

**Owner:** Jack Vander Pol

**Status:** Owner-approved design decisions; **implementation/conformance tracking below is separate from approval**. This is a pre-alpha authoring contract, not OVAL Board ratification or scanner certification.
**Primary work:** [#255](https://github.com/vanderpol/scap-ng/issues/255); case semantics [#267](https://github.com/vanderpol/scap-ng/issues/267); converter/evidence [#251](https://github.com/vanderpol/scap-ng/issues/251).

This register consolidates the 26 sequential decisions made 2026-10-30–31. The terms below take precedence over superseded 0.3 and intermediate 0.4 examples. **A schema feature is not locked merely because its owner decision is approved.** Until source, schema, converter, compiler, editor contract, fixtures, and documentation agree, mark that row as an implementation gap, not as complete. Historic examples remain evidence only.

## Approved decisions

| # | Normative rule | Enforcement surface |
|---|---|---|
| 1 | Use **`zero_or_more`** for optional cardinality/existence; retire `may_be_absent`. Preserve source semantics in provenance. | Requirement/common schemas, translator, negative fixtures. |
| 2 | Requirement inheritance is **Test → logical group → record → individual field**, with nearest complete explicit requirement winning. A field override changes the applicable pair; record correlation is maintained. No implicit fallback. | Requirement grammar, evaluation, examples. |
| 3 | Every **comparison Test** shall declare Test-level `field_requirement` (both `values_found` and `values_matching`). Individual fields normally inherit; explicitly exceptional fields override **both** values. Existence-only Tests exempt. | JSON Schema and positive/negative fixtures. |
| 4 | Infer datatypes deterministically from capability contracts, typed YAML values, explicit typed operators and typed Variables/Inputs. An explicit compatible datatype is permitted but never routinely required. Ambiguity/conflict is an error; never silently coerce. | Capability metadata, compiler, tests, authoring guide. |
| 5 | Remove legacy OVAL numeric suffixes from native capability names (e.g. `independent.textfilecontent54` → `independent.textfilecontent`); maintain complete original OVAL identifiers in provenance. Reject old aliases from finalized native authoring. | Mapping inventory, converter, schema enum/contract, regression. |
| 6 | Do not put `purpose: assessment/applicability` in an Assessment: its `class` and `mode` remain. Usage as an applicability check is determined by the typed reference at the Benchmark/Rule consumer, allowing the Assessment to be reused. | Assessment and reference schemas, converter/compiler, docs. |
| 7 | The graphical editor may display/hide documented defaults, but **all applicable defaults are materialized in saved YAML**. Document via JSON Schema `default` and `x-scap-ng-authoring` annotations (`group`, `hide_when_default`), including other rarely changed fields. Schema `default` is authoring metadata, **not a scanner/runtime default**. | Schema metadata, editor, serializer, tests. |
| 8 | Keep declarative `evaluate.if/then/else`, with static branch references and six-state results; no dynamic code, implicit loops, or deferred computation. | Expression schema, evaluator, branch tests. |
| 9 | For confirmed absence, use `values_found: none` when a **field** is absent; `items_found: none` when the entire Item is absent. Failed or incomplete collection is not proof of absence. | Requirement schema, scanner conformance, negative examples. |
| 10 | Native Assessment/Test/Object/Variable/Input/local dependency identifiers are concise, meaningful, stable, lower-case slug identifiers with suffix where prescribed, **maximum 64 characters including suffix**. Reject duplicates and random filename hashes. External original IDs are exempt. | ID propertyNames, compiler collision checks, naming policy. |
| 11 | Shared Assessment filenames use meaningful, stable names prefixed by the applicable platform family (`windows-`, `linux-`, `solaris-`, etc.), rather than SV-ID or generated hash. | Library layout and converter naming. |
| 12 | Promote an Assessment to the global shared library **only when reused across Benchmarks** and after semantic equivalence is demonstrated. Reuse inside one Benchmark stays local to it. Separate `automated` and `manual`; do not add a redundant `local` directory. | Normalizer, manifest, proof ledger, names. |
| 13 | Omit empty optional Rule metadata; retain required data whenever it affects evaluation/applicability. | Rule schema, converter, editorial policy. |
| 14 | Applicable automated Tests must explicitly contain `reported_elements`; the editor initially fills `all` and may hide it. Result redaction is an independent concern. | Test schema, editor metadata/default, converter. |
| 15 | Retain both Organizational Input `required` and `cardinality`. Distinguish unprovided Input from deliberately provided empty Input. | Input schema, evaluation, editor tests. |
| 16 | Optional Assessment Inputs may be omitted, but referencing Assessments must explicitly handle omission; an unguarded missing dependency/input is an error. | Dependency compiler, guards, tests. |
| 17 | Variable arrays use the same `values_found` / `values_matching` vocabulary; no separate implicit array behavior. | Variable grammar, comparison, tests. |
| 18 | Assessment IDs are unique across the compiled library, Test IDs within their Assessment, and Object/Variable IDs in their documented scopes. A shared Assessment retains identity. | Compiler/library collision and scope validation. |
| 19 | Incomplete collection is an `error` with reason/evidence, distinct from confirmed absence. Never fabricate missing Items. | Scanner result mapping, result schema, tests. |
| 20 | Do not expose OVAL `all_exist` as a native authoring option. Convert only where semantics remain faithful in a no-synthetic-Items model; preserve the source in provenance; otherwise block with a precise diagnostic. | Native schema, converter proof fixtures. |
| 21 | An incorrectly associated namespace/catalog is a **warning** if the intended binding resolves unambiguously; genuinely unresolved/ambiguous references are errors. | Source converter diagnostics and tests. |
| 22 | Case handling is specified **per capability and selector**. Windows registry/service/environment/EventLog/WMI selectors may be case-insensitive by the corresponding native API; Windows filesystem path lookup follows per-directory filesystem case-sensitivity configuration. Unix paths normally are case-sensitive. Collected **values** are independent: `equals` compares case-sensitively; `case_insensitive_equals` requests explicit insensitive comparison. No universal `case_sensitive` switch. | Capability metadata, Windows scanner contracts, schema annotations, tests. [#267](https://github.com/vanderpol/scap-ng/issues/267) |
| 23 | `windows.cmdlet.module_version` has the native semantic datatype **version**, inferred from the capability contract. Authors use a quoted version string without redundant `datatype`. Reject invalid version values; no generalized coercion. | Windows cmdlet capability mapping, validator, fixture. |
| 24 | An Assessment may explicitly reach a technically **`not_evaluated`** branch when a necessary check is knowingly beyond available inspection (e.g. remote share ACL). The Rule reports meaningful **informational/manual follow-up**, with observed evidence and why completion was impossible. Known noncompliance stays `fail`; unexpected collection failure stays `error`. | Expression grammar, result roll-up, branch fixtures. |
| 25 | `not_applicable` is an explicit, reason-bearing terminal outcome when applicability is genuinely disproved, not a euphemism for scanner inability. It can be selected from **any** `then`/`else_if.then`/`else` branch. False condition selects next branch; indeterminate condition propagates. The Rule applicability gate may independently produce N/A. Preserve OVAL-style Boolean aggregation. | Expression schema and evaluation, roll-up, examples. |
| 26 | Add ordered `evaluate.else_if: [{if: ..., then: ...}, ...]`, with required initial `if/then` and final `else`. Evaluate branches in order, first true wins, only selected branch runs; preserve six-state propagation. Compiler may normalize to nested `if/then/else`. | Expression schema, normalizer, evaluator, fixtures. |

## Boundary examples (normative meaning; validate against the actual revised schema before publishing)

**Presence policy with a field exception (Decisions 1–3 and 9).** Two fields inherit the Test-level pair; here only `mount_options` intentionally overrides it:

```yaml
require:
  items_found: one_or_more
  items_satisfying: every
  field_requirement: {values_found: one_or_more, values_matching: every}
  fields:
    path: {equals: /tmp}
    mount_options: {equals: nosuid, values_found: one_or_more, values_matching: one_or_more}
```

**Distinguishing absence from failed collection (Decision 9).** `items_found: none` is true only when collection successfully established no Item. `values_found: none` tests the absence of a field in a successfully collected Item. Neither is appropriate for an API error or incomplete response.

**Conditional applicability and remote evidence (Decisions 24–26).** This is a semantic sketch, not a claim that a corresponding Test/capability already exists:

```yaml
evaluate:
  if: {test: local-policy-selection-test}
  then: {test: local-file-permissions-test}
  else_if:
    - if: {test: remote-share-selected-test}
      then:
        not_evaluated:
          reason: Remote share ACL cannot be inspected from this endpoint
  else:
    not_applicable:
      reason: No affected logging configuration is enabled
```

The `not_evaluated` branch must carry the observations and follow-up details through the results contract. It must never transform a known failure into informational. [Windows 11 V-253415 (WN11-CC-000327)](https://www.stigviewer.com/stig/microsoft_windows_11/2025-05-15/finding/V-253415) motivated this case; independently verify the source STIG revision when providing an official fixture.

**Case semantics (Decision 22).** A Windows registry selector `object: {key: {equals: 'Software\\Example'}, name: {equals: Test}}` uses the case behavior documented for the Windows registry API. It does **not** turn `require.fields: {value: {equals: Test}}` into an insensitive value comparison. An author can explicitly use `case_insensitive_equals: Test` for the latter. For Windows files, the collector must inspect the containing directory's effective case-sensitivity before resolving each name component; the OS-level inspection command is `fsutil.exe file queryCaseSensitiveInfo <path>`. Native scanner code may instead use the appropriate filesystem API, observing API-specific behavior. Authoring cannot dictate a universal file-path case mode. See Microsoft's [case-sensitivity guidance](https://learn.microsoft.com/en-us/windows/wsl/case-sensitivity), [registry structure](https://learn.microsoft.com/en-us/windows/win32/sysinfo/structure-of-the-registry), and [registry value-name contract](https://learn.microsoft.com/en-us/dotnet/api/microsoft.win32.registry.getvalue). This evidence currently covers registry and file selectors; all other Windows capabilities need separate audit before a blanket rule can be declared.

**Version contract (Decision 23).** `object: {module_version: {equals: '1.0.0.0'}}` is a typed version selector because `windows.cmdlet` says so; it is not an untyped string cast. Incompatible explicit datatypes and invalid version tokens are rejected.

## Implementation lock and review criteria

This document records owner acceptance; the following must be checked **before** claiming 0.4.0 locked:

1. Update each version-local JSON Schema (`x-scap-ng-version`, `x-last-modified`), document standard editor defaults and case-selector metadata; inspect all native capabilities for vocabulary drift.
2. Add positive and negative fixtures for all 26 decisions, including `may_be_absent`, missing Test `field_requirement`, long native IDs, redundant `purpose`, wrong selector case, `else_if` ordering and six-state N/A vs not-evaluated.
3. Update converter, compiler, editor-facing guidance and examples to emit **only** the approved 0.4 authoring syntax; preserve OVAL 5.12.3 provenance and source evidence.
4. Run focused regression and source-equivalence tests, publish count of changed/blocked samples and **do not** claim semantic equivalence on schema acceptance alone. Rebuild broader 65-STIG gallery only as a separately authorized review build.
5. Publish a before/after review packet tied to #255/#267 and record exact commit, acceptance date, tests and remaining gaps. Release/Board ratification require separate approval.

**No change to history:** prior generated archives and source-proofs remain pinned historical evidence, not silently re-labeled as canonical content.

### Implementation checkpoint: initial schema-first branch

Working branch: `codex/v04-owner-contract-20261031`; deliberately not merged into `main` before converter alignment. Verified focused suites: `test_v04_owner_decision_schema_lock` (13), `test_v04_field_requirement_schema` (13), `test_v04_clear_cardinality_schema` (13), `test_v04_schema_draft` (9), `test_v04_evaluate_operator_schema` (5), `test_generate_capability_schema_v04` (14), and direct `test_v04_all_items_schema` (3 positive/6 negative). This is a partial syntactic lock, not a full suite pass.

Known red integration boundaries: `test_v04_native_schema_generation` has expected old generated-schema hash and direct conversion failures; `test_v04_canonical_requirement_oracle` still emits old Test requirements; `test_v04_field_requirement_schema_candidate` fails to import because it addresses a superseded schema key. Do **not** update any baseline hash solely to turn CI green. Migrate implementation, assess source equivalence, then deliberately review/rebaseline. Numeric native capability suffixes, full Windows case-contract census, Rule metadata pruning and compiler-wide ID/branch result checks also remain open.
