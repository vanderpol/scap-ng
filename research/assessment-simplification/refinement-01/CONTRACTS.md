# Refined contracts and comparison

**All SHALL/SHOULD/MAY requirements below are experimental proposals.**
They do not amend the established specification.

## Finite publisher-table expansion

The table SHALL have a closed kind, stable row IDs, explicit publisher defaults,
and finite literal rows. Organizational Input SHALL NOT supply rows, templates,
capabilities, commands or Test identities. Rows SHALL expand before publication
into ordinary Tests/Objects/States. Duplicate IDs SHALL fail; identical predicates
with distinct source identities SHALL remain distinct Tests. Reordering rows
SHALL preserve their named contracts. A change to a shared default SHALL be
visible as an authoring change affecting every row; per-row overrides remain
visible rather than inherited from runtime state.

This is a bounded two-kind authoring tool. No arbitrary macro language, generic
expression evaluation or new runtime capability has been implemented. A future
tool SHOULD expose an expanded diff so reviewers see all affected predicates.

The independent XML projection resolves all constant/concat Variables in the
audit selector graph, preserving scalar cardinality and literal regex bytes.
Other functions, multi-valued results, unfamiliar selectors, non-AND logic,
negation and applicability-marked criteria fail the projection. These capabilities
are not removed from SCAP-NG: they are outside this experiment's proof boundary.
The source tree is traversed from its actual seed, including extended Definitions;
the emitted tree contains each corresponding Test once. Incidental XML node
storage order is not execution order.

Comparison includes capability, selector values/operations/datatypes, instance,
audit filesystem scope and regex/item-creation behaviors, State field and
entity quantifiers, Test existence/check and State operator. Effective defaults
are read against pinned XSD; source explicitness remains in original XML/evidence.
The projected equality proves these bounded contracts, not all collector behavior
(canonical symlink resolution, textfile matches, permissions, target versions,
regex dialect, filesystem defaults outside the projection or runtime provenance).

The 17 folded audit Variables contain deterministic scalar constant/concat
expressions in this graph. Removing them in this experimental output is **not**
permission to inline shared Objects or runtime Variables in general. Existing
supported Sets, filters, functions, record fields and external inputs remain.

The two anomalous b64-named rows continue to select b32. The table has 24 Tests
and 22 distinct predicates; deduplication would change execution identity and
potential collection/provenance. A corrected 24-way matrix requires separately
identified intent-correction content. One global backend population is rejected:
eleven good backend Items can hide the twelfth missing backend under a global
`some` check; twelve per-row Tests correctly retain the missing-resource failure.

The runtime regression supplies observations to the existing schema-derived
result combiner for both projections. It exercises 3,816 row/collection-count/
State-outcome combinations, plus all 216 three-leaf six-state AND combinations.
The same helper is intentionally shared: this checks preserved result-controlling
parameters and grouping, **not** agreement between independent evaluators.
Incomplete zero-Item State evaluation is excluded rather than inventing an Item
to satisfy the helper's nonempty-result precondition. There is no target execution.

## DNS administrative acquisition

The fixed script MAY acquire observations with supported DNS administrative
cmdlets. It SHALL NOT scan the filesystem, accept script input, concatenate
commands from zone names, or return policy compliance Booleans. Zone names bind
to a named cmdlet parameter. The caller SHALL enforce timeout, exit code, output
bytes and UTF-8 JSON decoding. The prototype decoder rejects duplicate JSON
properties, duplicate/undeclared zone keys, invalid types, negative counts,
truncated output and nonzero/timeout outcomes.

Each inventory key SHALL identify its zone. Each RR type SHALL have status;
successful/partial observations have a nonnegative integer count, while errors
and not-collected observations SHALL NOT pretend to have zero counts. Complete
inventory with a missing zone record is a protocol error. Incomplete inventory
cannot prove all required zones satisfy the rule. A confirmed violation may
remain false under AND even when another observation is unknown/error, using the
existing technical-result precedence.

The candidate evaluator keeps the source's server-wide complete-empty/all-AD-
integrated bypass. A mixed inventory still evaluates all selected forward zones;
it does not silently skip individual integrated zones. Classified-network and
platform applicability SHALL stay in separate Assessments. Unsupported transport
is error, not successful empty inventory. Unknown/partial RR acquisition yields
unknown even when an observed count is favorable.

The script is not target-tested; cmdlet field availability, enumeration atomicity,
escaping/encoding, query privileges, module versions and record-type support
remain open. A GUID labels an acquisition **session**, not an atomic snapshot.
Pinned Server2025 cmdlet documentation lists RRSig/DnsKey/NSec3 and named ZoneName
arguments, but does not establish this target's zone metadata or privileges.
Inventory and per-zone queries can race; a future adapter SHALL detect/report a
changed snapshot or preserve incomplete status rather than claiming consistency.
Per-key identity is enforced by the decoder, not the disposable local JSON schema.

