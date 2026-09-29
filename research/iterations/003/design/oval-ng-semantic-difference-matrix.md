# OVAL 5.12.3 ↔ SCAP-NG Semantic Difference Matrix

**Status:** living conformance audit for iteration 003.

This matrix is a gating artifact. A behaviorally relevant OVAL construct is not
considered covered until it is classified here and backed by either corpus
round-trip evidence or a schema-derived stress case.

## Classification

- **exact** — semantics and decomposition are preserved.
- **normalized** — semantics are preserved but native NG intentionally represents
  the construct differently.
- **native-addition** — NG adds authoring/runtime capability without changing the
  imported OVAL meaning.
- **rejected** — intentionally unsupported/deprecated in NG.
- **pending** — semantics/design not yet sufficiently proven.
- **board-review** — proposed divergence/clarification requiring OVAL Board review.

| OVAL / SCAP construct | Authority | NG equivalent | Fidelity | Evidence | Board review? | Notes |
|---|---|---|---|---|---|---|
| Definition criteria tree | OVAL definitions XSD | Assessment Boolean tree | exact | RHEL9 422-file corpus + focused criteria tests | No | AND/OR, nested criteria, criterion edges and defaults preserved. |
| `extend_definition` | OVAL definitions XSD | Recursively inlined referenced result subtree | normalized | RHEL9: 382 source wrapper cases; full corpus 422/422 after semantic dereference | **Yes** | Definition identity retained in provenance, not executable native structure. |
| Criterion `negate` | OVAL definitions XSD | Negated Boolean edge | exact | focused `multistate-negated-criteria` | No | Must remain edge semantics. |
| Criteria/criterion `applicability_check` | OVAL definitions XSD | Applicability-marked result edge | exact | focused `criteria-applicability-check` | No | RHEL9 corpus does not exercise this on extend_definition edges. |
| Test `check` | OVAL definitions/common XSD | Check aggregation | exact | RHEL9 corpus | No | Schema-defined truth semantics are authoritative. |
| Test `check_existence` | OVAL definitions/common XSD | Collection existence aggregation | exact | RHEL9 corpus | No | Preserved independently of state comparison. |
| Test `state_operator` | OVAL definitions XSD | State aggregation operator | exact | focused `state-operator-or` + corpus | No | Multiple State references preserved. |
| Object | OVAL component schemas | Collection | normalized-name | RHEL9 422/422 | **Yes (terminology)** | Source Object boundary preserved during conversion. |
| Object entity literal | OVAL component schemas | Collection selector literal | exact | RHEL9 corpus | No | Datatype/operation/defaults preserved. |
| Object entity `var_ref` | OVAL definitions/component XSD | Collection selector Variable reference | exact | RHEL9 corpus | No | Includes `var_check`. |
| State | OVAL component schemas | State/predicate semantics | exact | RHEL9 corpus | No | Converted source keeps State boundary. Native NG may colocate one-use filters. |
| State entity `var_ref` | OVAL definitions/component XSD | Predicate Variable reference | exact | RHEL9 + focused many-to-many case | No | No-value error semantics remain part of execution model. |
| `entity_check` | OVAL common/definitions XSD | Entity-value quantifier | exact | focused many-to-many + corpus | No | Compared independently from `var_check`. |
| `var_check` | OVAL common/definitions XSD | Variable-value quantifier | exact | RHEL9 covers all/at least one/only one; focused many-to-many | No | Two-level quantification preserved. |
| Object Set UNION | OVAL definitions XSD | Collection Set UNION | exact | RHEL9 + focused set/filter cases | No | Source decomposition retained. |
| Object Set COMPLEMENT | OVAL definitions XSD | Collection Set COMPLEMENT | exact | RHEL9 corpus | No | Round-tripped in production content. |
| Recursive Set | OVAL definitions XSD | Recursive Collection Set expression | exact | focused `recursive-set-expression` | No | Leaf and nested set forms distinguished. |
| Filter include/exclude | OVAL definitions XSD | Collection Filter/State edge | exact on conversion | RHEL9 + focused cases | **Yes for native colocation** | Native NG may colocate one-use predicate in Collection. |
| Behaviors | Component XSD | Collection capability behaviors | exact | RHEL9 corpus | No | Attributes preserved, not scanner magic. |
| constant_variable | OVAL definitions XSD | Variable with literal values | exact | RHEL9 + focused | No | Multi-valued constants retained. |
| external_variable | OVAL definitions XSD | Externally supplied Variable/input | exact imported semantics | focused `external-variable-constraints` | Pending integration | possible_value and possible_restriction retained. Benchmark/tailoring input binding still broader design work. |
| local_variable | OVAL definitions XSD | Derived Variable | exact | RHEL9 corpus | No | Source Variable boundaries preserved. |
| variable_component | OVAL definitions XSD | Variable → Variable dependency | exact | RHEL9 + focused chains | No | Arbitrarily deep acyclic chains supported. Indirect-cycle rejection remains Board item. |
| object_component | OVAL definitions XSD | Collection field extraction into Variable | exact | RHEL9 + focused | No | Includes `record_field`. |
| literal_component datatype | OVAL definitions XSD | Typed literal expression operand | exact | focused `typed-literal-components` | No | Explicit datatype preserved. |
| concat | OVAL definitions XSD | Variable expression concat | exact | RHEL9 | No | Multi-valued operand product semantics retained. |
| arithmetic | OVAL definitions XSD | Variable arithmetic expression | exact | focused Cartesian case + corpus | No | Cartesian-product behavior required. |
| begin / end | OVAL definitions XSD | Variable string expression | exact | focused `remaining-core-functions` | No | |
| escape_regex | OVAL definitions XSD | Variable regex escape expression | exact | focused `remaining-core-functions` | No | |
| split | OVAL definitions XSD | Variable split expression | exact | RHEL9 + focused chain | No | |
| substring | OVAL definitions XSD | Variable substring expression | exact | focused `remaining-core-functions` | No | |
| time_difference | OVAL definitions XSD | Variable time-difference expression | exact | focused `remaining-core-functions` | No | Format defaults preserved. |
| regex_capture | OVAL definitions XSD | Variable regex-capture expression | exact | focused `remaining-core-functions` | No | |
| unique | OVAL definitions XSD | Variable unique expression | exact | RHEL9 + focused chain | No | |
| count | OVAL definitions XSD | Variable count expression | exact | RHEL9 + focused chain | No | |
| glob_to_regex | OVAL definitions XSD | Variable glob-to-regex expression | exact | focused `remaining-core-functions` | No | |
| merge | OVAL definitions XSD | Variable merge expression | exact | focused `remaining-core-functions` | No | delimiter/sort/order preserved. |
| Record-valued State entity | OVAL definitions/common XSD | Record predicate fields | exact | focused `record-state-entity` | No | Field-level semantics retained. |
| ObjectComponent `record_field` | OVAL definitions XSD | Record field extraction | exact | focused `object-component-record-field` | No | |
| `xsi:nil` entities | OVAL component/common XSD | Explicit nil entity | exact | focused `nillable-entities` | No | Must not collapse to empty string. |
| State entity `mask` | OVAL definitions/common XSD | Evidence masking semantic | exact | focused `masked-state-entity` | No | Results/evidence implementation must honor masking. |
| Source declaration order | XSD reference model | No native semantic meaning | normalized | corpus graph resolution | No | References determine dependencies. |
| Direct Variable self-reference | OVAL VariableComponent documentation | Invalid dependency | exact/clarified | schema research | No | Explicitly prohibited by legacy documentation. |
| Indirect dependency cycle | No complete explicit legacy prohibition found | Proposed validation error | pending / stricter NG | design research | **Yes** | See dependency-ordering-and-cycles.md. |
| Evaluation short-circuit | OVAL truth tables define outcome, not required order | Runtime exhaustive/decisive mode | native-addition | schema research | **Yes** | Decisive evaluation only when remaining children cannot alter result. |
| Collection caching/dedup | Not normative OVAL assessment semantics | Implementation optimization | normalized-away | design review | No | No assessment-wide snapshot guarantee. |
| System Characteristics persistence | OVAL system-characteristics/results schemas | Compact bounded evidence/results | intentional divergence | results design | **Yes** | NG does not intend to persist huge collected-item corpus. |
| Deprecated OVAL tests | OVAL schemas deprecation markers | Conversion error / author update required | rejected | project requirement | **Yes** | Native NG SHALL NOT carry deprecated test types forward. |

## Current corpus evidence

Pinned RHEL 9 production corpus:

- 422 automated OVAL documents;
- 422/422 OVAL → NG semantic fixture → OVAL comparisons pass;
- all Test/Object/State/Variable graphs compare semantically;
- source `extend_definition` wrappers are recursively dereferenced;
- deterministic v003 regeneration passes.

Focused schema-derived fixtures cover language features absent or rare in RHEL9,
including external Variables, typed literals, record fields, record States,
nillable entities, masking, applicability flags, nested functions, and explicit
many-to-many `entity_check` + `var_check`.

## Exit criterion

The lossless OVAL conversion model is not considered complete until:

1. every behaviorally relevant OVAL 5.12.3 XSD/Schematron construct is represented
   in this matrix;
2. each row is backed by production-corpus or schema-derived test evidence;
3. no row remains `pending` without an explicit deferred/Board decision;
4. every supported construct round-trips semantically; and
5. every intentional divergence is documented in the conversion contract and,
   where appropriate, Board-review material.
