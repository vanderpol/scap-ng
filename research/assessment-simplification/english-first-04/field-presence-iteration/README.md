# 0.4 research iteration — explicit field presence, distinct populations, readable decisions

**17 October 2026 · Research only · Issues [#235](https://github.com/vanderpol/scap-ng/issues/235) and [#229](https://github.com/vanderpol/scap-ng/issues/229).** The five complete revised files here are **NOT** approved 0.4 syntax and are not valid against the present normative 0.4 schema. The 0.3 release, 0.4 working schema, source converters and bundles are unchanged.

[Source-backed Gemini review audit](../GEMINI-SECOND-REVIEW-SOURCE-AUDIT-2026-10-17.md) demonstrated that replacing source graphs with invented typed collectors, rewriting regexes, or collapsing whole WMI States is not a legitimate simplification. **This iteration changes only typed presentation of existing requirements, never what is collected or how check results combine.**

## The tested candidate — full Assessment links on github.com

| Source-backed Assessment | Full revised research Assessment | Original complete research Assessment |
| --- | --- | --- |
| RHEL9 `/home` | [Revised](linux-home.revised.research.yaml) | [Original](../canonical-operators/linux-home.canonical.research.yaml) |
| Windows 11 seven-check WMI and user rights | [Revised](windows-wmi-rights.revised.research.yaml) | [Original](../canonical-operators/windows-wmi-rights.canonical.research.yaml) |
| Linux dependent initialization files | [Revised](linux-files.revised.research.yaml) | [Original](../canonical-operators/linux-files.canonical.research.yaml) |
| Apache four-check Include/config graph | [Revised](apache.revised.research.yaml) | [Original](../canonical-operators/apache.canonical.research.yaml) |
| Windows DNS five checks and command Variables | [Revised](dns.revised.research.yaml) | [Original](../canonical-operators/dns.canonical.research.yaml) |

These are **full files**, not excerpts. They retain the original `sources`, `metadata`, `evaluate`, exact check IDs, selectors, literal operands, original regexes, same literal comparisons, Variables, Set/foreach and reports. No fake `linux.user_init_files`, `apache.config`, `windows.dns_settings` or substituted Windows logon right.

## Three targeted changes

### 1. Make the population quantified by a matching rule unmistakable

Original root Item `require.match: all` becomes **`require.matching_items: all`**.

Original nested WMI `records: at_least_one; match: all` becomes **`records: at_least_one; matching_records: all`**.

No cardinality is dropped or folded into the other. In particular, WMI still says **either every record equals '1' or every record equals '3'**. Mixed `[1,3]` does not meet either whole State on a complete successful collection. The final Windows three-path `evaluate.or` is unchanged.

### 2. Make shared field existence visible *inside* the requirement

**Linux field permissions**, with exactly one `fields.and` group in each real check:

~~~yaml
require:
  items: if_present           # original source wording retained
  matching_items: all
  field_presence: required    # provisional alias for source fields.presence: all
  fields:
    and:
      - setuid: {equals: false}
      - setgid: {equals: false}
      # six other unchanged permission fields in complete file
~~~

The root-user check instead has `items: at_least_one`. This **does not** make the fields optional just because *root Items* may be absent in the separate non-system-user check.

**DNS signature bounds** had the original `all_state_fields_exist: true` *outside* `require`. Move only this requirement into the check's requirement namespace:

~~~yaml
require:
  items: at_least_one
  matching_items: all
  field_presence: required    # local research alias for that Test-level flag
  states:
    and:
      - stdout_line: {greater_than_or_equal: 48}
      - stdout_line: {less_than_or_equal: 168}
~~~

This is **not** a new `range` predicate. The two whole States remain two whole States. A future grammar must specify Test/group/field precedence for the inherited presence contract, prevent inheritance into Windows record members, and prove absent/unknown/error outcomes. **`required` is only a provisional alias for the precise original mode on these selected source-backed shapes**, not a license to collapse uncommon OVAL existence modes.

### 3. Show optional *field* presence separately from comparison

**Apache**, one of four unchanged complete checks:

~~~yaml
require:
  items: at_least_one
  matching_items: all
  stdout_line:
    presence: may_be_absent
    matches_regex: '\s*KeepAlive On'
~~~

This research pair reverses **exactly** to the existing source `stdout_line.when_present_matches_regex`, not to a newly interpreted "missing always passes" rule. The other original Apache optional comparison uses `subexpression.presence: may_be_absent` and `greater_than_or_equal: 100`, recovering `when_present_greater_than_or_equal`.

**A missing field is not a missing Item; neither is an unreadable field or an incomplete collection.** An exact six-state lowering must be demonstrated before treating either spelling as normative.

## Where inheritance is permitted — proposed authoring discipline, not yet a schema

- `require.field_presence` is an explicitly written **Test-scope policy** governing its ordinary scalar State fields. It is never a hidden default.
- A later State-group-level policy could override a Test-scope policy, and a local field presence could override it for that field. **The exact precedence and admissible field modes are not approved or implemented by this iteration.**
- Record fields remain independent: Test scalar field presence never silently applies to WMI record members.
- An editor must show the **effective** presence contract at the field use site, including where it came from. Merely collapsing all policies into a Boolean `strict_existence` loses distinctions.
- This prototype only rewrites the **two homogeneous Linux fields groups, two homogeneous DNS State groups, and two Apache optional operators** that are pinned. Other source patterns **fail closed** in the standalone research adapter rather than being inferred as aliases.

## Reproducible inverse / evidence boundary

The five complete candidates were independently re-inverted **byte-for-byte** to their five existing canonical research YAML files in the GitHub connector on 17 October 2026 (five of five). Full assessment names, collection code, source graphs, literal regexes, operator positions and `evaluate` trees were preserved.

Reproduce and validate YAML parsing using [the fail-closed verifier](../../../tools/research_04_field_presence_iteration.py):

~~~shell
python -m pip install "PyYAML>=6,<7"
python tools/research_04_field_presence_iteration.py --require-yaml
~~~

[GitHub Actions workflow](../../../.github/workflows/research-04-field-presence-iteration.yml) is configured to run the same research-only checks for changes to this directory. **Do not call CI passing until the actual run is inspected.** Even if it passes, source inversion and YAML parsing **do not** prove original OVAL six-state scanner/evidence parity, parser/schema acceptance of this new dialect, correctness outside five hand-selected complete files, or human comprehension.

## Internal adversarial review: revision log

| Pass | Specific challenge | Finding | Resolution |
| --- | --- | --- | --- |
| 1. First-time reader | What does `match: all` count? Why does DNS field existence appear before `require`? | Item/record matching scope and DNS policy placement are confusing. | Explicit `matching_items` / `matching_records`; field presence placed in `require`. |
| 2. Novice author | Is `state_fields_presence` understandable without OVAL training? | No: "State" sounds like a hidden internal object. | Shortened to `field_presence` within `require`, still only applying to the referenced ordinary scalar fields. |
| 3. Skeptical implementer | Can you recover all five original complete Assessments? Are WMI OR, regexes, selectors and dependency graphs untouched? | **Yes, exact source-text inverses for five checked files.** But no independent six-state execution proof; `required`/optional equivalence is constrained to the named origins. | Fail-closed standalone verifier and read-only CI; reject any automatic `in`/range/new collector transformation. |
| 4. First-time-reader retry | Can you infer optional *Item* vs optional *field*, three Windows pass routes, records `[1,3]`, and missing vs error? | Some scopes are clearer. But source status transitions, exact inherited-field semantics and full dependency graphs remain challenging without an editor. | No further decorative grammar wrappers. Require effective-contract hover/preview and a real out-of-model blind review. |
| 5. Adversarial repeat | Could shorter `fields.and`, `states.or`, or `where` be deleted? | No verified semantic-preserving deletion for these source anchors. A Set filter, selector and Test State have different meaning. | Retain unchanged pending counterexample-supported redesign, not a preference vote. |

The passes above are **deliberately different perspectives by the same assistant**, **not** five independent humans/models. We stop synonym experiments here; this is **not** the project's overall "no unresolved issues" stopping criterion.

## Auditor proof sheet, not another authored language

For the original Windows `evaluate` expression, a read-only auditor view can label its existing three `or` alternatives:

- **Domain joined, non-DC:** domain-joined WMI check AND Local account AND Guests AND Domain Admins AND Enterprise Admins right checks.
- **Standalone:** standalone WMI check AND Guests right check.
- **Deny everyone:** Everyone right check.

Those are **human editorial labels applied here to the existing AST for review**. The reader-facing explanation should eventually be **machine derived**, with each check ID still traceable to the original source, correct six-state truth handling, and error/unknown visibility. The labels do not change evaluation order, introduce priority `if/else`, or add `case` to the executable grammar.

## Unresolved issues / external test handoff

**Gating concerns:** (1) source-specific exact six-state truth table for `required` and `may_be_absent` aliases, including missing/errors and inherited field scope; (2) run and inspect read-only verifier CI; (3) broaden beyond five pinned files before proposing canonical 0.4; (4) genuinely unfamiliar auditor predictions for zero/mixed/duplicate/unknown; (5) generated not hand-authored proof view and authoring-editor tests.

**Next external gate:** [New answer-free Gemini review packet](GEMINI-NEXT-BLIND-REVIEW.md). Provide that document *alone* in a new conversation. Do not provide this README or the source-exact expected results before Gemini completes its blind phase.
