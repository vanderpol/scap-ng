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
