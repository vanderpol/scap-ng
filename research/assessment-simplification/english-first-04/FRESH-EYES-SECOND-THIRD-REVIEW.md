# Fresh-eyes second and third reviews: language comprehension and semantic integrity

**17 October 2026 — research #235; no normative schema changes.**

## Reviewer independence — do not misrepresent

These are **two adversarial perspectives taken by the same assistant**, not two independent model runs, not two human readers and not proof of blind usability. No isolated reviewer/sub-agent was available in the active tool environment. To obtain a genuinely independent read, send [the isolated blind packet](FRESH-EYES-BLIND-REVIEW-PACKET.md) to a human unfamiliar with the project or a *new memory-free conversation*, obtain the answers first, and only then show this explanation. Neither reviewer should begin with SCAP 1.4/OVAL instruction or the author's intended readings.

Reviewed: (A) rejected [observe/claims/pass_if alternative](PROOF-FIRST-GROUND-UP-ALTERNATIVE.md), (B) current [source-reversible split-requirements proposal](AUDITOR-SAMPLE-GALLERY.md), against [five complete real source-backed Assessments](canonical-operators/report.md). No run of a scanner and no six-state evaluator parity is claimed.

## Pass 2 — zero-context auditor: what can someone infer, without explanations?

| Excerpt | Cold-read failure or risk | What the source-backed comparison actually requires |
| --- | --- | --- |
| RHEL `items: at_least_one; match: all; mount_options: at_least_one_value_equals` | Which population does bare `match: all` quantify: partitions or mount option values? What does `items` mean? | At least one selected partition Item; **all selected Items** must satisfy: **at least one** observed mount-option value equals `nosuid` |
| Windows `states.or` with `records: at_least_one; match: all` | The nesting looks like 'DomainRole 1 OR 3'; a reader may assume mixed records `[1,3]` pass | Each OR alternative is a **complete State**: all records must be 1, *or* all records must be 3. Mixed 1/3 fails on complete data |
| Apache `when_present_matches_regex` | Is the *file*, collected command Item, or `stdout_line` optional? | At least one command Item remains required; the field-level comparison is conditional on the particular field being present |
| Linux `items: if_present` plus `fields.and; presence: all` | Seems contradictory: 'if present' yet 'all fields must exist'; no visible indication of which scope applies | Zero selected **files** may be acceptable in the non-system-user branch; if files exist each Item must have all eight required matching fields |
| DNS `all_state_fields_exist: true` outside `require` | Obscure inherited field rule, looks like serialization baggage; the gallery omits this meaningful line | Original State fields inherit a required-presence rule for the two bounds; absence behavior is not just number comparison |
| Whole Windows `evaluate: or: - and ...` | Reader may not know whether alternatives are independent routes or conditional branches, and cannot infer unknown/error propagation | Exactly three OR alternatives in the original seven-Test tree; **not** procedural first-match `if/else`. All outcomes are six-state, not simple booleans |

**Cold-read verdict:** A reader could infer the *intent* of simple RHEL nosuid, but cannot reliably predict results for nested Windows records, optional field-vs-Item absence or incomplete collection from syntax alone. The glossary and editor would be doing substantial work. This is a judgment about ambiguity, **not a measured human failure rate**.

## Pass 3 — skeptical implementer: delete every layer not carrying a contract

