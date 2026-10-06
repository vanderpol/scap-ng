# Human review packet — SCAP-NG 0.3.0 value flow and scoped iteration

**Human status:** pending-review  
**Research branch:** research/for-each-audit-20261006  
**0.2.0 impact:** none; frozen 0.2.0 is unchanged.  
**Proposed normative draft:** [PROPOSED-SPECIFICATION.md](PROPOSED-SPECIFICATION.md)

## Change

Introduce two distinct native SCAP-NG 0.3.0 concepts:

1. **Projection** — a flattened Object-field value source that preserves OVAL
   object_component value-set semantics without preserving source Item identity.
2. **Binding / scoped for_each** — lexical Item identity used only when
   assessment truth depends on a specific originating Item while evaluating
   dependent logic.

Narrow native Variable purpose so named Variables primarily represent external
inputs, reusable value sets, direct Variable-Test subjects, and meaningful value
transformations rather than mandatory temporary plumbing.

The proposal also defines compact scoped-result requirements and conversion
classes P0-P4. Automatic OVAL -> scoped for_each lowering remains disabled; no
production P2 class is currently approved.

## Reason

Real OVAL content uses Variables for several fundamentally different jobs:

- value-set projection;
- value transformation;
- runtime/policy input;
- dependency plumbing that looks loop-like;
- cases where policy intent actually requires per-Item relationship identity.

Treating all multi-valued Variables as loops changes OVAL semantics. Keeping all
of them as named Variables preserves compatibility but forces native authors and
editors to expose unnecessary plumbing.

A separate Projection primitive allows lossless simplification of flattened
value flow. A separate Binding primitive makes true correlated relationships
explicit and understandable.

This split also enables smaller, more meaningful results because scoped
relationships can retain bounded failure evidence without creating one Rule or
Assessment Result per Item.

## Before

Representative OVAL-derived native structure:

    objects:
      users:
        capability: unix.password

      files:
        capability: unix.file
        select:
          path:
            datatype: string
            variable_check: at least one
            value:
              variable: home-dirs

    variables:
      home-dirs:
        kind: local
        datatype: string
        expression:
          values:
            object: users
            field: home_dir

The Variable above is a flattened projection. It does not preserve which user
produced which home directory.

A true relational requirement is more awkward because flattened Variables
cannot generally retain:

    user -> that user's home_dir -> that user's expected gid

## After

### Lossless flattened dataflow

    objects:
      files:
        capability: unix.file
        select:
          path:
            datatype: string
            variable_check: at least one
            value:
              projection:
                object: users
                field: home_dir

This remains a flattened value set. It is not iteration.

### Native correlated logic

    tests:
      home-primary-group-correct:
        capability: unix.file
        for_each:
          - binding: user
            object: interactive-users
            check_existence: at_least_one_exists
            check: all

        object:
          capability: unix.file
          select:
            filepath:
              datatype: string
              value:
                binding: user
                field: home_dir

        states:
          - group_id:
              datatype: integer
              value:
                binding: user
                field: primary_gid

The Binding preserves one account Item and its related fields throughout the
scope.

## Semantic effect

### Projection

Projection intentionally has the same flattened semantics as OVAL
ObjectComponentType for migrated content:

- zero source Items -> error;
- missing projected field -> error;
- missing requested record field -> error;
- values from all matching source entities are flattened into one value set;
- source Item identity is not retained as semantic correlation;
- datatype/status and consumer quantifier semantics are preserved.

### Binding / for_each

A Binding retains one source Item's identity. Fields referenced through that
Binding are known to belong to the same Item.

Scoped iteration:

- is lexical;
- permits nesting;
- permits inner scopes to reference outer Bindings;
- prohibits Binding shadowing;
- does not introduce mutable state, recursion, while loops, break/continue, or
  arbitrary scripting;
- requires explicit existence and result aggregation semantics;
- does not use vacuous programming-language truth for empty populations;
- separates native partial-population semantics from migrated OVAL
  collected-object incomplete semantics.

