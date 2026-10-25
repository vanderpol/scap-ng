STATUS: SUCCESS
BASE_SHA: e1adacb5a5998dc9810e1f4250164eb6d0b96291
RESULT_SHA: 966a734729595cdaf210bf5b56a6268a662d0d1d
SOURCE_SHA256: 2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0
SCOPE: two-Rule Server 2025 experiment; fresh conversion code
VALIDATION: PASS, six JSON and six YAML documents
COMPILE: PASS, paired compilation and independent consumer
SOURCE_PARITY: PROVED, SV-278139 and SV-278080; bounded typed-term proof
PERFORMANCE: 235 ms standalone median; production speedup unproven
KNOWN_LIMITATIONS: bounded capabilities/policy wrapper; no scanner or trust acceptance
NEXT_OWNER_DECISION: review this experiment before authorizing another phase

# Direct-converter experiment: bounded success

[Owner assignment](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6397760243).
Fresh conversion code imports neither the preceding prototype nor production/0.3
conversion logic. Existing mappings, public gates and independent proof readers
remain external dependencies. Production behavior and release gates are unchanged.

**Source fidelity.** Server 2025 **SV-278139** (nested Registry acquisition,
local/constant Variables, regex capture, concatenation and shellcommand) and
**SV-278080** (simple Registry, selected by original structure) are **PROVED** by
independent original/native typed-term comparison and exact compiled operands.
One XML parse creates six component indexes. All **11 Profiles** are projected
onto two Rules; **289 Rules are explicitly omitted**. This is a labeled miniature
Benchmark, not whole-policy equivalence. Unsupported check selectors, competing
non-OVAL choices and Profile refinements now fail explicitly; named manual OCIL
choices are traced as omitted. Rule renaming still works. Set/Filter tests use an
actual pinned Object subtree plus controlled compositions, **not another Rule
proof**. The 24/883 coverage ledger is unchanged.

**Validation.** Eleven new tests pass, including altered Variables/selectors,
quantifiers, broken/scoped references, shared Objects, ordered Set Filters,
legacy grammar, absence, cycles and rejected casts/`all_exist`. Mandatory suite:
**2,984 → 2,995 tests; zero failures/errors; one identical existing optional skip**.
Clean Python 3.12 environment: only `PyYAML==6.0.3 jsonschema==4.25.1`; all eleven
pass, including the documented comparator-extension example. Public validation:
**6/6 JSON through its API; 6/6 YAML through its CLI** (the CLI discovers YAML
only). Unmodified paired compiler and independent package consumer pass:
**6 documents, 2 programs, 2 Tests, 1 Variable**. Manifest/embedded authoring
schemas and compiled operands pass; no separate normative compiled-program
schema exists, and none was invented. Eighteen bundle builds and three CLI
emissions reproduce; bundle SHA-256
`fecfd8ecea81f7cbb3b9007d1ed04cf2a84acd5deee6b28529689a2ed61d90b2`.

**Measurements.** Three fresh processes, each one cold/five warm calls; source
rebuilt every call; then three standalone CLI runs. Stage medians, milliseconds:

| Stage | Cold | Warm |
| --- | ---: | ---: |
| Integrity, parse/index/hash | 147 | 188 |
| Conversion, selection/trace | 16 | 47 |
| Public validation | 451 | 308 |
| Compiler including preflight | 344 | 254 |

Standalone CLI median **235 ms**, peak **41.8 MiB**; combined verification peak
**87.1 MiB**. Source parses once per invocation; shared-gate XSD parses eight
cold/zero warm. Hotspots include Profile projection and trace hashing. OS caches
and scheduling are uncontrolled; warm conversion was slower in these samples.
Legacy whole-Benchmark operations have unequal scope: **no production speedup
or equal-feature complexity ratio is claimed**. The unchanged public core rejects
these Definitions (`Variable/shared Object graph not supported`; `non-direct
criterion`), so it supplies no successful equivalent timing workload.

**Decision / five answers.** (1) Direct conversion works correctly for these two
source-backed cases. (2) The fresh **605-line, two-module core** is substantially
smaller than the measured legacy reference closure (77 modules/26,803 lines,
including shared/deferred code), with much narrower functionality. (3) Absolute
performance is measured; relative production efficiency remains unproven.
(4) Human-maintainability engineering assessment **PASS**: explicit contracts,
small functions, tracked architecture/extension guide, clean installation and a
working small-change exercise; no independent human usability study was done.
(5) **GO for owner review of further bounded architecture development;
NO-GO for production replacement.** No next phase has started.

Unsupported: other capabilities/functions, records, acquisition behaviors,
cross-datatype casts, Profile inheritance/refinement, platform/CPE/manual
execution and full policy metadata/scoring/remediation. Windows `all_exist` and
Oracle decisions remain unchanged. Signing trust and scanner acceptance are
separate gates; no scanner-runtime equivalence is claimed.

[Developer guide and exact commands](../developer/DIRECT-V04-CONVERTER.md).
[Machine evidence](v04-direct-converter-spike.json) contains original dependency
IDs/hashes, XML SHA-256
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`,
source revision, emitted content, compiled operands, negative diagnostics,
versions, per-sample measurements, code hashes and CI links. Reproduce with
`PYTHONPATH=tools python tools/test_v04_direct_converter.py --measure /tmp/new-direct-spike-evidence`;
mandatory command: `python tools/run_current_tool_regressions.py` with the existing
workflow's pinned Self-Assertion bindings and XSD link. No historical tests
were removed, skipped or demoted.

**Publication.** Implementation commits
[`648ff7435`](https://github.com/vanderpol/scap-ng/commit/648ff743592782efd3ece2444e680de5da855e4f)
and [`966a73472`](https://github.com/vanderpol/scap-ng/commit/966a734729595cdaf210bf5b56a6268a662d0d1d),
normal pushes to `main`, referencing #251. Exact implementation-head CI:
[rebaseline-smoke](https://github.com/vanderpol/scap-ng/actions/runs/40210080579),
[canonical fast](https://github.com/vanderpol/scap-ng/actions/runs/40210080578),
[current contracts](https://github.com/vanderpol/scap-ng/actions/runs/40210080611),
[documentation](https://github.com/vanderpol/scap-ng/actions/runs/40210080610),
[issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40210080583).
**All five checks passed** at this exact implementation head (including rebaseline).
Report-only publication checks are separate from these implementation checks.
Per the owner’s [handoff rule](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6397830903),
this committed report plus CI is the primary handoff if the single secondary issue
comment is denied; no permission retry loop is required.
