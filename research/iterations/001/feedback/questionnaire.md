# SCAP-NG Iteration 001 Review Questionnaire

**Purpose:** Obtain structured technical feedback on the first SCAP-NG architecture and prototypes.

Reviewers do not need to answer every question. Please preserve the question IDs in responses so comments can be traced into the decision register.

## Architecture

**ARCH-001** — Based on the supplied prototypes, which source organization is more maintainable: combined policy/assessment rule objects or split policy/assessment/binding objects? Please identify concrete reasons rather than only a preference.

**ARCH-002** — What failure modes or lifecycle problems do you expect from the combined model?

**ARCH-003** — What failure modes or lifecycle problems do you expect from the split model?

**ARCH-004** — Should a compiler be free to normalize either source model into a different optimized internal package representation?

## Policy-only and manual assessment

**POL-001** — Is existing STIG Check Content sufficient to serve as the default manual assessment procedure without a separate questionnaire definition?

**POL-002** — What additional fields, if any, would DISA need to author for useful policy-only SCAP-NG content?

**POL-003** — What standard manual outcomes and evidence metadata are required?

## Automation semantics

**AUTO-001** — Are the proposed `if / elif / else` semantics sufficiently deterministic for portable assessment content?

**AUTO-002** — What should happen when an IF/ELIF condition cannot be evaluated because evidence is missing or collection errors?

**BOOL-001** — Should scanners normally short-circuit AND/OR expressions once the final truth value is invariant?

**BOOL-002** — Should content be able to request additional independent failure causes after the verdict is already known?

**BOOL-003** — Is the distinction between `outcome_complete` and `diagnostics_complete` useful and sufficient?

**BOOL-004** — Does the nested-logic result example provide enough information to explain the root cause without a full OVAL-style result tree?

## Evidence and scale

**EVID-001** — Is author-controlled `max_records` appropriate for limiting returned failure evidence?

**EVID-002** — Is `stop_after_violations` appropriate when additional violations cannot change the outcome?

**EVID-003** — What count-quality terms should be standardized (for example exact, at_least, estimated, unknown)?

**EVID-004** — What evidence must be retained for successful large-population checks?

## OVAL migration

**MIG-001** — Which OVAL semantics are missing or oversimplified in these prototypes?

**MIG-002** — Which deprecated OVAL constructs still require migration handling because they appear in real trusted content?

**MIG-003** — What should be required before a converted assessment is labeled semantically equivalent to the original OVAL definition?

**MIG-004** — Is a temporary legacy OVAL compatibility execution mechanism acceptable as a migration safety valve?

## Results

**RES-001** — Does the compact result model contain enough information for troubleshooting and audit?

**RES-002** — Which current OVAL/XCCDF/ARF result fields must not be lost?

**RES-003** — Should compact, explain, and forensic result profiles be standardized?

**RES-004** — What additional requirements arise when aggregating results from 100,000+ systems?

## Packaging and signatures

**PKG-001** — Is a constrained ZIP container with individually addressable JSON members a suitable replacement for a monolithic SCAP datastream?

**PKG-002** — Should a published automated benchmark always contain the complete resolved policy and required automation?

**SIG-001** — Is signing a canonical manifest containing member hashes preferable to signing raw ZIP bytes?

**SIG-002** — Which signature/trust technologies must be supported for government publishing workflows?

## Capability model and command fallback

**CAP-001** — Which native collection capability families are essential for a first usable release?

**CAP-002** — How should the capability registry evolve without recreating OVAL's platform-schema proliferation?

**CMD-001** — What restrictions should be placed on command/shell fallback collection?

## Open reviewer comments

**GEN-001** — What is the most significant architectural risk in the current proposal?

**GEN-002** — What current SCAP/OVAL behavior is easy to overlook but must be preserved?

**GEN-003** — What real-world content should be included in iteration 002?

**GEN-004** — What would make this proposal easier for existing policy publishers, scanner vendors, and content authors to adopt?
