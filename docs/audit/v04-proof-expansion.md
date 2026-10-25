# Bounded source-proof expansion and fixed Windows 24 — #251

2026-10-25. [Owner authorization](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6392337337).
Started from reviewed `336cb37114aadf51d2810aa669b6325b9c03be7b` on synchronized
`main`. **Windows batch: 17 PROVED, 7 UNVERIFIABLE/UNSUPPORTED, zero MISMATCH.**
Original RHEL/Apache blockers: **two PROVED and one PROVED_WITH_EXPLICIT_APPROVED_NORMALIZATION**.
Oracle remains UNVERIFIABLE. The prior four exact proofs reproduce.

Coverage advances **4/883 → 24/883 (2.718007%), delta +20**: **23 ordinary proofs
and one explicitly conditional normalization proof**, leaving **859 unverified**.
No production converter/compiler, approved schema, specification, release gate,
editor/scanner, source file or canonical six-package artifact changed. No full
883 verification, corpus conversion or six-STIG rebaseline ran.

## Fixed batch and exact outcomes

The [24-identity manifest](v04-proof-expansion/windows24-manifest.json) was committed
**before any source comparison** as
[2ac5bb7a70131196a545b27ef4c2e8c201e1cede](https://github.com/vanderpol/scap-ng/commit/2ac5bb7a70131196a545b27ef4c2e8c201e1cede).
Its SHA-256 is `9969b6bdfa832e4aba03bf28fc20291c74839e74ddfc8153b4faf61049808598`;
the runner rejects any changed selection. It contains 8/8/8 previously unverified
unique identities, selected from native inventory for varied registry, WMI/record,
shellcommand, Variable and multi-Test/nested logic shapes. No candidate was swapped.

| Case | Platform | Rule / Assessment case | Outcome | Wall seconds | First obligation or result |
| --- | --- | --- | --- | ---: | --- |
| 01 | Windows 11 | SV-253259 | UNVERIFIABLE/UNSUPPORTED | 0.231 | all_exist outside exact approved source proof |
| 02 | Windows 11 | SV-253261 | PROVED | 0.224 | Complete source/package/program match |
| 03 | Windows 11 | SV-253263 | UNVERIFIABLE/UNSUPPORTED | 0.221 | datatype proof unavailable: version |
| 04 | Windows 11 | SV-253266 | PROVED | 0.221 | Complete source/package/program match |
| 05 | Windows 11 | SV-253274 | PROVED | 0.257 | Complete source/package/program match |
| 06 | Windows 11 | SV-253394 | PROVED | 0.234 | Complete source/package/program match |
| 07 | Windows 11 | SV-253401 | UNVERIFIABLE/UNSUPPORTED | 0.228 | Set/Filter/behavior collection proof unavailable: oval:mil.disa.stig.win:obj:25340100 |
| 08 | Windows 11 | SV-253446 | PROVED | 0.221 | Complete source/package/program match |
| 09 | Server 2025 | SV-277993 | PROVED | 0.258 | Complete source/package/program match |
| 10 | Server 2025 | SV-277998 | PROVED | 0.273 | Complete source/package/program match |
| 11 | Server 2025 | SV-278028 | UNVERIFIABLE/UNSUPPORTED | 0.257 | Set/Filter/behavior collection proof unavailable: oval:navy.navwar.niwcatlantic.scc.windows:obj:27802801; Set/Filter/behavior collection proof unavailable: oval:navy.navwar.niwcatlantic.scc.windows:obj:27802810; Set/Filter/behavior collection proof unavailable: oval:navy.navwar.niwcatlantic.scc.windows:obj:27802820; Set/Filter/behavior collection proof unavailable: oval:navy.navwar.niwcatlantic.scc.windows:obj:27802830 |
| 12 | Server 2025 | SV-278104 | PROVED | 0.244 | Complete source/package/program match |
| 13 | Server 2025 | SV-278139 | UNVERIFIABLE/UNSUPPORTED | 0.250 | native Object: unsupported keys ['select'] |
| 14 | Server 2025 | SV-278146 | UNVERIFIABLE/UNSUPPORTED | 0.248 | Set/Filter/behavior collection proof unavailable: oval:navy.navwar.niwcatlantic.scc.windows:obj:27814601 |
| 15 | Server 2025 | SV-278208 | UNVERIFIABLE/UNSUPPORTED | 0.249 | all_exist outside exact approved source proof |
| 16 | Server 2025 | SV-278234 | PROVED | 0.248 | Complete source/package/program match |
| 17 | DNS | SV-259334 | PROVED | 0.158 | Complete source/package/program match |
| 18 | DNS | SV-259339 | PROVED | 0.140 | Complete source/package/program match |
| 19 | DNS | SV-259346 | PROVED | 0.141 | Complete source/package/program match |
| 20 | DNS | SV-259351 | PROVED | 0.149 | Complete source/package/program match |
| 21 | DNS | SV-259360 | PROVED | 0.140 | Complete source/package/program match |
| 22 | DNS | SV-259377 | PROVED | 0.142 | Complete source/package/program match |
| 23 | DNS | SV-259381 | PROVED | 0.139 | Complete source/package/program match |
| 24 | DNS | SV-259384 | PROVED | 0.148 | Complete source/package/program match |

All native Assessment IDs here are the listed Rule ID plus `.automated`.
[Results](v04-proof-expansion/results.json) retain exact Benchmark/Rule/Assessment
IDs and member paths, all XCCDF check alternatives/catalog routes, complete
Definition/Test/Object/State/Variable closures and hashes, original ZIP/XML
checksums, exact program hashes, typed comparison terms and per-case proof-method
hash. Distinct checks/extensions were not replaced by partial subsets. Failed
examples remain in [24 source/native/program fixtures](../../tests/fixtures/v04-proof-expansion/),
with every fixture SHA in [fixture inventory](v04-proof-expansion/fixtures-manifest.json).
These are complete dependency extractions, not standalone XSD-conformant OVAL.

## Linux/Apache proof rules and earlier blockers

| Original case | Old | New | Evidence |
| --- | --- | --- | --- |
| RHEL SV-257889 | Unverified | PROVED | Complete two-Test file/password graph, pre-Set ordered Filters, ObjectComponent projection/for_each, explicit traversal and field predicates |
| RHEL SV-258179 | Unverified | PROVED_WITH_EXPLICIT_APPROVED_NORMALIZATION | All 24 Tests and complete regex/instance/Variable graph; exactly 16 admitted all_exist Tests under the existing pinned contract |
| Apache SV-214228 | Unverified | PROVED | Four Tests, 18 Variables and complete ordered/typed discovery graph, regex_capture, concat, merge and unique |
| Oracle SV-271844 | Unverified | UNVERIFIABLE | Original comparator-bearing stderr_line none_exist remains outside source-equivalence proof; archive exception unchanged |

[Proof-rule citations](v04-proof-expansion/proof-rule-anchors.json) bind existing
OVAL 5.12.3 XSD definitions and version-correct native contracts by file SHA.
The comparer independently reads both representations, preserves complete operands,
quantifier scopes, collection dependencies, error flags, Item creation, regex
modes, Filter placement/order and function order/defaults. Source function names
alone are insufficient: the whole typed dependency tree and exact compiled operands
must match. Discovery commands are compared verbatim, never executed.

Two comparison normalizations are spec-attested: AND/OR **State predicates**
commute under all six-state combinations (duplicates and scopes retained), and a
one-operand OVAL Set is the filtered complete operand for every Set operator.
Binary COMPLEMENT operand order remains significant. Early apparent Windows
value differences were reordered State OR branches; full operand multisets matched.
Only the comparer was corrected; no source or generated operand was repaired.
Evaluate binding trees, Filters and function sequences are never sorted.

The file for_each rule admits only the existing direct ObjectComponent → local
Variable → selector class with source-equivalent one_or_more quantification;
cohort, field, type, missing-field/collection dependency and Test aggregation
boundaries remain intact. Status tests retain the existing non-Boolean Filter
error policy. Incomplete evidence cannot become a complete-collection claim;
existing decisive partial true/false outcomes are preserved, not universally
collapsed to unknown.

RHEL normalization admission verifies the complete original closure against
`research/assessment-simplification/evidence/rhel_9/SV-258179/source-oval.xml`,
SHA-256 `463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9`,
and the exact full SCAP ZIP/Rule/Definition scope. It admits only 16 stateless
Test-level all_exist nodes and checks the current actual-Items schema permits
exists/error/not_collected, with no synthetic nonexistent Item. Test/Object IDs,
versions, hashes, native bindings, owner decision and schema hash are retained.
The original mixed existing/nonexistent Item counterexample remains false under
OVAL all_exist versus true under at_least_one_exists; the proof is **conditional**,
not unrestricted OVAL equivalence. Field/record quantifiers are unchanged. Windows
all_exist cases are not admitted by this source-specific exception.

Negatives include selector/quantifier, Filter action/order, Set order, for_each
scope/dependency, traversal/regex/instance/type, function capture/default/order and
missing graph mutants. A fully rehashed, schema-valid forged package—with source
graph hashes and compiled operands consistently updated—passes the independent
integrity consumer yet fails original-source comparison. Its miniature closed
wrapper is solely an adversarial test, not positive corpus proof. Positive corpus
proofs use the actual pinned packages and complete original check closures.

## Coverage and observed feature/cost evidence

[Coverage CSV](v04-proof-expansion/results-coverage.csv) preserves all 2,433 inventory
rows and the same **883 unique automated IDs**; prior proofs cannot disappear or
change native/program identity. Only actual successful proofs advance rows.

| Ownership namespace | Unique automated IDs | Proven, including conditional |
| --- | ---: | ---: |
| apache_server_2-4_unix_server | 23 | 1 |
| ms_windows_11 | 93 | 7 |
| ms_windows_server_2025 | 110 | 5 |
| ms_windows_server_dns | 21 | 9 |
| oracle_linux_9 | 41 | 0 |
| rhel_9 | 57 | 0 |
| shared | 538 | 2 |
| Total | **883** | **24** |

The two RHEL successes own shared-library identities. They are counted once,
proved at the recorded RHEL bindings; identical package copies and the other
536 shared identities are not automatically promoted. Proofs do not certify
other original Rule bindings, whole-Rule policy/applicability or a scanner.

The [observed feature matrix](v04-proof-expansion/feature-coverage.csv) shows
attempted/proved case counts and unresolved cases per construct, not complete
language coverage. [Per-case measurements](v04-proof-expansion/results-performance.json)
record wall/CPU seconds, source-node/Test counts and process high-water RSS.
This run's 32-case loop took **6.965 s wall / 6.958 s CPU**;
case median **0.230 s**, maximum
**0.328 s**. RSS is process high-water,
not per-case allocation. RSS is optional telemetry on platforms without the Unix
`resource` module; proof-tool imports and comparisons do not require it. The
import-without-resource guard and all 91 focused tests pass after this fix.
Measurements include package verification/source parsing,
exclude import/CI setup and scanner execution, and should not be extrapolated
linearly to all 883. Timing is separated from deterministic proof evidence.

## Source pins, commands and validation

All original signed NIWC inputs remain unchanged at immutable revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5`; full paths/XML members and hashes
are retained per case. Original ZIP SHA-256:

| Platform | SHA-256 |
| --- | --- |
| ms_windows_11 | `e4b8d55b58aa80124bd0974977af4c7f7bde35c748e2940e02857419292d8c3d` |
| ms_windows_server_2025 | `2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` |
| ms_windows_server_dns | `f674b67e74acbd3037093d50e33dc20765bd9d45a6c9ed2be5d463d009a6c6b8` |
| rhel_9 | `70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5` |
| oracle_linux_9 | `6733abd693380b43b2350c2692775e4ff902f895f16899db97b34fecf7fba74d` |
| apache_server_2-4_unix_server | `8894123788ba415373625eaecdbbd834f190668697803c3319393c11889f1b80` |

The six native bundle SHA-256 values remain the reviewed package-acceptance pins.
No new dependencies: use the existing Linux/Python 3.12 hash-locked environment
in [independent package acceptance](v04-package-acceptance.md).

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003
python tools/audit_v04_proof_expansion.py --inputs-dir /path/to/original-six-zips \
  --bundles-dir /path/to/pinned-bundles --report /tmp/expansion/results.json
python -m unittest test_v04_expanded_source_proof test_v04_source_package_semantics \
  test_v04_field_requirement_schema test_scap_converter_core \
  test_v04_all_exist_normalization test_v04_native_bundle_compiler \
  test_v04_package_consumer test_v04_public_validator
python tools/run_current_tool_regressions.py --report /tmp/expansion/mandatory.json
```

The last command uses the existing 23 pinned original-source bindings and vendored
OVAL XSD link from `rebaseline-smoke.yml`. `--fixtures-dir` explicitly re-extracts
only the fixed 24 Windows closures and exact native/program snapshots; the runner
always revisits the eight pilot identities and has no all-883 mode.
Repeated independent processes produce byte-identical proof JSON, coverage and
feature CSV; performance measurements intentionally differ.

**Final mandatory suite: 2,960 tests in 150.479 s, zero failures, zero errors,
one unchanged optional skip.** The baseline was 2,942 methods: eighteen added,
zero removed. **Focused suite: 91 passed**, including the original nineteen pilot
and eighteen expansion regressions. The unchanged skip is
`test_full_pinned_original_oval_census_when_corpus_supplied` in
`test_research_c_local_literal_inputs.LocalLiteralCollectionBindings`, reason
`run original source corpus through dedicated C workflow`.
Repository preservation passes with 34,242 baseline paths. Four Markdown sample
guards pass; navigation retains the same three pre-existing current Board heading
links and 39 historical broken links, with zero new broken links.
No baseline tests were removed, demoted or newly skipped.

Deterministic evidence SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| results.json | `62581c5917af2cb618dc539bcf2fa0aea536503968190c2c3df6db662fb9c337` |
| results-coverage.csv | `b30780d8c74ef65dd6626cdd28f1086727086f5e3e027c0d02b73f8152466a63` |
| feature-coverage.csv | `7edad20381f35d76691eb231f5948cc3abf2d9b519be7b2c9ce1daebcdc585c2` |
| fixtures-manifest.json | `17f8ce8d76b4545a01155562e98446263057070917a1622ff46fc899c21ec218` |
| proof-rule-anchors.json | `929be7d4b193c9be0bbeb642e4058adbe6411361e9ad286f657b5c6e91a073cb` |

## Remaining blockers and next bounded increment

The seven Windows rows remain visible: unadmitted source all_exist, version
comparison, registry behavior/collection and shell Set/Filter/select proof rules.
Any extension of the all_exist source profile requires owner approval and a new
exact source-backed review; this task does not extend it. Other missing proof
rules need focused positive/negative/status evidence before admission. Oracle's
archive-only discrepancy still needs separate owner review for source equivalence.

Recommended next step after review: fixed small batches for those seven existing
blockers, prioritizing source-version datatypes and collection/select/Filter
contracts; separately decide whether additional all_exist sources are admitted.
Then authorize another balanced fixed Windows batch. Do not start all 883.
Signing/trust, scanner acceptance and release thresholds remain separate gates.
Issue commenting remains blocked by the previously observed
`Post "https://api.github.com/graphql": Forbidden`; the committed report is the
#251 handoff without repeated attempts.


## Published commits and terminal hosted CI

Normal, non-forced pushes directly to `main`, all referencing #251:

- [2ac5bb7a70131196a545b27ef4c2e8c201e1cede](https://github.com/vanderpol/scap-ng/commit/2ac5bb7a70131196a545b27ef4c2e8c201e1cede): immutable 8/8/8 manifest before comparisons.
- [8717d081350809075b8c82dd402e70b1aef8a3de](https://github.com/vanderpol/scap-ng/commit/8717d081350809075b8c82dd402e70b1aef8a3de): independent proof-rule expansion, eighteen regression methods, 24 complete fixtures, additive fast-CI invocation, monotonic coverage and reports.
- [6d5383bc69464aedacab857c6145d043fd651ed5](https://github.com/vanderpol/scap-ng/commit/6d5383bc69464aedacab857c6145d043fd651ed5): optional Unix RSS telemetry, import-without-resource guard and refreshed reproducible method/fixture evidence. All 91 focused tests passed again after this fix; source/native outcomes and coverage are unchanged.

All five workflows triggered by the final implementation SHA `6d5383bc6`
completed **SUCCESS** (checked 2026-10-25 10:26 UTC):

| Workflow | Exact hosted run | Conclusion |
| --- | --- | --- |
| Maintained production regression | [40184501297](https://github.com/vanderpol/scap-ng/actions/runs/40184501297) | SUCCESS |
| Canonical authoring fast checks | [40184501296](https://github.com/vanderpol/scap-ng/actions/runs/40184501296) | SUCCESS |
| Current-design contracts | [40184501347](https://github.com/vanderpol/scap-ng/actions/runs/40184501347) | SUCCESS |
| Markdown navigation | [40184501279](https://github.com/vanderpol/scap-ng/actions/runs/40184501279) | SUCCESS |
| Commit issue references | [40184501240](https://github.com/vanderpol/scap-ng/actions/runs/40184501240) | SUCCESS |

[Repository preservation and boundaries at `8717d0813`](https://github.com/vanderpol/scap-ng/actions/runs/40155609881)
also completed **SUCCESS**; its path filters did not retrigger it for the telemetry
fix. Hosted conclusions were read from public Actions pages. Numeric test counts
above are the recorded local results; signed-in detailed logs remain unavailable
through the blocked API. No held/manual/historical workflow was dispatched or
represented as a fresh green check. This final documentation-only follow-up
records terminal CI; no further semantic work or 883-case audit is begun.
