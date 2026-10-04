# SCAP-NG 0.2.0 Board review content

Status: **awaiting bounded Codex sample Assessment pilot**

This directory is the human-reviewable sample-content portion of the SCAP-NG 0.2.0 OVAL Board checkpoint.

The checkpoint SHALL include 5–10 small SCAP-NG Assessments chosen to demonstrate important 0.2.0 semantics without forcing reviewers to inspect full STIG conversions.

## Required contents

The final sample set should contain:

- native-authored SCAP-NG Assessment examples;
- converted OVAL-backed examples with pinned provenance;
- independent expected results;
- concise per-sample review notes;
- validation commands/evidence;
- a manifest listing every included sample and the feature it demonstrates.

At least one sample should demonstrate a nontrivial reference/dependency path such as Variables, Sets, Filters, or another graph interaction. At least one should demonstrate Results/evidence that makes the reason for the outcome understandable.

## Design goals

Samples should be:

- small enough to review by hand;
- semantically representative;
- intentionally named;
- free of irrelevant benchmark bulk;
- usable later as canonical conformance examples after human acceptance.

Do not copy an entire benchmark into this directory merely to prove conversion works.

## Human acceptance gate

Codex may create and validate the pilot, but the directory is not considered an approved Board sample package until a human reviewer has examined the examples and their expected semantics.

When the pilot is ready for review, add a manifest with a per-sample status of `pending-review`. Human acceptance changes the status to `accepted`, with reviewer/date recorded.

See:
- `board/SCAP-NG-0.2.0-REVIEW-CHECKPOINT.md`
- `transition/codex-test-content-0.2.0-task.md`
- `MAINTAINING.md`
