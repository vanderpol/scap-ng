# DNS composition blind-review facilitator key — do not share before submission

**October 18, 2026 · Research #235 / #227.** This file must be withheld until a reviewer freezes their response to [the complete A/B packet](DNS-COMPOSITION-BLIND-REVIEW.md). It is not a normative 0.4 reference, not scanner validation, and not a record of a human study already performed.

## The two variants

- **A = existing full English-first research after** in [FULL-04-dns.md](FULL-04-dns.md): three separately named local command Variables.
- **B = proposed full inline-command research after** in [FULL-04-dns-INLINE-COMMAND-CANDIDATE.md](FULL-04-dns-INLINE-COMMAND-CANDIDATE.md): same three `concat` expressions at the point of use, with their named single-use Variable declarations omitted.

These are not two approved dialects. The study specifically tests whether removing source hops improves comprehension and authorability **without** introducing false beliefs about value iteration or errors.

## Expected reviewer insights

| Question | Intended source-visible distinction | Never award credit for |
| --- | --- | --- |
| 1. Named source | `list-all-forward-lookup-zones-object` uses `independent.shellcommand` with a PowerShell command filtering out forwarders, auto-created and reverse zones; the three command expressions read its `stdout_line` values. | Treating “all zones” in a prose title as unfiltered source input |
| 2. Zero/one/many values | The snippet alone lacks the value-function contract, so an unprimed reviewer should mark it **unknowable from the YAML**. **After freeze**, official [OVAL 5.12.3 concat](https://oval-community-guidelines.readthedocs.io/en/v5.12.3/oval-schema-documentation/oval-definitions-schema.html#concatfunctiontype) says multiple input values yield **multiple constructed strings**, not one joined string; do **not** infer provider execution count. Compare [official-source finding](OVAL-5123-CONCAT-MERGE-READABILITY.md). | Inventing a guaranteed one-command-per-zone *execution*, implicit scalar join, separator or native-0.4 scanner behavior |
| 3. Command locations | A requires lookup from a `collect.command.variable` to three definitions; B keeps the exact expressions inside the three `collect.command` fields. Same literal strings and zone source; **no new collection stage** should be inferred. | Suggesting the inlining inherently caches differently, escapes zone names or executes fewer shell commands |
| 4. No stdout vs no Item | The caching-only and AD-integrated cases retain `at_least_one_item_exists: true` but ask for **no values of `stdout_line`**; command-item presence and returned-field multiplicity are different scopes. | Declaring the two conditions contradictory, or changing the Item rule to optional |
| 5. Error/incomplete | `error_if_exit_status_not_0: false` and `error_if_stderr_exists: false` are explicit. The six-state behavior for unavailable/incomplete upstream zone data and mixed `concat` population is *not* explained by this file. | Claiming a missing source becomes empty text/false/true, or that a false flag proves all such data is valid |
| 6. Evaluate alternatives | `evaluate.any_of`: caching-only **OR** AD-integrated condition **OR** (signed **AND** both distinct zone/key-signature validity tests). All three signing checks apply only to the third branch. | Saying DNS signing is mandatory for caching-only, or erasing the AD-integrated standalone branch |
| 7. New-check authorability | Lookups and line counts are evidence, but correctness requires the original source-Item cardinality, command type, shell flags and independent results handling. Authors must distinguish “easy to copy a `concat`” from “knowing how multi-value command construction works.” | Preferring a shorter file without citing semantics, or inventing source typing |
| 8. Metadata | B removes the original named Variables' `title`, `kind: local`, `datatype: string`. A exposes them. An accepted inline form would need a resolved metadata/provenance/type contract. | Declaring omission harmless on a “not used by runtime” guess |

## Honest scoring, per sample

Apply to Q1–Q8 **0 = incorrect/unsupported confidence, 1 = partially correct with caveats, 2 = correct + uncertainty identified where necessary** (max 16 per sample). Also record:

- **Specific navigation burden:** number of jumps to see the original zone source and each command expression.
- **Author error tendency:** attempts to assume scalar versus array handling, to run per zone despite absence of `for_each`, to drop stderr/exit flags, or to mistake field absence for Item absence.
- **Correctness under uncertainty:** a good answer may say “the exact multi-value `concat` semantics aren't defined here.” The evaluator must not penalize this in favor of unwarranted confidence.
- **Authorability:** can a reader outline a new *fourth* derived command without hidden type/default guesses, and point to what must still be documented?

Record reviewer count, prior SCAP/OVAL familiarity, first-response text, date, and the exact sample SHA. Never summarize a model's or the designer's self-critique as an independent novice test.

## Preliminary designer critique — not human evidence

**Potential B benefit:** 3 fewer definition hops and 21 fewer non-comment lines; check and command transformation are colocated. **Potential B regression:** long multiline `concat` makes each check noisier, missing Variable `title/kind/datatype`, and a novice may be *more* likely to assume a per-zone implicit loop. In both designs, source result completeness/error handling and plural-value interpolation remain insufficiently documented.

**Recommendation before an owner decision:** Do not choose B because it is shorter. Require a separate typed composition contract and a blind first-read outcome showing fewer incorrect deductions. H2—keeping named Variables but showing an editor-side expanded preview—remains a legitimate control against B. No schema/converter modification is authorized by these documents.