### Variables

A multi-valued Variable remains a value set, not an implicit loop or zip.

Named Variables remain appropriate for:

- external/organizational input;
- reused values;
- direct Variable Tests;
- meaningful transformations;
- values whose identity is useful in results/provenance.

## Compatibility

### Existing 0.2.0 source

No 0.2.0 source or schema changes are proposed.

### SCAP 1.4 / OVAL conversion

Stage-1 compatibility conversion remains faithful to source OVAL semantics.

The converter may later apply only proven P1 structural normalization. The
first proposed P1 class is a single-use local object_component Variable whose
only consumer is one Object or State value position.

Automatic scoped iteration is **not** enabled for converted OVAL unless a
future P2 class proves complete equivalence.

### P1 automatic-normalization conclusion

The research conclusion is to propose automatic P1 normalization for the
fail-closed pure object_component -> one Object/State value-consumer class,
initially only where the removed OVAL Variable datatype is string or int and
maps exactly to the consumer datatype.

P1 SHALL preserve:

- Object/field/record-field identity;
- flattened value multiplicity;
- Variable datatype validity/error behavior;
- effective operation and value quantifier;
- collection/error/status propagation;
- effective OVAL variable_instance/input-binding invocation context;
- full removed-Variable provenance.

The RHEL 9 SV-257889 production-shaped sample successfully removes two
home-directory projection Variables while retaining their Object selectors and
quantifiers and creating no Binding scope.

### Results

The existing completeness dimensions remain:

- logical_complete;
- population_complete;
- evidence_complete.

Scoped Test results add aggregate scope/outcome counts plus bounded retained
Binding evidence. They do not multiply Assessment or Rule result documents per
Item.

## Source evidence

### Normative authority

The semantic authority order is:

1. pinned OVAL 5.12.3 XSD;
2. pinned OVAL 5.12.3 Schematron;
3. normative OVAL 5.12.3 schema/prose semantics and recorded standards
   corrections/decisions;
4. production corpus evidence;
5. evaluator behavior as non-authoritative implementation evidence.

OpenSCAP, ovaldi, SCC, and other evaluators may expose implementation behavior
or disagreements but SHALL NOT override the pinned standards contract.

### Production evidence

Pinned NIWC current corpus revision:

    8c8e5dff860af6b1290ee9273a282db24278f8d5

Completed corpus census:

- 65 benchmark packages;
- 7,344 per-rule/platform OVAL closures;
- 396 dependent-dataflow candidates;
- 70 nested dependency cases;
- 120 multi-projection cases;
- 3 same-Item correlation-risk cases.

Unique Variable census across benchmark-local graphs:

- 2,285 total;
- 541 constants;
- 434 external;
- 204 pure Object-field projections;
- 1,106 transforms.

The final enriched census identified 162 single-use pure projections feeding
one Object selector or State expected value after direct-Variable-Test
consumers, Variable-backed Objects and reuse were excluded. All 162 have exact
effective Variable/consumer datatype agreement: 139 OVAL string and 23 OVAL
int. The enriched 65-package run completed all 65 packages successfully and
emitted an exact P1 lowering recipe for each candidate.

The initial P1 normalizer is therefore deliberately bounded to this proven
pass-through class. The 845 single-use transformation Variables are not being
removed merely to reduce node count: concat, regex_capture, count, merge,
unique, arithmetic and similar work is meaningful value manipulation and
remains an appropriate Variable role unless a separate readability/equivalence
study later proves a better native expression form.

### Recurring manual relational family

Strong native scoped-automation evidence includes:

- RHEL 9 SV-258053;
- Oracle Linux 9 SV-271783;
- SLES 12 SV-217174;
- SLES 15 SV-234994;
- Solaris 11 SV-216188.

These require a home-directory property to match data belonging to the same
specific account. Where source OVAL automation is absent they are P4 native
automation candidates, not lossless automated conversions.

### Negative conversion family

