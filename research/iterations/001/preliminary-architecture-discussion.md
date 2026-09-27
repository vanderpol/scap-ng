# SCAP-NG Preliminary Architecture Discussion

**Iteration:** 001  
**Status:** Preliminary discussion document — not a specification  
**Audience:** OVAL Board members, NIST SCAP participants, DISA content stakeholders, scanner developers, content authors, and other configuration-assessment practitioners

## 1. Purpose

This document preserves the initial SCAP-NG architecture discussion so that subsequent work does not depend on conversation history or undocumented assumptions.

The goal is not to replace SCAP by discarding its investment. The goal is to preserve the useful semantics, trusted content, and vendor-neutral assessment model while removing architectural characteristics that make modern authoring, efficient execution, explainable reporting, and enterprise-scale aggregation unnecessarily difficult.

A key requirement is a practical migration path from existing SCAP 1.4 content. Reverse conversion from SCAP-NG to SCAP 1.4 is not a primary design constraint and may be impossible or lossy for new language features.

SCAP-NG does not have to use XML, and it does not have to preserve the current separation between XCCDF, OVAL, OCIL, CPE, ARF, and datastream structures.

## 2. Inputs to the initial discussion

The initial work considered:

- experience constructing and auditing a RHEL 10 SCAP benchmark;
- the current NIWC Atlantic SCAP Content Library, which contains a broad cross-platform corpus of SCAP 1.4 content;
- the SCAP 1.4 and OVAL 5.12.3 schema bundle;
- existing rule-reuse research across operating systems and product families;
- a representative Windows 11 SCC result set containing XCCDF, OVAL, OCIL, and ARF results;
- operational experience with SCC, including existing optimizations that stop expensive checks once enough violations have been found;
- the reality that DISA publishes authoritative STIG policy separately from automation and already maintains human-readable Check Content for each rule.

Relevant public starting references include:

- NIST SCAP 1.4: https://csrc.nist.gov/Projects/security-content-automation-protocol/scap-releases/scap-1-4
- NIST SP 800-126 Rev. 4: https://csrc.nist.gov/pubs/sp/800/126/r4/final
- NIST SCAP v2 project: https://csrc.nist.gov/projects/security-content-automation-protocol-v2
- NIST OSCAL Assessment Results: https://pages.nist.gov/OSCAL/learn/concepts/layer/assessment/assessment-results/
- DISA STIG downloads: https://www.cyber.mil/stigs/downloads
- NIWC Atlantic SCAP Content Library: https://github.com/niwc-atlantic/scap-content-library
- OVAL 5.12.3 schema documentation: https://oval-community-guidelines.readthedocs.io/en/v5.12.3/

## 3. Problems observed in the existing architecture

### 3.1 Authoring complexity

SCAP configuration assessment currently spans several independently designed XML vocabularies. A content author frequently has to understand rule metadata, check references, definitions, criteria, tests, objects, states, variables, applicability, catalogs, identifiers, namespaces, component references, result semantics, and schema-specific platform constructs.

The problem is not simply XML verbosity. The larger issue is the number of separate conceptual layers required to express an otherwise simple statement such as:

> collect the configured minimum password length and determine whether it is at least 15.

The SCAP-NG design should retain precise semantics without requiring authors to manually construct implementation-oriented object graphs when a direct declarative representation is sufficient.

### 3.2 Result stovepipes

Representative SCC output demonstrates that useful information is divided across XCCDF, OVAL, OCIL, and ARF result structures.

A user asking "why did this fail?" may require a consumer to traverse:

policy rule -> check reference -> OVAL definition -> criteria -> test -> object/state -> tested item -> system characteristic.

SCC currently places useful explanatory text into XCCDF rule-result messages as an implementation enhancement. That improves usability, but the information should be standardized structured result data rather than vendor-specific prose.

### 3.3 Result volume

A representative Windows 11 result ZIP supplied during the initial research was approximately 0.8 MB compressed and roughly 14 MB expanded for one endpoint assessment. The ARF was the largest individual artifact. The OVAL and OCIL result structures also repeated substantial static assessment content.

Exact sizes will differ by benchmark and system, but the design implication is clear: a next-generation result model intended for fleets of 100,000 or more endpoints should not reproduce complete benchmark, OVAL, or questionnaire definitions for every endpoint.

Static content should be stored once and identified by immutable digest. Endpoint results should contain compact outcomes, decisive evidence, completeness information, and references to the exact content used.

