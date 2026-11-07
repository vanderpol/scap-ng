# SCAP-NG application developer guide

SCAP-NG 0.4.0 is pre-alpha. This guide describes contracts and implementation
gaps; structural validation does not establish scanner support or equivalence.
Pin the entire repository commit, including schemas, specification and examples.

## Reading order

1. [Shared schema reference](../generated/schema-reference.md): Assessment and Test structure.
   [Shared contract model](../generated/developer-guide-contract-model.md): variables, evaluation, cardinality and documentation status.
2. [Platform index](../generated/developer-guide-index.md): read only the capability families you implement. Windows implementers do not need the UNIX guide. Read independent capabilities only when implementing them.
3. [Specification](../../specification/README.md): shared evaluation and result contracts. Capability pages supplement those contracts; they do not define alternative evaluation rules.
4. [Gap inventory](../generated/developer-guide-gaps.json) and [implementation plan](plan.md): work still needed before qualification.

The same frozen mappings and resolved selector contracts supply both author
fields and implementer tables. Reviewed pilot prose has one temporary home in
[the annotation sidecar](../metadata/schema-documentation-pilot.json).
[Ownership and the future annotation proposal](annotation-proposal.md) explain
how to prevent a second documentation authority. No 0.4.0 schema bytes change.

## Shared implementation boundaries

- Resolve schemas locally from the pinned snapshot. Apply documented semantic
  checks as well as structural validation; schema acceptance alone does not
  prove that an Assessment has an executable collection contract.
- Keep target identity, applicability, selected Items and result evidence linked.
  Use the shared specification for evaluation; unresolved acquisition details
  must not silently become vendor defaults.
- Preserve absence, inaccessible data, incomplete collection and comparison
  failure as distinct inputs wherever the native contract distinguishes them.
  An unavailable collector is not proof that the selected object does not exist.
- For shell commands, enforce package/signature verification policy outside the
  command string, as recorded by the capability's trust rule. Execution policy,
  resource limits and failure mappings still require contract review.
- Preserve evidence provenance and decisive reasons in structured results.
  Reports are views of that evidence. This guide does not prescribe a storage
  engine, programming language, framework or operating-system API.

[Three-pilot review](pilot-review.md) separates frozen facts, OVAL research and
open decisions. Legacy OVAL descriptions are implementation research inputs;
they do not add requirements to SCAP-NG.

[Phase 2 semantic research and decision packets](semantic-research.md) cover the
three priorities and five continuation capabilities; recommendations are not
adopted semantics.
