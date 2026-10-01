# OVAL Round-Trip Findings for the SCAP-NG Specification

**Status:** research-derived specification input, not itself normative  
**Iteration:** 003  
**Date:** 2026-09-30  
**Source authority:** pinned upstream OVAL 5.12.3 XSD and embedded Schematron, original SCAP 1.4 source; published NIWC and OVAL Self-Assertion corpora provide interoperability evidence.  
**Boundaries:** standard OVAL is in scope. SCC/NIWC `sqlext` is explicitly out of scope pending the user's planned migration to `sql512`. No XCCDF/datastream behavioral equivalence is implied by the OVAL round-trip tests.

## What the regression evidence establishes—and does not

The original OVAL → versioned semantic representation → native NG assessment → regenerated OVAL → independent canonical semantic-graph comparison exercises real corpus graphs and preserves substantially more than byte-level XML text. Self-Assertion, RHEL 9, Oracle Linux 9, RHEL 10 (singles and aggregate), Windows 11, Windows Server 2025, and a broader application/OS sample have passing applicable regression gates (standard definitions, XSD, source-baselined Schematron). These are compatibility **evidence**, not an executable proof that SCAP-NG produces identical OVAL results on a target machine, nor proof of coverage of all valid schema combinations. A bug shared by both translator and semantic comparator remains a residual risk.

- Source-relative Schematron checks mean **no newly introduced findings**, not that source content had zero findings.
- XSD-conforming references may still be *logically invalid*; validate cross-component type compatibility and execution meaning independently.
- A source may contain non-standard SCC extensions even when validated against a locally augmented schema. For *standard* OVAL classification use pinned **upstream** XSD vocabulary, not the augmented local copy.
- Only the exact pinned source/schema/tool versions and the verified regression run establish a passing claim; future edits must rerun all gates.
- Conversion preserves source defects faithfully and separately flags them; it does not silently repair upstream content.

## Findings and their specification implications

Each entry captures (a) discovery, (b) required normative direction or candidate, (c) needed proof. Requirements marked **candidate** are not automatically ratified.

### 1. Collector/Test/State identity, shape, and compatibility

**Discovery:** nginx SV-278400 uses `unix.file_test` with `independent.shellcommand_object` and `independent.shellcommand_state`. Initial conversion silently retagged the Object/State as `unix.file`. An ID-independent graph comparison detected the mismatch; keeping separate Test/Object/State capability identities restored round-trip fidelity. This appears to be a *source-content defect* that schema validation missed, not an intended normative NG cross-family feature.

**Specification:** a Collection and an assertion predicate SHALL retain their independently declared typed interfaces; conversion SHALL NOT infer either from its caller. A validator SHALL check compatible Test-to-Object and Test-to-State bindings and give a source-fidelity diagnostic when invalid. Preserving invalid source structure for diagnosis SHALL NOT imply it is valid or executable native NG content.

**Proof:** positive matching-family examples; negative cross-family example (SV-278400); nested variable/object component type checks; conformance diagnostics with source locations.

### 2. Complete graph closure and cycles

**Discovery:** RHEL 10 chains reached at least 10 dependency edges, other corpora include Variable→Object→Set→Object and Variable→Object→Variable chains. A SQL `sqlext` Object hidden behind an `object_component` initially escaped the unsupported-feature walker.

**Specification:** reference resolution, unsupported-feature detection, cycle checks, provenance inventory, execution scheduling and graph equivalence SHALL all traverse the same complete closure, including extended Definitions, criteria, Tests, Objects, States, filters, nested set members, Object components, Variable components, function operands and external inputs. Native evaluation SHALL schedule a typed dependency DAG rather than assume a fixed one-pass 'collect then derive then assert'. Missing references and unsupported reachable nodes SHALL be reported, never ignored. Cycle policy and error propagation need specified outcomes.

**Proof:** deep mixed chains, intentionally missing references, cycles, reused subgraphs, extension behind nested variable and filter.

### 3. Variables are typed collections, not scalar placeholders

**Discovery:** local variables can recursively call Objects or other Variables; function operands may carry zero/one/many values. The OVAL model requires `var_check` and `entity_check` as distinct quantifiers. A source review correction on 2026-10-01 confirmed that OVAL 5.12.3 `VariableType` documentation states that a variable returning no value is an analysis error generally; SCAP-NG SHALL NOT reinterpret an empty variable as Object absence or invent a separate Object-versus-State rule without stronger normative evidence.