### 3.4 OVAL graph explainability

OVAL's separation of definitions, tests, objects, states, variables, system characteristics, and results supports precise evaluation semantics. However, reconstructing a human explanation from that graph can be difficult, particularly for nested AND/OR criteria.

SCAP-NG should preserve the semantics while making a structured explanation a normative result.

### 3.5 Repeated automation

The same underlying technical requirement frequently appears in multiple policy documents and benchmark revisions. Some checks can be reused exactly; others can share a parameterized assessment; still others appear similar but differ in applicability or implementation details.

Reuse must therefore be explicit and provenance-aware. Similar titles, CCI references, or policy concepts are not sufficient proof of technical equivalence.

### 3.6 Shell command overuse

A generic command-execution facility is useful as a capability gap escape hatch, but arbitrary commands obscure intent and prevent scanners from substituting more efficient native collection.

SCAP-NG should favor semantic collection capabilities. A scanner should know that content asks for package inventory, a registry value, password policy, filesystem metadata, or structured configuration data rather than merely seeing an opaque shell command.

A command fallback should return evidence, not a precomputed compliance verdict.

## 4. Core design objectives

The initial discussion established the following objectives.

### 4.1 Preserve trusted content investment

Existing SCAP/OVAL content contains years of authoring, testing, operational deployment, and institutional trust. Migration must be able to preserve existing behavior before content is simplified or refactored.

The initial importer should distinguish exact native translations, normalized-but-equivalent translations, legacy-compatible checks, items requiring review, and unsupported constructs. Nothing should be silently dropped or approximately translated.

### 4.2 Make policy useful without automation

A valid SCAP-NG benchmark must be allowed to contain policy with no automation.

DISA already publishes Check Content for STIG rules. That Check Content is effectively a human assessment procedure and should be directly usable by scanners that support manual/interactive assessment.

A policy publisher should not have to author a separate questionnaire merely to make policy manually scannable.

### 4.3 Make automated results explain themselves

A normal result should directly answer:

- what rule was evaluated;
- what outcome was reached;
- what was observed;
- what was expected;
- what comparison or logical condition was used;
- why the decisive branch applied;
- whether collection was complete;
- whether evidence was truncated;
- what evidence supports the result;
- what exact signed benchmark was used.

A consumer should not need to reconstruct an arbitrary assessment graph merely to explain an ordinary pass or fail.

### 4.4 Optimize collection without changing semantics

SCAP-NG should describe required observations rather than prescribe implementation details whenever possible.

A scanner may deduplicate identical observations, batch platform queries, share package or registry inventory across rules, combine compatible filesystem traversals, avoid unselected conditional branches, and terminate collection when an outcome is already mathematically invariant.

Such optimization must remain visible enough in results to distinguish a complete diagnostic evaluation from a logically complete verdict.

### 4.5 Scale to large enterprises

The result architecture should treat 100,000+ endpoints as a normal design target.

Result size should tend toward the number of rules plus meaningful exceptional observations rather than the number of every object examined.

Large-population checks need standard evidence caps and early-termination semantics.

## 5. Proposed information concepts

The eventual specification is expected to define a small coherent information model rather than several unrelated assessment languages.

Likely concepts include:

- benchmark/package identity;
- policy rule;
- profile/tailoring;
- applicability;
- automated assessment;
- manual/interactive assessment;
- typed collection capability;
- expression/assertion;
- reusable parameters;
- binding or association between policy and assessment, depending on the architecture selected;
- evidence;
- rule result;
- provenance;
- package manifest and signature metadata;
- controlled extensions.

The precise file organization remains intentionally unresolved in iteration 001.

## 6. Authoring and interchange direction

The current preferred direction is:

**Human authoring:** restricted YAML  
**Canonical scanner interchange:** JSON  
**Optional compact enterprise result encoding:** potentially CBOR, subject to later evaluation  
**Redistribution:** signed ZIP-based SCAP-NG package

The YAML form should map predictably to the canonical JSON model. Scanners should not be required to implement multiple authoring syntaxes.

The restricted YAML profile should avoid ambiguous or surprising features that could cause two implementations to interpret identical source differently.

## 7. SCAP-NG package direction

The current packaging hypothesis is a normative ZIP-based bundle, tentatively using a `.scapng` extension.

The package should remain modular internally rather than collapsing all content into one enormous document.

