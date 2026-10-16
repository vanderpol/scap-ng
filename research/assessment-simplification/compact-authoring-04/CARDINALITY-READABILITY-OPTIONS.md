# 0.4 research — make Item and field requirements understandable

**Status: proposal for author review, NOT adopted 0.4 syntax.** Source-backed context: [RHEL 9 `/home` `nosuid` example](ASSESSMENT-REVIEW-OVERVIEW.md#three-ng-examples-from-the-actual-six-stig-r3-content) and [Discussion #213's Slang feedback](../slang-feedback-04/README.md). Before freezing 0.4, test whether the language itself can express this check in ordinary words, rather than relying on explanatory prose.

## The actual requirement, without OVAL terminology

> **Find one or more partitions selected by the Object. Every selected partition must have at least one mount option equal to `nosuid`.** Other mount options (such as `rw` and `nodev`) are allowed.

| Selected partition | Its observed `mount_options` | Field expectation | Whole Test |
| --- | --- | --- | --- |
| `/home` | `[rw, nosuid, nodev]` | Pass: `nosuid` occurs | Pass if this is the only selected partition |
| `/home` | `[rw, nodev]` | Fail: no `nosuid` | Fail |
| `/home` and `/var/home` | first contains `nosuid`, second does not | First pass, second fail | **Fail**: not all selected partitions pass |
| None | no selected Items | No field check | **Fail**: at least one Item must exist |

Incomplete and error collections are **not** automatically false (or true); OVAL's six-result reference semantics must be preserved. The source Object currently selects `mount_point` by regex `.*\\/home`; do not tighten it to exact `/home` simply for better readability.

## A. Current 0.4 research preview: long fused names

```yaml
      states:
      - mount_options:
          equals: nosuid
          require: at_least_one_exists_and_some_match
      collected_items_require: at_least_one_exists_and_all_match
```

**Strength:** one field per scope; every combined existence/matching pair is explicit. **Problem:** author must decode 20 controlled phrases and remember *which population* each phrase describes. The same word `match` refers to distinct Item and field scopes.

## B. Candidate to test: short, structured requirements with two explicit axes

```yaml
      states:
      - mount_options:
          equals: nosuid
          require: {exists: at_least_one, matches: some}
      collected_items_require: {exists: at_least_one, matches: all}
```

**How to read:** “Some **values** of `mount_options` equal `nosuid`. All selected **Items** must have a matching State. Both populations must be nonempty.”

- `exists` and `matches` are **independent axes**. They replace *one* fused name; they do not introduce a second authoring dialect.
- `exists:` values: `none`, `exactly_one`, `at_least_one`, `all`, `optional` map to the five original existence modes. **Do not** interpret `all` as `at_least_one`; OVAL collection semantics can differ.
- `matches:` values: `none`, `exactly_one`, `some`, `all` map to OVAL match cardinality. `some` means **one or more**, not “any value including zero.”
- Both keys are mandatory for a State-bearing Test or State field, including rare `none` existence combinations; do not invent defaults or drop “inert” original comparisons.
- For a **State-free Test**, only `exists` is needed after the existing source-equivalence proof that its matching mode is inoperative. The context must be known to the compiler and source audit.
- Preserve scoping: `state_fields_require` at Test/group scope can use this same map; **record and nested record-field scopes stay separate**. `value_match` of array/Variable expected operands is a third independent dimension and **must not** be merged.
- No implicit inheritance across the collected-Item/State-field boundary. Missing either axis for a State-bearing predicate, unknown scope, or conflicting scoped overrides **fails validation**.

This uses two small typed enums instead of asking a human to decode twenty concatenated enum labels. It is *not* fewer YAML parameters than OVAL, but the nesting and explicit scope are easier to teach and can be rendered on one short inline line.

## C. A tempting natural-language membership predicate — needs much stronger limits

```yaml
      states:
      - mount_options:
          includes_value: nosuid     # hypothetical, NOT legal 0.4
      collected_items_require: {exists: at_least_one, matches: all}
```

This is attractive: “the `mount_options` field **includes** `nosuid`.” But `includes_value` would have to be a **fully specified compound operator**, not `equals` with a hidden default. It would lower to *exactly* `equals: nosuid` plus `exists: at_least_one, matches: some` **only when** the capability schema confirms the field is a multi-valued entity of the correct datatype. It must not be a substring comparison on a scalar string.

Before adding such a key, disprove mismatches for missing field, empty/partial Item collection, errors, duplicate observed values, unexpected datatype, and expected-value arrays/Variables (`value_match`). A general `contains` or `includes` synonym is **not recommended** without that proof. Nor should the author be offered both A and B as optional legal ways to spell one normative 0.4 Assessment.

## D. User-proposed direction: scope is in the noun, not in a 50-character phrase

A promising refinement of B is to make **observed field values** and **collected Items** use different, self-documenting nouns *and* verbs, while still retaining both exact OVAL axes:

```yaml
# RESEARCH ONLY — not currently accepted or schema-valid 0.4
states:
  - mount_options:
      equals: nosuid
      observed_values:
        exist: at_least_one
        matching: at_least_one

collected_items:
  exist: at_least_one
  satisfying: all
```

Reading naturally:
- **Observed values:** at least one `mount_options` value exists and at least one **matches** `equals: nosuid`.
- **Collected Items:** at least one partition Item exists and **all satisfy** the Test's State expression(s).

This may outperform both A (one long `require` phrase at each level) and B (the same `{exists, matches}` verb pair under different enclosing scopes). Although it requires more lines than A, the *scope* is explicit at a glance and no reader needs to infer whether `some_match` means “some options” or “some partitions”.

**Critical boundaries:** `satisfying` must be *defined* to lower **exactly** to the existing Test-level OVAL matching/check aggregator, even when the Test has alternative States, nested Boolean `evaluate`, partial/error Items and six technical outcomes. It must not silently introduce ordinary two-valued success/failure semantics. `matching` must lower exactly to the field's OVAL entity `match`; `exist` retains the original five existence modes. Keep `value_match` for comparison operands independent. Where a field is itself a record, the record and its nested field populations are distinct; `observed_values` cannot simply be inherited into them.

**Potential downside:** serializing existence and matching as two fields revives some longhand, and `satisfying: all` may not obviously communicate “all collected Items' **State outcomes**” until defined. It needs a novice comprehension test, not only a schema designer's preference.

### Other real examples under D (illustrative, not executable)

```yaml
# DNS SV-259345: exactly one observed stdout_line value, and it matches
states:
  - stdout_line:
      equals: 'True'
      observed_values: {exist: exactly_one, matching: all}

# Windows registry SV-253254: all observed type/value fields within each
# permitted State alternative must match; all collected registry Items satisfy
state_fields_require: {exist: at_least_one, matching: all}
collected_items: {exist: at_least_one, satisfying: all}

# Absent stderr_line: presence and matching must not be conflated
# (original State may retain a comparison even when absence is required)
states:
  - stderr_line:
      equals: ''
      observed_values: {exist: none, matching: all}
```

The draft's `state_fields_require` map in this illustration would need to inherit only into **ordinary scalar State fields**, never record/record-field nodes; it is not a newly approved scope rule. Full examples must also preserve `states_match` and `value_match`. Neither `matching` nor `satisfying` implies hidden defaults.

**Narrow recommendation:** compare A, B and D with a human exercise first; C (`includes_value`) is an operator/computed-membership feature and can be considered separately. Choose **one** normative spelling for 0.4 once proven. This is not a request to add a second dialect.

## E. English-first, resource-first reading test

**This is an illustration, not a schema decision.** Start from the real RHEL 9 requirement in ordinary words:

> Select partitions whose mount points match the source `.*\\/home` regex. Find at least one. Every selected partition must have `nosuid` among its `mount_options` values.

Try a native authoring structure with a single local **inspect → where → expect** sequence:

```yaml
# EXPERIMENTAL, not valid native SCAP-NG v0.4 today
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\\/home'}
expect:
  items_found: at_least_one
  every_item:
    mount_options:
      includes_value: nosuid
```

**Why this feels natural:** `items_found` is the collected-Item existence requirement; `every_item` is the collected-Item matching requirement; `includes_value` is a **precise multi-value membership predicate**, not substring search. The capability schema must type `mount_options` as a suitable multi-valued field, and the predicate must lower to *field existence one_or_more + field match one_or_more + equals nosuid*. Any incomplete/error/unknown behavior must be preserved. The original selector regex can match mounts other than exact `/home`, and must not be narrowed for a prettier example.

**Other real cases, same sentence-first design** (illustrative field blocks; entire Test/selector not repeated):

```yaml
# DNS SV-259345: "each collected result has exactly one stdout_line,
# and that line must equal 'True'"
expect:
  items_found: at_least_one
  every_item:
    stdout_line:
      values_found: exactly_one
      every_value:
        equals: 'True'

# Apache SV-214228: "if a KeepAlive line is present, every one must match"
expect:
  items_found: at_least_one  # demonstrate scope; original source must be checked
  every_item:
    stdout_line:
      values_found: optional
      every_value:
        matches_regex: '\\s*KeepAlive On'
```

**Important design risk:** `includes_value` is a *compound* operator, while `values_found` + `every_value` expose two axes. We do **not** want to publish two permanent alternatives for the same source meaning. Before deciding, test whether an entirely compositional form such as `items_found` + `items_passing` + `values_found` + `values_matching` is easier to understand than these ordinary-English predicate words. Existing OVAL includes unusual combinations (including no Item existence with State comparisons) that cannot be omitted for the sake of a happy-path demonstration. A human-readable editor sentence **does not replace** an exact serialized source contract.

### Concrete design discipline for E

1. Write one plain-English sentence for every example **before** its YAML, and ask a new reader to predict pass/fail/unknown on actual populations.
2. One concept per word: `found` / `items` names collection counts, `item(s)_passing` the Test result aggregator, `value(s)` field populations, `record(s)` nested record populations. Use `matching` for predicate outcomes, not existence.
3. For everyday checks, prefer familiar verbs (`includes_value`, `every_item`, `exactly_one_value`), **only** where the complete source semantic meaning can be made intrinsic by the typed capability schema. No undocumented defaults or overloaded substring behavior.
4. Require **one grammar**, not an English facade plus a second “canonical authoring” syntax. Mechanically lower that one grammar to the existing evaluated semantics; avoid two equivalent accepted spellings.
5. Reject any proposed macro whose precise six-state, incomplete-collection, negative-match or evidence behavior is not independently proven. Test source-preserving transformations, especially exact-one, optional, no-State, nested WMI record and `value_match` arrays.

**Ranking proposal:** test A (fused enum), B (generic pairs), D (separate scope nouns) and E (English-first vocabulary) with blind novices and experienced OVAL authors. If E cannot express outliers without a second grammar, prefer D or improve the one compositional grammar rather than standardizing E prematurely.

## F. Wording refinement: existence of Items vs evaluation of each collected Item

A reviewer found the concrete `check / inspect / where / require` example easier to understand, and asked two important questions:
- Does `all_found` really mean "**for each collected Item**"? **Yes for the Item result aggregation**, but `for_each` is *already* a distinct SCAP-NG collection-expansion operation. Prefer **`every_collected_item`** as an author-facing phrase over a misleading `for_each` in the Test.
- Is `at_least_one_item_exists: true` clearer than `at_least_one_found: true`? It appears clearer in a simple read-aloud test; it names the population instead of an ambiguous `found` value.

```yaml
# Leading wording to test; NOT valid current SCAP-NG v0.4 grammar
check: /home filesystems must use nosuid
inspect: linux.partition
where:
  mount_point:
    matches_regex: '.*\\/home'
require:
  at_least_one_item_exists: true
  every_collected_item:
    mount_options:
      includes_value: nosuid
```

**Do not confuse universal evaluation with a runtime loop:** `every_collected_item` is equivalent in intent to applying the original Test `match=all` over the already collected partition Item population. It must **not** cause repeated collector execution, new target queries or per-Item Assessment result creation. This is fundamentally different from an Object's `for_each` projection, which may expand collected source Items into another combined target Item population.

**Review question that this short example does not answer:** how does the same grammar express `one`, `none`, and `one_or_more` collected-Item match aggregation, versus independent existence modes `none`, `one`, `one_or_more`, `all`, `optional`? A separate Boolean key for every combination (`exactly_one_item_exists`, `no_items_exist`, `items_may_be_absent`, etc.) may make the language larger and harder to validate. Test this against a structured alternative like `items_exist: at_least_one` *without* prematurely picking either option. `true` must not imply that unknown/error/incomplete collection becomes ordinary `false`.

**Next experiments:** preserve source `collected_items_require` (existence and match independently) and State-field/record comparisons on Linux initialized files (one branch may have no matching Items), Windows WMI role branches, DNS command outputs, and Apache optional fields. Disallow any silent two-valued short-circuit or derived-field alias without exhaustive proof.

## Apply the same idea to harder real content

| Real example | Existing label | Candidate structured form | Important scope |
| --- | --- | --- | --- |
| RHEL 9 `mount_options=nosuid` | `at_least_one_exists_and_some_match` | `{exists: at_least_one, matches: some}` | Field values within one partition |
| RHEL 9 collected partitions | `at_least_one_exists_and_all_match` | `{exists: at_least_one, matches: all}` | Collected Items |
| Win Server DNS `stdout_line=True` | `only_one_exists_and_matches` | `{exists: exactly_one, matches: all}` | Field values of one command Item |
| Apache optional `KeepAlive On` line | `may_be_absent_and_all_match` | `{exists: optional, matches: all}` | Field values; absent is not error |
| Win 11 `stderr_line` must be absent | `none_exist` | `{exists: none, matches: all}` when a State comparison survives | Field absence (not zero command Items) |
| Win 11 nested WMI record | `at_least_one_exists_and_all_match` | `{exists: at_least_one, matches: all}` | **Both** record and `domainrole` member, separately |

These are **syntactic translations**, not newly executed scan examples. Preserving the exact original OVAL two-axis pair is required; any special absence-only simplification must be separately proven.

## Proposed decision gate — before freezing 0.4

1. Test **A vs B vs D**, blind, with novice readers and at least one original author/OVAL implementer. Ask them to predict outcomes for: `[rw,nosuid]`, `[rw]`, two selected mounts with one failing, no mounts, and incomplete/error collection.
2. Exhaustively round-trip every current **20 State-bearing requirement names** and **5 State-free presence names** between current 0.4 candidate and B/D. Reject missing/conflicting keys. Compare results against existing pinned six-state reference fixtures, **not just byte-equivalent serialization**.
3. Include Windows nested records, alternative registry States, source `none`/exact-one conditions and array `value_match`. Be able to point to the exact OVAL source graph and collection status for each.
4. If B or D is genuinely clearer, promote **one** structured form everywhere in the 0.4 schema, native capability schemas, converter, examples and editor. Do not expose A and B as permanent mutually accepted dialects.
5. Treat C as a later candidate only if it clearly improves author comprehension *and* has a strict source/capability proof. Otherwise stop at B and retain `equals` plus explicit scoped requirements.

**Provisional recommendation:** Compare B and D against A in a real readability/semantic proof before 0.4 becomes normative. D may be particularly promising because it names Items and observed values separately. A has enough validated source coverage to be a comparison baseline, not necessarily the best human-facing syntax. A reviewer's inability to explain the original pair is a genuine authoring-design warning, **not** grounds for weakening the source assessment meaning.

Tracking: [vocabulary / semantics #227](https://github.com/vanderpol/scap-ng/issues/227) · [semantics gate #229](https://github.com/vanderpol/scap-ng/issues/229) · [scope inheritance research](SCOPED-FIELD-REQUIRE-REVIEW.md) · [source pair census](../slang-feedback-04/EXISTENCE-MATCH-CATALOG.md).
