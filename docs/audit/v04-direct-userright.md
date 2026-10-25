# Direct Windows user-rights source proof — 2026-10-25

Continued from `a2ce5fd94641942752aa87fba5ef0d84e15e69fc` under
[#251 engineering ownership](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271).
The fetch found no newer commits. Original Windows Server 2025 ZIP/XML bytes and
approved 0.4.0 schema semantics remain unchanged.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `a2ce5fd94641942752aa87fba5ef0d84e15e69fc` |
| RESULT_SHA | `c80f84c0a46ca49ad651fa5345da05819a10aaab` |
| IMPLEMENTED | Capability-driven user-rights acquisition, fields, arrays, Filters and Sets |
| CANDIDATES | **39** original Rule dependency closures; **34** fully supported, **5** blocked by WMI records |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **183 / 0 / 108** of 291 original Rules |
| AUTHORING | 183 Assessments / 227 Tests; 147 inline Test Objects, 9 shared references to 2 named Objects, 71 intentional no-Object Tests, 120 compact Registry Objects; deprecated grammar zero |
| TESTS / CI | **3,032 tests**, zero failures/errors, one unchanged skip; **all five implementation-head workflows PASS** |
| NEXT | Independent WMI record conversion/proof to unblock complete mixed closures |

**Implementation and proof.** The producer adds the versioned capability to its
supported catalog and reuses its generic recursive dependency visitor. Enum
acquisitions require known values and supported equality; computed enum membership
stays blocked. The independent reader obtains field/enum boundaries from original
OVAL XSD, not the producer's mapping. It independently traverses user-right
selectors, Variable arrays, ordered Filters, nested Sets, trustee comparisons,
cardinalities and Boolean logic. The source graphs contain 79 Definitions,
53 Tests, 34 Objects, 18 States and one Variable; some Objects/States are WMI.
No Rule-ID implementation switches or partial Rule substitutes were added.

Six focused regressions cover all 34 original conversions and exact compiled
operands; all 39 candidates; original constant-Variable/Filter/absence semantics;
source-backed controlled Sets and legitimate shared acquisition; enum/field/cycle
rejections; and quantifier, Filter, conjunction, field-absence and Item-absence
mutants. The original seven-use legal-notice identity test still asserts its
unchanged ID/title/references, independently of which newly supported Assessment
happens to be the first shared example.

**Source concern preserved.** Original SV-278030 uses 45 distinct user-right
constants with no `var_check`, an include Filter matching present empty
`trustee_name` plus `trustee_sid` beginning `S-`, and `check_existence="none_exist"`.
OVAL's EntityAttributeGroup explicitly defaults omitted `var_check` to `all`.
The native selector therefore retains **`value_match: every`**. A scalar right
cannot equal all 45 distinct rights under complete evidence; this is a concern
about the original check's apparent intent, not permission to change its meaning.
Changing the quantifier to `one_or_more` fails independent proof. No source-specific
repair, fabricated Item, confirmed-absence substitution for empty trustee names,
or error/incomplete/unknown normalization was introduced.

**Five complete closures remain blocked:** SV-278184, SV-278185, SV-278187,
SV-278188 and SV-278249 require `wmi57` acquisition and record predicates.
Source IDs, original dependency hashes and exact blockers belong in the machine
packet. A supported user-rights branch is never emitted alone as the Assessment
for one of these Rules. WMI is the next bounded capability/construct milestone;
further `all_exist` normalization remains outside this implementation.

**Reproduce.** Use `PYTHONPATH=tools python tools/test_v04_direct_userright.py -v`.
Regenerate actual examples with
`PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --capability windows.userright --output /tmp/direct-userright-examples`.
The [developer guide](../developer/DIRECT-V04-CONVERTER.md) documents public
converter/validator/compiler/consumer commands, source pins and extension rules.
No scanner parity, complete Benchmark policy equivalence, six-STIG coverage,
signing/trust or release readiness is claimed. The earlier examples remain pinned
to their original converter commits.

The public paired gates validate **368 JSON and 368 YAML documents**, compile
183 programs and pass the separate package consumer. All **149** pre-existing
program hashes remain unchanged. The [machine packet](v04-direct-userright.json)
contains the 34 individual original-source proofs and every remaining blocker.

[Actual YAML/JSON examples](../examples/direct-userright/README.md) include the original nonempty Filter, constant Variable and named shared acquisition; source pins and converter SHA are in their manifest. Exact implementation CI: [rebaseline](https://github.com/vanderpol/scap-ng/actions/runs/40241776187), [canonical](https://github.com/vanderpol/scap-ng/actions/runs/40241776293), [current regression](https://github.com/vanderpol/scap-ng/actions/runs/40241776411), [documentation](https://github.com/vanderpol/scap-ng/actions/runs/40241776297), [issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40241776268).

Issue commenting failed exactly: `Post "https://api.github.com/graphql": Forbidden`. One attempt was made; this committed report is the authorized fallback.