A conceptual package could contain:

```text
META-INF/
  manifest.json
  signature.cose

benchmark.json
rules/
assessments/
bindings.json
profiles/
provenance/
```

The final directory layout depends partly on the combined-versus-split decision being prototyped in this iteration.

The published automated benchmark should be self-contained. A scanner operator should install one package containing the complete policy and all automation required to assess and report that policy. Runtime installation of independently versioned policy and automation packages should not be required because it invites mismatched versions and operational confusion.

Source-development reuse may still occur across repositories or libraries. Build tooling resolves those dependencies into a complete scanner-facing package.

## 8. Package integrity and signatures

The package should support signing the complete logical contents.

The preferred direction is to sign a canonical manifest rather than raw ZIP bytes. ZIP byte streams can vary because of compression choices, timestamps, ordering, and container metadata even when logical content is identical.

The manifest should identify every normative member and include its cryptographic digest. Except for explicitly defined signature/container metadata, unlisted members should invalidate a conforming package.

Conceptually:

```text
content member -> digest
content member -> digest
content member -> digest
               |
               v
         canonical manifest
               |
               v
            signature
```

The exact signature technology, certificate/trust model, canonicalization requirements, and deterministic-ZIP profile remain open questions.

## 9. Policy-only content and manual assessment

Policy is independently useful.

A policy-only benchmark should contain enough information to provide normal STIG reporting:

- stable rule identifiers;
- title;
- severity;
- discussion;
- references such as CCI;
- applicability metadata where available;
- Check Content;
- Fix Text;
- benchmark/profile organization;
- source/provenance/version metadata.

Existing Check Content should serve as the default manual assessment procedure.

A scanner could present the policy procedure and capture a standardized outcome, comments, justification, assessor identity/role where appropriate, and optional evidence attachments or references.

An explicit structured manual-assessment block may eventually be useful for richer interactions, but it must not be required merely to use existing STIG Check Content.

## 10. Automated assessment model

### 10.1 Collection and assertion

The proposed native model should emphasize two concepts:

**collect** — obtain typed observations using a declared semantic capability;  
**assert** — evaluate those observations using deterministic expressions.

For example:

```yaml
collect:
  password_policy:
    capability: auth.password-policy

assert:
  compare:
    actual: $password_policy.minimum_length
    op: ge
    expected: 15
```

This is intentionally closer to the security requirement than an explicit test/object/state graph.

### 10.2 Capability registry

A standardized capability describes what evidence is returned, not how a product must collect it.

Candidate capabilities include filesystem metadata/content, structured configuration, package inventory, services, processes, accounts/groups, password policy, registry, Windows security policy, certificates, security hardware, kernel/sysctl, mounts, audit configuration, database settings/query results, application configuration, Kubernetes/API resources, and network-device configuration.

The registry should be extensible without requiring the core standard to be revised for every new product family.

### 10.3 Command fallback

A command capability remains necessary for gaps, but it should be explicitly second-class.

The command should collect meaningful evidence. Assertions determine compliance. Tools should be able to lint content that uses command execution where a standardized semantic capability exists.

## 11. Native conditional logic

SCAP-NG should support declarative `if / elif / else`.

This is intended to address requirements whose logic is naturally conditional but becomes cumbersome when represented only through Boolean criteria, sets, filters, and variable graphs.

Conditional logic can be useful for:

- choosing which assertion applies;
- selecting an appropriate collector/implementation;
- deriving an expected value;
- determining a policy branch.

Unselected branches must not execute. This is semantic branch selection, not merely an optimization.

The language should remain declarative: no mutable state, arbitrary procedural loops, goto-like behavior, or side-effect-dependent execution.

Converted OVAL content should initially preserve its original logical structure. A later reviewed normalization pass may simplify equivalent OVAL graphs into conditional constructs, but the converter should not invent new control flow during faithful migration.

## 12. Boolean logic and short-circuiting

IF/ELSE does not replace AND/OR.

For Boolean expressions, a scanner should be allowed to stop evaluating when the enclosing expression's result becomes mathematically invariant, subject to required diagnostics/evidence.

For example, one false child proves an AND expression false. One true child proves an OR expression true.

However, exhaustive evaluation can reveal additional remediation problems. The current design therefore distinguishes:

- **outcome completeness** — sufficient evaluation occurred to determine the rule outcome with certainty;
- **diagnostic completeness** — all relevant branches were evaluated.

