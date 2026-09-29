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
| external_variable | externally supplied typed value set plus optional allowed values/restrictions | prototype | round-trip case covers possible_value and possible_restriction; execution binding still needed |
| local_variable | one ComponentGroup member producing zero/one/many values | prototype | full recursive component coverage |
| variable_component | variable -> variable dependency | prototype | deep chains, shared dependencies, cycle rejection |
| object_component | object -> item field -> variable values, optional record_field | prototype | record_field round-trip covered; 0/1/many runtime item behavior remains |
| literal_component | typed literal expression input | prototype | typed-literal round-trip covered; datatype/cast runtime rules remain |
| arithmetic | 2+ operands; int/float; Cartesian product for collections | prototype | product cardinality, casts, error propagation |
| begin | one string component plus required character/string | prototype | collection-valued input and datatype constraints |
| concat | 2+ components; Cartesian product; DNE/error flag propagation | prototype | exact flag/result semantics |
| end | one string component plus required character/string | prototype | collection-valued input |
| escape_regex | one string component mapped over collection | prototype | exact escaping subset |
| split | one string component -> collection including empty values | prototype | delimiter edge cases |
| substring | one string component with start/length semantics | prototype | boundary/error cases |
| time_difference | string/int date/time operands and format semantics | prototype | complete format/type cases |
| regex_capture | one string component; capture semantics | prototype | no-match and collection behavior |
| unique | de-duplicate collection values | prototype | datatype equality rules |
| count | collection -> integer count | prototype | zero/DNE/error inputs |
| glob_to_regex | glob conversion semantics | prototype | round-trip representation covered; exact execution conversion rules still need interpreter tests |
| merge | merge one or more component value sets with delimiter/sort/order semantics | prototype | round-trip representation covered; execution ordering semantics still need interpreter tests |
| var_ref in object entities | variable supplies selector values | prototype | all operations, multi-valued var_check |
| var_ref in state entities | variable supplies expected values | prototype | round-trip many-to-many var_check + entity_check covered; truth-table execution still needed |
| var_ref datatype matching | referenced variable datatype must match consuming entity rules | design | validator generated from schema constraints |
| entity mask | mask suppresses corresponding collected value in OVAL Results while retaining definition semantics | prototype | round-trip covered; NG result redaction semantics still to define |
| nillable entities | xsi:nil remains distinct from empty string where component schemas permit nil | prototype | round-trip covered; native syntax uses explicit nil state |
| record-valued entities | record parent plus named fields, per-field operation/entity_check/mask/var_ref semantics | prototype | non-deprecated sql512 State round-trip covered; broader runtime evaluation remains |
| State operator | combines State entity predicates; default AND | prototype | non-default OR round-trip covered |
| criteria applicability_check | marks criteria/criterion/extended definition as applicability evaluation | prototype | criterion applicability round-trip covered; NG applicability lowering remains architectural |
| var_ref on record entity | prohibited | design | static rejection |
| empty variable consumed by Object | Object considered not to exist | design | execution/result conformance |
| empty variable consumed by State | State evaluation error | design | execution/result conformance |
| variable evaluation error propagation | error propagates to consuming entity | design | result-state tests |
| var_check default | effective `all` when var_ref exists and var_check omitted | design | parser normalization |
| var_check aggregation | all / at least one / only one / none satisfy etc. per CheckEnumeration | design | evaluation truth tables |
| entity_check + var_check | two-level many-to-many state evaluation | prototype | structural/semantic round-trip covered; exhaustive execution truth-table tests remain |
| nested functions | arbitrary recursive FunctionGroup composition | prototype | broad FunctionGroup round-trip coverage exists; deeper mixed nesting and runtime flag semantics remain |
| dependency graph | reference-driven variable/object/state dependencies | design | planner/order proof; indirect-cycle rejection is pending OVAL Board review |
| object set recursion | nested sets with schema-constrained arity | prototype | direct recursive Set round-trip covered; runtime set evaluation remains |
| set object references | 1..2 refs; referenced objects same type as parent | design | Schematron compatibility validation |
| set filters | zero..many state references applied before set operator | prototype | ordering/composition tests |
| filter action | include/exclude; default exclude | prototype | multiple/conflicting filters |
| variables inside filter states | State var_ref participates in collection filtering | prototype | chained dependency test |
| variables inside objects used by sets | variable-dependent collection feeding set | prototype | chained dependency test |
| status/flag propagation | complete/incomplete/error/DNE/not-collected/not-applicable as defined per function | design | schema evaluation-chart tests |
| operation/datatype compatibility | operation set constrained by datatype | design | generated/static validation |
| implicit defaults | schema defaults must be normalized without semantic loss | design | comparator normalizes major exercised defaults; full schema-wide default inventory remains |
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
5. direct self-reference is rejected, and the Board resolves the proposed rule for indirect dependency cycles;
6. datatype and operation constraints derived from XSD/Schematron are enforced;
7. Self-Assertion tests cover language primitives; and
8. production RHEL 9 / Windows 11 examples cover realistic deep combinations.
