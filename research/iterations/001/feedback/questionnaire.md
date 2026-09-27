# SCAP-NG Iteration 001 Review Questionnaire

**Purpose:** Obtain structured technical feedback on the first SCAP-NG architecture and prototypes.

Reviewers do not need to answer every question. Please preserve the question IDs in responses so comments can be traced into the decision register.

## Architecture

**ARCH-001** — Based on the supplied prototypes, which source organization is more maintainable: combined policy/assessment rule objects or split policy/assessment/binding objects? Please identify concrete reasons rather than only a preference.

**ARCH-002** — What failure modes or lifecycle problems do you expect from the combined shared-rule + constrained-overlay model?

**ARCH-003** — What failure modes or lifecycle problems do you expect from the split model?

**ARCH-004** — Should a compiler be free to normalize either source model into a different optimized internal package representation?

**ARCH-005** — In the combined model, are constrained overlays easier to understand/version than explicit policy-to-assessment bindings, or do they introduce problematic inheritance semantics?

**ARCH-006** — Which fields should an overlay be permitted to specialize (ID, title, severity, references, discussion, Check Content, Fix Text, applicability, declared parameters), and which must be immutable?

**ARCH-007** — Should benchmark membership and source provenance be kept outside intrinsic policy-rule semantics so exact rule objects can be reused across benchmarks when appropriate?

## Policy-only and manual assessment

**POL-001** — Is existing STIG Check Content sufficient to serve as the default manual assessment procedure without a separate questionnaire definition?

**POL-002** — What additional fields, if any, would DISA need to author for useful policy-only SCAP-NG content?

**POL-003** — What standard manual outcomes and evidence metadata are required?

## Automation semantics

**AUTO-001** — Are the proposed `if / elif / else` semantics sufficiently deterministic for portable assessment content?

**AUTO-002** — What should happen when an IF/ELIF condition cannot be evaluated because evidence is missing or collection errors?

**AUTO-003** — Does the real OVAL corpus justify a first-class typed `derive` phase between collection and assertion?

**AUTO-004** — Which derivation primitives are essential in the core language (for example unique, count, path operations, coalesce, regex capture, concat, typed conversion)?

**AUTO-005** — Should general set algebra remain a core author-facing feature if corpus migration can represent most current set/filter usage through collection scopes, predicates, quantifiers, and derivations?

**AUTO-006** — What safeguards are needed so the derive layer does not become another general-purpose scripting language?

**BOOL-001** — Should scanners normally short-circuit AND/OR expressions once the final truth value is invariant?

**BOOL-002** — Should content be able to request additional independent failure causes after the verdict is already known?

**BOOL-003** — Is the distinction between `outcome_complete` and `diagnostics_complete` useful and sufficient?

**BOOL-004** — Does the proposed decisive outcome explanation provide enough information to explain nested Boolean failures without a full OVAL-style result tree?

**BOOL-005** — For a failed AND, should one decisive failed child be the required minimum while additional failed children are optional diagnostics?

**BOOL-006** — For a failed OR, do reviewers agree that the explanation must contain a decisive failure for every alternative necessary to prove the OR false?

**BOOL-007** — When several equally minimal decisive explanations exist, should the standard require deterministic selection of one, or allow bounded multiple explanations?

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

**MIG-005** — When may a converter replace OVAL Boolean compliance logic with explicit SCAP-NG applicability, as demonstrated by the Windows Store case?

**MIG-006** — What differential-test evidence should be required before a real-world prototype translation can move from `prototype_native_translation` to `exact_native` or `exact_normalized`?

## Scoring

**SCORE-001** — Should severity determine the default effective rule weight rather than requiring policy authors to populate a separate weight value?

**SCORE-002** — What severity-to-weight mapping should be normative or default?

**SCORE-003** — Should exceptional per-rule weight overrides be allowed, and what justification/provenance should they require?

**SCORE-004** — How should Error, Indeterminate, Not Evaluated, and Not Applicable affect the compliance-score denominator?

**SCORE-005** — Should scanners report a separate assessment-coverage percentage alongside compliance percentage?

## Results

**RES-001** — Does the compact result model contain enough information for troubleshooting and audit?

**RES-002** — Which current OVAL/XCCDF/ARF result fields must not be lost?

**RES-003** — Should compact, explain, and forensic result profiles be standardized?

**RES-004** — What additional requirements arise when aggregating results from 100,000+ systems?

**RES-005** — Should structured decisive explanations be mandatory for automated Fail results, with human-readable summaries treated as derived convenience text?

**RES-006** — Are `decisive`, `additional_findings`, `supporting`, and `unevaluated` the right categories for explanation data?

## Packaging and signatures

**PKG-001** — Is a constrained ZIP container with individually addressable JSON members a suitable replacement for a monolithic SCAP datastream?

**PKG-002** — Should a published automated benchmark always contain the complete resolved policy and required automation?

**SIG-001** — Is signing a canonical manifest containing member hashes preferable to signing raw ZIP bytes?

**SIG-002** — Which signature/trust technologies must be supported for government publishing workflows?

## Capability model and command fallback

**CAP-001** — Which native collection capability families are essential for a first usable release?

**CAP-002** — How should the capability registry evolve without recreating OVAL's platform-schema proliferation?

**CAP-003** — Are higher-level contracts such as package verification, effective audit rules, crypto policy, and PostgreSQL instance/settings collection appropriate standard capabilities, or are any too implementation-specific?

**CAP-004** — What conformance evidence is necessary to prove two scanner implementations return semantically equivalent evidence for the same capability?

**CMD-001** — What restrictions should be placed on command/shell fallback collection?

## Open reviewer comments

**GEN-001** — What is the most significant architectural risk in the current proposal?

**GEN-002** — What current SCAP/OVAL behavior is easy to overlook but must be preserved?

**GEN-003** — What real-world content should be included in iteration 002?

**GEN-004** — What would make this proposal easier for existing policy publishers, scanner vendors, and content authors to adopt?
