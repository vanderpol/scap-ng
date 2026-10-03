# Capability reference template

**Status:** authoring guide for this incomplete catalog. Replace every placeholder
before publishing a capability reference; this template does not define a new
capability or claim implementation support.

## Identity and status

Record canonical capability identifier, supported source/result specification
versions, accepted versus proposed semantics, mapping location, target/platform
scope, and implementation/conformance maturity. Distinguish NG schema version
from an Assessment's own revision.

## Purpose and acquisition

Explain the resource/value being assessed in terms an author can understand.
Identify the Test's source kind: Object, direct Variable, or none. Describe target
identity, platform/version prerequisites, privileges, acquisition boundaries,
and meaningful behavior settings. State whether named, embedded, Set, and filter
forms are supported. Do not require a particular shell command/backend merely
because source documentation uses it as an example.

## Object selectors

List each native selector with datatype, cardinality, alternatives, nullable
meaning, allowed operations/values, units, and selection effects. State when
combinations are invalid. If no Object exists, explain why and reject artificial
Object indirection. Link shared traversal/selection rules rather than copying
independently maintained truth tables.

## State and Item field reference

Provide one row per field with native name, datatype/cardinality, meaning/units,
selector/comparison/result-only role, absence/error semantics, and a source
documentation locator. Explain fields whose names invite mistakes, such as inode
change time versus creation time, mode bits versus effective access, or enum-like
values whose native contract does not actually restrict the full value domain.

Expand inherited source fields and structured record/list contracts; do not
assume an empty local declaration means an empty contract. Document every
supported uncommon field. Result-only additions do not become selectors or
predicates without an explicit separately justified decision.

## Test behavior and results

Describe source binding, existence, comparison and State/Item aggregation.
Link shared rules and document any justified exceptions. Cover zero/one/many
resources or values, denied/failed collection, unknown, N/A, not evaluated,
incomplete population, entity statuses, and evidence truncation where meaningful.
Keep technical truth separate from Rule-policy outcome.

Explain applicable reported-element controls, required identity/decisive fields,
redaction, resolved names and lookup provenance. Identify which effects are
implemented and which remain specified or unresolved.

## Examples and expected results

Link a small maintained standalone Assessment, fixtures/setup, independently
explained expected results, and reproducible commands. Include meaningful
positive, negative, boundary, invalid-reference, absence/error, and interaction
cases. Record the coverage gap if a case or target is unavailable.

Label synthetic callback outcomes, recorded observations, model-only cases,
migration evidence, and live target execution separately. A Test title or a
comment containing a capability name does not establish conformance coverage.

## Migration and provenance

Pin source repository/artifact revision, schema/documentation files and relevant
element/type locators. Record native field crosswalks, retained semantics,
intentional divergences, effective deprecation/governance disposition, source
defects, and unresolved interpretations. Use Common, Adapted, Inherited, and
Evidence/Audit classifications accurately.

## Open questions and completeness

List unresolved collection/comparison behavior, missing target execution and
oracle cases, and linked tracking issues. A reference is complete only when all
native fields/settings have a disposition and the reader can distinguish defined
behavior from an open question. Catalog completeness additionally requires every
supported capability and every shared Assessment feature to be accounted for.
