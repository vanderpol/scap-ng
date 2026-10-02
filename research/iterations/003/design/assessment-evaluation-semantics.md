# SCAP-NG Assessment evaluation semantics

**Status:** pre-alpha specification extraction for iteration 003  
**Authority:** current SCAP-NG working design plus semantics verified against pinned OVAL 5.12.3 source and conformance fixtures  
**Purpose:** durable evaluator contract. This document records behavior, not YAML/JSON serialization details.

This document is the current detailed home for Assessment evaluation semantics discovered during SCAP 1.4 / OVAL migration work. JSON Schema may express structural portions of this contract, but schema validation is not a substitute for these runtime rules.

## 1. Evaluation model

### Objectless unknown capability

The working `independent.unknown` capability preserves OVAL 5.12.3
`independent:unknown_test`: its implementation is unknown and evaluation always
produces `unknown`. It consumes no Object or State. The capability declaration
expresses this behavior; an authored Test SHALL NOT carry `result: unknown`.
That field belongs to the runtime Test result. The source-required `check`
attribute is ignored for this Test under the pinned independent XSD, so reverse
conversion may emit any valid value. Source explicitness belongs in provenance.
This is preserved source behavior, not proof of a native runtime implementation
or Board ratification of the working capability name.

An automated Assessment is a typed dependency graph of Tests, Objects, States, Variables and an `evaluate` expression.

- A **Test** evaluates Items produced by an Object, optionally against one or more States.
- An **Object** identifies a population of Items. Sets and filters are Object semantics.
- A **State** evaluates predicates against an Item.
- A **Variable** produces a typed collection of values used by Objects, States, functions or other Variables.
- `evaluate` combines Test results into the Assessment result.
- Runtime Collection is the act of evaluating an Object and producing Items plus collection status/completeness.

Reference resolution and evaluation SHALL be independent of YAML/JSON mapping key order.

## 2. Result domain

The OVAL-derived compatibility contract retains these distinct result states where the corresponding semantics are required:

- `true`
- `false`
- `error`
- `unknown`
- `not evaluated`
- `not applicable`

An implementation SHALL NOT collapse these states to Boolean pass/fail during Assessment evaluation. Rule-policy mapping occurs above the Assessment layer.

## 3. Test evaluation order

For an Object-backed Test:

1. Resolve/collect the Object and determine its collection status.
2. Evaluate `check_existence`.
3. If existence is conclusively false, that result determines the Test; State comparison cannot repair it.
4. If existence permits State evaluation and the Test references States, evaluate each State against each applicable Item.
5. Combine a single Item's referenced State results using `state_operator`.
6. Combine the resulting per-Item results using `check`.

A Test without States uses existence semantics only; `check` and `state_operator` have no behavioral effect in that case.

### 3.1 `check`

The retained OVAL values are:

- `all`
- `at least one`
- `only one`
- `none satisfy`

The six-state precedence behavior is exercised by `tools/test_oval_result_truth_tables.py`. A decisive Boolean outcome may dominate error-like outcomes where the inherited truth table says the final result is already known.

### 3.2 `check_existence`

The retained OVAL values are:

- `all_exist`
- `any_exist`
- `at_least_one_exists`
- `none_exist`
- `only_one_exists`

Existence is distinct from State value comparison and from State-entity existence.

### 3.3 `state_operator`

Multiple States referenced by one Test are evaluated independently against an Item and then combined using the Test's `state_operator`.

## 4. State evaluation and quantifier order

A State contains one or more predicates/entities combined by the State `operator`.

Where a State entity references a multi-valued Variable, evaluation order SHALL be:

1. compare one corresponding Item entity against each Variable value;
2. combine those comparisons using `var_check`;
3. if multiple corresponding Item entities exist, combine those entity results using `entity_check`;
4. combine the resulting State predicate/entity results using the State `operator`;
5. Test `state_operator` then combines multiple State results for the Item;
6. Test `check` then combines per-Item results.

These levels are not interchangeable. Implementations SHALL preserve their scopes and ordering.