**Specification:** value-producing nodes SHALL carry datatype, cardinality, value set, evaluation status and provenance. Define zero-values, error, unknown and not-collected distinctly. The semantic model SHALL describe ordered/unordered combinations, Cartesian products, variable quantification and datatype validation where applicable. An input constrained to modify expected state SHALL NOT be able to change command text, selected collectors or execution privileges.

**Proof:** multi-value constants, zero-value variable analysis-error fixtures at Object and State reference sites, many-to-many quantifier truth tables, Cartesian-product function tests, record_field extraction, errors propagating across dependencies.

### 4. External variable value constraints were genuinely missing

**Discovery:** late v003 regression commits added preservation, regeneration and semantic comparison of `external_variable` allowed value/restriction information. A round-trip that compares only a variable ID, datatype, or binding would miss changes in its permitted input domain.

**Specification:** the native Parameter/Organizational Input contract SHALL represent allowed values and restrictions and enforce the constraints *before* runtime binding. It SHALL specify datatype, multiplicity, restriction evaluation and invalid-input outcomes. Migrated constraints SHALL remain distinguishable from organization-specific tailoring provenance. Restriction expressions must be audited for prompt/text injection into executable collectors.

**Proof:** allowed values, restriction patterns/ranges, mixed lists, invalid input, omitted versus unconstrained domain, round-trip and execution validation.

### 5. State grouping occurs at two independent Boolean levels

**Discovery:** one OVAL Test may refer to multiple distinct State elements combined via `state_operator`; each individual State can itself combine multiple entity predicates using its own operator. Collapsing the boundaries caused round-trip/schema failures.

**Specification:** explicitly model Test-level state association plus State-level entity conjunction/disjunction. Preserve scope and quantifier order. A native author may express these more readably, but Stage-1 lowering SHALL NOT collapse them without proof of equivalent error/unknown semantics.

**Proof:** AND/OR state combinations, nested entity predicates, multiple-state tests, XSD and executable truth tables.

### 6. Criteria edge semantics are not merely XML decoration

**Discovery:** real-world `extend_definition` plus `negate`/`applicability_check` edges caused RHEL10 mismatches; correcting edge-flag canonicalization repaired many definitions at once. Flattening an extended Definition changes XML serialization while preserving truth semantics if flags are applied at exactly the same scope.

**Specification:** criteria SHALL support AND, OR, ONE, XOR and the appropriate negation/applicability flags. Extended-Definition references MAY be dereferenced during migration only when their complete truth semantics, scoping and outcome propagation remain equivalent. Nested Definition metadata should go into a separate provenance ledger.

**Proof:** nested flags, XOR/ONE, extended dependencies with several levels, AND/OR truth and error tables, deliberate cycles.

### 7. Collection composition is not interchangeable with State assertion

**Discovery:** OVAL Objects may have behaviors, filters, and recursively nested set expressions with UNION/INTERSECTION/COMPLEMENT and associated referenced States. Object selector operations and State comparisons both use variables but differ in effect and result semantics.

**Specification:** preserve collection selection, set combinators, filter polarity/order, behaviors, existence, state comparisons and evidence boundaries as separate concepts. Do not transform a collection constraint into a result assertion without demonstrating equivalence. Collection and comparison operations need capability-specific field typing.

**Proof:** set/member/filter combinations, zero collections, nested filters, multi-value variables, conflicting filters, cardinality tests.

### 8. Existence and quantifiers are central

**Discovery:** many failures are 'item exists when prohibited' or 'required item absent'. Source `check_existence`, `check`, `var_check`, `entity_check` have different scopes and defaults. Existence-only Tests can lack a State entirely.

**Specification:** each scope SHALL be explicit with well-defined defaults and truth tables, including none_exist and at_least_one_exists. Structured failure reasons SHOULD distinguish unexpected existence, missing expected items, mismatched values and collection errors. Evidence cap/early stop MAY limit records but SHALL NOT alter truth conditions.

**Proof:** zero/one/many results with States absent/present, each quantifier, unknown/error, early-stop effects.

### 9. Schema-valid does not mean content-valid

