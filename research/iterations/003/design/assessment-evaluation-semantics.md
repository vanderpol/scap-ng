# SCAP-NG Assessment evaluation semantics

**Status:** pre-alpha specification extraction for iteration 003  
**Authority:** current SCAP-NG working design plus semantics verified against pinned OVAL 5.12.3 source and conformance fixtures  
**Purpose:** durable evaluator contract. This document records behavior, not YAML/JSON serialization details.

This document is the current detailed home for Assessment evaluation semantics discovered during SCAP 1.4 / OVAL migration work. JSON Schema may express structural portions of this contract, but schema validation is not a substitute for these runtime rules.

## 1. Evaluation model

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

### 5.1 Zero values

Pinned OVAL 5.12.3 VariableType documentation states that a Variable returning no value produces an analysis error.

Therefore:

- `[]` is an error condition for OVAL-derived compatibility semantics;
- an implementation SHALL NOT reinterpret zero values as an empty Object population;
- `var_check` or `entity_check` SHALL NOT turn an unresolved/error Variable into a successful predicate;
- conversion tooling SHALL NOT synthesize a replacement value merely to avoid the error.

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

A runtime evaluator SHALL NOT coerce `error`, `unknown`, or other non-Boolean State outcomes using host-language truthiness.

**Open semantic item:** exact collection-status behavior for every non-Boolean filter-State outcome is not yet promoted to normative SCAP-NG text. Until supported by authoritative source and independent execution evidence, implementations/converters SHALL surface the condition rather than guess.

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
- more than one observed Item when `check_existence=only_one_exists` -> false;
- a decisive State/`check` result where additional Items cannot change the truth result according to the applicable truth table.

This semantic rule is separate from evidence truncation. A scanner MAY cap retained evidence, but a cap SHALL NOT alter assessment truth.

## 10. Early termination and evidence caps

A scanner MAY terminate collection/evaluation early only when the remaining unseen data cannot change the semantic result.

Results SHALL distinguish:

- conclusive early termination;
- incomplete/unknown evaluation;
- evidence truncation after truth has already been established.

Evidence retention limits SHALL NOT be used as evaluation limits unless the result remains semantically correct.

## 11. Conversion versus native authoring

Lossless migration SHALL preserve effective legacy semantics and source provenance, including whether values were source-explicit or inherited/defaulted.

Native SCAP-NG source SHOULD make behavior-affecting settings explicit where doing so improves reviewer clarity and avoids hidden runtime semantics.

Migration provenance SHALL remain outside executable native content except for stable source-identification metadata required by the adopted format.

## 12. Conformance evidence

Current focused executable evidence:

- `tools/oval_result_truth_tables.py`
- `tools/test_oval_result_truth_tables.py`
- `tools/test_oval_effective_attributes.py`
- `tools/test_state_entity_roundtrip.py`
- `tools/test_variable_filter_dependencies.py`
- `tools/scap_ng_roundtrip_v003/test_explicit_semantics.py`

Representation round-trip evidence is necessary but does not prove target-runtime equivalence.

## 13. Unresolved items

These remain open and SHALL NOT be silently guessed:

- exact non-Boolean filter-State outcome propagation for all cases;
- per-capability comparison/collection edge behavior not fully stated by generic OVAL schemas;
- complete runtime behavior for resource-limit/cycle failures;
- differential execution against an independent OVAL evaluator/reference scanner;
- precise early-termination proofs for every Test/quantifier combination.

As each item is resolved, the change SHALL leave behind specification text, a focused conformance fixture, and where applicable a schema/validator rule.
