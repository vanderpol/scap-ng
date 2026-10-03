# Draft 0.2.0 Item inclusion/materialization contract

Provenance: **Evidence/Audit** of the owner's instruction to complete the next
schema task; **Common** original helper/tests and synthetic examples. Adapts the
maintained Assessment Result and collected Item drafts; no external target
observations are represented as new conformance evidence. Working draft pending
Board review; 0.1.0 and conversion output remain unchanged.

## Inclusion scope

Result assembly accepts `item_scope="all"` by default, or `"consumed"`. This is
an explicit producer serialization control, not a new authored Object selector,
State predicate, Test execution control or Tailoring/Organizational Input field.
No content-authored inclusion syntax is invented by this checkpoint.

`all` includes every locally available observation supplied to the invocation.
It does not mean every Item in an unbounded target population: acquisition caps,
errors and population/evidence completeness remain explicit. `consumed` retains
all Items referenced by recorded Test/per-Item results, included Variables'
`item_refs`, and actual direct or indirect field-use lineage. It SHALL NOT discard
Items required by existence, comparison, filter, selection, Variable extraction
or decisive explanation. The producer must record those uses completely.

Materialization validates available Items before selection, so malformed or
inconsistently redacted unused fields cannot disappear silently. It preserves
consumed canonical fields in full; `reported_elements` remains a later derived
projection. Runtime Object Item-reference lists are restricted to local included
Items. `item_materialization` records original available/included/omitted counts
both per invocation and per Object. Available counts describe the supplied
observation set, not an independently verified whole-target population. They
are producer assertions, not independently provable from omitted payloads.

Serialization omission of genuinely unused Items does not by itself change
technical truth or acquisition completeness. Collection status still describes
acquisition, while materialization counts describe representation. Source caps
and incomplete evidence SHALL NOT be relabeled complete by either scope. Existing
result artifacts without the new optional accounting metadata remain readable;
new helper assembly emits it. Already-materialized inputs are rejected by the
helper to avoid overwriting original availability accounting.

## Verified imports

`import_items` requires exact UTF-8 JSON source artifact bytes, an independently
trusted `sha256:<hex>` pin, expected source execution ID, exact target reference,
exact nonempty binding-set ID, selected source Item IDs and an explicit unique
source-to-local ID mapping. JSON duplicate members/nonfinite numbers, bad byte
pins, wrong targets/bindings, missing source Items, invalid observations and local
mapping collisions fail. Local collisions with existing Items fail at assembly.

The helper copies canonical typed observations, not source Test truth or report
projections. It preserves original values, status/redaction, locators, numeric
identities and name-resolution context without another lookup. New origin pins
record source execution, source Item ID, exact artifact digest, binding context
and source completeness. Reimporting appends the earlier origin to
`context.import_history` and records the immediate source separately. Imported
Items remain locally materialized so consumers need no external join to explain
local Tests/Objects/Variables.

New imports cannot use different target/binding contexts. Different-context reuse
may someday be justified by a reviewed collector-specific cache key, but is not
silently assumed here. Digest verification is not a signature, producer trust,
freshness guarantee, cache authorization or proof of source technical accuracy.
The producer must establish those before reuse. Legacy two-field origins remain
unverified provenance snapshots; they do not establish verified import pins.

When included imported observations carry incomplete source population/evidence
flags, assembly conservatively propagates those two flags as false and validation
rejects their loss. This may be more conservative than a future collector-specific
subset-completeness proof. Consumer logical completeness and outcome are independently
supplied/evaluated; the source Assessment's final outcome is never imported as
local Test truth.

## Coverage and remaining gates

Sixteen focused methods cover all/consumed defaults/counts, indirect/Variable uses,
empty consumption, missing/duplicate identities, invalid unused observations,
verified import pins, target/binding errors, reimport chains, redaction, local
collisions, incompleteness, metadata tampering and committed known-result copies.
Current regression CI includes the suite on Ubuntu and Windows.

This completes the bounded representation/materialization helper, not collection
cache execution, real collector lineage, freshness authorization, evidence-cap
algorithms or multi-context result-package composition. The complete vendor corpus
(#128), OVAL 6/untested capability audit (#131), broader result-package/Benchmark
integration, target conformance and Board decisions remain release prerequisites.

Local validation checkpoint: all **69** current-regression commands passed,
including the **16** focused methods and existing conditional/result/reporting
contracts. The preservation audit reports no failures across 34,242 baseline
paths; all draft schemas meta-validate in the result integration suite. The
committed exact-byte import and scope/count fixtures pass offline checks.