**Discovery:** nginx type inconsistency passed existing schema checks. Upstream XSD constrains element grammar and some keyrefs; embedded Schematron catches additional issues, but neither substitutes for semantic binding validation or execution.

**Specification:** separate validation passes: lexical/schema, XSD-derived vocabulary, Schematron, referential graph, type compatibility, semantic/static checks, runtime/differential execution. A passing generic OVAL document SHALL not be presented as proven executable correctness without the applicable stages.

**Proof:** intentional negative fixtures for each stage, with precise error categories and expected diagnostics.

### 10. Authoritative upstream vocabulary versus publisher extensions

**Discovery:** bundled SCC-augmented independent schema declared `sqlext_*`, while pinned upstream OVAL 5.12.3 did not. The generic converter initially treated those as standard and emitted XML invalid against authoritative upstream XSD. Correct classification requires recursive detection, including extensions hidden within dependent objects.

**Specification:** standard language surfaces SHALL derive from pinned upstream XSD/Schematron and a versioned exception/reinstatement ledger. Publisher extensions SHALL be namespaced and isolated, never silently elevated to standard capability status. `sqlext` is **out of scope** and is not a normative SCAP-NG capability. Conversion SHALL report an explicit blocker without treating this as a converter defect. Future `sql512` content can enter standard compatibility tests.

**Proof:** SQL Server published corpus, nested extension dependencies, intentionally conflicting augmented versus upstream schema.

### 11. Deprecated Tests: reject rather than guess

**Discovery:** real Windows and SQL corpora exercise deprecated tests, and OVAL schema deprecation annotations have documented effective-status exceptions/reinstatements.

**Specification:** a native NG processor SHALL NOT support deprecated OVAL Tests as native capabilities; conversion SHALL report each exact reachable deprecated type and documented replacement where available. An explicit versioned governance/reinstatement decision may supersede old annotations, but never silently substitute a supposedly equivalent test. Keep that decision separate from extension classification.

**Proof:** one fixture per deprecated family, negative traversal through extended Definition/variables, reinstatement overrides and auditable versioning.

### 12. Semantic identity, deduplication, and reuse

**Discovery:** the RHEL10 aggregate contains duplicates; canonical equivalence and deduplication reduced repeated dependency nodes while retaining equal root Definition semantics. XML IDs and output element ordering may differ without changing behavior, but over-aggressive reuse would be dangerous.

**Specification:** separate stable logical identity, semantic equivalence fingerprint, file location, and legacy source identifier. Deduplication MAY occur only where capability type, selectors, operators, quantifiers, external inputs, errors and evidence-relevant semantics are proven equivalent. Preservation of same-name/different-semantics nodes must be tested.

**Proof:** aggregate pre/post graph compare, adversarial near-equal nodes, shared variables and distinct source IDs.

### 13. Descriptive metadata, actual semantics, and provenance

**Discovery:** a new generated document can be semantically equivalent despite different IDs, ordering, generator metadata, criteria comments, and flattened extended Definition structure. Root Definition class, version (including legitimate version 0) and deprecation are substantive compatibility metadata and were explicitly added to comparison.

**Specification:** specify distinct authoritative Assessment metadata, truth semantics, build/package provenance and legacy migration lineage. Retain useful human-readable Test/Object/State/Variable descriptions without making them execution inputs. Do not invent replacement metadata by assuming source version is positive. Document classification for each allowed structural difference; **unclassified differences fail**.

**Proof:** version 0, root class/version/deprecation variants, metadata-only edits, generator changes, source lineages, full diff report.

### 14. Results and observability

**Discovery:** author-facing root causes need existence-focused messages; large scans require evidence caps; complete raw SCAP/ARF payloads are too heavy. Semantic conversion evidence alone cannot establish the meaning of actual runtime results.

**Specification:** results SHALL identify effective policy context, selected assessment/selector, parameter binding provenance, target identity, capability outcome, evaluation status, completeness/truncation and structured failure reason. Preserve 'why' independently of capped evidence; distinguish early termination with a conclusive result from incomplete evaluation. Do not collapse unknown/error/not-evaluated/not-applicable into pass/fail.

**Proof:** executable reference scanner and differential evaluation against known ground truth/SCC, including 0/1/million records and capped evidence.

### 15. Security and deterministic computation

**Discovery:** some native capabilities run shell commands, inspect SQL, parse files, and dereference untrusted object/variable graphs. Legacy external inputs can affect collection targets or commands.

