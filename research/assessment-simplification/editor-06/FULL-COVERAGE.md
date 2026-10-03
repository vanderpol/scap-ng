# Complete content support is an editor requirement

**Owner requirement recorded 2026-10-03; implementation proposals remain experimental.**
The owner identifies the prior SCAP 1.x editor failures as large XML, the broad Test
library, and complex Variable/Filter dependency chains. The explicit requirement
is to analyze the complete content language and make the editor handle **ALL**
supported content, including deeply composed cases. Straightforward forms and
recipes do not define the supported subset.

This strengthens the earlier direct-editor proposal. Raw-text preservation is
necessary but **insufficient** to call a feature fully supported. Release gates
must distinguish preservation, inspection, creation/editing and semantic validation.
A small prototype may prove an architecture slice; it must not be advertised as
a complete editor. No editor implementation or complete coverage is claimed here.

## Precisely define the universe

For a pinned supported native language/capability version, every valid authored
Benchmark, Rule, Assessment, applicability binding, supported manual method,
Tailoring and Organizational Input must be representable and editable. The
capability catalog must include every in-scope field, datatype, comparison,
collection parameter, behavior, record/list form and legal reference position.

Current mapped capabilities, remaining schema-only candidates, unsupported source
extensions, effective deprecation and intentional native divergences are different
statuses. The historical crosswalk's approximate half-excluded count is provisional;
it does not establish that capabilities were removed merely for being unused.
The [preservation/disposition rule](../../../specification/migration/legacy-feature-disposition.md)
retains supported semantics used in production or validation content. Governance
reinstatements override raw deprecation metadata. Rarity alone is insufficient
for removal. Existing documented removals are recorded rather than silently reversed.

“All possible content” cannot mean reading every future document or enumerating
all infinitely many nesting combinations. It means a complete contract inventory,
recursive/composable editing support, observed production checks, authoritative
conformance cases and generated adversarial combinations. Any unresolved native
language gap remains explicit; a convenient editor cannot decide the standard.

## Initial measured inventory, not a coverage result

The [snapshot](authoring-obligations.json) records **100 current mapping files**,
all **28 shared schema definitions**, seven authoring schema pins and the pinned
OVAL Variable ComponentGroup/FunctionGroup members (**13 functions**). It retains
each mapping's complete native shape and semantic obligations, not only its name.
Every editor implementation status is `not_implemented` and fixture evidence is
empty. Schema-only/unmapped candidates remain reconciliation work; 100 is not a
claim that the entire possible standard surface has exactly 100 capabilities.

Reproduce from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/scap-ng/bin/python research/assessment-simplification/editor-06/inventory_editor_surface.py
```

The snapshot is research evidence, not a second authoritative schema or registry.
It is derived from current mappings and pinned schemas/contracts. Verification
matched all 100 native shapes/semantic-obligation lists to their mappings, checked
113 source-file hashes, confirmed every editor status is unimplemented, and checked
13 local documentation links. No editor or scanner semantic tests were run.

## The dependency graph is the foundation

The [existing Variable/dataflow matrix](../../iterations/003/design/oval-variable-coverage.md)
already makes the decisive point: Variables participate in collection itself.
The legal graph can contain:

```text
Variable -> Object selector -> Items -> Object component -> Variable
         -> State -> Filter -> Set -> Object component -> another Variable