A future standard may support a bounded diagnostic control such as `max_failure_causes`. This would let scanners gather several independent root causes without requiring an exhaustive expensive scan.

Results must disclose logical short-circuiting and unevaluated branches when diagnostically significant.

## 13. Evidence caps and early termination

Content authors should be able to cap the number of detailed evidence records returned for large-population failures.

Example concept:

```yaml
evidence:
  max_records: 50

evaluation:
  stop_after_violations: 50
```

These controls are related but distinct.

`max_records` limits serialized detailed evidence.

`stop_after_violations` allows collection to end once a threshold has been reached and continuing cannot change the final outcome.

Results should distinguish exact from lower-bound counts:

```yaml
violations:
  observed: 50
  count_type: at_least

collection:
  complete: false
  termination:
    reason: violation_threshold_reached
    threshold: 50
```

If a full traversal occurs, `count_type: exact` is appropriate.

An implementation or enterprise policy may impose a stricter operational cap than the content requests, but this must be visible in the result rather than silently changing reporting behavior.

## 14. Decisive outcome explanation

Iteration 001 uses a **decisive outcome explanation** rather than relying on free-form root-cause text or a complete OVAL-style result graph.

For an automated Fail, the scanner should emit the smallest evaluated expression subtree, or set of subtrees, sufficient to prove the reported outcome. Atomic decisive assertions carry subject, actual value, operator, expected value, outcome, and evidence references.

Boolean proof semantics determine what must be retained:

- a failed AND needs at least one failed child to prove failure;
- a failed OR needs a decisive failure from every required alternative;
- a failed NOT reports the successful child condition that made the prohibited condition true;
- universal population checks may fail from one violating item;
- positive existence failures require evidence that the searched scope was complete;
- conditional results separately record branch-selection evidence and the decisive outcome explanation inside the selected branch.

The result distinguishes decisive findings, optional additional findings, supporting context, and unevaluated branches. It also distinguishes outcome completeness from diagnostic completeness.

Collection errors, unsupported capabilities, parse errors, and similar conditions are structured result reasons, not compliance root causes.

A human-readable summary may be generated from the structured explanation, but consumers should not need to parse prose to determine why a rule failed.

The detailed prototype contract is documented in `result-explanation-model.md`.

A forensic result profile may retain the complete evaluation trace when needed for debugging or migration validation.

## 15. Result outcomes

The current direction is a small primary outcome vocabulary such as:

- `pass`
- `fail`
- `not_applicable`
- `not_evaluated`
- `indeterminate`
- `error`

Specific reasons belong in structured reason codes rather than forcing many overloaded top-level outcomes.

Examples include incomplete collection, permission denied, unsupported capability, missing required value, parse error, timeout, and intentional short-circuiting.

The exact vocabulary remains subject to review.

## 16. Result profiles

The discussion identified a likely need for different levels of detail:

**Compact** — outcome, decisive reason/comparisons, completeness, and essential evidence;  
**Explain** — enough evidence and branch information for a human to understand the decision;  
**Forensic** — full diagnostic trace or references to detailed collected observations.

The normal enterprise result should not embed copies of policy or assessment definitions. It references the immutable signed benchmark digest.

A reporting UI can join that digest to the locally stored benchmark and show all policy text alongside the result without transmitting the policy 100,000 times.

## 17. Reusable automation and reusable policy structure

Automation reuse should be first-class, but reuse must not silently imply policy equivalence.

A reusable assessment can be parameterized. Multiple policy rules can use the same technical assessment with different thresholds or role parameters when the assessment contract explicitly permits those parameters.

Iteration 001 also demonstrated that policy membership and rule identity should be separate concepts. A policy rule should not need to embed the identity of every benchmark that contains it. Benchmark membership belongs to the benchmark/profile structure; source provenance belongs to provenance metadata. This permits exact policy-rule reuse when complete policy semantics are genuinely identical without forcing it as a common DISA publishing pattern.

A reusable semantic assessment may have platform-specific implementations only when the resulting semantic contract remains equivalent. Similar titles, CCI references, or policy concepts are insufficient evidence of equivalence.

The Windows Client and Windows Server prototypes deliberately exercise cross-benchmark reuse with different policy rule IDs and wording.

## 18. Combined rule versus split policy/assessment/binding

Two source architectures are being prototyped. Both now demonstrate genuine cross-STIG automation reuse.

### 18.1 Combined rule with constrained shared-rule overlays

