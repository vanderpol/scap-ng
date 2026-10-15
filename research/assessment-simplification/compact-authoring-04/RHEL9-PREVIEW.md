# RHEL 9 — full 445-Rule compact authoring preview

**Status: research only.** This is *not* adopted SCAP-NG 0.4 syntax or a scanner bundle. All original Rule, Benchmark, manual Assessment and applicability semantics are retained. No Board decision implied.

**[Download the research authoring ZIP and measured Rule report](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-rhel9-compact-authoring-research)** · [CI structural-equivalence proof](https://github.com/vanderpol/scap-ng/actions/runs/38729659094) · [Source and compiler](https://github.com/vanderpol/scap-ng/blob/main/tools/research_04_rhel9_compact_preview.py)

The source is the **immutable published six-STIG 0.3 authoring ZIP**. The preview includes the complete RHEL 9 Benchmark and its **445 Rules**, every unchanged local manual Assessment, local automated/applicability Assessments, and **only those shared Assessments referenced by RHEL 9 Rules** (not the entire six-STIG shared catalog). Each changed Assessment opts into an explicit `authoring_format: scap-ng-compact-research/0.4`. The experimental compiler lowers it back to the **identical parsed published 0.3 Assessment**; all Rule, Benchmark, and manual bytes are unchanged.

**Follow-up evidence:** [Five-preset sensitivity study](PRESET-SENSITIVITY.md) found **398/417** automated-by-default Rules can express every Test/State existence/match pair with five explicit presets, versus **269/417** under the original three. This was an additional source-equivalence experiment; the downloadable ZIP below **still uses the original three proposed presets** and has not been silently changed.

## Correct default-assessment accounting

| RHEL 9 Rule selection | Rule count |
| --- | ---: |
| Total Rules | **445** |
| Default automated | **417 (93.7%)** |
| Default manual | **28 (6.3%)** |
| Manual alternative available via tailoring | **445 (100%)** |
| Both automated and manual alternatives | **417** |

**Important:** 444 local manual Assessment files exist because the content supplies universal manual fallbacks. That does **not** mean 444 Rules are manual by default. The 50 local automated files alone also undercount automation: most automated Rules reference Assessments under `authoring/shared/`. The report resolves Assessment IDs from each Rule rather than counting files as default choices.

## What happens to the 417 default-automated Rules?

| Research result | Rules | Meaning |
| --- | ---: | --- |
| All quantifiers use proposed presets | **269** | No explicit Test/field `existence` + `match` pairs left |
| At least one quantifier pair needs explicit longhand | **148** | The exact existing pair is preserved |
| At least one comparison is not eligible for scalar equals/regex aliases | **205** | More complex operation or array/Variable/typed comparison remains explicit |
| No longhand pairs **and** no longhand comparisons | **139** | These areas can use the compact research syntax throughout |
| Above 139 **and** single-Test `evaluate` | **113** | Still may have non-comparison complexity elsewhere |
| Complex / multi-Test `evaluate` | **115** | Evaluation trees are preserved, never collapsed |

These categories overlap. **148 does not mean 148 Rules become manual**, and 139 does not mean an entire Assessment contains no longhand YAML. The exact quantifier syntax selected for this research is limited to three names: `at_least_one_all_match`, `at_least_one_some_match`, `none_exist` (State-free Test only with an exact `none/all` source pair). The original varied pairs and complex evaluation are not assumed away.

## Structural proof across all selected Assessments

The program compiled every transformed document back to its original parsed 0.3 source:

| Independent scope | Count |
| --- | ---: |
| Automated/applicability Assessment files round-tripped | **423 / 423** |
| Named Tests in those Assessments | **658** |
| Field predicates represented by their field-name keys | **574 / 574** |
| Test-level quantifier pairs shortened | **439** |
| Test-level quantifier pairs retained explicit | **219** |
| Field-level quantifier pairs shortened | **562** |
| Field-level quantifier pairs retained explicit | **12** |
| Scalar selector comparison aliases | **928** |
| Scalar State comparison aliases | **520** |

A record of **every** Rule, with remaining longhand counts and the reason, lives inside the downloadable ZIP as `research/RULE-CLASSIFICATION.csv`; the full counts, including original pair frequencies, are in `research/REPORT.json`. The ZIP also contains the complete actual compact authoring tree and before/after source excerpts.

## An actual RHEL 9 check: SV-257777

The vendor-supported release check tests **four possible RHEL 9 minor versions** using four comparisons against the same observed `subexpression` field. Its native `states_match: any` is unchanged.

**Existing 0.3 canonical State representation (excerpt)**

```yaml
states:
  - field: subexpression
    value: 7
    operation: equals
    existence: one_or_more
    match: all
  - field: subexpression
    value: 8
    operation: equals
    existence: one_or_more
    match: all
  - field: subexpression
    value: 9
    operation: equals
    existence: one_or_more
    match: all
  - field: subexpression
    value: 10
    operation: equals
    existence: one_or_more
    match: all
states_match: any
existence: one_or_more
match: all
```

**Proposed 0.4 research authoring State representation (excerpt)**

```yaml
states:
  - subexpression:
      equals: 7
      require: at_least_one_all_match
  - subexpression:
      equals: 8
      require: at_least_one_all_match
  - subexpression:
      equals: 9
      require: at_least_one_all_match
  - subexpression:
      equals: 10
      require: at_least_one_all_match
states_match: any
require: at_least_one_all_match
```

Each list entry remains separate. We intentionally **did not** convert `states` to a YAML mapping with repeated `subexpression` keys, which could silently overwrite comparisons.

### Static-Variable arrays do not compete with these presets

Real RHEL 9 Rule **SV-257923** uses four candidate directories as a single source Object selector value array. The array, its explicit datatype, and `value_match` remain exactly as published:

```yaml
select:
  directory:
    value: [/lib, /lib64, /usr/lib, /usr/lib64]
    operation: equals
    datatype: string
    value_match: one
```

The source-only shorthand changes the spelling of a **State's** field identifier and optionally an Item/field `existence` + `match` pair. `value_match`, which decides comparisons against multiple **expected values**, is an **independent third cardinality** and cannot be silently merged. A separate [composition test](https://github.com/vanderpol/scap-ng/actions/runs/38727447660) verifies a full round-trip containing both Object and State arrays, short field identifiers and Test/field presets.

## What this research does **not** prove

- No live-scanner parity test or scanner-package binary-equivalence claim.
- No JSON Schema enabling new compact syntax yet; a versioned, capability-aware authoring schema and invalid-shape fixtures are a remaining prerequisite.
- No arbitrary coercion of array/Variable values to scalar `equals`.
- No simplification of the 115 complex/multi-Test evaluate structures; those require their own independent design decision.
- No normative 0.4 approval, replacement of the canonical 0.3 syntax, or change to Board Discussion #213.

**Bottom line:** The preview demonstrates that field-name-as-key and carefully scoped matching presets can compose with existing features without changing parsed content. Deciding whether this becomes a **single new canonical 0.4 grammar** or a **separate, discoverable authoring-only grammar** remains the design decision for the Board.