Same-Item arithmetic must not be inferred from flattened OVAL projections:

- RHEL 9 SV-258155;
- Oracle Linux 9 SV-271596;
- Amazon Linux 2023 SV-274067.

OVAL collection-valued arithmetic may produce Cartesian combinations. Replacing
that with row-wise bound Item arithmetic can change semantics.

## Alternatives considered

### A. Keep Variables as the only value-flow mechanism

**Advantage:** minimal language change and closest surface resemblance to OVAL.

**Rejected as preferred native model because:** temporary projection Variables
remain authoring/editor plumbing and do not solve explicit Item correlation.

### B. Treat every multi-valued Variable/Object dependency as for_each

**Advantage:** superficially simple rule.

**Rejected:** provably changes semantics for value-set comparison, Cartesian
functions, flattened collection fanout, shared/duplicate child Items, and
zero/error behavior.

### C. Add Binding but keep object_component projection only inside Variables

**Advantage:** smallest scoped-iteration addition.

**Not preferred:** still requires named Variables for simple one-use flattened
projection plumbing and makes editor source noisier than necessary.

### D. Projection + lexical Binding/for_each

**Recommended.** Projection owns flattened value-set derivation. Binding owns
Item identity. Variables own named inputs/reuse/transforms. This makes semantic
intent explicit without turning the assessment language into a general
programming language.

### E. Add a general scripting/comprehension language

**Rejected:** would complicate static dependency analysis, signing/review,
security, deterministic execution, and converter equivalence.

## Tests

Focused executable research currently covers:

- object_component zero source Items;
- missing projected field;
- record_field extraction/missing record field;
- flattened multi-Item projection;
- Binding versus projection identity;
- OVAL Cartesian function counterexample;
- var_check versus loop aggregation counterexample;
- zero-child/vacuous truth counterexample;
- incomplete versus native partial population;
- shared child Item across two parent Bindings;
- lineage versus semantic scope;
- bounded evidence versus truth;
- lexical nested scope visibility;
- Binding shadowing rejection;
- undeclared Binding rejection;
- P1 normalization positive case;
- P1 multi-use rejection;
- direct Variable Test rejection;
- datatype mismatch rejection;
- missing variable_check rejection;
- projection-into-transform rejection.

## Machine evidence

Completed research evidence includes:

- full 65-package structural/Variable census — successful;
- selected multi-platform correlation audit — successful;
- scoped prototype schema/lexical tests — successful after one schema-fragment
  harness correction;
- scoped aggregation/partial-population reference tests — successful;
- direct Variable-Test consumer regression — successful;
- OVAL result/Variable truth-table regressions — successful;
- OVAL Self-Assertion object_component one/many Item/entity cardinality matrix —
  successful;
- P1 string/integer datatype-compliance tests — successful;
- production-shaped RHEL 9 P1 normalizer tests — successful;
- enriched 65-package P1 lowering census — successful, 65/65 packages complete.

OpenSCAP supporting differential experiments are recorded separately and are
not normative proof gates.

OpenSCAP differential experiments are implementation evidence only and are not
normative gates for this proposal.

## Human status

**pending-review**

No language/schema meaning in this packet is accepted current design merely
because the research tests pass.

### Requested human decisions

1. Accept or reject the semantic split:
   **Projection = flattened value set; Binding = Item identity.**
2. Accept or reject narrowing native named Variables toward
   inputs/reuse/transforms rather than mandatory one-use projection plumbing,
   including the bounded automatic P1 pass-through Projection class.
3. Accept or reject Test-level lexical for_each as the preferred scoped
   authoring construct.
4. Accept or reject the P0-P4 migration classification and the rule that no
   automatic P2 scoped lowering occurs until differential equivalence is proven.
5. Accept or revise the proposed compact scoped-result model.
6. After semantic acceptance, review exact vocabulary/YAML spelling and the
   0.3.0 enum-alignment work before schema promotion.

Reviewer/date: pending.
