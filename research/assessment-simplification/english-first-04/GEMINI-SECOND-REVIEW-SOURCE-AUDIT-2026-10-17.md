# Second Gemini independent-language review: source audit and disposition

**17 October 2026 — issue [#235](https://github.com/vanderpol/scap-ng/issues/235); semantic gate [#229](https://github.com/vanderpol/scap-ng/issues/229).** The owner supplied the full second Gemini review in conversation. This document assesses its claims against the five pinned complete GitHub Assessments, rather than accepting a model's unsupported "verified" labels. **Disposition: accept specific readability observations as research feedback, reject the proposed "0.4.1" executable YAML as a lossless candidate. No normative schema, compiler, content bundle or release changes.**

The outside-model review is genuinely a separate *model's response*, but its own auditor/architect/author passes are not separate independent people or three distinct model runs. Its phase-two assertions do not include a credible per-source/line crosswalk, the proposed YAML cannot be parsed, and its claimed "All OVAL 5.12.3 ... preserved" is false for documented counterexamples.

## Hard failures against actual source

| Severity | Gemini's proposal or source claim | Pinned source, counterexample and consequence | Disposition |
| --- | --- | --- | --- |
| **Critical** | WMI `any_of: [{domain_role: 1}, {domain_role: 3}]` | [Windows source, lines 32–46](canonical-operators/windows-wmi-rights.canonical.research.yaml): *each* State requires **all** nested records to equal '1' or **all** to equal '3'. One root Item containing records `[1,3]` **fails** the two complete alternative comparisons but **passes** a naive per-record membership `in: [1,3]` predicate. The proposed `any_of` has no independently defined scope, making this regression likely. | **Reject** this rewrite. Keep the two whole States, root/record existence and record matching scope. |
| **Critical** | Windows Guests check uses right `SeInteractiveLogonRight` | [Windows source, lines 21–26 and 58–68](canonical-operators/windows-wmi-rights.canonical.research.yaml) selects `SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME` (deny log on through RDP). Gemini substituted a **different** user-right identifier. A system could have Guests on one right but not the other. | **Reject**; preserve the exact selector and its source identity. |
| **High** | RHEL original regex `.*\/home` rewritten as `^.*/home$` | [RHEL source, lines 17–26](canonical-operators/linux-home.canonical.research.yaml) retains the source regex without anchoring. e.g. `/home/users` may match the source expression but not the anchored rewrite. | **Reject** selection change. Allow regex cleanup only with proven equivalent behavior or explicit author-directed correction. |
| **High** | `target: linux.user_init_files` replaces account-derived file collection | [Linux source, lines 12–63 and 87–111](canonical-operators/linux-files.canonical.research.yaml) uses two separate account collections, Set `difference` and exclusion, `for_each_source`, `unix.file` selectors, traversal, and directory exclusions; non-system and root branches have **different** Item existence requirements. The new name has no defined collector or parity fixture and loses the required root branch. | **Reject** as a direct rewrite; research a real typed collector separately, with proof. |
| **High** | `target: apache.config` and `keep_alive: optional` | [Apache source, lines 12–244, 256–331](canonical-operators/apache.canonical.research.yaml) uses 18 Variables, discovered/includes-loaded config paths, four independent shell-command checks, and `and` evaluation. Replacing these with one apparent setting erases observable acquisition and three checks. | **Reject** as source-equivalent authoring. A typed collector is an entirely separate prospective capability. |
| **High** | `target: windows.dns_settings` + `signature_validity_hours.range` | [DNS source, lines 12–169](canonical-operators/dns.canonical.research.yaml) has three command-generating Variables and five checks, with signed-zone and signing-key validity subconditions; the two bounds are **two States** with inherited field existence. The new range has no declared repeated-value, error, source or six-state equivalence contract. | **Not proven**, reject automatic lowering; retain whole source semantics. |
| **High** | Proposed entire `0.4.1` document is executable YAML | Gemini wrote `assessment: id: ...` alongside a same-indent `- target: ...` and later `evaluate`. The result mixes a sequence and mapping directly under `assessment` and is a **YAML parse error**, independently reproduced with a YAML parser. None of the seven components is presented as a valid whole executable Assessment. | **Reject** as schema/testable candidate. |
| **Medium** | `cardinality: at_least_one; match: any` | Original Windows source says `items: at_least_one`, `match: at_least_one`. Substituting `any` invites confusion with distinct inherited OVAL `any_exist`/other operators; no lowering or truth-table test is supplied. | **Reject** unproved synonym. |
| **Medium** | "A source actually uses `linux.partition_collection`" | [RHEL source](canonical-operators/linux-home.canonical.research.yaml) explicitly uses `inspect: linux.partition`. Gemini's phase-two source claim is inaccurate. | Mark as **unsupported factual claim**. |
| **Medium** | "`all_state_fields_exist` is a global schema-validation flag" | [DNS source, lines 136–145, 158–167](canonical-operators/dns.canonical.research.yaml) places the property on **two local Tests** preceding their requirements. It is a meaningful inherited State-field evaluation requirement, not a document-global JSON-Schema validity flag. | Reject factual characterization; retain **real** visibility/precedence problem. |
| **Medium** | `strict_existence: true` and `optional: true` solve missing-field semantics | A Boolean does not explicitly distinguish missing Items, missing field, no values, unreadable, incomplete collection, or State/record-level cardinality; no native compiler contract or six-state fixture was provided. | Keep as **UX hypotheses**, not safe replacement syntax. |
| **Medium** | Gemini concluded `items: exact_count: 1` is needed | Existing experimental source-reversible grammar already supports `items: exactly_one` (documented in [Test Item existence research](TEST-ITEM-EXISTENCE-REVIEW.md)). | Its authorability critique here is a misunderstanding, not evidence of a missing feature. |

**Parser check:** An extracted minimal version of Gemini's proposed `assessment` structure fails PyYAML `safe_load` with `ParserError: expected <block end>, but found '-'`. This is a syntax check, not a scanner test.

## Gemini's blind predictions: what we learned and what it assumed

- **Correct, useful first-read:** RHEL A1/A2/A3; WMI whole-State reading and mixed records B3; Windows Guests C1–C3; Linux permission D2/D3/D6; Apache present-field matches E3/E4/E5; three logical Windows `or` alternatives after Gemini self-corrected.
- **Unproved status predictions:** Gemini assigned `Indeterminate` generically to any incomplete collection (A5/B8/D7/F7). [The actual Assessment Method](../../../specification/assessment/assessment-method.md) says incomplete collection **can still have a decisive true or false**, depending on existence/match logic and what is already known; fail-closed six-state cases matter.
- **Unproved field conclusions:** F4 "missing implies Error," D4 "missing implies Fail," and E2 "pass or fail" are **not** independently resolved by Gemini. E2 correctly identifies a readability problem, but a correct mapping must preserve optional-field semantics, root Item requirements and acquisition outcome.
- **No valid proof of source parity:** Source-only excerpts and statements such as "all cardinalities ... remain fully intact" do not constitute a reversible lowering, diff of full ASTs, or independent runtime truth-table evaluation.
- **Scope-sensitive novice confusion is real:** WMI records, shared State-field existence, optional `stdout_line`, and separate root Item / field populations remain worth testing even though Gemini's replacement syntax failed.
- **Quality-control trap:** Gemini first described "two top-level structures" for G before recognizing the third OR leaf; all three actual Windows alternatives are in the original Assessment. The blind review is useful as an observed interpretive stumble, not authoritative execution evidence.

## Recover the genuinely valuable ideas

1. **Field presence should be local and legible.** Revisit the inherited field-presence contract across Test, State group, field, and nested record scopes. Preserve the old flags until a new placement/precedence model passes exact source-inversion and non-Boolean fixtures. Plain `optional: true` or `exists: required` might be editor language, but is **not** enough as a proven technical replacement.
2. **Named passing paths are valuable for auditors.** Show "domain-joined", "standalone" and "deny everyone" routes as *generated names* for the original final `or` alternatives, without adding a new procedural or priority-language construct or replacing the original `evaluate` AST.
3. **Keep source-selection distinct from compliance requirements.** Current `inspect/where/require` already establishes the separation at sibling keys. Trial `target/filter/assert` only with complete Set/filter/foreach source anchors and blind authorability evidence demonstrating a benefit, because `where` Object selection and `exclude_if` post-collection filters are different pipeline stages.
4. **Revisit safe shorthand for ordinary repeated requirements.** A combined at-least-one-matches construct may save lines only if it cannot hide a meaningful Item-existence mode or change error/incomplete precedence. Use the pinned [split-vs-merged source experiment](POST-03-LANGUAGE-SPLIT-VS-MERGED.md), not ambiguous `match: any`.
5. **Investigate typed collectors separately.** Native typed Apache/Linux/DNS acquisition *could* simplify complex dependency graphs dramatically; it needs a newly specified collector, platform/error/evidence contract and performance test. Merely writing `target: apache.config` is not an implementation.

## Demonstrated safe direction (presentation only; aliases still experimental)

**Simple original source remains fully identifiable:**

~~~yaml
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\/home'}
require:
  items: at_least_one
  matching_items: all
  mount_options:
    at_least_one_value_equals: nosuid
~~~

This is still **research**, with `matching_items` not yet source-lowered. The underlying [canonical research Assessment](canonical-operators/linux-home.canonical.research.yaml) uses `match: all`. Do not replace its regex or infer field/error behavior.

**Windows scope-distinguishing fragment, not executable complete Assessment:**

~~~yaml
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
~~~

No collapse to membership. The named WMI source remains as in [the original](canonical-operators/windows-wmi-rights.canonical.research.yaml).

**A generated auditor view (not new authored grammar):** "Domain-joined non-DC: all of five checks; standalone: both checks; deny everyone: one check. Any complete alternative can establish compliance. Unknown/error states follow the pinned result aggregation tables."

## Next iterative gate (not complete)

| Check | Current status |
| --- | --- |
| Source exactness of Gemini's rewrite | **Failed** by concrete WMI, user-right, regex and collection changes |
| YAML syntax of Gemini's whole proposal | **Failed** to parse |
| Proposed aliases `matching_items`/`matching_records` | **Unproven** lossless mapping, needs inverse and six-state fixtures |
| Field-presence local vs inherited model | **Open**, highest-priority *language* concern |
| Original OVAL result propagation and collection status | Existing normative *inherited* contract, needs independent boundary fixtures |
| New typed collectors | **Separate capability research**, not default 0.4 rewrite |
| External blind review | Gemini supplied one model response; useful novice confusion evidence but **not** a measured human usability test |
| Editor authorability | **Open**, must write unfamiliar whole valid checks with provenance and complete source selection |

**Recommendation:** Keep Gemini's observations as design hypotheses, **do not rename to 0.4.1 or adopt its YAML**. Continue the scoped field-presence/whole-State work, rerun source-exact and six-state fixtures, generate a full-Assessment auditor proof sheet, and ask an outside model/human to challenge *that* unchanged evidence-backed candidate. The stopping criterion is no new *material* defects and all blocking semantics proved—not two passes of confident prose.

## Grounding

- [Canonical six-STIG proof](canonical-operators/report.md)
- [Source-backed selected Test requirements](TEST-ITEM-EXISTENCE-REVIEW.md)
- [Original selection/filter semantics](../../../specification/assessment/selection-and-filters.md)
- [Original OVAL result/collection semantics](../../../specification/assessment/assessment-method.md)
- [Next readability gate](NEXT-READABILITY-DECISION-GATE.md)
