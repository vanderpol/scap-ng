# One explicit no-existence shorthand (0.4 research)

**Research only.** Do not alter frozen 0.3, OVAL truth/error semantics, or the informal [Discussion #213](https://github.com/vanderpol/scap-ng/discussions/213).

## Proposed author wording

**No matching Items may exist.**

```yaml
# Research-only shorthand at Test scope
require: none_exist
```

This **does not** say that one Item must match. It is an absence-only Test: no State requirement is present, and the Test is only concerned with collected Item existence.

## What the released six STIGs actually do

The pinned 0.3 corpus has **71 Tests** with `existence: none`, and **all 71 contain no States**:

| Original pair | Tests | Real examples |
| --- | ---: | --- |
| `none` + `all` | **68** | Absence-only Tests in the published six-STIG corpus |
| `none` + `one` | **2** | Windows 11 SV-257592: two PortProxy checks |
| `none` + `one_or_more` | **1** | Windows Server 2025 SV-278016: FTP Server role absence |
| **Total** | **71** | All are State-free |

Because **there are no State evaluations to combine**, `Test.match` cannot change the result of these Tests. The pinned OVAL-aligned evaluator checks existence and short-circuits when `has_state=false`; tests confirmed invariant outcomes for the four match choices across complete, incomplete, does-not-exist, not-collected, error and not-applicable collection flags, multiple existing/missing/errored Item cardinalities.

A strictly defined **source-authoring** alias can therefore lower to canonical 0.3:

```yaml
# after compiler expansion; canonical NG 0.3 remains explicit
existence: none
match: all
# no states
```

For **68 Tests**, this is *structurally identical* to the original after expansion. For the other **three**, it changes only an OVAL-inert `match` attribute; this is *semantic*, not structural identity. A content migration report must record those exact three original values so provenance is preserved. The prototype rejects any Test with an explicit `states` key, even an empty one; expanding to canonical NG is allowed only after a State-free guard.

## Separate State-field scope

Another **21 State-field predicates** have `existence: none`, `match: all`, often involving `stdout_line`. These represent **absence of the relevant field instances**, **not absence of the collected Item itself**.

The identical abbreviation `require: none_exist` could be used **at the State-field location**, because all 21 pairs compile back to exactly `none/all`. But these predicates **still have a State**, and their intended checks (such as forbidden command output versus no output field at all) should be inspected against source OVAL before a combined consumer-facing example is finalized. Do not treat their `match` as automatically redundant under the Test-level proof.

## Verification

- [Completed six-STIG proof](https://github.com/vanderpol/scap-ng/actions/runs/38712543324): **71/71** no-State Test aliases accepted, **21/21** State-field exact aliases, and **3** Test-only ignored-match normalizations isolated.
- [Read-only rare-combination audit](https://github.com/vanderpol/scap-ng/actions/runs/38712170912) with original Test names and file paths.
- [Prototype](../../../../tools/research_04_none_exist_alias.py) and [eight result-model and refusal tests](../../../../tools/test_research_04_none_exist_alias.py).

This verifies the **repo's OVAL-aligned reference result model** and parsed 0.3 structures. It does **not** independently prove every historical OVAL vendor implementation's behavior or demonstrate live-scanner differential conformance.

## Suggested Board disposition

This is a **particularly strong** macro candidate: the author need only express that no Items may exist, not pick an otherwise unused check aggregator. Prefer an absence-only `require: none_exist` at Test scope with explicit no-State restriction. Leave the rest of the 0.3 combinatorial vocabulary available and prohibit hidden assumptions in converted canonical output. Consider State-field alias separately after source-level semantic review.