A normal combined rule contains policy and its assessment in one object.

For reuse across policies, iteration 001 adds a build-time shared-rule model:

1. a reusable combined rule base contains common rule semantics and automated assessment logic;
2. a STIG-specific overlay supplies policy identity/wording and declared assessment parameter values;
3. the build resolves the base and overlay into a complete scanner-facing rule;
4. validation requires the resolved policy portion to match the authoritative policy-only rule.

An overlay must not directly patch collector/assertion logic. A change to shared automated semantics requires a new shared-rule version. Parameter values are legal only when declared by the shared rule's parameter schema.

Advantages to test:

- retains a rule-centric authoring view;
- supports cross-STIG reuse without duplicating assessment logic;
- produces simple fully resolved scanner-facing rules;
- can keep policy-specific identity and wording separate from reusable automation.

Risks to test:

- introduces inheritance/overlay semantics;
- source dependencies may be less obvious than a single complete file;
- override rules must be tightly constrained to prevent accidental semantic divergence;
- provenance/versioning across base rule and overlay may become complex.

### 18.2 Split policy / assessment / binding

Policy, assessment, and their binding are separate objects.

The same Windows prototypes represent shared technical assessments once and bind them to different policy rules, including parameterized reuse.

Advantages to test:

- explicit reuse and composition;
- independent policy/automation provenance;
- natural fit with current internal SCAP development practice;
- straightforward policy-only publication;
- shared technical assessments across rules and benchmarks.

Risks to test:

- mapping bookkeeping;
- dangling references;
- harder one-file human review;
- potentially greater content-tool complexity.

### 18.3 Refined architecture question

The iteration 001 question is no longer whether both designs can support reuse. Both can.

The more useful question is which abstraction is safer and easier to author, validate, version, migrate from SCAP 1.4, review in source control, explain to content publishers, and implement consistently:

- **inheritance plus constrained overlays**, or
- **explicit policy + assessment + binding composition**.

Regardless of source representation, a published automated `.scapng` package should contain complete resolved policy and automation. Shared source dependencies are build-time concerns, not scanner runtime dependencies.

The purpose of the prototypes is to decide this question from concrete complex examples rather than preference.

## 19. Migration from SCAP 1.4

Migration should be designed as a staged process.

### 19.1 Semantic inventory

The existing XSD corpus should be mined to inventory constructs, types, operations, behaviors, status semantics, deprecations, and platform-specific features.

The XSDs are migration requirements, not a blueprint for the new architecture. A mechanical XSD-to-JSON conversion would preserve too much existing complexity.

### 19.2 Deprecated OVAL constructs

A construct marked deprecated in OVAL should not automatically become a native SCAP-NG capability.

Deprecated constructs must still be recognized by migration tooling so old content is not silently lost.

The inventory should record deprecation status, rationale, and replacement when known.

Migration can map deprecated constructs to a modern equivalent, retain them temporarily through legacy compatibility, require review, or mark them unsupported.

### 19.3 Faithful lift before normalization

Existing content should first be represented without semantic change.

A migration status model should distinguish concepts such as:

- exact native;
- exact normalized;
- legacy compatible;
- requires review;
- unsupported.

Only after faithful migration and equivalence testing should duplicate assessments be deduplicated or complicated graphs rewritten into simpler NG constructs.

### 19.4 Differential equivalence testing

Converted content should be tested by comparing legacy and NG behavior against equivalent fixtures or target systems.

Schema validity alone is insufficient. Applicability, pass/fail behavior, missing-value behavior, collection errors, boundary cases, and decisive observed values must remain equivalent.

## 20. Relationship to policy publication

A strategic goal is to make SCAP-NG useful to DISA even without automation.

A DISA policy-only package could be converted from the fields DISA already maintains. Check Content becomes the default manual procedure.

An automation-producing organization could then create a complete automated benchmark that contains the policy plus automation. The scanner operator installs only that complete benchmark, not separate potentially mismatched policy and automation packages.

This avoids asking DISA to maintain duplicate manual-question artifacts while still allowing scanners to conduct policy-only manual assessments.

## 21. Repository and publication workflow

The current research repository separates:

- `research/` — architectural discussion, prototypes, feedback, and design evidence;
- `schema/` — future normative or experimental schema definitions;
- `tools/` — reusable research, conversion, validation, and packaging utilities.

Research is organized into numbered iterations to keep the base directory stable.

