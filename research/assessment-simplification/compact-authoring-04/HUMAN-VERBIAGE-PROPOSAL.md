# SCAP-NG 0.4 research: one human-readable Assessment grammar

**Proposal for design review only — not an approved 0.4 specification.** This is intended as **the single normative Assessment authoring representation**, *not* an optional compact language layered over a different published authoring language. Legacy SCAP 1.4 and NG 0.3 content would be migrated by a converter. The scanner-visible semantics, collection and results contracts must not change.

**Source-backed proof:** [three-STIG one-grammar CI](https://github.com/vanderpol/scap-ng/actions/runs/38737558392) · [OVAL six-valued semantic checks](https://github.com/vanderpol/scap-ng/actions/runs/38734873333) · [prior Windows record source proof](https://github.com/vanderpol/scap-ng/actions/runs/38733493967).

## The language direction

1. **Fields are keys, not `field:` wrappers.** Preserve State arrays for repeated fields and logical composition.
2. **Every observation/requirement explicitly says what qualifies.** A required `require:` uses *one documented controlled-vocabulary string* at the Test, State-field, record, and nested record-field scope. One grammar, no alternative `existence:/match:` authoring form and no hidden defaults.
3. **Comparison operators are keys everywhere.** `equals: 0`, `matches_regex: '...'`, `not_equal: 0`, `bitwise_and: 4096`, `version_greater_than: '...'`; all native 0.3 OVAL comparison operations remain expressible and typed, not just simple scalar equals/regex. Exactly one comparison operation per scalar predicate. Direct arrays, Variables and Inputs remain valid comparator operands and preserve the separate `value_match:`.
4. **Records remain structured.** A record has its own `require`; `record.fields.<name>` has a separate `require` and comparator. Never flatten record fields into ordinary scalar States: absent record subfields can produce **error**, not absence-success.
5. **Object Set filters use the same named predicates.** `include`/`exclude` remain explicit actions, represented as filter verbs with nested field-key predicates; Object Set membership and error semantics are unchanged.
6. **Collection, evaluation, provenance and disclosure remain explicit.** This proposal does not remove `evaluate`, change collection or filter results, replace manual alternatives, simplify `reported_elements`, or alter native capabilities. Collector parameter matching and expected-value matching are separate from Test/State `require`.

### Real examples, abbreviated only for presentation

**RHEL 9 /home nosuid** (SV-257851):

```yaml
tests:
  home-nosuid:
    capability: linux.partition
    object:
      capability: linux.partition
      select:
        mount_point:
          matches_regex: '.*\\/home'
    states:
      - mount_options:
          equals: nosuid
          require: at_least_one_exists_and_some_match
    require: at_least_one_exists_and_all_match
evaluate:
  test: home-nosuid
```

**RHEL 9, only one config entry and its value must match** (relevant pattern in SV-258084):

```yaml
states:
  - subexpression:
      equals: 0
      require: at_least_one_exists_and_all_match
require: only_one_exists_and_matches
```

A State-free Test requiring one Item simply says `require: only_one_exists`. This difference was observed in the actual source: two RHEL 9 State-free Tests and three with States use the original `one/all` pair. Do **not** shorten it to `only_one_matches`: that means multiple Items could exist.

**RHEL 9, forbid a promiscuous network flag** (SV-257941):

```yaml
states:
  - flag:
      matches_regex: '(^|\\s)PROMISC(\\s|$)'
      require: at_least_one_exists_and_none_match
```

No scalar regex is inverted. The original State field's `existence: one_or_more` and `match: none` are preserved exactly; **`none_match` is not `none_exist`**.

**Windows 11 native record**, antivirus `productstate` (SV-253264):

```yaml
states:
  - value:
      record:
        require: at_least_one_exists_and_some_match
        fields:
          productstate:
            bitwise_and: 4096
            require: at_least_one_exists_and_all_match
```

The first `value` is the observed field *name*, not an expected literal. The record-level requirement and `productstate` requirement are separate. Do not flatten to `value: {bitwise_and: 4096}`.

**Multiple Object values still work** (RHEL 9 SV-257923 illustrates the selector; surrounding Test omitted):

```yaml
select:
  directory:
    equals: [/lib, /lib64, /usr/lib, /usr/lib64]
    datatype: string
    value_match: one
```

`value_match: one` is a distinct **expected-value comparison quantifier**. It cannot be deduced from `require` on a Test or State. The compiler must enforce it on arrays and Variable/Input comparisons.

### Object Set filters and WMI collector field selection

**RHEL 9 recursive file collection** uses Set filters. The one-grammar representation retains the filter action instead of silently changing it:

```yaml
filters:
  - exclude:
      mode:
        greater_than: 493
        require: at_least_one_exists_and_all_match
```

(The values illustrate the structure; they are not a verbatim transcription of a particular Rule.) The source `action: exclude` and typed field predicate lower exactly back to the original. Real RHEL 9 contains **62** such filter entries; Windows 11 has **43**, and Server 2025 has **49**, all structurally reconstructed.

**Windows WMI/cmdlet collection** also contains a different kind of matching requirement at `object.collect.select.fields` or `object.collect.parameters.fields`. For example, the real TPM source includes the collection property names `tpmpresent,tpmready,tpmenabled`. The source is `match: all` **without any `existence` field**. The candidate spelling is:

```yaml
collect:
  select:
    fields:
      property:
        equals: 'tpmpresent,tpmready,tpmenabled'
        selection_match: all
```

`selection_match` is **not** a shorthand for Item/State `require`, and no existence setting is invented. All **31** Windows 11 and **28** Server 2025 occurrences of this collector-only match field lower back exactly. Keep `selection_match`, `value_match`, and `require` distinct in the full capability schema and glossary.

## Controlled English: initial requirement vocabulary

The human-facing grammar uses precisely **one** `require` string. The full *research-only* matrix supports all **20** original `existence × match` pairs rather than inventing a second "longhand" dialect for edge cases. A JSON Schema must enumerate permitted names for each capability and position; no unspecified synonyms or defaults are accepted.

| Situation | Proposed `require` | Precise source meaning |
| --- | --- | --- |
| No collected Items, Test without States | `none_exist` | Test `none/all` |
| No observed instances of a field | `none_exist` | Field `none/all` |
| At least one exists and all match | `at_least_one_exists_and_all_match` | `one_or_more/all` |
| At least one exists and at least one matches | `at_least_one_exists_and_some_match` | `one_or_more/one_or_more` |
| All must exist and all match | `all_exist_and_all_match` | `all/all` |
| May be absent; otherwise all match | `may_be_absent_and_all_match` | `optional/all` |
| Only one exists (no State) | `only_one_exists` | `one/all`; match is inoperative |
| Only one exists and matches | `only_one_exists_and_matches` | `one/all`; Test has State(s) |
| At least one exists and none matches | `at_least_one_exists_and_none_match` | `one_or_more/none` |
| All must exist and none matches | `all_exist_and_none_match` | `all/none` |
| May be absent and none matches | `may_be_absent_and_none_match` | `optional/none` |
| At least one exists and exactly one matches | `at_least_one_exists_and_only_one_matches` | `one_or_more/one` |
| Exactly one exists and exactly one matches | `only_one_exists_and_only_one_matches` | `one/one` |
| May be absent; some match when present | `may_be_absent_and_some_match` | `optional/one_or_more` |

The remaining theoretical pair combinations have generated unambiguous labels for lossless source migration, but some are linguistically awkward or potentially contradictory (e.g., no Items exist yet one must match). **The Board should not rubber-stamp twenty phrases as intuitive.** Resolve semantic validity and publishing policy before ratification. A schema may reject logically impossible State-bearing combinations while the converter explicitly reports an unsupported source rather than quietly changing meaning.

### Presence-only Tests

A Test with no States compares no values. The natural requirement is **only its existence condition**:

```yaml
require: only_one_exists
# or
require: none_exist
# or
require: at_least_one_exists
```

Prior Windows 11 and Server 2025 source contains `none/one`, `none/one_or_more` and `one_or_more/one_or_more` Tests without States. The reference OVAL result model showed these checks do not consult the `match` aggregator in **480** investigated combinations of collection status, count and check selection. The converter can normalize their ignored match to `all`, with a provenance report. A live-scanner differential is still needed before calling that behavior vendor-proven.

### One troublesome source outlier is preserved, not rewritten

RHEL 9 boot-loader password SV-257789 has a Test using `none/all` **with a State**. Our prototype does **not delete or replace the State**. It emits `require: none_exist` and retains the State untouched, so compiled content is an **exact parsed structural match** to 0.3. We should separately determine whether that State is redundant under real OVAL scanner behavior, especially with zero Items and incomplete/error flags. Until then, do not silently remove it and do not change its evaluator method merely for aesthetic uniformity.

## What the measured prototype proves

The one-grammar prototype compiled every existing automated Assessment referenced by the three benchmarks, including required shared Assessments, plus applicability Assessments:

| Verified from published 0.3 | RHEL 9 | Windows 11 | Server 2025 |
| --- | ---: | ---: | ---: |
| Total Rules | 445 | 257 | 291 |
| Automated by default | **417** | **245** | **259** |
| Automated/applicability Assessment files compiled | **423** | **251** | **268** |
| Exact parsed 0.3 reconstruction | **423** | **245** | **262** |
| Files containing only State-free, model-equivalent `match` normalization | **0** | **6** | **6** |
| State and Object Set filter field-name predicates transformed | **636** | **623** | **883** |
| Object Set filter actions preserved | **62** | **43** | **49** |
| WMI/cmdlet collector `selection_match` (no existence pair) | **0** | **31** | **28** |
| Nested record wrappers preserved | **0** | **36** | **59** |
| Native comparison operations transformed | **2,387** | **1,061** | **1,300** |

**921/921** default-automated Rules are representable within this single candidate syntax. This is *syntactic/structural completeness*, **not** proof that every one is scan-capable or simpler to author, and **not** equivalence of live vendor results. It required a complete controlled vocabulary, including rare logical cases. Of the **942** Assessment documents, **930** reconstructed exactly and **12** had State-free matching normalization supported by the reference truth model. These twelve are *documents*, not numbers of normalized Test occurrences.

**No newly introduced shell-command or manual fallback** was needed to represent any tested Test, State, record or selector. Pre-existing `independent.shellcommand` content remains what it was; this work does not magically replace it with native checks.

## Proof of semantic rewrite versus literal source encoding

The [OVAL result-table study](https://github.com/vanderpol/scap-ng/actions/runs/38734873333) verified:

- **1,554** nonempty six-valued combinations: aggregating *none satisfy P* equals aggregating *all satisfy exact complement of P* at the **aggregation level**. Another **2,064** Test/collection contexts preserved that identity, **conditional on actual comparison outcomes being exact complements**. A regex or complex native operator is **not automatically invertible**; there is no generic `not_pattern_match` in 0.3.
- **520** cases: when `only_one_exists` is the existence requirement, `match: all` and `match: one` aggregate the same at a Test, because the existence gate prevents multiple existing Items; this is a candidate semantic normalization, subject to live-scanner parity.
- **480** State-free-Test checks: `match` values are inoperative in the reference evaluator.
- Counterexamples show **only one Item exists** is not the same as **one Item matches**, **no Items exist** is not the same as **none matches**, and record missing subfields produce **error**, not success. Naive Boolean rewrites lose `error` and `unknown` propagation.

That means there is **no justification for rewriting an automated registry/WMI/text check into shell commands**, or for converting it to manual, simply to fit the language. Prefer **lossless vocabulary/grammar coverage first**; attempt semantic source rewrites only when a complete truth/differential proof supports them.

## Remaining approval gates

1. Create a **complete 0.4 JSON Schema** using the selected single grammar, native capability-specific field names and operation types, with forbidden/invalid fixtures (especially record nesting, fields literally called `value`, array `value_match`, absence, and contradictory requirements).
2. Compare old OVAL 5.12.3 / 0.3 / candidate 0.4 outcomes against a conformant evaluator on representative true, false, error, unknown, not applicable, incomplete and zero-item cases. Treat OpenSCAP as useful but not independently authoritative.
3. Investigate the rare `none_exist` Test with States; preserve its exact source semantics until adjudicated.
4. Have novice content authors review names, especially `optional`, negative matching, `one` versus `only one matches`, and the complete 20-pair migration inventory. Make **one** spelling normative, with concise field-key and record examples.
5. Extend the structural proof to the remaining non-macOS full SCAP 1.4 source corpus and handle known deprecated/SQL errors explicitly. No commitment to unsupported tests, hidden defaults or shell fallbacks.

**Bottom line:** One authoring grammar appears feasible for RHEL 9, Windows 11 and Server 2025, including their unusual pairs and Windows records. We do **not** need a second authoring dialect or wholesale semantic test-method rewrites to attain representation coverage. This remains a proposal until the validator and runtime semantic tests are complete.
