# Conformance and Validation

**Status:** pre-alpha normative draft

## 1. Roles

SCAP-NG distinguishes at least two implementation roles:

- **content producer** — creates SCAP-NG source or compiled content;
- **content consumer** — accepts compiled SCAP-NG content, processes it, and
  produces results.

An implementation MAY perform both roles.

A future conformance profile MAY define additional roles such as converter,
validator, package compiler, result exporter, or interactive review tool.

## 2. Conformance claims

A product or content artifact that claims SCAP-NG conformance SHALL identify
the SCAP-NG specification version to which it claims conformance.

A product conformance claim SHOULD identify the roles and optional capabilities
implemented.

The final conformance-profile and use-case taxonomy remains under design.

## 3. Source validation

A conformant SCAP-NG build process SHALL validate, as applicable:

- serialization syntax;
- object schema;
- stable identity;
- reference resolution;
- duplicate identity;
- Benchmark membership;
- Profile inheritance;
- Platform references;
- applicability references;
- Assessment Method references;
- Parameter/input bindings;
- Tailoring references and allowed modifications;
- package completeness.

A build process SHALL reject unresolved required references.

A processor SHALL NOT silently substitute guessed content for an unresolved
reference.

### Explicit semantic choices

Native SCAP-NG content SHALL NOT rely on hidden semantic defaults. When two or
more meaningful behaviors are possible for collection, evaluation, reporting,
or results, the authored content SHALL state the selected behavior explicitly
and the governing schema or semantic validator SHALL reject its omission.

A semantic that is inherent in the definition of a construct is not a hidden
default. For example, a construct with only one defined traversal direction may
encode that direction in the construct's type rather than repeat a redundant
field. This exception SHALL NOT be used where omission would choose among
multiple valid behaviors.

Implementations SHALL NOT invent a fallback value after validation for a
required semantic choice.

## 4. Semantic validation

Schema validity alone is insufficient for SCAP-NG conformance.

Validators SHALL enforce semantic requirements that cannot be expressed by
basic serialization schemas, including:

- Profile rule selection is subtractive where required by the Profile model;
- a child Profile does not re-enable a Rule disabled by an ancestor;
- Rule applicability identifiers resolve in the governing Benchmark catalog;
- policy values do not modify executable Assessment behavior;
- source paths resolve unambiguously during compilation;
- compiled references use stable logical identity rather than authoring paths;
- duplicate authoritative definitions are rejected.

## 4A. Conformance evidence layers

SCAP-NG conformance evidence SHALL identify what has actually been proven. The
following layers are distinct and SHALL NOT be collapsed into a single
"validated" or "conformant" claim:

1. **serialization/schema validity** — the artifact is structurally valid;
2. **semantic validity** — cross-field, cross-reference, datatype, capability,
   cardinality, and other normative semantic constraints are satisfied;
3. **known-result evaluator conformance** — supplied observations/inputs produce
   independently predetermined outcomes and evidence;
4. **collection/acquisition conformance** — an implementation obtains the
   required target observations with the capability's specified identity,
   completeness, status, datatype, and error behavior;
5. **live target execution conformance** — collection plus evaluation is proven
   against representative real targets for the claimed platform/capability;
6. **migration equivalence evidence** — supported legacy source semantics are
   shown to survive conversion without semantic weakening or strengthening.

Evidence at one layer SHALL NOT be claimed as evidence at a stronger layer.
In particular:

- successful JSON Schema, XSD, or Schematron validation does not prove runtime
  evaluation or target collection;
- synthetic supplied Items/observations can prove evaluator behavior but do not
  prove a collector can acquire those observations;
- successful document round-trip comparison does not prove collector or
  evaluator equivalence;
- one implementation's behavior does not become normative merely because the
  reference implementation behaves that way.

Conformance reports SHOULD identify the exact fixture/source revision,
implementation version, capability, target context when applicable, and the
evidence layer being claimed.

## 5. Invalid or unsupported content

A content consumer SHALL detect invalid compiled content before execution.

A consumer SHALL NOT execute content that fails integrity verification when the
package declares integrity metadata that cannot be validated.