## 5. Variable cardinality and status

Variables are typed collections, not scalar placeholders.

A Variable result SHALL preserve at least:

- datatype;
- zero/one/many cardinality;
- values;
- evaluation status;
- provenance sufficient to identify the source/binding.

### 5.1 Zero values and reference context

Pinned OVAL 5.12.3 generic VariableType documentation states that a Variable returning no value is an analysis-error condition. More specific entity `var_ref` documentation refines that behavior at the reference site, so native evaluation SHALL preserve **zero values as a distinct intermediate status** until reference context is known.

For OVAL-derived entity references:

- an Object entity `var_ref` that resolves to zero values causes the referenced Object to be considered **not to exist**;
- a State entity `var_ref` that resolves to zero values produces an **error** for State evaluation;
- `var_check` or `entity_check` SHALL NOT convert the zero-value/error condition into a successful State predicate;
- migration and conversion tooling SHALL NOT synthesize a replacement value merely to avoid zero cardinality.

This context-specific rule takes precedence over treating zero cardinality as one universal result. Native implementations SHOULD represent zero cardinality distinctly during Variable resolution so Object and State consumers cannot accidentally collapse the two behaviors.

### 5.2 Empty string is not zero values

`[""]` is one real string value and is not equivalent to `[]`.

An author/capability MAY intentionally define an empty string or another sentinel when its meaning and safety are explicit. Migration tooling SHALL NOT invent such sentinels. This distinction has a dedicated regression in `tools/test_oval_result_truth_tables.py`.

### 5.3 Variable status propagation

Variable resolution status is processed before `var_check`/`entity_check` aggregation. Error/unknown-like status SHALL propagate according to the applicable result contract rather than being hidden by favorable comparison rows.

## 6. Object sets

OVAL-derived Object sets retain:

- `UNION`;
- `INTERSECTION`;
- relative `COMPLEMENT`.

Set outputs are unique Item populations.

`COMPLEMENT` is directional: `A COMPLEMENT B` is not interchangeable with `B COMPLEMENT A`.

The default `set_operator` inherited from OVAL is `UNION` for migrated content. Native SCAP-NG authoring should prefer explicit behavior-affecting values rather than hidden defaults.

## 7. Filters

A filter references a State and is applied to an Object's Items before the enclosing set operator.

- The inherited default filter action is `exclude`.
- `include` retains matching Items.
- `exclude` removes matching Items.
- Multiple filters are applied to the candidate population before set combination.
- Conflicting filters may legitimately produce an empty population.

A runtime evaluator SHALL NOT coerce `error`, `unknown`, `not evaluated`, or `not applicable` State outcomes using host-language truthiness.

SCAP-NG explicitly resolves the legacy ambiguity as follows: a non-Boolean filter-State result SHALL produce a collection/evaluation **error** for the enclosing Object path. It SHALL NOT be interpreted as either an include or exclude decision.

This is an intentional native clarification rather than a claim that OVAL 5.12.3 generic schema prose defines every propagation step. Historical MITRE ovaldi behavior is used as sanity-check evidence: its core filter implementation rejects any State result other than true/false, and the Object collector converts the resulting exception to a collected-Object error. Because ovaldi predates 5.12.x, it supports the reasonableness and continuity of this rule but is not its normative authority.

## 8. Collection status and Object-set propagation

The OVAL-derived compatibility contract distinguishes collected-Object flags:

- `error`
- `complete`
- `incomplete`
- `does_not_exist`
- `not_collected`
- `not_applicable`

Direct Test mapping and set-operator flag combinations are encoded in `tools/oval_result_truth_tables.py` and exercised by `tools/test_oval_result_truth_tables.py`.

Set flag propagation is operator-specific. In particular, `COMPLEMENT` is order-sensitive. Implementations SHALL NOT reduce collection completeness/status to a Boolean before set composition.

## 9. Incomplete collection

An incomplete collection generally yields `unknown` unless already-observed evidence is sufficient to determine a conclusive outcome under the inherited Test semantics.

