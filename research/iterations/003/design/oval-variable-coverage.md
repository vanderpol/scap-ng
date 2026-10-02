# Iteration 003 OVAL Variable / Dataflow Coverage Matrix

**Status:** working conformance matrix derived from OVAL 5.12.3 XSD + Schematron.

This matrix is intended to answer a single question:

> Can native SCAP-NG represent every behaviorally relevant variable/dataflow
> construct allowed by the authoritative OVAL schema set without importing the
> legacy XML object model?

Status values:

- **native** — native NG concept exists and is intended to preserve semantics;
- **prototype** — lowering exists but conformance is not yet proven;
- **design** — required semantics are known but native representation is still
  under design;
- **test-needed** — representation exists conceptually but requires schema-driven
  conformance cases;
- **unsupported** — no lossless native representation currently exists.

| OVAL semantic area | Required semantics | Current v003 status | Required next proof |
|---|---|---|---|
| constant_variable | one or more typed literal values | prototype | multi-value constants, datatype validation |
| external_variable | externally supplied typed value set plus optional allowed values/restrictions | prototype | focused mixed possible_value / possible_restriction round-trip now covered; runtime binding validation remains conformance work |
| local_variable | one ComponentGroup member producing zero/one/many values | prototype | full recursive component coverage |
| variable_component | variable -> variable dependency | prototype | deep chains, shared dependencies, cycle rejection |
| object_component | object -> item field -> variable values, optional record_field | prototype | 0/1/many items and repeated item entities; record_field |
| literal_component | typed literal expression input | prototype | datatype/cast rules |
| arithmetic | 2+ operands; int/float; Cartesian product for collections | prototype | exact-static success/error fixtures added; runtime collection/error propagation remains #26 |
| begin | one string component plus required character/string | prototype | exact-static fixture added; collection-valued/runtime conformance remains #26 |
| concat | 2+ components; Cartesian product; DNE/error flag propagation | prototype | exact flag/result semantics |
| end | one string component plus required character/string | prototype | exact-static fixture added; collection-valued/runtime conformance remains #26 |
| escape_regex | one string component mapped over collection | prototype | exact-static escaping fixture added; independent runtime comparison remains #26 |
| split | one string component -> collection including empty values | prototype | empty-field delimiter fixture added; broader runtime edge cases remain #26 |
| substring | one string component with start/length semantics | prototype | success and out-of-range error fixtures added |
| time_difference | string/int date/time operands and format semantics | prototype | two-operand exact-static fixture added; one-operand current-time case remains runtime-dependent |
| regex_capture | one string component; capture semantics | prototype | match/no-match fixtures added; collection runtime comparison remains #26 |
| unique | de-duplicate collection values | prototype | exact-static duplicate fixture added; datatype equality cross-check remains #26 |
| count | collection -> integer count | prototype | exact-static count fixture added; DNE/error runtime cases remain #26 |
| glob_to_regex | glob conversion semantics | prototype | exact-static conversion + invalid-pattern fixtures added; differential execution remains #26 |
| merge | merge component values with delimiter/sort/order semantics | prototype | lexical success + numeric-sort error fixtures added; record/runtime variants remain #26 |
| var_ref in object entities | variable supplies selector values | prototype | all operations, multi-valued var_check |
| var_ref in state entities | variable supplies expected values | native | many-to-many var_check + entity_check truth-table ordering is covered; target execution remains #26 |
| var_ref datatype matching | referenced variable datatype must match consuming entity rules | prototype | converter now diagnoses explicit/effective string mismatches and var_check-without-var_ref; schema-derived capability validators remain the long-term source |
| var_ref on record entity | prohibited | design | static rejection |
| empty variable consumed by Object | Object considered not to exist | native | source-backed reference-context semantics and regression covered; differential execution remains #26 |
| empty variable consumed by State | State evaluation error | native | source-backed reference-context semantics and regression covered; differential execution remains #26 |
| variable evaluation error propagation | error propagates to consuming entity | native | result-state propagation tests are covered; differential execution remains #26 |
| var_check default | effective `all` when var_ref exists and var_check omitted | native | parser provenance and omitted/explicit-default regressions covered |
| var_check aggregation | all / at least one / only one / none satisfy etc. per CheckEnumeration | native | exhaustive OVAL-derived truth-table coverage |
| entity_check + var_check | two-level many-to-many state evaluation | native | ordering and non-commutative truth-table cases covered |
| nested functions | arbitrary recursive FunctionGroup composition | prototype | depth and mixed-function tests |
| dependency graph | arbitrary acyclic variable/object/state dependencies | design | DAG planner + cycle diagnostics |
| object set recursion | nested sets with schema-constrained arity | prototype | recursive set evaluation |
| set object references | 1..2 refs; referenced objects same type as parent | design | Schematron compatibility validation |
| set filters | zero..many state references applied before set operator | prototype | ordering/composition tests |
| filter action | include/exclude; default exclude | prototype | multiple/conflicting filters |
| variables inside filter states | State var_ref participates in collection filtering | prototype | chained dependency test |
| variables inside objects used by sets | variable-dependent collection feeding set | prototype | chained dependency test |
| status/flag propagation | complete/incomplete/error/DNE/not-collected/not-applicable as defined per function | native | generic truth/flag charts covered; capability-specific execution remains #26 |
| operation/datatype compatibility | operation set constrained by datatype | design | generated/static validation |
| implicit defaults | schema defaults must be normalized without semantic loss | native | #8/#9 schema-backed provenance and fail-closed behavior-default separation |
| deprecated constructs | deprecated source semantics SHALL trigger migration/update policy | design | deprecated inventory and diagnostics |

## Important structural conclusion

The OVAL schema does not support a model where variables are evaluated in a
separate phase and then simply substituted into assertions.

Variables participate in collection itself:

    variable
      -> object entity
      -> collected items
      -> object_component
      -> another variable
      -> state entity
      -> filter
      -> set
      -> another object_component
      -> another variable

Accordingly, a SCAP-NG scanner needs a dependency planner over typed nodes, not
a fixed linear `collect -> derive -> assert` pipeline.

The human-facing model can still present those concepts in that intuitive order,
but the normative execution model SHALL resolve the graph first and schedule
nodes according to dependencies.

## Reference-location rule

For native NG, the default design principle should be:

> Any typed value position MAY consume a literal or a variable/value reference
> unless the corresponding native type explicitly forbids references.

This better reflects the OVAL EntitySimpleBaseType model than adding
variable-reference support field-by-field.

The validator SHALL still enforce datatype, operation, cardinality, and
context-specific restrictions.

## Conformance gate

The v003 Assessment model SHALL NOT be considered lossless for OVAL variables
until:

1. every FunctionGroup member has a defined native semantic mapping;
2. Object and State variable references preserve var_check behavior;
3. object/state empty-variable behavior and error propagation are tested;
4. nested variable/object/set/filter dependency graphs are supported;
5. dependency cycles are rejected deterministically;
6. datatype and operation constraints derived from XSD/Schematron are enforced;
7. Self-Assertion tests cover language primitives; and
8. production RHEL 9 / Windows 11 examples cover realistic deep combinations.
