# 0.2.0 Assessment Result integration checkpoint

Provenance: **Evidence/Audit** of owner direction to integrate the merged
conditional, collected-Item and reported-elements work; **Common** original
integration code and synthetic fixtures. The result structures adapt maintained
0.1.0 repository contracts and the already-reviewed 0.2.0 draft Item extensions.
No external content or target acquisition result is represented as new evidence.

## Representation and identity

The new versioned `assessment-result.schema.json` connects each invocation's
expression trace, Test/Object/Item/Variable results, dependency execution IDs,
completeness and optional marked Item report. Existing Test/State/entity/manual
result layers are retained. Shared result types and collected-Item contracts
are promoted into the actual v0.2.0 namespace, with the approved lookup/locator/
import provenance shapes. Capability-specific Item contracts are generated from
the maintained 100 capability mappings: 99 produce Items; unsupported/unknown
capabilities and fields are rejected by the semantic validator.

Each invoked Assessment receives a distinct execution reference within a run.
Reusing an Assessment in the same target/binding context reuses that reference.
Each trace row has an owner execution reference; a dependency row additionally
identifies its child's execution. The expression-stage result now includes an
invocation ledger. It never exposes the callback's raw binding values.

The `assessment-result-set.schema.json` container is development transport for
separate per-invocation artifacts, not a replacement Benchmark/Rule Result or a
final result-package format. Each invocation's Test/Object/Item/Variable links
resolve locally. Dependency summaries resolve to exact identity/version/outcome
records in this transport. Imported Items are locally materialized observations
with original origin references retained; this helper does not import or
re-resolve external Items, or silently acquire evidence from a dependency.

## Validation and reporting

`tools/assessment_results_v02.py` assembles records from an expression invocation
ledger and explicit per-invocation observations. It rejects duplicate execution
or local identities, missing materialization, wrong targets, wrong source
bindings, mismatched dependency executions, missing Test/Item field-use lineage,
compared entities absent from lineage, and altered projections/completeness.
It replays authored expression scheduling using recorded normalized Test/manual
outcomes and compares the trace, including skips and reuse. This verifies logical
consistency; supplied Test and State outcomes still require producer conformance.

Reports use the merged reporting module and retain canonical Items in full.
All known executed uses are supplied by the producer, including indirect
Variable/Filter/selection use. Full paths and other identity/decisive requirements
must be recorded explicitly. The helper does not guess complete acquisition
lineage from Test references. Producers remain responsible for redaction across
every result path; recursively inconsistent `redacted: true` values are rejected,
including comparison/evidence paths. Selection is not a confidentiality control.

Completeness flags are mandatory producer observations, never inferred from a
Boolean outcome or successful schema validation. Bounded/incomplete acquisition
may preserve a decisive false outcome and must preserve its incomplete flags.
Bindings may be included as protected/redacted records with provenance; expression
scheduling cannot independently establish effective input values from traces.

## Limits and next gates

This remains an experimental integration slice. The expression evaluator supports
one target and one shared binding context per run. Separate contexts/runs have
distinct execution IDs; multi-context result-package composition is downstream.
The adapter does not perform collectors, Variable functions, State comparisons,
manual lifecycle, evidence capping or automatic Item inclusion/import selection.
It does not claim a complete 0.2.0 release or scanner equivalence. The canonical
schema closes the representation gap; production acquisition/lineage generation,
final Item inclusion/import controls, result-package/Benchmark linkage, full
vendor cases (#128), untested capability/OVAL 6 audit (#131), and Board disposition
remain. Issue #125 remains open for those broader acceptance gates.

All 0.1.0 files remain unchanged. The original reported-elements feature remains
its ordinary one-commit unit; this separate integration commit can also be
reverted. No frozen review iteration or historical workflow is modified.

## Validation

The focused suite covers six known guard outcomes, actual fixture UID comparison,
shared dependency reuse and distinct executions, local evidence/import origins,
manual six-state outcomes/provenance, redacted bindings, wrong/duplicate/dangling
references, altered scheduling, false projection values, incomplete evidence,
unavailable identities and all draft schema meta-validation. Current regression
CI runs it and validates the committed full result snapshot on Ubuntu/Windows.

Local checkpoint: all **68** current regression commands passed, including the
**17** result integration methods and the unchanged 465-evaluation conditional
suite. The preservation audit reports no failures across 34,242 baseline paths.
Source examples pass the authoring vocabulary check; all draft schemas
meta-validate. Vocabulary and schema checks do not establish target equivalence.