Examples of conclusive evidence include:

- an observed Item when `check_existence=none_exist` -> false;
- an observed Item when `check_existence=at_least_one_exists` -> true;
- an observed Item when `check_existence=any_exist` -> true, because later error/not-collected observations cannot overturn that OVAL truth-table outcome;
- more than one observed Item when `check_existence=only_one_exists` -> false;
- a decisive State/`check` result where additional Items cannot change the truth result according to the applicable truth table.

The current conformance fixtures explicitly test that every implemented early-termination shortcut is **irreversible** under additional observations. A scanner SHALL NOT add a shortcut merely because it is common or efficient; the final semantic result must be invariant for every permitted unseen continuation.

This semantic rule is separate from evidence truncation. A scanner MAY cap retained evidence, but a cap SHALL NOT alter assessment truth.

## 10. Early termination and evidence caps

A scanner MAY terminate collection/evaluation early only when the remaining unseen data cannot change the semantic result.

Results SHALL distinguish:

- conclusive early termination;
- incomplete/unknown evaluation;
- evidence truncation after truth has already been established.

Evidence retention limits SHALL NOT be used as evaluation limits unless the result remains semantically correct.

### 10.1 Dependency cycles and resource limits

Static dependency cycles are invalid Assessment content, not ordinary runtime truth outcomes.

- A compiler/validator SHALL reject statically detectable cycles involving Variables, Objects, Sets, Filters, States, Tests, or Assessment-result dependencies before target evaluation.
- Cycle diagnostics SHOULD identify the dependency path sufficiently for an author to correct the content.
- An implementation SHALL NOT resolve a cycle by arbitrary ordering, fixed-point guessing, recursion truncation, or by returning `false`.

Runtime resource exhaustion is different from a semantic cycle. Limits on recursion depth, memory, item count, wall-clock time, or implementation-specific resources MAY stop execution, but such a stop SHALL be reported as an execution/resource error or explicitly incomplete evaluation according to the applicable result contract. It SHALL NOT be reported as a semantic `false` merely because evaluation could not finish.

Evidence caps remain separate: once truth is already established, retained evidence MAY be truncated without changing the Assessment result.

## 11. Conversion versus native authoring

Lossless migration SHALL preserve effective legacy semantics and source provenance, including whether values were source-explicit or inherited/defaulted.

Native SCAP-NG source SHOULD make behavior-affecting settings explicit where doing so improves reviewer clarity and avoids hidden runtime semantics.

Migration provenance SHALL remain outside executable native content except for stable source-identification metadata required by the adopted format.

## 12. Conformance and differential evidence

The evidence hierarchy for evaluator semantics is:

1. **Normative authority:** pinned OVAL 5.12.3 schemas, Schematron, and published language documentation.
2. **Primary legacy differential reference for core OVAL behavior:** MITRE's OVAL Definition Interpreter (`ovaldi`). The accessible GitHub repository `OVALInterpreter/ovaldi` is an unofficial Git conversion of the historical SourceForge/Subversion code; its own documentation identifies the MITRE interpreter as an open-source reference implementation of the OVAL Language. Because the implementation predates OVAL 5.12.x, it is evidence for stable/core semantics, not authority for later-version additions.
3. **Secondary differential implementation evidence:** OpenSCAP. Results MAY be compared to expose implementation disagreements, but OpenSCAP SHALL NOT by itself settle an ambiguous OVAL semantic rule. A disagreement between OpenSCAP and the normative language or the MITRE reference lineage must be investigated rather than normalized into native NG behavior.

Differential execution is supporting evidence, not a replacement for normative text. When legacy evaluators disagree, SCAP-NG SHALL preserve the ambiguity until stronger source evidence or an explicit standards decision resolves it.

Current focused executable evidence:

- `tools/oval_result_truth_tables.py`
- `tools/test_oval_result_truth_tables.py`
- `tools/test_oval_effective_attributes.py`
- `tools/test_state_entity_roundtrip.py`
- `tools/test_variable_filter_dependencies.py`
- `tools/scap_ng_roundtrip_v003/test_explicit_semantics.py`

