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

## 12. Root cause should mean logical outcome explanation

The prototypes initially used `root_cause` and `root_causes` fields inconsistently.

**Lesson:** The normative model should instead define one structured decisive outcome explanation. It explains the logical/evidentiary reason the assessment reached its outcome; it does not claim to identify the human or operational cause of the misconfiguration.

For Boolean expressions, the explanation is a pruned proof tree. A failed AND may need only one failed child, while a failed OR requires failure evidence for every acceptable alternative. Additional independently useful failures belong in bounded diagnostics rather than being confused with the minimal proof.

Collection errors and applicability decisions use separate structured reason/applicability data.

See `result-explanation-model.md`.

## 13. Complex-language hypotheses must be revalidated against published NIWC content

Earlier development-repository experiments suggested useful ideas around derivation, quantifiers, semantic capabilities, and reuse. Those examples are no longer part of the published-content evidence corpus.

**Lesson:** keep the architectural hypotheses, but do not cite them as real-world proof until the same semantic pressures are reproduced from pinned NIWC `Current/` packages.

The first depth pass now uses RHEL 9, Oracle Linux 9, Windows 11, and Windows Server 2025.

## 14. Cross-platform reuse should be measured, not assumed

RHEL 9 and Oracle Linux 9 are intentionally paired to quantify overlap. Windows 11 and Windows Server 2025 provide a second reuse axis.

**Lesson:** report several overlap levels separately: shared policy references, similar wording, equivalent OVAL semantics, exact reusable assessments, and parameterizable reusable assessments. Similarity alone does not justify automation reuse.

## 15. Published-source provenance is part of the prototype

A migration case is useful evidence only if it can be traced to the exact signed NIWC publication artifact.

**Lesson:** every real-world prototype needs the pinned repository revision, ZIP path/digest, component identity, XCCDF rule, and OVAL definition provenance.

## 16. Full-corpus breadth follows priority-platform depth

The four priority platforms are for learning quickly from current content; they do not reduce the final conversion obligation.

**Lesson:** prototype deeply on the four anchors, then run the same converter across every individual benchmark in the pinned NIWC `Current/` corpus before specification finalization.

## 17. Experimental content must remain visibly separate from evidence

Development and prototype repositories are valuable for experimentation but can blur the line between published behavior and research assumptions.

**Lesson:** experimental content may motivate a hypothesis, but only pinned published NIWC content can substantiate public-corpus migration findings in iteration 001.

## 18. SCAP 1.4 conversion constrains every authoring experiment

SCAP-NG is intended to inherit the existing SCAP content investment rather than require a clean-sheet rewrite.

**Lesson:** Forward conversion from SCAP 1.4 is a hard requirement. A human-friendly syntax is not viable if real XCCDF/OVAL/datastream semantics cannot be emitted into it deterministically.

The original research syntax and the Ansible-inspired syntax should therefore be treated as two renderings of one faithful semantic model. Both should be generated from the same migrated source cases and compiled back to canonical semantics for equivalence comparison.

This also prevents syntax preference from contaminating migration logic: faithful interpretation of SCAP 1.4 happens first; authoring presentation happens second.

## 19. Questions carried forward

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
