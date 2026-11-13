# Proposed wording crosswalk

For the owner-requested short author-facing candidates, start with [Editorial review batch 1](EDITORIAL-REVIEW.md). The table below retains the original Phase 1 Codex drafts, not editorial approval.

The table shows the source-reviewed priority set; the [complete machine crosswalk](crosswalk.jsonl) includes every deficient canonical target. It is a review proposal, not a second documentation authority. Structural-only remainder text is explicitly provisional where meaning cannot be established; no proposal is approved or applied.

| Schema URI + pointer | Role | Existing wording | Defect | Proposed replacement | Basis / decision | Status |
| --- | --- | --- | --- | --- | --- | --- |

## Exact application model

The [patch bundle](proposed-annotations.patch.json) has per-file SHA-256 preconditions and exact add/replace/test operations. Only `description`, `examples` or `title` annotation destinations are permitted. New annotations use an absent-old-value precondition; replacements test the old text. There is no command that writes the bundle to frozen schemas.

Approve wording by proposal ID with an approval link and accepted/rejected/deferred disposition. An accepted annotation must later move into the coordinated next-version canonical schema and drive renderer/editor help from that same node. Do not keep independently maintained Markdown copies.

Inline Input/Variable wrapper copies and typed comparison copies are mapped to one proposed shared description per role/domain; their existing validation shapes are not assumed equivalent. These consumer bindings are non-annotation follow-ups with no copied description patch. A future annotation-only shared binding needs review. Editor deployment association is likewise a non-annotation follow-up with no fake description patch. Assertion-only/Boolean schemas are inventoried but not treated as separate public prose fields; wrapping them would require a separately reviewed structural proposal.

## High-impact before/after review


All schema acceptance tests are structural. No scanner execution, function-runtime parity or release-readiness result is claimed.
