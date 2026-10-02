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
| constant_variable | one or more typed literal values | native | multi-value constant and explicit datatype round-trip fixtures covered |
| external_variable | externally supplied typed value set plus optional allowed values/restrictions | native | focused mixed possible_value / possible_restriction round-trip now covered; runtime binding validation remains conformance work |
| local_variable | one ComponentGroup member producing zero/one/many values | native | every schema ComponentGroup member is represented; mixed nested functions and deep chains covered |
| variable_component | variable -> variable dependency | native | deep shared chains and cycle rejection covered |
| object_component | object -> item field -> variable values, optional record_field | native | record_field is now losslessly round-tripped; 0/1/many collected-item and missing-field execution remains #26 |
| literal_component | typed literal expression input | native | explicit datatype preservation covered; runtime cast behavior remains #26 |
| arithmetic | 2+ operands; int/float; Cartesian product for collections | native | exact-static success/error fixtures added; runtime collection/error propagation remains #26 |
| begin | one string component plus required character/string | native | exact-static fixture added; collection-valued/runtime conformance remains #26 |
| concat | 2+ components; Cartesian product; DNE/error flag propagation | native | exact flag/result semantics |
| end | one string component plus required character/string | native | exact-static fixture added; collection-valued/runtime conformance remains #26 |
| escape_regex | one string component mapped over collection | native | exact-static escaping fixture added; independent runtime comparison remains #26 |
| split | one string component -> collection including empty values | native | empty-field delimiter fixture added; broader runtime edge cases remain #26 |
| substring | one string component with start/length semantics | native | success and out-of-range error fixtures added |
| time_difference | string/int date/time operands and format semantics | native | two-operand exact-static fixture added; one-operand current-time case remains runtime-dependent |
| regex_capture | one string component; capture semantics | native | match/no-match fixtures added; collection runtime comparison remains #26 |
| unique | de-duplicate collection values | native | exact-static duplicate fixture added; datatype equality cross-check remains #26 |
| count | collection -> integer count | native | exact-static count fixture added; DNE/error runtime cases remain #26 |
| glob_to_regex | glob conversion semantics | native | exact-static conversion + invalid-pattern fixtures added; differential execution remains #26 |
| merge | merge component values with delimiter/sort/order semantics | native | lexical success + numeric-sort error fixtures added; record/runtime variants remain #26 |
| var_ref in object entities | variable supplies selector values | native | multi-valued Object var_check round-trip matrix covered; operation-specific collection execution remains #26 |
| var_ref in state entities | variable supplies expected values | native | many-to-many var_check + entity_check truth-table ordering is covered; target execution remains #26 |
| var_ref datatype matching | referenced variable datatype must match consuming entity rules | native | pinned OVAL 5.12.3 EntityAttributeGroup Schematron requires exact entity/Variable datatype equality; converter diagnoses mismatches, and source-invalid Self-Assertion/NIWC cases are quarantined as source defects rather than treated as missing NG capability |
| var_ref on record entity | prohibited | native | converter source audit rejects record entity var_ref |
| empty variable consumed by Object | Object considered not to exist | native | source-backed reference-context semantics and regression covered; differential execution remains #26 |
| empty variable consumed by State | State evaluation error | native | source-backed reference-context semantics and regression covered; differential execution remains #26 |
| variable evaluation error propagation | error propagates to consuming entity | native | result-state propagation tests are covered; differential execution remains #26 |
| var_check default | effective `all` when var_ref exists and var_check omitted | native | parser provenance and omitted/explicit-default regressions covered |
| var_check aggregation | all / at least one / only one / none satisfy etc. per CheckEnumeration | native | exhaustive OVAL-derived truth-table coverage |
| entity_check + var_check | two-level many-to-many state evaluation | native | ordering and non-commutative truth-table cases covered |
| nested functions | arbitrary recursive FunctionGroup composition | native | depth-32 and mixed-function round-trip fixtures covered |
| dependency graph | arbitrary acyclic variable/object/state dependencies | native | deep shared chains and direct/indirect mixed cycles are regression-tested |
| object set recursion | nested sets with schema-constrained arity | native | depth 4/10/32 round-trip and all-depth type validation covered; live evaluation remains #26 |
| set object references | 1..2 refs; referenced objects same type as parent | native | all-depth namespace-aware validation + upstream Schematron candidate tracked in #37 |
| set filters | zero..many state references applied before set operator | native | conversion/dependency ordering and #11 filter-before-set semantics covered; live collection remains #26 |
| filter action | include/exclude; default exclude | native | default/include/exclude and conflicting filter semantics covered by #11; live collection remains #26 |
| variables inside filter states | State var_ref participates in collection filtering | native | deep chained filter-State variable dependency round-trip covered |
| variables inside objects used by sets | variable-dependent collection feeding set | native | nested depth-4 Set + variable-dependent referenced Object round-trip covered |
| status/flag propagation | complete/incomplete/error/DNE/not-collected/not-applicable as defined per function | native | generic truth/flag charts covered; capability-specific execution remains #26 |
| operation/datatype compatibility | operation set constrained by datatype | native | pinned XSD/Schematron validation is an M0 gate; converter adds var_ref/record diagnostics and capability schemas enforce narrowed native fields |
| implicit defaults | schema defaults must be normalized without semantic loss | native | #8/#9 schema-backed provenance and fail-closed behavior-default separation |
| deprecated constructs | deprecated source semantics SHALL trigger migration/update policy | native | deprecated tests/definitions are inventoried and diagnosed; native deprecated execution is not synthesized |

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


### Source-invalid var_ref datatype fixtures

The pinned OVAL 5.12.3 `EntityAttributeGroup` Schematron explicitly asserts
that an entity using `var_ref` has the same effective `datatype` as the
referenced Variable.  If the entity omits `datatype`, its effective datatype
is `string`, so the referenced Variable must also be `string`.

The SCAP Self-Assertion corpus contains a small number of intentional or
historical Schematron-invalid examples that violate this rule, including
cross-datatype `pid`, package `version`, and `is_installed` references.
Published NIWC IIS content also contains such a mismatch.  These cases are
valuable validation evidence, but they are not valid automated OVAL semantics
to synthesize into native NG.

Migration behavior is therefore fail-closed and evidence-preserving:

- diagnose `var_ref_datatype_mismatch` from the reachable source graph;
- classify it as `source_content_defect` only when that exact positive
  semantic finding is present;
- omit the invalid automated Assessment;
- retain exact source IDs/detail in conversion evidence;
- use a verified source manual Assessment only where the source provides one;
- keep mixed or unknown unsupported findings as hard blockers.

This correction does **not** weaken the datatype rule.  It separates valid
language coverage from intentionally/actually invalid source content.