The original per-command Variable-instance behavior is not independently executed.
Therefore this adapter is a typed-acquisition proposal with stronger explicit
scope/status, not a proven lossless replacement. Three favorable RR counts from
three different zones fail the candidate's per-zone requirement. This is a
counterexample to flattening; it is not proof of a source OVAL false pass.

## Apache explicit-occurrence acquisition library

The restricted parser SHALL consume precollected native file snapshots with
statuses. It SHALL preserve installation/context/file/line and occurrence order,
including repeated Include references. It SHALL NOT derive effective settings,
merge installations, insert defaults, discard earlier conflicting values or
scan files in shellcommand. It supports literal nested Include/IncludeOptional
paths and descriptive VirtualHost/Directory context only. Glob includes,
conditional sections, variable expansion and unsupported grammar explicitly fail.
The caller supplies ServerRoot. A directive changing it fails before subsequent
relative Includes; selecting against the old root is a demonstrated false-good
counterexample in the restricted acquisition model, not an Apache source defect.

IncludeOptional SHALL ignore only a path with explicit native `does_not_exist`
evidence. A path absent from an incomplete snapshot is uncollected, not absent.
Unreadable optional paths remain errors. Include cycles and resource limits are
acquisition failures; they SHALL NOT become policy failures or partial good passes.
Valid files may retain observed rows alongside the aggregate error for explanation.

Tests cover spaces in paths, nested includes, repeated directives/Includes,
separate installations, native absence/access failure, unsupported contexts,
cycles and budgets. They do not establish Apache's full grammar or original shell
acquisition equivalence. The useful architectural proposal is a shared typed
explicit-occurrence interface, reused by KeepAlive, SessionCookie and DocumentRoot
selection. Effective configuration remains a separate high-cost, changed method.

## Measured comparison

| Case/method | Author-visible change | Scanner cost | Compatibility and evidence |
| --- | --- | --- | --- |
| Audit finite table | 65 named runtime nodes in before snapshot become 4 regex templates + 24 publisher rows; output retains 24 Objects/Tests, folds 17 static Variables | No proposed new collector; existing regex/file work remains | All 24 projected contracts equal; 924 → 127 authoring lines, 34,682 → 4,376 bytes; two anomalies retained |
| Crypto finite table | Twelve expected paths/values and one per-kind override replace repeated node scaffolding | Existing symlink/file collectors unchanged in concept; output still 36 nodes | All 12 projected contracts equal; 339 → 58 lines, 8,853 → 2,028 bytes; no row omitted |
| DNS typed acquisition | One fixed query interface and per-zone typed RR observations replace command-building chains | Module/platform, scope, query races, errors and key completeness move into adapter | 256 two-zone predicate combinations plus adversarial transport/status cases; no Windows execution |
| Apache shared explicit occurrences | Reusable acquisition interface across three cases; policy predicates remain visible | Substantial discovery/include/context work remains; limited parser implemented | Synthetic literal-include fixtures only; glob/conditional/effective semantics unsupported |
| Windows directory/principal tables | Candidate reuse of finite rows with native effective-rights Objects and filters | Existing Windows collector complexity remains | Inherited source/matrices only for expansion; do not claim this table emitter supports AD graphs |

Line/byte reductions describe these two authoring files, excluding the shared
expander/oracle code and expanded review artifact. They are secondary metrics,
not a claim of runtime speed or usability improvement. Static row defaults reduce
repeated editing locations, but regex grammar and twelve backend expectations are
necessary review burden. No field-author trial or performance measurement ran.

## Rejections and unresolved choices

- Reject runtime-controlled tables/tests/scripts and compliance-returning collectors.
- Reject global existence over heterogeneous required paths and deduplication by predicate.
- Reject generic joins as a default response to command/dataflow verbosity.
- Reject effective Apache defaults/override collapse as lossless replacements for explicit checks.
- Reject error-to-empty-success, optional-uncollected-to-absent and stdout truncation as passing evidence.
- Retain native filesystem traversal, exclusion, permission, symlink/junction and collection contracts.
- Retain every supported capability; deprecated Tests are blocked, never supported by these proposals.

Before a Board-facing language change: decide whether finite tables belong only
in authoring tooling; define collector scope/status/consistency rules; establish
how a changed method gets distinct Assessment identity; obtain implementation and
author feedback. No unresolved decision currently blocks this bounded research.