When a consumer encounters a valid SCAP-NG capability it does not implement, it
SHALL report the unsupported capability distinctly from a compliance failure.

The final standardized unsupported/not-evaluated result vocabulary remains
under design.


## 6. Check-selector conformance

Validators SHALL verify that every explicitly selected check selector resolves
to an alternative exposed by the governing Rule policy.

Processors SHALL NOT silently substitute a default or different selector for an
unresolved explicit selection.

Conformance tests SHALL include at least:

- default check resolution when no explicit selector is supplied;
- explicit selection of an automated alternative;
- explicit selection of a manual alternative;
- distinct selector identities that intentionally share one Assessment Method;
- extensible selector names other than `automated` and `manual`;
- failure for an unknown selector;
- preservation of effective selector identity in results;
- explicit failure for non-equivalent same-selector checking-system alternatives
  when the implementation cannot preserve their fallback semantics; and
- Stage-1 migration of representative XCCDF selectable-check content.

Unsupported or non-equivalent legacy check-selection semantics SHALL cause an
explicit conversion failure rather than semantic approximation.


## 7. Existence and cardinality conformance

Conformance tests SHALL exercise first-class expected-state existence semantics
independently of any one collection capability.

At minimum, the base test set SHALL establish:

| Expected state | Observed matches | Required outcome |
| --- | ---: | --- |
| `none` | 0 | pass |
| `none` | 1 | fail |
| `none` | more than 1 | fail |
| `one_or_more` | 0 | fail |
| `one_or_more` | 1 | pass |
| `one_or_more` | more than 1 | pass |

A failing expected-absence case SHOULD identify
`unexpected_existence`. A failing expected-presence case SHOULD identify
`required_item_missing` or a more specific standardized missing-match reason.

SCAP 1.4 migration conformance SHALL verify preservation of source OVAL
`check_existence` semantics, including at least `none_exist` and
`at_least_one_exists`.

A converter that cannot preserve a source existence/cardinality construct SHALL
report an explicit conversion blocker rather than substitute another condition.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: SCAP-NG Requirements Index](../requirements-index.md) · [Contents](../README.md) · [Next: Benchmark, Rule, and Group Model →](../policy/benchmark.md)

<!-- spec-nav:end -->


## Behavior conformance gate

A conforming assessment compiler/validator SHALL verify that every
Collection's behavior settings are supported by the selected capability,
have valid types and values, and satisfy cross-field applicability rules.
It SHALL NOT silently ignore behavior settings it cannot execute.

A capability claiming OVAL migration support SHALL document per-behavior
coverage for explicit settings, effective defaults, optional parent-element
omission, and relevant error/existence side effects. Runtime conformance
SHALL be demonstrated with controlled collection fixtures; an XSD-valid
round trip does not establish such behavioral conformance.

**Current limitation:** iteration 003 copies explicit OVAL behavior
attributes but has not established a schema-wide effective-default resolver
or complete runtime behavior verification. This SHALL remain an open gate
before any blanket claim of full OVAL behavior compatibility.

## 8. Schema-derived assessor semantic checks

Beyond syntax and schema conformance, a SCAP-NG semantic validator SHALL:

- validate independently typed Test/Collection/State capability interfaces and
  reject incompatible links rather than coerce component families;
- traverse all reachable nested references, including Object→Variable→Object,
  set members and filter States, to detect missing dependencies, unsupported
  features and cycles;
- enforce typed Variable/Parameter allowed values and restrictions before
  binding them to assessments;
- preserve distinct Test-level State combiners, State/entity operators and
  variable-value quantifiers; and
- distinguish deprecated standard capability blockers from non-standard
  publisher extensions and genuinely unsupported standard language constructs.

A scanner SHALL NOT claim executable content correctness solely because XSD
and Schematron validations pass. Negative conformance fixtures SHOULD include
the known nginx Test/Object/State family mismatch, a nested publisher extension,
a malformed dependency cycle, and invalid external-variable restrictions.

The pinned upstream OVAL 5.12.3 schemas, not a locally modified or augmented
copy, define standard OVAL vocabulary during migration. The SCC/NIWC
`sqlext` family is intentionally outside the standard-Oval conversion
profile for this iteration.
