# SCAP-NG 0.4 — iterative readability revision and repeated red-team review

**17 October 2026 — research experiment; not approved v0.4 syntax, scanner behavior, or independent usability evidence.** Work tracked in [#235](https://github.com/vanderpol/scap-ng/issues/235), [#229](https://github.com/vanderpol/scap-ng/issues/229). The executable baseline remains the [canonical source-reversible six-STIG research examples](canonical-operators/report.md). This document **does not** alter `schema/v0.4.0`, converter output, signed bundles, or the independent review packet from the previous round.

## Repeatable method and honest stopping rule

The same assistant applied **three distinct critical passes**, with a targeted revision between passes. This is **not** three independent reviewers. The passes deliberately used the **same six original source-backed patterns** from [the earlier blind packet](FRESH-EYES-BLIND-REVIEW-PACKET.md), plus missing/error/duplicate-data counterexamples. A real outside review is supplied separately in [the answer-free Gemini packet](GEMINI-INDEPENDENT-REVIEW-PACKET.md).

Repeat until two consecutive critical passes produce **no newly actionable ambiguity in the proposed author-facing wording**. This is a **provisional lexical stopping criterion**, **not** permission to close unresolved source semantics, non-Boolean statuses, or reviewer comprehension. If any new source-semantic mismatch is found, block the candidate and restart, even if the words read well.

## Original candidate (v1)

```yaml
require:
  items: at_least_one
  match: all
  mount_options: {at_least_one_value_equals: nosuid}
```

The [two prior reviews](FRESH-EYES-SECOND-THIRD-REVIEW.md) found real first-reader ambiguity about whether `match: all` counts Items, records, or field values; `items: if_present` and `fields.presence: all` appear contradictory; and `states.or` is readily mistaken for value membership.

## Revision 1 — remove ambiguous match scope, not the cardinality distinction

* Replace outer `require.match` with **`matching_items`**, when the original Test compares Items.
* Replace `match` directly inside a record requirement with **`matching_records`**, only when its scope really is record Items.
* Keep `items` and `records` as distinct **existence** counters. Keep `at_least_one_value_equals` for repeated **field values**.
* Keep `states.and/or` as groups of **whole States**, never collapse distinct States into field `in` membership.
* **Do not** add `valid`, `condition`, a universal `scope` wrapper, or a second execution DSL.

These names are **proposed research aliases only**. They have **not** been through the 871/872 source-reconstruction proof, schema validation, or six-state reference evaluation. Existing canonical YAML continues to use `match`.

### Pass 1 — auditor reading for the first time

**Better:** In Linux `matching_items: all` names the partition population; in Windows WMI `matching_records: all` names nested record comparison. **New issues:** `items: if_present` still reads as if every comparison is optional, `fields.presence: all` fails to say which fields, and `all_state_fields_exist` in DNS is still off to the side. Missing/error status cannot be guessed from a short fragment. **Result: revise.**

## Revision 2 — targeted words, without semantic invention

1. Try **`items: may_be_absent`** in the non-system Linux initialization-file check. It means zero selected Items is permitted **if acquisition is successfully complete**; it does **not** mean present Items can ignore their fields. This is a candidate alias for the original `if_present`, **not** a proven mapping over six-state outcomes.
2. For the Linux State-field `and`, trial **`listed_fields_must_exist: true`** under `fields:`. It points to the fields **listed within that same State group** (eight original permission fields), not all possible fields or the existence of files. This remains unproved against nested overrides and error behavior; original `presence: all` is not deleted from executable research.
3. In the DNS bounds example, **show the existing source `all_state_fields_exist: true` explicitly**, do not silently remove it. A future scoped spelling requires an inheritance/precedence proof. The bare words are still not suitable for a first-time auditor; a source-derived editor explanation must state the affected fields.
4. Keep Apache's **`when_present_matches_regex`** on the `stdout_line` field. At least one *command Item* is independently required. Absence of that field is **not** the same as an absent, failed, unreadable, or uncollected Item.
5. A named set of Windows passing alternatives is an **auditor explanation** of the original `evaluate` expression, not an added `case` / priority / `if/else` authoring wrapper.

### Revised v2 excerpts — same real source cases, not standalone runnable Assessments

**A. RHEL9 SV-257851 — mount selection and repeated mount-option values**

```yaml
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\/home'}
require:
  items: at_least_one
  matching_items: all
  mount_options: {at_least_one_value_equals: nosuid}
```

**B. Windows 11 SV-253495 — two entire WMI State alternatives**

```yaml
from: windows-wmi57-object
require:
  items: at_least_one
  matching_items: all
  states:
    or:
      - result:
          records: at_least_one
          matching_records: all
          domainrole: {equals: '1'}
      - result:
          records: at_least_one
          matching_records: all
          domainrole: {equals: '3'}
```

The relevant [whole seven-Test Assessment](canonical-operators/windows-wmi-rights.canonical.research.yaml) still includes five user-right comparisons, two WMI role checks, and the exact final `or` of three possible complete paths. These State alternatives must be evaluated as **two complete comparisons**, not merged into `domainrole: {in: ['1', '3']}`. `from` identifies the [named source](canonical-operators/windows-wmi-rights.canonical.research.yaml); no invented collector is omitted from the full source.

**C. Windows 11 SV-253495 — one or more trustee Items matching Guests**

```yaml
from: windows-userright-object
require:
  items: at_least_one
  matching_items: at_least_one
  trustee_name: {case_insensitive_equals: Guests}
```

**D. Linux SV-257889 — optional *file population*, mandatory *fields in existing files***

```yaml
require:
  items: may_be_absent
  matching_items: all
  fields:
    and:
      - setuid: {equals: false}
      - setgid: {equals: false}
      - sticky: {equals: false}
      - group_write: {equals: false}
      - group_execute: {equals: false}
      - other_read: {equals: false}
      - other_write: {equals: false}
      - other_execute: {equals: false}
    listed_fields_must_exist: true
```

The real Assessment has a **different root-account branch** with a non-optional Item requirement, plus account-derived Set/difference/`for_each`, filesystem traversal and directory exclusion. Do not treat the above as a complete Assessment. [Full source](canonical-operators/linux-files.canonical.research.yaml).

**E. Apache SV-214228 — required command Item, comparison when field present**

```yaml
require:
  items: at_least_one
  matching_items: all
  stdout_line:
    when_present_matches_regex: '\s*KeepAlive On'
```

The complete Assessment contains four checks and an 18-Variable discovery/command dependency chain that the excerpt cannot simplify. [Full source](canonical-operators/apache.canonical.research.yaml).

**F. Windows DNS SV-259345 — two independent bound States and inherited field existence**

```yaml
all_state_fields_exist: true # existing source spelling, not a new proposal
require:
  items: at_least_one
  matching_items: all
  states:
    and:
      - stdout_line: {greater_than_or_equal: 48}
      - stdout_line: {less_than_or_equal: 168}
```

This fragment retains the source-level placement precisely; it intentionally demonstrates that merely renaming `match` **has not solved** Test/State inherited field presence. Full DNS source contains five checks with three possible `evaluate` branches and dynamically built PowerShell commands. [Full source](canonical-operators/dns.canonical.research.yaml).

### Pass 2 — skeptical scanner implementer, looking for changed meanings

**Checks preserved in the excerpt:** `where` still means collection selection; required collected Items and matched Items are separately counted; repeated mount-option values are separate; whole-State OR remains separate from per-record matching; required vs optional field is no longer silently conflated. **Concerns remaining:** `may_be_absent` and `listed_fields_must_exist` lack a full six-state/inheritance lowering; `all_state_fields_exist` remains jargon; quoted regex and Windows values must not be normalized for aesthetics. Exact-one, none-existing, legacy all-existing, unreadable and not-collected patterns must be regression fixtures, not new hidden defaults. **Result: do not change established semantic structures; mark two new aliases experimental and block promotion.**

## Pass 3 — novice author and editor, not familiar with OVAL

Ask: Can this person put acquisition, selection, cardinality, field comparisons, and final Boolean decision in the right place without copying a previous example? **Positive:** The new labels directly identify Items vs records; there is no extra wrapper to navigate. **Remaining issue:** the full Linux Set graph, DNS/Apache Variables and seven-Test Windows `evaluate` tree are intrinsically complex; a short excerpt cannot prove novice authorability. Need an editor that asks **which resources, how many must exist, how many must match, which fields are required, and which whole check paths combine**. It must derive a preview from the same parsed Assessment, not a hand-written second source of truth. **Result: no additional justified YAML wrapper or synonym.**

## Pass 4 — adversarial same-case replay, unchanged v2

Replay the same five data-shape traps from the previous packet:

| Observation / question | Wording-only issue after v2 | Semantic gate |
| --- | --- | --- |
| One mount `rw,nosuid`; two mounts, one noncompliant | No new Item-vs-value ambiguity identified | Source regex/value and incomplete Item status |
| WMI two records with roles `1` and `3` | `matching_records: all` helps; `states.or` still demands understanding whole alternatives | Six-state State grouping and mixed records |
| No Linux non-system files vs one file missing a permission field | Population-vs-field distinction clearer | Required field absence/error semantics and provenance |
| One Apache command Item with absent `stdout_line` vs no Item | Scoped keyword helps; error behavior still opaque | Exact optional-field and Item-status proof |
| DNS bound States with absent `stdout_line` | No new rename justified | Inherited field presence not normalized |
| Windows seven-Test `evaluate`, three OR routes | No new YAML wrapper justified | Source-derived preview and unknown/error propagation |

**Pass 4 conclusion:** No *new* actionable keyword/wrapper change identified by this assistant after Pass 3. **Not** "no issues": field inheritance, the native six-state semantics and independent usability are still open. In particular, `listed_fields_must_exist` and `may_be_absent` remain **unproven suggested names**. If the independent review finds any ambiguity or missed result case, reopen this loop rather than proclaim success.

## Conditional candidate and next evidence gate

- **Retain for further testing:** `require.items` + `require.matching_items` and nested `records` + `matching_records` as a scoped-naming experiment, but keep source-tested `match` as the executable baseline.
- **Do not yet standardize:** `may_be_absent`, `listed_fields_must_exist`, DNS inherited-field syntax, or new simplified collection contracts. Never infer pass from missing/unreadable data.
- **Next:** Exact inverse conversion and invalid-input tests of proposed aliases on the pinned corpus; original-source truth fixtures for missing/incomplete/Error/Unknown/Not-Applicable cases; a machine-derived proof view of complete checks; then outside review.
- **Reviewers:** Use the new [answer-free independent packet](GEMINI-INDEPENDENT-REVIEW-PACKET.md). Ask for a concrete wrong example for *each* proposed change, not preference-only votes. The Gemini review must not be given this rationale or the expected result table until after its first answers.
- **Decision threshold:** No material semantic discrepancy, no confirmed "fails interpreted as passes" in complete cases, and no new, actionable grammatical confusion in **two independent outside review rounds**. This document alone does not reach that threshold.
