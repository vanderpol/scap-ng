# Iteration 001 Prototype Lessons Learned

**Status:** Internal working record  
**Purpose:** Capture conclusions learned from implementing the prototypes so later architecture work and external review do not depend on conversation history.

## 1. Source organization must be visible, not merely package organization

The first full-benchmark build correctly emitted modular JSON package members but accidentally used aggregate YAML source files. That made the source-level architecture comparison misleading.

**Lesson:** Authoring structure is itself part of the experiment. Iteration 001 now uses individual policy rules, assessments, bindings, overlays, benchmark/profile documents, and provenance files.

## 2. Authoring reuse and scanner distribution are different concerns

Reusable source material can live once while every distributed automated benchmark remains self-contained.

The split model resolves shared assessments into each target package. The combined model resolves shared rules plus overlays into each target package.

**Lesson:** Runtime dependency resolution is not necessary to obtain authoring reuse.

## 3. A fair combined-model prototype needs real reuse

Simply duplicating inline automation made the combined model look artificially weak.

The Windows Client/Server experiment now reuses five technical concepts through shared combined rules and STIG-specific overlays.

**Lesson:** The architecture decision is not "reuse versus no reuse." It is **inheritance/overlay reuse versus explicit composition/binding reuse**.

## 4. Overlays require strict boundaries

An unrestricted overlay is effectively an arbitrary patch language and could make provenance or equivalence impossible to reason about.

Iteration 001 therefore treats assessment logic as immutable through an overlay. Policy-specific fields and declared parameter values may be specialized; automated semantic changes require a new shared-rule version.

**Lesson:** If the combined model survives review, the allowable overlay surface must be normative and small.

## 5. Policy-only content is an authoritative comparison point

The build can compare each resolved automated combined rule with the corresponding policy-only rule.

**Lesson:** Automation augmentation should not silently mutate policy. A compiler should fail when the automated resolved representation diverges from authoritative policy fields.

## 6. Policy membership is not necessarily rule identity

Embedding a generic field such as `source: Windows Server STIG` inside every rule unnecessarily couples the rule to one benchmark and mixes provenance with normative references.

**Lesson:** Benchmark membership belongs in benchmark/profile structure. Publisher/source lineage belongs in provenance. Normative references such as CCI remain rule properties.

This does not assume DISA will frequently reuse exact policy rules across STIGs; it simply avoids prohibiting that capability.

## 7. Cross-STIG reuse should be demonstrated with different policy identities

The Windows prototypes intentionally use different Client and Server rule IDs/titles while reusing equivalent technical logic.

**Lesson:** Automation equivalence must be based on technical semantics, not title, STIG ID, or CCI coincidence.

## 8. Parameterized reuse is materially different from exact reuse

The password-policy example uses one shared technical definition but different role and threshold parameters for Client and Server.

**Lesson:** Parameters need typed schemas, validation, provenance, and compatibility/versioning rules. They cannot be untyped template substitution.

## 9. The scanner-facing package should contain resolved objects

Neither overlays nor external assessment libraries need to become scanner runtime dependencies.

**Lesson:** Source complexity should be resolved by build tooling. Scanner interoperability benefits from a complete signed artifact with deterministic resolved semantics.

## 10. Build tooling is part of conformance evidence

Iteration 001 now validates rule closure, binding references, shared-rule versions, resolved-policy equivalence, package member hashes, and prototype signatures.

**Lesson:** The eventual standard should define semantic validation requirements, not just schemas.

## 11. Scoring should not blindly reproduce historical authoring behavior

A per-rule numeric weight exists in XCCDF, but relying on every policy author to populate meaningful values is unlikely to produce consistent scoring.

**Lesson:** Every scored rule needs a deterministic effective weight. Severity-derived default weighting is the leading direction, while exact numeric mappings, overrides, and treatment of unresolved outcomes remain open.

A nominal compliance percentage should also not conceal incomplete assessment; separate assessment-coverage reporting is worth prototyping.

## 12. Questions carried forward

The most important unresolved questions after these prototypes are:

- combined shared-rule overlays versus split policy/assessment/binding;
- exact legal overlay fields and provenance;
- reusable rule/assessment identity and versioning;
- scoring weights and denominator semantics;
- compliance percentage versus assessment coverage;
- exact outcome vocabulary;
- short-circuit defaults and bounded diagnostics;
- signature/trust mechanism;
- capability registry design;
- migration equivalence criteria.

These should be treated as explicit reviewer questions rather than quietly resolved by implementation convention.