| Term / level | Keep / reject / gate | Justification |
| --- | --- | --- |
| `valid` | **Reject** | It adds no scope or technical meaning; its `all` child already carries the matching quantifier |
| `observe`, `claims`, `pass_if`, `on`, `using` | **Reject as a whole-language rewrite** | These mostly rename `sources`, `checks`, `evaluate`, `from` and `inspect`; `pass_if` could incorrectly imply two-valued evaluation |
| `checks.<id>` | **Keep** | Creates an identified assertion usable by the complete evaluation tree and evidence provenance |
| `from` and `where` | **Keep** | `from` identifies an existing typed source; `where` restricts collection/selection, which is not the pass predicate |
| `require` | **Keep provisionally** | Separates observed-data predicates from Test metadata/source selection and preserves a structural namespace for arbitrary capability field names; deleting it needs reserved-name/collision proof |
| `require.items` and `require.match` | **Keep the distinction** | Existence and matching are independent even if the label `match` is ambiguous to beginners. Splitting can be edited as two separate controls |
| `states.or` | **Keep when whole-State alternative is source meaningful** | Cannot flatten the `[1,3]` record counterexample to field-membership OR |
| `result` | **Keep** | Actual capability's WMI result field, not an arbitrary wrapper introduced to pretty-print a State |
| `records` and local record `match` | **Keep** | Record occurrence count and record agreement are independent of parent Item matching |
| `fields.and` / `presence: all` | **Keep provisionally as typed semantic grouping, simplify exposure** | The shared field requirement legitimately applies at a separate scope, but the author must be able to tell *which* State fields are covered. Inherited scope and local overrides remain unproved across all error/incomplete cases |
| `all_state_fields_exist: true`, `no_values_exist: true`, `when_present_...` | **Redesign, don't delete semantics** | Not all represent the same thing. Required/optional/absent fields and exact-one field values exist in original source content; these are the unfinished portion of current language |
| Duplicate check `inspect` when `from` points to typed source | **Candidate for deletion** | Seven WMI/userright checks had exact source-backed duplicate-type removal; needs broader source-type and reference validation |
| Repeated `match` at Items/records/field values | **Comprehension problem, not evidence of redundant semantics** | Try a typed editor display such as 'every collected Item' / 'every record' while preserving canonical controls; do not drop quantities or invent a generic cascading `scope` |

## Requirements that cannot be solved by another synonym

1. **No source status represented as ordinary Boolean by default.** Zero matching Items, a missing field, incomplete collection and an Item with `error` are not interchangeable.
2. **One quantifier always has one typed population.** Parent Items, records, record members, repeated observed field values, and expected literal arrays are distinct even when vocabulary repeats.
3. **Source discovery still dominates complex authoring.** The Apache source includes 18 Variables and a deep command graph; describing it as a 'claim' does not reduce the dependencies. Better native collection contracts, typed source navigation and reuse are real engineering work.
4. **The two record role States must not be collapsed.** The concrete `[1,3]` failure demonstrates why visual concision is not semantic equivalence.
5. **Source inversion isn't a usability or six-state proof.** The current split proposal reconstructs 871/872 whole Assessments and 1374/1375 Tests, but reader comprehension and reference runtime outcomes remain unproven.

## Decision after both passes

**Do not adopt the ground-up literal YAML. Do not pronounce the current split grammar auditor-readable yet.** Preserve the smallest tested structural language as a technical candidate, **stop adding wrapper labels**, and focus the next artifact on a **machine-derived, read-only auditor explanation of complete original content**. A good review surface should show the precise collected population, the existence and matching rule, missing-data/status cases, and the three Windows ways to satisfy the original AND/OR tree. The editor can ask the same questions in accessible form without the user memorizing nested YAML.

If the independent blind packet yields consistent wrong predictions, change the **particular ambiguous line**, not the entire grammar. Candidate: bare `match: all` may need scope-explicit display in the editor; that is a readability hypothesis, not an accepted keyword rename.

**Go/no-go for 0.4 authoring readability:** obtain responses from people who haven't seen OVAL or this discussion; judge their predictions for zero Items, one failing of two, missing/error field, WMI mixed records, and allowed versus forbidden Apache values. No adoption based only on shorter source or same-source dictionary reconstruction.

## Independent blind packet and grounded answer check

- [Send this packet unchanged to a separate reviewer first](FRESH-EYES-BLIND-REVIEW-PACKET.md).
- Source-backed check: [six-example gallery](AUDITOR-SAMPLE-GALLERY.md) plus [complete original research documents](canonical-operators/report.md).
- The published [split-vs-merged comparison](require-presentation-comparison/report.md) proves both originally reconstructed the same 871/872 with lossless source encoding; it is **not** proof that split is more intuitive.
- One problematic original bootloader Assessment remains a fail-closed source exception, not a feature the grammar should silently accommodate.
