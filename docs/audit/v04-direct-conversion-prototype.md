# Direct 0.4 prototype — bounded decision report

**Experiment: SUCCESS for the slice. GO for review of the direct approach;
NO-GO for production replacement. Relative production speedup is unproven.**
[Owner scope](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6397760243).
Baseline: `bf9cfde96231e6c825c1faaf3d33c38951e9ecb2`.

**Source/proof.** The complete signed Server 2025 ZIP is a
[254,194-byte pinned fixture](../../tests/fixtures/v04-direct-prototype/provenance.json),
SHA-256 `2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0`.
SYSVOL **SV-278139** and simple Registry **SV-278080** both pass independent
original OVAL dependency/operand comparison. The latter was selected by source
structure; equivalent Rule renaming still converts and stale identity fails.

One XML parse builds six scoped component indexes; checklist-local catalog/hrefs
resolve without global OVAL-ID collisions. Direct recursive conversion has no
0.3 intermediate or Rule-ID dispatch. Constants retain source quantifiers;
Variable-local Registry capability remains explicit. All **11 Profiles** have
independently checked selection projected onto two Rules; **289 Rules are omitted**.
Original metadata/dependencies and omissions are traced externally. This is a
**miniature compilation fixture**, not full Rule-policy/Benchmark conversion:
CPE/platform execution, manual choices, remediation/scoring are unsupported.
Scanner/signature-trust gates and 24/883 coverage remain unchanged.

**Correctness.** Unmodified public validator: **6/6 JSON + 6/6 YAML**. Paired
compiler and independent consumer: PASS; **6 documents, 2 programs, 2 Tests,
1 Variable**. Eighteen compiled outputs and three authoring/trace emissions
reproduce identically. Bundle SHA-256:
`fecfd8ecea81f7cbb3b9007d1ed04cf2a84acd5deee6b28529689a2ed61d90b2`.
Ten prototype tests pass: identity/scope, selectors/dependencies/quantifiers,
Profiles, wrappers, cycles, invalid attributes, blocked `all_exist` and
comparator-bearing absence. Mandatory baseline **2,974** → **2,984**, both
**0 failures/errors, 1 identical optional skip**. Historical errors and pending
Windows/Oracle decisions were not repaired or reclassified.

**Performance.** Three fresh processes, each one cold + five warm calls;
warm calls rebuild the source. Stage medians, milliseconds:

| Stage | Cold (3) | Warm (15) |
| --- | ---: | ---: |
| Integrity, parse/index/hashes | 141 | 184 |
| Conversion, selection/trace | 16 | 17 |
| Public validation | 424 | 324 |
| Compiler, including preflight | 317 | 252 |

Standalone CLI: **267 ms** including startup/output; peak **41.7 MiB**, combined
measurement/verification **87.0 MiB**. Per invocation: one source parse, zero
reparses; shared validator XSD parses eight cold/zero warm. Hotspots: Profile
selection/trace hashing. OS caches/scheduling uncontrolled. Legacy whole-Benchmark
work is non-comparable; no speedup ratio is claimed.

**Complexity/recommendation.** Core: **1 module / 422 lines** (386 nonblank,
noncomment), stdlib + PyYAML output; test/measurement harness: 383 lines. Static
reference closure: **77 modules / 26,803 lines**; prototype verification closure:
**60 / 17,000**, including reused gates and deferred imports. This demonstrates
a smaller bounded conversion core, not equal-feature/toolchain simplification.
Sets/Filters/shared Objects, records, other capabilities/functions remain
unsupported. Review the prototype; do not replace production or widen scope.
Production converter/compiler/schema, gates/triggers and release artifacts are
unchanged. No broad corpus run occurred.

**Reproduce.** Python 3.12, PyYAML 6.0.3, jsonschema 4.25.1:

```bash
PYTHONPATH=tools python tools/test_v04_direct_conversion_prototype.py -v
PYTHONPATH=tools python tools/test_v04_direct_conversion_prototype.py --measure /tmp/direct-measure.json
```

[Details](v04-direct-conversion-prototype.json) contain CLI commands, exact
environment, source trace, native documents/programs, diagnostics and hashes.
Actual outputs: `/workspace/.onboarding/direct-prototype/frozen-cli-0/`
(six JSON, six YAML, source trace), `prototype.{json,yaml}.zip`, and
`compiled/benchmark.direct-slice.scapng` under the same workspace base.

**Terminal CI:** implementation
[`e68581c56a2539db841b0d050db874b382edbe2d`](https://github.com/vanderpol/scap-ng/commit/e68581c56a2539db841b0d050db874b382edbe2d),
**5/5 SUCCESS**: [maintained smoke](https://github.com/vanderpol/scap-ng/actions/runs/40198692298),
[current regression](https://github.com/vanderpol/scap-ng/actions/runs/40198692329),
[canonical fast](https://github.com/vanderpol/scap-ng/actions/runs/40198692284),
[documentation](https://github.com/vanderpol/scap-ng/actions/runs/40198692285),
[issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40198692290).
