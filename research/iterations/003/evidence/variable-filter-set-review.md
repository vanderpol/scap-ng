# Variable filter and set conversion review

Date: 2026-09-30

Base converter commit: `ad8b4c12695efdcb578efa102f166152a784ffdc`
Scope: educational review followed by verified converter and source-audit fixes.
Existing source architecture is retained; no scanner runtime equivalence or
universal graph-depth support is claimed.

## Findings and changes

1. Feature accounting did not traverse variables in filter States. Missing
   Variables and publisher Objects reachable through their object components
   could escape the unsupported-feature inventory. It now indexes the source
   nodes and follows a worklist across Definitions, Tests, Objects, States and
   Variables, including sets and filters.
2. Feature accounting had no visited Object guard. Cyclic set references raised
   `RecursionError`. The worklist terminates on visited nodes while preserving
   source diagnostics; it is not itself a general cycle-policy decision.
3. Native variable lowering checked reserved names before active expressions,
   permitting direct/indirect cycles to appear as completed shared Variables.
   Active-node checking now precedes reuse. Cycles that cannot finitely lower
   produce blockers, with no partial Assessment.
4. Static synthetic `independent.variable_object` set evaluation also lacked an
   Object cycle guard. It now returns an explicit cycle status.
5. Static concat allocated the Cartesian product before enforcing its 4096-value
   default ceiling. It now checks candidate cardinality first and returns
   bounded status without partial values. Native lowering retains the complete
   expression; this does not change OVAL concat semantics or create a runtime
   evidence cap.
6. The source type audit only covered direct Test bindings. It now checks
   nested-set Object reference compatibility iteratively at every depth.
7. Very deep finite graphs still encounter recursive native lowering limits.
   That condition now reports `conversion_resource_limit:python_recursion`
   rather than crashing or implying invalid OVAL.

## Validation evidence

`python tools/test_variable_filter_dependencies.py` passes 15 focused tests.
Five targeted tests were also executed against the original converter/IR:
all five exposed the pre-change defects (four failed assertions and one
unbounded Object-set recursion). The other fixes have separate negative cases.

The focused suite covers chains and sets through depth 32, nested functions,
reused completed Variables, filter-hidden dependencies, direct/indirect and
mixed cycles, a 1200-node feature-accounting chain, resource-limit reporting,
qualified set types, missing references, and concat pre-allocation limits.
An XSD-valid incompatible set reference reproduces the upstream pattern's
depth-4 coverage gap. This test isolates `oval-def_setobjref`; it does not assert
that every third-party validator accepts the defect.

The existing effective-attribute, State-entity, census-summary and explicit
semantics suites add 31 passing tests (46 total).

Production evidence is separate from these synthetic language tests:

| Checked-in split corpus | Source XML files | Definition instances | Comparator equal | Blocked |
| --- | ---: | ---: | ---: | ---: |
| RHEL 9 V2R9 | 418 | 811 | 811 | 0 |
| Windows 11 V2R10 | 246 | 470 | 469 | 1 |

These are per-rule OVAL singles committed under iteration 001, not a fresh
whole-package split or a count of unique rules/Definitions. Nested extended
Definitions and shared dependencies can be counted repeatedly. The v003
converter is used; no iteration-001 generator is imported.

Both manifests pin NIWC `8c8e5dff860af6b1290ee9273a282db24278f8d5`.
RHEL9 ZIP SHA-256:
`70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5`.
Windows11 ZIP SHA-256:
`e4b8d55b58aa80124bd0974977af4c7f7bde35c748e2940e02857419292d8c3d`.
The existing Windows blocker is `windows.user_test` in
`oval:navy.navwar.niwcatlantic.scc.windows:def:253476`; the original converter
produces the same 469/470 comparison and blocker. It is not a new regression
and remains excluded under the deprecated-test policy.

The expanded set audit inspected 114 references in RHEL9 singles and 56 in
Windows11 singles, with zero mismatching or missing Object targets.
These counts include repeated per-rule dependencies.

Reproduction:

    python tools/test_variable_filter_dependencies.py
    python tools/scap_ng_roundtrip_v003/roundtrip_corpus_v003.py --corpus research/iterations/001/generated/niwc-rule-splits/rhel9 --include oval.xml --out /tmp/rhel9-variable-review --report /tmp/rhel9-variable-review.json
    python tools/scap_ng_roundtrip_v003/roundtrip_corpus_v003.py --corpus research/iterations/001/generated/niwc-rule-splits/windows11 --include oval.xml --out /tmp/windows11-variable-review --report /tmp/windows11-variable-review.json

The Windows command intentionally returns nonzero for the existing deprecated
test. Do not relabel it as a passing complete benchmark. Corpus comparisons
establish representation fidelity, not target execution, full XSD/Schematron
conformance, or independent assessor truth.

## Provenance and remaining work

| Category | Source | Use |
| --- | --- | --- |
| Inherited | Pinned OVAL 5.12.3 core and Unix schemas | Recursive components/sets, same-type set references and concat cardinality semantics |
| Common | Worklist traversal, active-node guards and product cardinality calculation | Original implementation using ordinary graph algorithms; no external code copied |
| Evidence/Audit | Original synthetic fixtures and original-versus-patched checks | Reproducers and bounded claims about converter behavior |
| Evidence/Audit | Pinned NIWC singles and their manifests | Production migration regression; separate from language conformance |
| Evidence/Audit | Coworker modernization draft and reported depth concern | Educational impetus only; no draft text or private scanner implementation copied |

Follow-ups: #10 (variable graph/function conformance), #11 (set/filter outcomes),
#37 (upstream pattern gap) and #38 (resource budgets and remaining recursion/
sharing limitations). General Board cycle policy remains pending in
`../board-review/dependency-ordering-and-cycles.md`.
Do not change original source, upstream schemas or native architecture to mask
these findings. Resource limits and incomplete/error propagation need explicit
conformance contracts before reference-scanner implementation.
