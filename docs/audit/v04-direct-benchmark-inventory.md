| Status | Result |
| --- | --- |
| Completed | Complete original inventory and generic automatic admission; isolated experiment |
| Verified | 291 Rules reconciled; 84 authoring-valid/compiled; 81 independently source-proved |
| Failed required CI | None; all five implementation-head checks passed |
| Known blockers | 207 blocked Rules; three compiled Registry Set cases lack independent source proof |
| Owner decisions | Review this bounded phase; authorize any subsequent work separately |

# Direct conversion: whole-Benchmark inventory and supported subset

[Owner assignment](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6400378082).
Base `e621735fde9330d82513a411dd6189ad3e607bcd`. Implementation `384e396fe4052458fc9e79de3f6e5db203bca86b`.
Original Server 2025 ZIP remains byte-identical, SHA-256
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0`;
XML SHA-256 `52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.

**Inventory and admission.** The complete source is parsed once per producer
process and indexed by component. All 291 Rules, 843 checks, 11 Profiles and
recursive OVAL dependencies are inventoried, including unsupported branches.
The artificial two-Rule limit is removed. `--inventory-only` discovers everything;
`--all-rules` automatically admits whole supported closures; repeated `--rule`
remains a strict focused interface. No Rule/Definition/Test IDs choose algorithms.
Mappings alone never establish support. Expected per-Rule failures do not hide
other Rules. Every source Rule has hashes, component/check links, capability and
construct requirements, selection, output paths or exact blockers. Unknown
capability internals remain uninterpreted; later implementation may reveal
additional obligations.

**Results.** 84 converted + 207 blocked = **291**. All 84 use only already
supported Registry/shellcommand semantics; no new family, function, normalization
or grammar acceptance was added. Shared acquisitions now get source-derived
`object_title` metadata required by the existing schema. The output is explicitly
an automated subset; manual alternatives, platform/applicability execution and
full policy metadata/scoring/remediation are accounted for as omitted. Profiles
are projected only onto admitted Rules; unsupported Rules have no dangling
Assessment links. Zero admitted Rules produce coverage only, not an empty package.

**Proof and gates.** All 84 Assessments compile and pass independent exact-program
operand checks. **81 are source-proved; three are compiled-unproved** because the
existing independent reader lacks Registry Set collection proof. Exact unresolved
obligations are retained for SV-278192, SV-278193 and SV-278194; no source equivalence
is claimed for them. Both original proofs (SV-278139/SV-278080) remain PROVED.
Source-proved coverage of this experiment is 81/291 (27.84%); converted coverage
84/291 (28.87%). This does **not** update the packaged 883-Assessment ledger.

Strict serialized JSON/YAML validation, unmodified paired compiler and separate
package consumer are exercised on focused and automatic output. The automatic
subset has 170 authoring documents. Manifest/embedded authoring schemas and exact
compiled-program operands are checked; there is no separate normative program
schema. Scanner execution, signing trust and complete Benchmark/policy equivalence
remain outside the claim.

**Tests.** Recorded baseline **2,995 → 3,003 Python tests**, zero failures/errors,
one unchanged optional skip. Eleven retained tests and eight new tests pass;
all existing mandatory test identities/gates remain intact. Public automatic
package acceptance: **170/170 JSON + 170/170 YAML**, 84 programs, 99 Tests,
one shared Object and one Variable. Three fresh CLI emissions per mode reproduce
byte-identical authoring/trace/coverage. Automatic bundle SHA-256:
`b35dffdead48550cccfe591cfd9dc6e87bce473e8747ead2533b4716bbd3370b`.

**Measurements.** Three sequential fresh CLI processes per mode; no competing
local tests; OS caches/scheduling uncontrolled. Median seconds / peak Linux RSS:

| Work | Focused two Rules | Inventory only | Automatic subset |
| --- | ---: | ---: | ---: |
| CLI wall, including emission/admission | 0.353 | 2.338 | 15.083 |
| Inventory stage | — | 1.996 | 2.130 |
| Recursive conversion stage | 0.019 | — | 0.084 |
| Admission validation stage | — | — | 11.308 |
| Peak producer RSS, MiB | 50.8 | 55.2 | 68.3 |

Separate serialized public validation: 1.230 / 23.179 seconds (focused/full);
paired compilation including preflight: **1.741 / 75.167 seconds**; independent
consumer: 0.514 / 11.045 seconds. These external gates are additional to CLI wall,
not hidden in the conversion number. Validation/compilation dominate; no matched
production workload or relative speedup is claimed.

**Maintenance.** The direct core is **946 lines/three modules**; independent audit
orchestration is separate. Engineering maintainability assessment PASS, with
explicit contracts/error paths and a tested extension exercise; no independent
human usability study is claimed.
The [developer guide](../developer/DIRECT-V04-CONVERTER.md) documents APIs, CLI,
admission/diagnostics, coverage, safe capability extension and the still-passing
comparator exercise. Detailed commands, versions, source node denominators, every proof,
blocker counts and measurements are in the machine evidence. No production,
schema, release gate, historical test partition or generated corpus package changed.

**Recommendation.** This phase demonstrates complete discovery and automatic
bounded conversion, not full-Benchmark support or production replacement. Potential next capability priorities are audit-policy subcategories (43 Rules),
userright (39) and WMI query (26); these are overlapping requirements, not
guaranteed conversion gains. There are also 34 Registry-dependent and 18
shellcommand-dependent blocked Rules, including eight with `all_exist` blockers.
Owner authorization is needed for any subsequent capability/construct work; investigate the three Set proof gaps separately. No following phase
has started and no new normative decision was made.

[Complete machine coverage](v04-direct-benchmark-coverage.json) ·
[All-Rule human coverage](v04-direct-benchmark-coverage.md) ·
[Machine engineering/proof/performance evidence](v04-direct-benchmark-inventory.json).
The latter records 1,484 indexed OVAL nodes and 1,428 unique nodes referenced by
Rule checks, with exact per-kind denominators, source revision/URL and individual
proof obligations. Regenerate with the documented public audit command; generated
native packages remain outside Git. Original source files are preserved.

**Publication/CI.** [Implementation commit](https://github.com/vanderpol/scap-ng/commit/384e396fe4052458fc9e79de3f6e5db203bca86b)
was normally pushed to `main` with #251 linkage. Exact-head checks all PASS:
[rebaseline-smoke](https://github.com/vanderpol/scap-ng/actions/runs/40215463838),
[canonical fast](https://github.com/vanderpol/scap-ng/actions/runs/40215463901),
[current contracts](https://github.com/vanderpol/scap-ng/actions/runs/40215463834),
[documentation](https://github.com/vanderpol/scap-ng/actions/runs/40215463785),
[issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40215463811).
Report-only publication checks are separate. If issue commenting is Forbidden,
this committed report is the owner-authorized handoff; no retry loop is required.