Source authoring is expected to use small Git-friendly files. Published automated benchmarks are expected to be compiled/resolved into one signed self-contained package.

## 22. What iteration 001 is intended to prove

Iteration 001 does not attempt to prove that the proposed syntax is final.

It is intended to answer whether the fundamental ideas remain understandable when applied to complex cases:

1. Can a conditional rule be easier to author and easier to explain than an equivalent Boolean workaround?
2. Can a nested OVAL-style AND/OR tree produce a small result that identifies the decisive root cause?
3. Can a very large filesystem check remain correct while returning only a bounded number of violations and optionally terminating early?
4. Can existing STIG Check Content drive useful manual assessment with no separate questionnaire?
5. Which content organization is more maintainable: combined rule or split policy/assessment/binding?
6. Can both architectures compile into the same self-contained signed distribution concept and equivalent result semantics?

## 24. Scoring direction

SCAP-NG should define deterministic benchmark scoring rather than merely inherit XCCDF's per-rule weight field without examining how it is actually used.

Every scored applicable rule needs an effective numeric weight. The current leading direction is for severity to determine the default effective weight through a standard or scoring-profile mapping, rather than requiring content authors to populate a separate weight on every rule.

An explicit per-rule weight override may still be necessary for migration fidelity or specialized profiles, but it should be exceptional and provenance/justification-aware rather than routine authoring.

The exact severity-to-weight values remain open.

Scoring must also distinguish compliance from assessment completeness. A benchmark that passes every successfully evaluated rule but has collection errors or unevaluated applicable rules should not appear indistinguishable from a complete clean assessment.

Iteration 001 should therefore prototype and seek feedback on:

- the exact severity-to-weight mapping;
- whether per-rule overrides are allowed and under what conditions;
- treatment of `not_applicable`, `error`, `indeterminate`, and `not_evaluated` in scoring;
- whether a separate assessment-coverage percentage is mandatory;
- how raw weighted totals are represented so the percentage is reproducible.

## Appendix A — Accepted design directions for iteration 001

These are working design directions, not immutable specification requirements.

A1. Forward conversion from SCAP 1.4 is essential; reverse conversion is not a primary constraint.

A2. XML is not required for SCAP-NG.

A3. Existing trusted content must be preservable before normalization.

A4. Native semantic collection is preferred over opaque command execution.

A5. Policy-only content is valid and useful.

A6. Existing policy Check Content should be usable directly as the default manual assessment procedure.

A7. Automated benchmarks distributed to scanners should be self-contained, combining complete policy and required automation in one installable package.

A8. A ZIP-based signed bundle is the leading distribution model.

A9. Static content should be stored once in enterprise result systems; endpoint results reference exact content digests.

A10. Result explainability is normative rather than a vendor-specific enhancement.

A11. Content may cap detailed evidence returned for large violation populations.

A12. Scanners may terminate expensive collection once the result is logically invariant, provided the result discloses completeness/termination semantics.

A13. `if / elif / else` should be explored as a native declarative construct.

A14. Deprecated OVAL constructs are migration inputs but do not automatically justify native NG features.

A15. The XSD corpus should be semantically inventoried rather than mechanically transformed into the NG schema.

A16. Complex AND/OR results should identify concise decisive root causes and reserve full trace data for forensic detail.

A17. Authoring-source reuse and scanner-facing distribution are separate concerns. Shared source dependencies should be resolved into self-contained published packages.

A18. Benchmark membership should be expressed by benchmark/profile structure rather than by embedding benchmark identity as generic rule-source metadata.

A19. Policy provenance should be represented separately from normative policy references such as CCI.

A20. Both architecture candidates must be evaluated with genuine cross-benchmark reuse: constrained shared-rule overlays for the combined model and explicit bindings for the split model.

A21. Combined-rule overlays must not directly alter shared assessment logic; automated semantic changes require versioned shared-rule changes. Declared parameters may specialize reusable logic.

A22. Build validation should verify that an automated resolved rule preserves the authoritative policy-only rule semantics.

A23. Benchmark scoring must be deterministic and reproducible. Severity-derived effective weight is the leading default direction; exact mappings and override rules remain open.

A24. Automated results should contain a structured decisive outcome explanation. For Fail, this is the minimal evaluated expression subtree or set of subtrees sufficient to prove failure, with evidence references and explicit completeness semantics.

