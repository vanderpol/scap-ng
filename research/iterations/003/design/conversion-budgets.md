# Converter computation budgets

**Status:** M0 implementation contract; thresholds are implementation policy,
not OVAL language limits.

Conversion limits SHALL be reported independently from invalid source,
unsupported semantics, and runtime Assessment truth. A valid OVAL document may
exceed an implementation budget without becoming invalid OVAL.

The converter budget surface is represented by
`scap_upconvert_v003.conversion_budget.ConversionBudget`:

- `dependency_nodes`
- `dependency_edges`
- `expression_depth`
- `generated_values`
- `value_bytes`
- `elapsed_ms`

A `None` value means that resource is not bounded by this budget instance.
No number in this contract is normative for SCAP-NG.

A breach produces a deterministic diagnostic shaped as:

`conversion_resource_limit:<resource>:limit=<n>:observed=<n>`

The affected Definition remains identifiable. A resource breach SHALL NOT be
reported as semantic `false`, source-invalid, or successful partial
conversion.

## Current wiring

The complete reachable-feature worklist accepts an optional budget and enforces
dependency-node, dependency-edge, expression-depth and elapsed-work limits.
With no supplied budget its behavior is unchanged.

Static Variable evaluation now accepts the same optional budget. `concat`
preflights `generated_values` before Cartesian-product allocation when the
candidate cardinality is known; all exact-static value results enforce both
`generated_values` and UTF-8 `value_bytes`. A budget breach returns a
`resource_limit` result without partial values. The older `max_values` safeguard
remains a separate compatibility/default implementation ceiling for callers
that have not yet moved to the explicit budget object.

Native lowering still catches host Python recursion exhaustion as
`conversion_resource_limit:python_recursion`. Replacing remaining recursive
paths or routing them through explicit `expression_depth` policy is still
required.

## Non-goals

- These budgets are not evidence caps.
- They do not authorize truncating source ASTs or generated Assessments.
- They do not define scanner runtime limits.
- They do not establish a language maximum graph depth.
- They do not repair cycles or unsupported content.

Focused adversarial fixtures cover deep dependency chains, node/edge/depth
limits, elapsed-work diagnostics, and the existing pre-allocation Cartesian
product safeguard.