**Specification:** define capability-specific safety boundaries, privileges, execution sandbox, time/resource limits, sensitivity and redaction, resolver cycle and expansion limits, and safe input binding. Stage-1 lossless conversion may retain legacy execution-affecting input only in explicitly separated compatibility mode; Stage-2 native source SHALL enforce restricted organizational inputs.

**Proof:** malicious input fixtures, large Cartesian-product limits, dependency bombs, credential-bearing evidence, command injection checks.

## Specification extraction order

We should **start now** by deriving a versioned semantic requirements catalog from every authoritative XSD and Schematron component:

1. **Core OVAL definition grammar:** criteria/criterion/extend_definition, class/version, logical operators, flags, evaluation statuses.
2. **Generic tests/objects/states:** check/check_existence, multi-state operators, collection selectors, states/entity comparison/quantifiers, sets/filters/behaviors.
3. **Variables and functions:** constant/external/local, permitted restrictions, all component/function semantics, collections, Cartesian product and dataflow/error propagation.
4. **Common capability entity schemas:** OVAL's platform and Independent test families, each Object/State entity type, nil/record treatment, allowed operations, datatypes and schema defaults.
5. **Per-capability evaluation behavior:** collection mechanics, evaluation outcomes, error/unknown/not-collected behavior, safety limitations, field-specific semantics.
6. **OVAL results and system characteristics:** use them to define runtime outcome/evidence semantics, not to copy entire legacy result XML.
7. **Language validation constraints:** compile an automated rule catalog identifying whether XSD, Schematron, an NG semantic validator or a runtime conformance case enforces each rule.

For every extracted rule, record: upstream source path, source anchor/element, kind (structural/semantic/runtime/security), precise inherited behavior, normalized NG concept, whether normative or deferred, evidence fixture, and conformance test status. Preserve a link to the original upstream reference instead of dumping XML annotations into native schema.

### What belongs in specification NOW

- Core Assessment contract, typed Collection/State/Test separation, dataflow and graph closure, quantifiers, existence and error semantics, constraints, standards vocabulary boundary, and core semantic validation.
- An explicitly **provisional** capability family/type inventory with upstream source anchors.
- Normative requirements that are independently supported by schema, Schematron and working examples.
- Open questions recorded visibly rather than made artificially normative.

### What should wait until the reference scanner exists

- Detailed collector implementation behavior for every platform-specific type.
- Normative exact execution/error propagation tables wherever OVAL prose or run behavior remains ambiguous.
- Decisions about revised NG-native ergonomics that intentionally depart from OVAL.
- Full conformance certification claims and complete execution equivalence.

## Stage gates

**Gate A (now):** complete schema/Schematron extraction inventory and map each rule to draft NG contract, with missing-mapping counts; incorporate demonstrated semantics into draft Assessment specification and unit fixtures.

**Gate B (before declaring v003 conversion frozen):** complete pinned standard-OVAL census; make unsupported/deprecated/extension decisions explicit; zero unexplained semantic/structural differences; preserve source defect diagnostics.

**Gate C (reference scanner):** implement capability interface plus typed graph evaluation; build independent execution truth tables and compare representative source OVAL evaluation to NG behavior. No blanket compatibility claim before this.

**Gate D (normative assessor detail):** finalize per-capability assessor semantics and conformance tests only for capabilities with evidence, while keeping other capabilities provisional; reserve all missing/deferred semantics on a published coverage matrix.

## Existing documents to reconcile

- `specification/assessment/assessment-method.md`: core model.
- `specification/migration/oval-5.12.3-to-ng.md`: semantic mappings.
- `specification/migration/oval-5.12.3-capability-crosswalk.md`: remove `sqlext` from standard candidate inventory, recalculate coverage.
- `research/iterations/003/design/variable-dataflow.md` and `oval-variable-coverage.md`: detailed current variable requirements, update status after new conformance evidence.
- `research/iterations/003/design/conversion-contract.md`: specific flattening/extension decisions.
- `specification/core/conformance.md`: add type consistency, graph closure, supported vocabulary and failure isolation checks.
- `specification/results/results.md`: runtime evidence and outcome requirements.

This ledger SHALL be maintained as the OVAL corpus and reference scanner reveal further requirements. It is not a claim that all enumerated behaviors are already implemented.
