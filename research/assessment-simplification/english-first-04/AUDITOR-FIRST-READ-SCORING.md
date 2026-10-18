# Scoring the first-read Assessment comparison

**Facilitator material only — keep this separate from the unprimed [review packet](AUDITOR-FIRST-READ-PACKET.md).** Research [#235](https://github.com/vanderpol/scap-ng/issues/235). No auditor has yet taken the test; a test packet or an assistant's own critique is **not** usability evidence.

## Intended facts taken from the pinned current 0.4 source

These facts serve as the *answer key for intended meaning*, **not** as proof that the three authoring formats all have an executable implementation.

| Question in review packet | Evidence-based intended answer | Traps to catch |
| --- | --- | --- |
| 1. Source/selection | The native collection type is `linux.partition`. The source Object selects by `mount_point.matches_regex: .*\\/home`. The literal regex is **not an exact, fully anchored `/home` equality**; matching other path strings depends on the provider's regex/matching behavior. | Calling it an exact `/home` equality from the English `check` title; equating selection with state matching. |
| 2. Required population | At least one selected mount **Item** must exist, and every selected Item must satisfy the State. In a **complete** collection with zero selected Items, this requirement fails. | Thinking “every Item matches” is vacuously true when the required population is empty. |
| 3. Two Items | If exactly one of two selected mount Items lacks `nosuid`, the complete Test fails, even though the other Item matches. | Confusing “some mount-options values match” with “some collected mount Items match.” |
| 4. Field multiplicity | `mount_options` is multi-valued in the source capability. The State field has an explicit *at least one value exists and some value matches* requirement; each selected Item must satisfy it. | Treating the entire options array as one scalar or requiring every option be `nosuid`. |
| 5. Incomplete/error/missing | The snippet **does not define the detailed six-state result charts** or collector error/field-missing behavior. A first-time reader should state uncertainty rather than manufacture `false` or `true`. | Claiming a generic `false` for unknown/incomplete/error; claiming not_applicable from omission. |
| 6. Two-sentence explanation | “Collect Linux mount information and select Items matching the authored mount-point regex. Require at least one selected mount and require **every** selected mount to have **at least one** mount-option value equal to `nosuid`.” | Replacing exact source conditions with an inaccurate “all home files are safe” summary. |
| 7. Authoring from scratch | They may change the literal field comparison in principle but **cannot prove validity, availability or all six-state behavior without a vocabulary/capability reference**. That uncertainty is a legitimate result of blind review. | Confidently asserting unshown operators/defaults are supported. |
| 8. Unnecessary wrappers | Count specific friction: repeated native capability on the inline Object, null/empty source metadata, redundant nested English paraphrases, and ambiguous field/item scope. | Equating raw YAML line count with comprehension; proposing to delete original provenance without a reconstruction plan. |

## A transparent rubric

For Q1–Q4 and Q6: award **2** if answer gets source and Item/field truth boundaries right, **1** if partly correct but ambiguous, **0** for incorrect or unsupported confidence. For Q5 and Q7: award **2** for identifying exactly what is inferable **and** what documentation is missing, **1** for partial recognition, **0** for guessed defaults or unconditional result claims. For Q8: award **2** for naming a real, specific issue tied to a YAML path, **1** for superficial terms without technical consequence, **0** for ungrounded preferences. Maximum **16 points per sample**. Compare A/B/C **within each reviewer**, not across changing reviewers or prompts.

Separately capture:

- Number of times the reviewer scrolls or jumps to locate the source, predicate and final `evaluate` references.
- Specific misinterpretations of Item multiplicity, field multiplicity, regex selection, six technical result states and standalone provenance.
- Whether they can propose a changed check using only a one-page capability/reference table, without violating the intended source requirement.
- Their two rankings: **understanding** and **writing**. Do not collapse these into a popularity vote.

## Disclosure and evidentiary boundaries

The three packet variants are ordered: **A = pinned current 0.4 source; B = 18 Oct lean candidate; C = prior English-first research**. Do **not** reveal these labels until the reader freezes their answers. B has **no compiler/schema validation or proven exact reversal**, even though it retains the apparent Item/field predicates. C has prior research roundtrip for complex generation; the simple inline example was hand-assembled and was *not independently roundtripped*. A sample can be more understandable and still **not** be semantically approved.

An independent non-OVAL reviewer has not yet completed this exercise. Results must report sample count, assessor background, answers, ambiguity rate and evidence; do not fabricate human validation or infer it from existing GitHub CI.

## Next evidence before promotion

Use the same unprimed approach for a **complete** complex Assessment, beginning with [Windows 11 SV-253495](FULL-03-win11-rights.md). The facilitator's expected outcome should distinguish its three top-level OR alternatives, WMI role/record predicates, multiple denied trustees and reused Guests Test. Then test the [Linux account-dependent file check](FULL-02-linux-files.md) with special attention to absent Item populations. A successful readable syntax must make both understandable **without** assuming the alternative branches are ordinary Boolean `if/else` or confusing collected Item count with State-member count.