A25. Logical failure explanation, additional remediation findings, supporting Pass context, and unevaluated branches are distinct result concepts.

A26. Error/collection failure reasons are not compliance root causes and must remain distinct from Fail explanations.

## Appendix B — Questions that must be answered before a specification can stabilize

### Architecture

**ARCH-001:** Should policy and automation be authored as one combined rule object or as separate policy, assessment, and binding objects?

**ARCH-002:** If the combined model is selected, are constrained shared-rule overlays a sufficiently clear and safe reuse mechanism, and which policy fields may legally be overlaid?

**ARCH-003:** If the split model is selected, what validation and tooling are required to eliminate mapping/version mistakes and make dependencies as understandable as a resolved combined rule?

**ARCH-004:** Should the compiled scanner-facing representation preserve the source architecture exactly, or may a compiler normalize either source model into one internal package model?

**ARCH-005:** Which policy properties belong to reusable rule identity versus benchmark membership or source provenance?

**ARCH-006:** For the combined model, should overlay resolution be normative source semantics or only a standardized build convention?

**ARCH-007:** What provenance must a resolved rule retain about its shared base, overlay, parameters, and digests?

### Policy and manual assessment

**POL-001:** What minimum policy fields are required for a valid policy-only benchmark?

**POL-002:** Is policy Check Content always the default manual procedure, or can publishers explicitly disable manual execution?

**POL-003:** What standardized manual result choices are required, and how should existing STIG vocabulary map to them?

**POL-004:** How should manual evidence, assessor identity, comments, and N/A justification be represented without recreating OCIL complexity?

### Automated expression model

**AUTO-001:** What exact semantics should `if / elif / else` have for indeterminate/error conditions in a `when` expression?

**AUTO-002:** Which Boolean, comparison, quantifier, set, string, version, numeric, time, and transformation operations belong in the core expression language?

**AUTO-003:** How should local/derived values and external parameters replace OVAL variables while remaining deterministic?

**AUTO-004:** Should an assessment be allowed to select between multiple collection implementations based on scanner capabilities?

### Boolean evaluation and diagnostics

**BOOL-001:** Should short-circuit evaluation be the default for AND/OR, or merely permitted?

**BOOL-002:** Should content authors be able to request a maximum number of additional independent failure causes after the outcome is already known?

**BOOL-003:** How should `outcome_complete` and `diagnostics_complete` be represented?

**BOOL-004:** What algorithm or definition should determine a "minimal explanatory failure set" for arbitrary nested expressions?

### Evidence and scale

**EVID-001:** Is `max_records` an author requirement, a hint, or a maximum that enterprise policy may reduce?

**EVID-002:** What count-quality vocabulary is required: exact, at_least, estimated, unknown?

**EVID-003:** When may a scanner terminate population collection without computing an exact total violation count?

**EVID-004:** Should pass results normally store representative evidence, summary evidence, or only a decisive assertion summary?

**EVID-005:** What evidence-sensitivity and redaction controls belong in the standard?

### Results

**RES-001:** What is the final top-level result vocabulary?

**RES-002:** Which fields are mandatory in every automated Pass and Fail explanation?

**RES-003:** Should compact/explain/forensic be normative result profiles?

**RES-004:** How should shared evidence be referenced by many rule results without duplication?

**RES-005:** What streaming representation is needed for 100,000+ endpoint ingestion?

**RES-006:** Should a compact binary encoding such as CBOR be standardized or left to transport systems?

### Collection capabilities

**CAP-001:** Which native capability families are required for an initial release?

**CAP-002:** How are new capability families registered and versioned without repeating OVAL's schema proliferation?

**CAP-003:** What capability-negotiation information must a scanner expose?

**CAP-004:** How are equivalent observations defined strongly enough that different scanner implementations can optimize collection safely?

### Command execution

**CMD-001:** What restrictions apply to command fallback collectors?

**CMD-002:** Must command output conform to a declared typed schema?

**CMD-003:** Can command execution ever directly determine compliance, or must it always return evidence evaluated by an assertion?

### Reuse

**REUSE-001:** What constitutes the identity of a reusable assessment: stable ID plus version, digest, or both?

**REUSE-002:** How are parameterized assessments versioned when logic changes but the conceptual requirement remains the same?

**REUSE-003:** How should cross-platform variants be represented without implying false semantic equivalence?

**REUSE-004:** What provenance is required when one assessment originates from a different publisher than the policy?

