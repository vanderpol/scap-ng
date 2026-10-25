| Field | Verified result |
| --- | --- |
| BASE_SHA | `284705ee6cca8faf770ec1a8936abd93c92b226d` |
| RESULT_SHA | `840242a144a48cb8f2415ebe13057b2b67335b1a` |
| IMPLEMENTED | Common Set proof, bounded integer comparison increment, reproducible validation profiling |
| SOURCE_PROVED | 81 → **87** of 291 original Rules |
| COMPILED_UNPROVED | 3 → **0** |
| BLOCKED | 207 → **204** |
| REGRESSIONS / TESTS | Zero; **3,008 tests, zero failures/errors, one unchanged skip** |
| CI | All five implementation-head checks PASS |
| PERF | Baseline 170-document public validation: 9.409 s unprofiled; 25.238 s with profiler overhead; no speedup claimed |
| NEXT | GO: audit-policy singleton-system source; NO-GO: production promotion |

# First engineering milestone: architecture acceptance

[Owner execution directive](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271).
The complete original Server 2025 input remains pinned to ZIP SHA-256
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0`.
The [machine packet](v04-architecture-acceptance.json) includes original source
node hashes/excerpts, all 87 proof outcomes/program hashes, all remaining blockers,
profile output, test counts and exact-head CI links. Earlier audit packets remain
immutable; this is an experiment coverage overlay, not an update to the packaged
883-Assessment ledger or a scanner-runtime equivalence claim.

**Set results.** SV-278192, SV-278193 and SV-278194 are now independently PROVED.
Their 14 referenced composite Objects use nested, default UNION acquisitions.
The gap was in the independent reader: common Set traversal was unnecessarily
restricted to certain collector families. The converter's Set output was unchanged.
The proof keeps operand boundaries, source family checks, nested structure and
ordered Filter positions. Tests read all **108** collection-flag combinations
from the original OVAL 5.12.3 charts, including error/incomplete/not-collected and
asymmetric relative COMPLEMENT. Operator, operand and quantifier mutants fail.
Unary identity and Filters-before-operator rules are tied to the pinned original
XSD. This proves the bounded declarative collection terms/contracts, not execution
by a scanner or arbitrary unsupported acquisition behavior.

**Generic increment.** Integer GT/GTE/LTE use existing approved 0.4 comparators.
Automatic discovery newly admits SV-278147, SV-278176 and SV-278204, all independently
source-proved and compiled. For SV-278204 the source's two Registry States retain
`value > 0` AND `value <= 30`, with original dword checks and quantifiers; no
source State authoring aliases or Boolean shortcuts are introduced. Changed
inclusive boundaries fail source comparison. GTE is additionally tested on a
clearly labeled controlled source copy; it is not an additional original Rule
claim. String/Boolean ordering and other unproved datatypes remain blocked.
All 87 admitted Assessments pass exact compiled operands; the maintained public
JSON/YAML validator, paired compiler and separate consumer regression now covers
176 documents in each format. No production converter/compiler/schema changed.

**Validation diagnosis.** Reproduced the reported ~11-second hotspot on the same
170-document baseline workload. The tracked profiler separates instrumentation
overhead from ordinary wall time. Nested `oneOf`/`anyOf` and
`unevaluatedProperties` repeatedly traverse schemas/instances; IO caching would
not address the dominant cost. No safe gate-preserving optimization was verified
in this checkpoint, so none was introduced. Schema pruning, assumed-capability
fast paths and validation bypass are rejected. The hotspot remains open;
performance/source proof/compiler/scanner/release gates remain distinct.

**Ranked queue.** Audit-policy subcategories (43 blocked Rules) are next: the
source census finds 86 Definitions, 63 Tests, 75 States and two empty Objects,
with no Variable or mixed-capability dependency. Its approved contract explicitly
omits a meaningless native singleton Object. Next are userright (39 Rules) and
WMI query (26); these are overlapping dependency upper bounds, not promised
conversion gains. Each increment must independently establish the entire closure,
negative boundaries, strict validation/compilation and maintained CI. Unresolved
Windows `all_exist`, record/cast/behavior choices and source-specific exceptions
are not normalized by this milestone.

Reproduce: run `python tools/test_v04_direct_acceptance.py -v`; use
`python tools/profile_v04_direct_validation.py AUTHORING --samples 1 --output /tmp/profile.json`
on the baseline public authoring emission; then the existing
`tools/run_current_tool_regressions.py` with its pinned Self-Assertion bindings.
See the [maintainer guide](../developer/DIRECT-V04-CONVERTER.md). No new capability
is assumed supported merely because a mapping exists.
