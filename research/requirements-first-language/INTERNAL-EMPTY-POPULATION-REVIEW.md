# Internal adversarial review: empty populations, existence and matching

**17 October 2026 — #235. Internal same-model analysis, NOT an independent naive review, specification decision or evaluator-conformance result.** To run a cold read, use [the answer-free packet](NAIVE-REVIEW-PACKET.md) first. Do not reveal this document to a reviewer before initial predictions are frozen.

## Problem

The previous discussion confused two separate questions: **Does every selected resource satisfy the constraint?** and **Does a required resource actually exist?** It was too quick to agree that a `require: every` statement automatically implies at least one selected resource. It was also too quick to treat `if_empty: fail` as gratuitous without comparing legitimate optional populations.

Universal quantification in logic treats `every` on a proven empty collection as true (vacuous truth). Everyday auditors may instead interpret the prefix `require` as existence. **That disagreement is an authorability defect even before choosing either runtime rule.** The current prototype requires `if_empty: pass/fail/unknown` to force a decision, which is explicit but looks like low-level branching and repeats often.

## Cases that distinguish the interpretations

| Security policy | Proven complete zero selected resources | A natural auditor expectation | Reviewer warning |
| --- | --- | --- | --- |
| The exact `/home` filesystem must be mounted with nosuid | No `/home` resource | Fail | `every` without additional cardinality does not say the mount must exist |
| All existing guest accounts must be disabled | No guest accounts | Pass (if no separate guest-account existence policy) | `every` may be vacuously true; default-required would incorrectly fail |
| Every privileged login account has MFA | No privileged login accounts | Policy-dependent | Some policies require an admin account; others only protect existing accounts |
| No prohibited service is running | No prohibited services | Pass | Use `none` with an explicit matching predicate, not `every` plus a negative property |
| Every file under the selected directory must have safe permissions | Empty directory | Policy-dependent | The existence of the directory and contents is a distinct policy condition |
| One RRSIG zone-signing key must exist and be in range | No keys | Fail | Existence matters independently of `every` bounds |
| Scanner observed zero mounts but was unable to complete enumeration | Unknown population | Cannot conclude just from zero observed | Incomplete is NOT a proven empty set; OVAL-like decisive evidence may still exist |
| Windows WMI returned contradictory nested role records `[1,3]` | Multiple raw records | Cannot rewrite using ordinary `one_of` membership | Item/record cardinality and source grouping remain the conversion burden |

## Alternative authoring designs to compare, no decision yet

**Candidate A — mandatory `if_empty` on every:** explicit zero behavior, but authors must understand empty and supply low-level result values in almost every collection. The research validator currently accepts this, for testing only.

**Candidate B — `every` means universal quantification, with separate resource-presence requirement:** mathematically consistent but forces added structure for `/home`, and a new author may not expect an empty selection to pass.

**Candidate C — `every` implies one-or-more:** concise `/home` but silently fails legitimate optional populations (guest accounts, zero matching files); would need a second `if_present_every` operator, recreating complexity by other means.

**Candidate D — first-class unique, named resources plus optional collection rules:** for fixed singleton facts an author writes a named `require` against `linux.mount_at`, `windows.registry_value` or a typed `windows.service`; providers define the missing-resource response and provenance. For variable populations the author writes `for_each` or `every` over an explicitly selected list. Might be easiest for auditors, but requires a rigorous typed resource catalog and a separately expressive generic fallback, and cannot silently translate original multi-record/multi-value OVAL.

**Candidate E — explicit readable cardinality as a policy statement:** `there_must_be`, `at_least_one`, or a range constraint alongside `every`, with editor-guided selection. More verbose than a provider-specific singleton resource but less ambiguous than `if_empty: fail`.

## Internal design preference, deliberately provisional

**Test D against two demanding native policies before adopting it:** a concrete required singleton configuration (e.g. precise Linux mountpoint), and a universal requirement over a legitimately optional population (e.g. guest accounts). The natural English distinguishes them without making auditor authors learn vacuous quantification: `require the /home mount to have nosuid` versus `for each existing guest account, require disabled`. A single generic `every` form cannot reliably encode both unless the author supplies a cardinality condition, a second operator or a provider contract that carries the distinction.

Do **not** claim that a typed provider automatically resolves the source data. The provider must separately define empty/missing, unknown/error/partial, data identity, multiplicity and the error boundary. A compiler must reject rather than re-interpret original source conditions that it cannot preserve.

## Stop conditions

- Do not modify the normative 0.4 specification or invert previous YAML migration examples merely because the new grammar is nicer to read.
- Do not change the current research validator's `if_empty` rule until a specific replacement is documented and negative tests cover both policies.
- Run the [naive clean-room packet](NAIVE-REVIEW-PACKET.md) without this answer key, then classify first-read confusion by source, quantifier, selection, matching, field presence, and incomplete acquisition.
- Prefer the smallest conceptual distinction the reviewer can explain correctly with confidence, not the shortest YAML.
