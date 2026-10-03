# Proposed authoring semantics, version 1

**Experimental proposals, not amendments to the current native specification.**
The prototype grammar is documented here and checked by executable validation;
there is no newly accepted production schema. Established backend behavior and
proposed author conveniences are distinguished below.

## Established target and proposed lowering

The current reviewed `unix.file` mapping exposes twelve independent permission
booleans. A State compares one field; a Test references an Object and States with
explicit existence/item/State quantifiers. The emitted capability declarations
are independent on all three kinds of nodes. Metadata/sections use current
presentation order. The author abbreviation `files` chooses a fixed compiler
target, rather than changing native capability inference rules.

Proposed requirements:

1. `permissions_at_most` SHALL denote a set allowance, not numerical mode ordering
   or exact equality. Its four categories SHALL list unique literal typed rights:
   owner/group/other accept read/write/execute; special accepts setuid/setgid/sticky.
   Empty categories SHALL be explicit. Omitted categories SHALL be an error,
   rather than a hidden policy default.
2. For each forbidden right, the compiler SHALL emit a Boolean false comparison
   State with native `operation: equal`, `datatype: boolean`, `match: all`, and
   entity `existence: some`. Allowed rights SHALL impose no comparison and SHALL
   remain independently addressable in native content. Their individual observation
   errors SHALL NOT poison this predicate; an Object-level error still applies.
3. `every` SHALL retain native per-Item all semantics. All generated States SHALL
   refer to comparisons on the same Item through the native Test's `states_match:
   all`; fields from different Items SHALL NOT satisfy each other's constraints.
4. `missing: allowed` SHALL compile to `existence: optional`; `violation` SHALL
   compile to `some`. This controls confirmed object absence only. It SHALL NOT
   turn collection failure, a missing collection record, or unknown values into
   a confirmed empty population.
5. Native six-state result and collection control flow SHALL be preserved by this
   transform. It SHALL NOT import method-02's experimental monotone-positive
   relation semantics or its smaller four-state model. The current prototype
   delegates its synthetic Test control-flow checks to the pinned repository
   OVAL-derived helpers; that delegation is evidence of alignment, not independent
   scanner conformance.
6. Objects SHALL retain exact literal selectors, matcher strings, traversal and
   filesystem scope. The prototype SHALL NOT ignore account discovery, Sets,
   Filters, Variables or other unsupported source plans. Regex dialect/selection
   behavior SHALL remain the native capability's contract, not Python's regex.
7. A compiler SHOULD retain stable Test identity and map generated States back to
   author clauses. Such maps SHALL be separate evidence, not executable legacy
   serialization. Native output SHALL run without the compiler's source map.
8. Publisher-authored graph structure SHALL be fixed at compile time. Organizational
   Input SHALL NOT inject commands, select Tests or change the graph. Future
   delegated expected values MAY use established constrained typed inputs after
   separate implementation/review; this bounded prototype rejects them.

## Supported grammar and deliberate boundaries

Root keys: `format: experimental-permission-authoring-v1`, literal `id` and `title`,
nonempty `objects` and nonempty `tests`. IDs use stable lowercase names independently
of titles. Evaluation is the fixed conjunction of the authored Tests. No policy,
platform/applicability selection, score or runtime truth is placed in this form.
The resulting Assessment has purpose assessment/class compliance; applicability
remains a separate Assessment in the existing Benchmark → Rule → Assessment model.

Each Object has `files` with either literal `path` plus explicit `filesystem`, or
literal `directory`, `names_matching`, nonnegative integer `depth`, native Unix
`recurse`, and `filesystem`. `depth` abbreviates `max_depth`; its specific documented
name benefits the limited human-facing form without renaming native traversal.
Full-path selection SHALL NOT take directory traversal. Native schemas reject
Windows junction traversal on Unix and unknown filesystem scopes.

Each Test has exactly `every`, `missing`, `permissions_at_most`. Arbitrary commands,
expressions, Variables, six-state literals, new providers or conditions are not
part of this prototype. Unknown fields and duplicate YAML keys are rejected;
SafeLoader rejects executable YAML tags. This is an intentionally small research
compiler, **not removal of advanced forms or supported native capabilities**.
Advanced authoring SHALL remain available in ordinary native Assessments.

The fully unrestricted twelve-right allowance is rejected here. Correctly lowering
it to an existence-only Test needs a separate zero-predicate control-flow test set;
it is not silently emitted as an empty State conjunction. This implementation
limit does not imply a new native capability restriction.

## Concrete result cases

| Observations for one scoped Test | Expected result in bounded checks |
| --- | --- |
| Complete, mode 0740 or 0600 | true |
| Complete, mode 0604 | false: other read is forbidden despite smaller numeric mode |
| Complete, special setuid bit present | false |
| Forbidden bit unknown; other constraints true | unknown |
| Forbidden bit comparison error; other constraints true | error |
| Allowed owner-read bit unknown/error; forbidden bits false | true |
| Required forbidden-bit entity explicitly does not exist | entity existence false; not a passing permission observation |
| Complete two files, one violating | false, even if another passes |
| Complete two files, one false and another unknown | false under native all aggregation |
| Incomplete collection with passing observed file | unknown |
| Incomplete collection with violating observed file | false under preserved decisive native all semantics |
| Object collection error, with a known bad file too | error under preserved Object-level control flow |
| Confirmed no user initialization files | true for optional existence |
| Confirmed no root initialization files | false for some existence |
| Not collected / missing collection record | unknown, not confirmed absence |
| Not applicable collection flag | not applicable; no four-state coercion |

The test suite feeds explicit comparison outcomes and collection summaries. It
does not define a new Item wire protocol, interpret an omitted field as an observed
false bit, or claim every inconsistent summary is legal. Full collector validation
and independent target evaluation remain subsequent work.