```

Arrow direction here describes data feeding a consumer. Typed dependency references
and scheduling must preserve that graph; presentation order is not execution order.
A fixed collect/derive/assert pipeline cannot represent the full model.

The editor's common graph services should own reference resolution, typed edges,
stable IDs, use-sites, transitive dependency inspection and safe refactoring.
The authoritative validator retains context-specific semantic checks. Named and
private embedded Objects, shared intermediates and cross-Assessment result
dependencies must survive. No automatic flattening, cloning of shared nodes or
replacement of Variable collections by scalar placeholders.

Recursive expressions require an explicit tree representation with iterative or
stack-safe traversal. Valid acyclic depth SHALL NOT have an arbitrary language
limit of three/five levels. Resource/memory/time limits are separate implementation
constraints, reported honestly without truncating saved content or returning false.
Direct/indirect cycles are invalid and need the actual cycle path in diagnostics.
Deep acyclic graphs, repeated references and cycles are three different cases.

## Two ways of editing the same complete native model

**Guided views** make common checks convenient: registry rows, numeric thresholds,
permission bits, service facts and finite expectations. They cannot remove advanced
fields or coerce a complex graph into a simpler pattern.

**A complete structured workspace** supplies the general editor:

- Object selector/collector modes and legal behavior controls.
- Recursive function/expression editing, literals and named Variable references in
  every permitted typed position, with correct argument order and arity.
- Nested Set operations and Filter State references, with their actual scope/order.
- Record/list entities and per-level datatype/quantifier/existence controls.
- Arbitrarily nested evaluate expressions and supported Assessment dependencies.
- Separate capability declarations and explicit source kinds for each native node.
- Independent Rule/Benchmark/manual/applicability/input editors.

Use shared schema primitives and reviewed capability metadata to populate general
forms; domain widgets improve presentation. JSON Schema alone cannot describe the
entire semantic contract, so explicit reference/behavior contracts and maintained
validators remain required. A bespoke hand-coded form for every capability would
repeat the maintenance burden the user is concerned about.

Native text remains editable and linked to the same nodes. Text can be a powerful
advanced tool, but “paste the complicated part yourself” does not satisfy complete
structured editing support. A raw-only implementation is labeled preserve-only.
Likewise a full-page diagram with thousands of nodes is not a usability solution.

## Make a deep chain understandable

Inspect one dependency path at a time, keeping other branches collapsed. Show:

- What feeds this value, and which selectors/States/Tests use it.
- Datatype, possible cardinality, named/embedded identity and reference scope.
- Ordered function arguments and Set operand order, especially COMPLEMENT.
- Whether a value is static, input-dependent or requires target collection.
- The source of a diagnostic and the affected transitive dependents.

In a preview, distinguish declared/inferred type/cardinality from actual observed
values/status. Known constant subexpressions may be evaluated using reviewed
semantics. A target-dependent Variable must not receive invented values. Intermediate
collection/error/completeness flags remain visible where preview is implemented.

Examples of necessary explanations: empty Variable consumed by an Object has
different behavior from empty Variable consumed by a State; filters apply before
the enclosing Set operator; multi-valued function operands can produce Cartesian
products; var_check/entity_check/State/Test aggregation operate at different scopes.
An editor must help the author see these facts without quietly changing them.

Possible views include a dependency outline, “where used” list, a focused graph,
typed expression tree, breadcrumbs and side-by-side native content. A recipe can
label a recognized subgraph without owning or rewriting its native semantics.
Performance needs indexed references, incremental validation and virtualized views,
not recursion depth restrictions or silent content reduction.

## A coverage matrix with separate evidence columns

For every feature and interaction, track:

| Obligation | Required evidence |
| --- | --- |
| Read/preserve | Import/save retains meaningful content, sharing, ordered expressions and unedited regions |
| Inspect | Correct dependency, type, scope and where-used information |
| Create/edit | General structured editor can construct/change every permitted form, including deep nesting |
| Refactor | Rename/change/replace updates correct references without cloning or breaking relationships |
| Validate | Native structure, semantic graph and document-binding diagnostics have explicit enforcement owners |
| Explain | Missing, unknown, incomplete and error behavior is accurately described; unimplemented preview is explicit |
| Guided presentation | Convenience view supports the feature when implemented; this is not a prerequisite for general support |
| Runtime agreement | Separate conformance/target evidence where evaluation/observation preview makes runtime claims |

All mandatory editing columns need evidence before claiming complete editor
support. Runtime agreement is separate: schema success, read-only preservation
and source round trips are not scanner equivalence. A product may support full
authoring while not implementing a reference scanner, provided it is candid about
preview/target execution coverage.

## Analyze the full semantic surface, not just the STIG sample

Three evidence tracks remain separate:

1. **Native contracts:** all supported source schemas, reviewed mappings, native
   semantics, reference locations, functions, graph constraints and documented
   source dispositions. Include schema-only/unmapped candidates in the gap register;
   valid future capabilities require explicit version support, not silently unknown
   fields in otherwise “complete” claims.
2. **Production:** pinned complete NIWC packages and their reachable assessment
   graphs. Existing 65-package conversion evidence can guide selection after
   verifying its pins/current status. The 736-rule RHEL/Windows Check Text reading
   provides requirement interpretation, not 736 resolved automation graphs.
3. **Conformance:** pinned OVAL Self-Assertion plus authoritative XSD/Schematron
   semantics and deliberate native-divergence cases. Rare valid constructs remain
   requirements even when the production STIG sample never exercises them.

Then generate legal compositions and invalid-nearby cases. Cover every function's
arity/datatype/status behavior; every legal variable-reference site; typed record
fields; every Set operation, filter action and filter-before-set boundary; forward
references and shared fan-out; all relevant existence/quantifier levels; and full
six-state truth plus collection flags. Also cover platform-specific traversal,
behavior defaults, supported capability versions, manual evidence and policy binding.

Large/deep fixtures should include hundreds/thousands of nodes, long mixed chains,
branching/sharing, nested records/functions/Sets, many consumers of one Variable
and narrow independent edits. Stress depths are tested values, not a new normative
maximum. Invalid cycles/dangling references/datatype mismatches must be rejected
with precise paths. Temporary invalid edits should remain repairable in drafts.

For transformation/edit tests, independently compare the untouched semantics and
expected effect of the intended edit. Two views using the same broken core can
agree; cross-frontend agreement is therefore insufficient. Property-based and
metamorphic tests can expose interaction bugs; finite tests alone do not prove
all possible runtime semantics. Composition needs a documented argument and
independent expected contracts, followed by target evidence for runtime claims.

## Architecture and sequencing consequence

TypeScript/React remains a proposal, but complete recursive native-model handling
and preservation are the first architecture gate. Begin with both a simple case
AND a hard mixed Variable/Object/Filter/Set case, plus shared references and invalid
cycles. A unix.file-only demonstration cannot justify the all-content architecture.
The generic editor and graph services take priority over recipes, hosted Git
integration and desktop packaging. Language/tool choice can change if evidence
shows it cannot meet these requirements.

Next bounded research (potentially expensive overall; individual inventory and
fixture tasks can be moderate): reconcile the complete native/capability scope,
link production/conformance cases to every row, identify uncovered interactions
and select adversarial acceptance fixtures before implementing the UI. The proposed
new research repository should inherit this contract and the pinned inventory;
schema/specification authority stays in scap-ng.

No current partial editor is being certified. No capability/schema/converter was
changed, no new repository or Board vote was created, and no test suite was rerun
to imply implementation proof. Provenance: **Inherited** native semantics and
mapping registry; **Adapted** prior direct-editor proposal strengthened by owner's
all-content requirement; **Common** coverage workflow/dependency views and release
gates; **Evidence/Audit** snapshot, explicit exclusions, gaps and scope limits.
