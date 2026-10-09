# Governance and published decisions

This directory contains SCAP-NG governance material: published proposals, voting
records, and preserved 0.2.0 review material. It is **not** a second project or
specification overview.

For the current project/design review, use:

- [Current review](../review/current/README.md)
- [Draft specification](../specification/README.md)
- [Real Benchmark and Rule policy examples](../specification/examples/README.md) and [technical Assessment examples](../specification/examples/assessments.md)

## Current 0.3 Board-decision review (not yet published as votes)

- [Candidate decision register](review/0.3-vote-shortlist.md) — **18 independently reviewable areas**: 11 automated Assessment/OVAL-successor questions and seven broader SCAP-NG integration questions. This is an *internal candidate bank*, not a demand for 18 Board votes.
- [Audit of 61 published Discussions](review/0.3-discussion-audit.md) — full P001–P058 dispositions, current-0.3 conflicts and participation evidence.
- [Coordination issue #209](https://github.com/vanderpol/scap-ng/issues/209) — decide which questions and which standards/governance audience warrant a first focused round.

**Now live:** [single A/B/C/D Assessment vocabulary vote — GitHub Discussion #211](https://github.com/vanderpol/scap-ng/discussions/211). The [side-by-side comparison](ASSESSMENT-VOCABULARY-DISCUSSION.md) shows the same real RHEL 9 STIG in three vocabularies. This remains a nonbinding preference poll; source conversion and conformance are mandatory acceptance gates. The old [issue #207](https://github.com/vanderpol/scap-ng/issues/207) is preserved as the original discussion history, not a second voting location.

## Historical published proposals

[VOTES.md](VOTES.md) retains links to the 58 previously published, **unvoted** yes/no proposal Discussions. They are **not** the current proposed 0.3 ballot set, and no ratification is implied. Original [proposal text](proposals/) is preserved.

**Publication rule for each eventual new Discussion:** state one clearly scoped decision and genuine alternative, identify the 0.3 baseline, link directly to its coordinating **GitHub implementation issue and related issue(s)**, cite short source-backed/conformance evidence, distinguish Board feedback from implementation acceptance, and avoid unnecessary verbosity. A proposal whose issue links or compatibility claim is not verified stays in draft.

## 0.2.0 preserved review material

The historical 0.2.0 schemas are preserved under
[../schema/v0.2.0/](../schema/v0.2.0/). They are the durable evidence of
that design checkpoint; **rebuilding its converter output or Board-pilot
samples is not a 0.3 release requirement**.

Older [0.2 review material](review-content/0.2.0/) may remain for historical
context only. It is not a maintained validation baseline. Current examples
and acceptance criteria are in the specification and current review area.
