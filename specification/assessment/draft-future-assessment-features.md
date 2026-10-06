# Draft future Assessment features

**Status:** non-normative design draft; deferred; not part of JSON Schema v0.1.0

This document makes likely future Assessment-language directions visible to
reviewers without turning unsettled examples into executable schema contracts.
The authoritative decision history remains in GitHub Issues #25 and #44.

Nothing in this document changes current SCAP 1.4 conversion output.

## 1. Conditional evaluation

Integration checkpoint, 2026-10-03: the working proposal now has a
[partial versioned 0.2.0 schema and callback evaluator](../../schema/v0.2.0/README.md),
including static compiler/package dependency closure and explicit N/A. The older
illustrative `assessment_result`/`equals` form below is superseded in that draft
by the ordinary `assessment` alias leaf. This does not amend v0.1.0, establish
Board ratification, or declare a released v0.2.0 implementation.

Owner-directed 2026-10-03 experiment:
[conditional known-result content](../../tests/conditional-0.2.0/README.md).
It demonstrates six-state guard handling, nested/dependent conditions, skipped
paths, intrinsic applicability and a proposed explicit `not_applicable` outcome
with a reason. Its controlled Test-result model and fixture grammar are
experimental; passing them does not promote the proposal into v0.1.0 or claim
that a released v0.2.0 implementation exists. Owner follow-up, 2026-10-03: automatic conditional normalization and candidate
detection are removed from planned features because the general rewrite is not
lossless across six-state truth or collection/evidence behavior.
[Issue #126](https://github.com/vanderpol/scap-ng/issues/126) is closed as not planned;
source-authored conditional support continues.

SCAP-NG is considering a constrained declarative conditional-evaluation
construct.

Two use cases are explicitly required if the feature is adopted:

1. branch on a local Test result;
2. branch on the result of a statically declared dependent Assessment,
   including an existing applicability Assessment.

Illustrative semantics only:

```yaml
evaluate:
  if:
    test: fips-enabled
  then:
    test: fips-policy-correct
  else:
    test: normal-policy-correct
```

and:

```yaml
evaluate:
  if:
    assessment_result: server-role
    equals: true
  then:
    test: dc-setting-correct
  else:
    test: member-setting-correct
```

The second form SHALL NOT require duplication of the referenced applicability
Assessment's Tests, Objects/Collections, Variables, or criteria.

If adopted, all possible branches and dependencies must remain statically
declared in signed content. Conditional evaluation must not become a general
scripting mechanism and must not dynamically construct shell commands, SQL,
paths, capability names, or unsigned content.

Open decisions include:

- final syntax, including whether a declarative `case/when` surface is clearer
  than programming-language-like `if/elseif/else`;
- propagation of `error`, `unknown`, and `not_applicable`;
- short-circuit behavior versus semantic evaluation;
- dependency-cycle handling;
- whether typed Variables/inputs may be conditional operands;
- whether ordinary Assessments may produce runtime `not_applicable`;
- result fields explaining which branch was selected and why.

### Conversion boundary

The SCAP 1.4 -> SCAP-NG converter should normally ignore this feature entirely.
It SHALL NOT invent conditionals merely because converted content could be made
shorter or more elegant.

Only a concrete legacy construct that cannot otherwise be represented
losslessly may justify converter emission of the future conditional construct.
Such a case must be backed by source evidence and regression tests.

## 2. Shared collection execution

**Partial promotion note:** first-class Assessment-result dependencies are no
longer deferred; they are part of the current Assessment Method and executable
schema. This section now tracks only the still-deferred problem of sharing
runtime collection execution and materializing reused Items.

The design must distinguish:

- Assessment-result dependency;
- authored Object/Collection definition reuse;
- runtime collection-execution reuse;
- Item/result materialization.

The current working principle is:

> Share collection work at runtime; materialize the observations needed to make
> a standalone consuming Assessment result coherent.

For example, if a shared collection execution produces 500 Items and a
consuming Assessment reuses those observations, the consuming Assessment may
serialize local/imported Item representations before Items produced by its own
additional Objects/Collections. Its Tests then reference Items available within
that same Assessment result.

This duplicates result bytes but avoids repeating the expensive collection
operation and keeps a standalone Assessment result independently understandable.

Imported Items should preserve provenance back to the shared collection
execution even though their result-local identifiers belong to the consuming
Assessment.

Open decisions include:

- whether all available imported Items or only actually consumed Items are
  materialized;
- local sequential IDs versus stable content-derived IDs;
- provenance fields connecting local Items to the shared execution;
- interaction with evidence caps and incomplete collection;
- normalized whole-scan result representations that can deduplicate observations
  without making standalone Assessment singles dependent on other result files;
- execution-DAG and cache-key rules;
- redaction/sensitivity behavior.

## 3. Terminology note

This decision has been promoted into the current design: native authoring uses
**Object**, **Test**, **State**, **Variable**, and **Item** where those concepts
retain the corresponding OVAL semantics. **Collection execution** describes the
runtime act of evaluating an Object; `Collection` is not the authored node
name.

The current v0.1.0 Assessment schema therefore validates `objects`,
`states`, `tests`, and `variables`. Older iteration artifacts that use
authored `collections` are historical baselines, not current schema examples.


## 4. Target-scoped Organizational Input resolution

**Status:** deferred design issue for a post-0.2.0 iteration. This section is
non-normative and does not change the frozen 0.2.0 Organizational Input model.

SCC's experimental NIWC `independent.sqlext` content demonstrates a useful but
technology-sensitive case: an end user may supply an organization-defined value
and scope that value to combinations of target identity such as:

- Computer: all computers or selected computers;
- SQL Server instance: all instances or selected instances;
- Database: all databases or selected databases.

The underlying problem is broader than SQL Server. A run can legitimately need
multiple values for the same organization-resolved Parameter, with the effective
value depending on **which assessed resource instance** is being evaluated. The
current 0.2.0 contract intentionally avoids implicit Input Set selection from
hostname, inventory, intended-scope metadata, or scanner-local convention, and
Organizational Input cannot alter Object targeting or executable Assessment
semantics. Those protections remain unchanged.

A future design therefore needs to decide whether **target-scoped value
resolution** is a portable SCAP-NG policy concept or remains an orchestration /
scanner/vendor responsibility.

Questions to resolve before promotion include:

- Is the portable concept simply a generic resource selector attached to an
  Organizational Input value, with technology-specific target dimensions defined
  by the applicable capability or asset model?
- Should SCAP-NG define only generic dimensions such as host/system identity and
  allow capability-specific dimensions (for example SQL instance and database)
  through typed/namespaced extensions?
- Should SQL instance/database scope remain entirely scanner/vendor-defined
  because those dimensions are not meaningful across most technologies?
- How does a processor deterministically resolve overlapping scopes (for example
  global, host-specific, instance-specific, and database-specific values) without
  relying on source order or hidden precedence?
- Must each scoped value identify an explicit resource identity already produced
  by authored Assessment logic, rather than allowing the Input Set itself to
  discover or select execution targets?
- How are missing, duplicate, ambiguous, stale, or conflicting scoped values
  reported?
- How is scope provenance represented so results can explain **why this value
  applied to this resource**?
- Can the model support analogous non-SQL cases (for example service instance,
  container, tenant, virtual host, application instance, or named datastore)
  without building SQL-specific concepts into the core language?

A likely design boundary to preserve is that scoped Organizational Input may
choose **which policy value applies to an already identified assessment target**,
while it SHALL NOT create targets, select Objects/Tests, construct SQL or other
queries, or otherwise change executable Assessment semantics. This boundary is a
candidate for future review, not an accepted design decision.

The `sqlext` implementation is evidence for the use case only. It is a NIWC/SCC
publisher extension and SHALL NOT by itself establish a native SCAP-NG SQL
capability or normative targeting model.

## 5. Content authorship

Assessment content authorship is deferred to the 0.3.0 design track. The focused
proposal is documented in
[draft-0.3.0-content-authorship.md](draft-0.3.0-content-authorship.md).

The 0.2.0 converter uses publisher-neutral native IDs; source repository and
migration provenance SHALL NOT be mistaken for authorship.

## Scoped Item binding and flattened value flow — 0.3.0 research

The active research proposal for separating flattened Object-field Projection,
lexical Item Binding/`for_each`, named Variables, lineage, and collection
execution reuse is maintained in one authoritative research document:

[SCAP-NG 0.3.0 value-flow and scoped-iteration proposal](../../research/for-each-0.3.0/PROPOSED-SPECIFICATION.md).

That proposal is not part of frozen 0.2.0. This file intentionally does not
duplicate its semantics. Promotion follows the feature-promotion rule below.


## 6. Promotion rule

A deferred feature should move into normative specification text and executable
JSON Schema only after:

1. semantics are agreed independently of syntax;
2. result/error behavior is defined;
3. security implications are reviewed;
4. examples cover important real-world cases;
5. conversion impact is understood;
6. conformance tests can distinguish valid from invalid behavior.

Until then, these sections are design guidance only.

### Item materialization checkpoint — 2026-10-03

The older open Item-scope/provenance questions above now have a bounded
[0.2.0 working contract](../../transition/item-materialization-2026-10-03.md):
producer serialization defaults to all locally available observations; consumed
mode retains all recorded logical/decisive uses. Explicit local IDs, byte-pinned
origin context, import chains and conservative incompleteness are represented.
This is a helper/result-schema checkpoint; runtime collection-cache reuse,
collector-specific cache keys/freshness authorization, whole-scan deduplication
and Board ratification remain open. No automatic source conversion uses it.