### Applicability

**APP-001:** Should applicability use the same expression language as compliance assertions?

**APP-002:** How should CPE and other existing product identifiers map into NG applicability facts?

**APP-003:** How are "not applicable", "could not determine applicability", and "applicability collection error" kept distinct?

### Migration

**MIG-001:** What is the complete inventory of OVAL 5.12.3 constructs actually used by current content?

**MIG-002:** Which deprecated OVAL constructs appear in trusted production content, and what are their safe migration paths?

**MIG-003:** How long should a legacy OVAL compatibility execution path remain part of SCAP-NG?

**MIG-004:** What evidence is required before a translation can be labeled `exact_native`?

**MIG-005:** Should normalization/deduplication occur automatically after equivalence testing, or always require explicit review?

### Scoring

**SCORE-001:** Should every scored rule receive its default effective weight from severity?

**SCORE-002:** What normative high/medium/low severity-to-weight mapping produces useful compliance percentages?

**SCORE-003:** Should explicit per-rule weight overrides be allowed, and if so must they include justification/provenance?

**SCORE-004:** Which outcomes participate in the compliance-score denominator?

**SCORE-005:** Should assessment coverage be a separate mandatory percentage so collection errors and unevaluated applicable rules cannot be hidden by a nominal 100% compliance score?

**SCORE-006:** Which raw weighted totals must be emitted so independent consumers can reproduce the reported score?

### Packaging and signatures

**PKG-001:** Should ZIP be the normative container format?

**PKG-002:** What exact ZIP subset and path-normalization rules are required?

**PKG-003:** Must every normative file be listed in the signed manifest?

**PKG-004:** Should deterministic ZIP construction be required in addition to logical manifest signing?

**SIG-001:** What signature technology should be normative (for example COSE, JWS, or another mechanism)?

**SIG-002:** What canonical JSON rules are required for manifest hashing/signing?

**SIG-003:** How should organizational certificate/trust policies remain separable from the content model?

### Authoring

**AUTH-001:** What restricted YAML features are allowed?

**AUTH-002:** Must source YAML have a one-to-one canonical mapping to published JSON?

**AUTH-003:** Which validation failures belong to schema validation versus semantic validation?

**AUTH-004:** What author-facing constructs are required to keep simple rules genuinely simple?

### Governance and compatibility

**GOV-001:** Who should control the core schema, capability registry, extension namespaces, and conformance tests?

**GOV-002:** What naming avoids confusion with the historical NIST SCAP v2 effort?

**GOV-003:** Which conformance classes should exist for authors, compilers, scanners, result producers, result consumers, and converters?

**GOV-004:** What compatibility guarantees should be made between SCAP-NG specification revisions?

## Appendix C — Questions specifically for the OVAL Board and NIST reviewers

C1. Which OVAL semantics are easiest to underestimate when designing a simpler object/collection/assertion model?

C2. Which OVAL 5.12.3 features are considered essential despite low apparent usage?

C3. Which deprecated OVAL constructs still appear in operational content and cannot be safely ignored during migration?

C4. Are there known cases where short-circuit evaluation would violate expected OVAL behavior or useful diagnostic assumptions?

C5. What historical SCAP/OVAL design constraints remain relevant today, and which existed primarily because of XML/schema/tooling limitations of the time?

C6. What prior SCAP v2 or related standards work should be explicitly reused rather than reinvented?

C7. What minimum evidence is necessary to claim semantic equivalence between a converted OVAL definition and a native SCAP-NG assessment?

C8. Which current result fields are relied upon by downstream products even though they appear redundant or excessively verbose?

C9. What package/signature requirements are essential for existing government content publication and validation processes?

C10. What would prevent an organization such as DISA from publishing policy-only SCAP-NG content derived directly from the information it already maintains in STIGs?

C11. Do the shared-rule overlay and split binding prototypes exercise the architecture question fairly, or are important reuse/lifecycle cases still missing?

C12. What additional complex real-world OVAL definitions should be added to subsequent prototype iterations?

C13. Does a constrained shared-rule overlay model create unacceptable inheritance/versioning complexity compared with explicit assessment bindings?

C14. Which policy fields should be considered intrinsic rule semantics, and which should instead belong to benchmark membership, profile/tailoring, or provenance?

C15. Should SCAP-NG standardize severity-derived scoring weights, and how should unresolved/error outcomes affect compliance and assessment-coverage reporting?
