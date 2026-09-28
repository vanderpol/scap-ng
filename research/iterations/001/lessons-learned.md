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

## 20. Rule splitting must follow variables to a fixed point

The four published priority benchmarks produced 1,333 standalone OVAL rule documents. All validate against the SCAP 1.4 Omni schema with zero unresolved references.

RHEL 9 `SV-258179` demonstrates why a definition/test/object-only traversal is insufficient: its closure includes 17 variables and 64 variable-to-variable references.

**Lesson:** dependency closure must treat variables as first-class graph nodes and recursively follow variable, object-component, set, filter, definition, test, object, and state references until a fixed point. Standalone schema validation provides an independent closure check.

## 21. Faithful migration must preserve published defects

The published RHEL 9 xattr audit rule contains 24 tests but only 22 unique semantic conditions. Two b32/root checks are duplicated and the corresponding b64/root conditions are absent.

**Lesson:** a converter must not infer and silently add the apparently intended conditions. The faithful NG representation preserves source behavior and records the discrepancy as `requires_review`. Correction is a separate reviewed action.

## 22. Semantic fingerprints can prove reuse across policy identities

RHEL 9 `SV-258179` and Oracle Linux 9 `SV-271536` produce the same normalized semantic fingerprint despite having different XCCDF rule IDs and policy identities.

**Lesson:** reusable assessment identity should be based on canonical technical semantics, not title, CCI, platform name, or rule identifier.

The same example also shows that reused logic can reuse a defect, so provenance and review state must travel with reusable assessments.

## 23. Ansible familiarity is not automatically terser

The generated faithful RHEL 9 example is 115 lines in the original NG spelling and 121 lines in the Ansible-inspired spelling.

**Lesson:** evaluate Ansible-inspired syntax on comprehension and adoption familiarity, not an assumption that it will reduce authoring size. Both remain renderings of one semantic model.

## 24. Full-datastream conversion should preserve first, normalize second

The first end-to-end RHEL 9 converter deliberately lowers OVAL into a generic structured SCAP-NG assessment graph before attempting elegant capability-specific normalization.

**Lesson:** conversion correctness and native-language elegance are separate gates. A mechanically faithful graph provides a complete migration path and provenance baseline; reviewed normalizers can then promote repeated patterns to `exact_native` or `exact_normalized` without changing source policy identity.

This avoids making every new OVAL collector pattern a prerequisite for demonstrating whole-benchmark conversion.

## 25. XCCDF needs the same loss-accounting discipline as OVAL

OVAL closure work became reliable only after every reference and construct was explicitly accounted for. Full benchmark conversion exposes the same requirement for XCCDF profiles, Values, checks, references, fixes, group membership, applicability, and less-common rule children.

**Lesson:** the benchmark IR retains both normalized fields and the complete XCCDF subtree for each policy object. Missing dedicated NG syntax therefore remains visible rather than being silently dropped.

## 26. Candidate source organizations must be rendered from one benchmark IR

A fair architecture comparison cannot use separately authored content.

**Lesson:** the full RHEL 9 conversion renders both combined-rule and split policy/assessment/binding layouts from one unified XCCDF+OVAL benchmark IR. A verifier compares policy and assessment semantics rule-by-rule so renderer drift becomes a build failure.

## 27. Generated evidence and reusable tooling have different Git requirements

A complete converted benchmark may contain hundreds of large generated source files, while the converter itself and the architectural conclusions are long-lived assets.

**Lesson:** shared tools, schemas/overrides, workflows, lessons, compact summaries, blockers, hashes, and representative converted cases belong in Git. Complete large conversion trees can be retained as reproducible CI artifacts when committing every duplicated rendering would add repository weight without additional review value.

## 28. Reference scanner belongs after format stabilization

A reference SCAP-NG scanner will eventually be necessary to prove that migrated content produces the same assessment outcomes as its SCAP 1.4 source on the same target system.

**Lesson:** do not let an early scanner implementation prematurely constrain the language while the OVAL Board is still choosing and stabilizing the SCAP-NG representation. First finalize the semantic model and source/package format, then build a small reference implementation against that stable contract.

The reference scanner's primary role should be conformance and differential testing rather than product competition. For each migrated benchmark, run the legacy SCAP 1.4 content and the SCAP-NG content against the same target and compare:

- applicability decisions;
- per-rule outcome;
- incomplete/error/not-evaluated states;
- decisive evidence and collected facts where comparison is meaningful;
- profile/value resolution and effective rule selection;
- scoring inputs separately from scanner-specific presentation.

Exact equality should be required for normative semantics. Differences caused only by intentionally improved NG diagnostics or bounded evidence presentation should be classified separately from semantic differences.

The converter and current IR should therefore continue exposing stable execution boundaries (collectors, derived values, predicates, result algebra, applicability, and processing plans) so the later reference scanner can implement them without redesigning the content model.

## 29. Windows migration blockers are useful adoption evidence

The published Windows 11 benchmark contains an automated rule that still uses an effectively deprecated OVAL `user_test`, while other rules in the same benchmark use supported Windows constructs such as `userright_test` and `wmi57_test`.

**Lesson:** the Windows demonstration should make source-remediation debt visible and actionable rather than silently carrying obsolete OVAL into SCAP-NG. For each blocked rule, report the exact rule identifier, deprecated test family, supported replacement when one exists, and the fact that the remainder of the benchmark converts independently.

This is particularly useful for standards/content-author review because it demonstrates a practical upgrade path: repair the published SCAP 1.4 source using supported OVAL semantics, validate it there, then rerun the deterministic SCAP-NG conversion. The demonstration should frame these findings as migration-readiness feedback, not as criticism of the original content authors.

## 30. Benchmark-to-benchmark mapping should use Check Text and OVAL semantics

Cross-benchmark rule identity should not depend on STIG rule IDs, titles, or CCI identifiers being the same.

**Lesson:** use two independent mapping signals:

1. **Normalized Check Text equality.** If two rules have the same Check Text after presentation-only whitespace normalization, treat them as corresponding policy requirements.
2. **Equivalent full OVAL semantics.** If the complete normalized OVAL definition/test/object/state/variable logic is semantically equivalent, treat the rules as corresponding even when their policy wording or identifiers differ.

"Equivalent OVAL" means equivalent assessment logic, not merely use of the same OVAL test family. Two unrelated rules that both use `registry_test` are not considered equivalent.

Keep rule alignment separate from automation reuse. A Check Text match can establish policy alignment even when the implementations differ. Equivalent OVAL semantics establishes alignment and is evidence for exact assessment reuse. Parameterized reuse remains a separate reviewed classification.

## 31. Reuse savings should be measured in maintenance units before dollars

Cross-STIG assessment reuse can reduce authoring, review, regression-test, and maintenance work, but a universal dollar value would require unsupported labor assumptions.

**Lesson:** first report observable units: assessment instances, unique reusable assessments, duplicate definitions avoided, reuse fan-out, and maintenance-unit reduction percentage. Then provide formulas so organizations can apply their own average review hours, change frequency, and loaded labor rate.

This keeps the economic argument evidence-based while still allowing the Board and implementers to estimate savings at their own scale.

## 32. Questions carried forward

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