Representation round-trip evidence is necessary but does not prove target-runtime equivalence.

## 13. Sensitive-value redaction versus OVAL `mask`

A pinned corpus census on 2026-10-01 scanned 212 source files across NIWC Current and SCAP Self-Assertion, including XML inside package ZIPs, and found **zero source-explicit OVAL `mask` attributes**. XSD-inherited `mask=false` was intentionally excluded from the census.

SCAP-NG therefore SHALL NOT expose a generic OVAL-compatible `mask` property on every native Object/State entity merely because the legacy base type carried that attribute.

Where a capability can collect sensitive values, SCAP-NG SHOULD provide an explicit **sensitive-result/evidence redaction** mechanism tied to disclosure of collected evidence rather than to generic comparison syntax. Such a mechanism SHALL NOT alter collection, comparison, or Assessment truth semantics.

Migration tooling SHALL preserve source provenance if explicit legacy `mask` usage is encountered outside the pinned corpus and SHALL diagnose unsupported semantics rather than silently dropping it.

Evidence: GitHub Actions run 36931308817, source-explicit mask census; 212 files scanned, 0 explicit occurrences, 0 scan failures.

## 14. State-entity existence

OVAL State entities have their own `check_existence`, distinct from Test
`check_existence`. The pinned OVAL 5.12.3 `ExistenceEnumeration`
documentation explicitly states that its evaluation charts apply secondarily
to State entities in corresponding Items.

A conforming evaluator SHALL evaluate the corresponding Item-entity status
population with the same five ExistenceEnumeration modes before ordinary value
comparison/quantifier aggregation. In particular:

- `error` and `not collected` statuses SHALL retain their chart-defined
  `error` / `unknown` effects;
- decisive existence results SHALL NOT be replaced by favorable value
  comparisons;
- State-entity existence SHALL remain a separate scope from Test existence.

The generic chart is executable in
`evaluate_state_entity_existence()`. The helper deliberately stops at the
existence piece; it does not invent a value-comparison result when the existence
mode permits zero corresponding entities.

The EntityState base-type prose includes an example for `none_exist` phrased
in terms of one or more `does not exist` entities, while the authoritative
ExistenceEnumeration chart also defines the all-zero status population. The
native contract follows the explicit chart for the existence piece and does not
derive additional zero-entity comparison semantics from that example alone.

## 15. Record entity evaluation

OVAL-derived record values have capability-specific semantics that are stricter
than ordinary scalar entities. These rules are source-backed by the pinned OVAL
5.12.3 `EntityStateRecordType` and `EntityStateFieldType` documentation and
are part of the native compatibility contract.

For a record State entity:

- the datatype SHALL be `record`;
- the record-level operation SHALL be `equals`;
- record-level `var_ref` SHALL NOT be used;
- record-level `var_check` SHALL NOT be used;
- each expected named field is compared independently against corresponding
  same-name fields in the collected Item;
- if an expected field is absent from the Item, that field result SHALL be
  `error`;
- when an Item contains multiple fields with the same name, the field's
  `entity_check` combines the comparison results for those occurrences;
- the resulting expected-field results for one record are combined with logical
  AND;
- if multiple corresponding record entities exist at the enclosing Item/entity
  scope, the ordinary parent record `entity_check` is applied after each
  record has been evaluated.

A processor SHALL preserve field grouping. It SHALL NOT flatten record fields
into unrelated Item entities before applying the above aggregation order.

Executable coverage is provided by `tools/oval_result_truth_tables.py` and
`tools/test_oval_result_truth_tables.py`.

## 16. Unresolved items

These remain open and SHALL NOT be silently guessed:

- per-capability comparison/collection edge behavior not fully stated by generic OVAL schemas;
- differential execution against an independent OVAL evaluator/reference scanner;
- precise early-termination proofs for every Test/quantifier combination.

As each item is resolved, the change SHALL leave behind specification text, a focused conformance fixture, and where applicable a schema/validator rule.
