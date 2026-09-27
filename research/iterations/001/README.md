# SCAP-NG Research Iteration 001

**Status:** Preliminary research / architecture exploration  
**Purpose:** Preserve the initial design discussion and provide concrete prototypes for review by the OVAL Board, NIST SCAP participants, DISA, scanner developers, and content authors.

Iteration 001 is intentionally **not a draft specification**. It records the starting design direction, unresolved questions, and controlled prototype examples needed to make later decisions with evidence rather than preference.

## Contents

- `preliminary-architecture-discussion.md` — consolidated discussion and rationale from the initial SCAP-NG design work.
- `prototype-comparison.md` — criteria for comparing the two candidate content architectures.
- `prototypes/` — side-by-side combined-rule and split policy/assessment/binding examples.
- `feedback/` — questionnaire, response format, evidence archive, and decision register.
- `notes/` — supporting observations, including analysis of representative SCAP 1.4 results.

## Prototype architectures

### A. Combined rule

Policy metadata, manual check procedure, and automated assessment are represented in one rule object. Reusable automation may still require a reference mechanism.

### B. Split policy / assessment / binding

Policy, automation, and the mapping between them are separate objects. The published scanner-facing bundle is nevertheless self-contained and contains the complete resolved policy and automation.

Neither architecture is selected by this iteration. The examples intentionally exercise the same semantics so reviewers can compare them directly.

## Prototype scenarios

1. **Windows conditional policy** — uses native `if / elif / else` semantics and shows why a particular branch was selected.
2. **Windows nested Boolean logic** — represents a complex OVAL-style AND/OR tree and demonstrates compact root-cause reporting.
3. **Linux large-filesystem ownership** — demonstrates evidence caps, decisive early termination, and compact reporting for very large populations.
4. **DISA-style policy-only rules** — demonstrate that existing Check Content can serve directly as the default manual assessment procedure without requiring a separate questionnaire artifact.

All rule IDs, titles, policy language, values, and observations in these prototypes are illustrative unless explicitly identified as sourced material. They must not be interpreted as official DISA requirements.

## Iteration workflow

Feedback should be captured using `feedback/questionnaire.md` and `feedback/response-template.md`. Returned feedback files should be placed under `feedback/responses/` unchanged as evidence. Accepted conclusions should then be reflected in `feedback/decision-register.md` with stable decision IDs.

The next iteration should be created only after the important questions from this iteration have been evaluated and the decision register identifies which assumptions changed.
