# Observation execution/result contract research

**Status:** research only; tracked by #166. No normative 0.3 schema change.

## Design goal

An Observation is a reusable producer of gathered or derived data. It does not
perform Tests and does not produce Assessment truth.

The result contract should therefore reuse existing SCAP-NG runtime concepts
without pretending an Observation is an Assessment.

## Source artifact

The bounded Apache prototype currently proves value exports:

```yaml
observation:
  id: shared.apache.httpd.discovery
  version: 1
  specification:
    id: scap-ng.pre-alpha.observation
    version: 0.3.0-research

  objects:
    # private acquisition graph

  variables:
    # private derivation graph

  exports:
    httpd_executable:
      kind: values
      variable: apache-path-httpd-or-apache2-variable
      datatype: string
      cardinality: zero_or_more

    primary_and_included_configs:
      kind: values
      variable: httpd-conf-merged-included-conf-files-from-include-refernces-in-variable
      datatype: string
      cardinality: zero_or_more
```

The final language may also support an Item export:

```yaml
exports:
  configuration_files:
    kind: items
    object: configuration-files
    capability: unix.file
```

Only `kind: values` is proven by the current Apache prototype. `kind: items`
remains a candidate that should reuse the existing Item/materialization work
rather than invent a parallel representation.

## Execution identity

A candidate Observation execution/result needs:

- `execution_id`;
- immutable Observation identity/version/content digest;
- `target_ref`;
- effective input/binding identity when inputs exist;
- completeness;
- diagnostics;
- private Object collection results and Variable results as needed for
  provenance/debugging;
- declared export results.

It deliberately does **not** have:

- Assessment `class`;
- Assessment `purpose`;
- Test outcomes;
- an `evaluate` tree;
- a six-state technical truth `outcome`.

## Top-level status

A truthless execution still needs to say whether its requested work completed.

Candidate top-level status:

- `complete`;
- `incomplete`;
- `error`;
- `not_evaluated`;
- `not_applicable`.

Zero observations is not itself an execution failure. For a value export, the
existing Variable-result `zero_values` status distinguishes a successful
zero-cardinality result. For an Item export, Object/collection status and
Item references retain the corresponding acquisition meaning.

This top-level status is execution characterization, not technical truth.

## Completeness

Reuse the existing result completeness vocabulary:

```yaml
completeness:
  logical_complete: true
  population_complete: true
  evidence_complete: true
  stop_reason: null
```

For an Observation, `logical_complete` means the declared derivation graph
reached a definitive runtime status, not that a policy proposition evaluated
true or false.

If that wording proves misleading, the field name should be revisited rather
than silently redefining it. Population/evidence completeness already have the
right meaning.

## Value exports

A `kind: values` export should preserve the semantics already represented by
`variable-result.schema.json`:

- datatype;
- runtime status;
- runtime cardinality;
- typed values;
- Item references consumed while deriving the values;
- provenance;
- diagnostics.

Conceptually:

```yaml
exports:
  primary_and_included_configs:
    kind: values
    source_variable: primary-and-included-configs
    result:
      datatype: string
      status: complete
      cardinality: many
      values: [...]
      item_refs: [...]
      provenance: {...}
```

The authored contract cardinality (`zero_or_more`, etc.) and runtime observed
cardinality (`zero`, `one`, `many`) are different concepts and should not
share one field silently.

## Item exports

A future `kind: items` export should reuse:

- Object collection-result status/completeness;
- canonical collected Items;
- Item origin/import provenance;
- source execution identity;
- source digest;
- binding-set identity.

This should converge with the existing item-materialization/runtime-reuse work
rather than create an Observation-specific Item format.

## Consumer binding

Research consumer form:

```yaml
observations:
  apache:
    source: ../../shared/observations/apache-httpd-discovery.observation.yaml
    expected_id: shared.apache.httpd.discovery
    expected_version: 1
```

A consumer may reference only declared exports:

```yaml
variable:
  observation: apache
  export: primary_and_included_configs
```

or an equivalent final syntax.

Private Object/Variable names in the Observation are not addressable by the
consumer.

## Compatible execution reuse

A scanner may reuse one Observation execution across multiple consumers only
when the execution context is compatible.

At minimum, compatibility requires equality of:

- Observation identity/version/digest;
- target identity;
- effective input/binding set;
- any target/resource instance identity that affects acquisition;
- acquisition semantics/version.

A scanner optimization SHALL NOT reuse an Observation merely because the source
file ID matches.

Freshness/cache policy remains a runtime concern and must not change authored
truth semantics.

## Consumer result provenance

A consuming Assessment Result should record the Observation execution/export it
used, conceptually:

```yaml
consumed_observations:
  - alias: apache
    observation:
      id: shared.apache.httpd.discovery
      version: 1
      digest: sha256:...
    execution_id: obs-exec-17
    target_ref: target-1
    binding_set_id: ...
    exports:
      - primary_and_included_configs
    reused: true
```

If Items are materialized into the consumer result, their existing origin/import
provenance points back to the Observation execution.

If value exports are materialized, equivalent provenance must identify the
Observation execution and export source Variable.

## Error/status propagation

Consuming an Observation export does not convert its status into Assessment
truth by itself.

The consumer context determines how a value/item status affects:

- Object selection;
- Variable derivation;
- Test evaluation;
- final six-state Assessment outcome.

This mirrors current OVAL-derived behavior: acquisition/dataflow status and
Test/Definition truth are related but distinct layers.

## Current Apache proof

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37619407392

- 15 eligible Rule Assessments;
- 0 rejected;
- 4 private Objects;
- 11 private Variables;
- 2 public value exports;
- 39 external export references;
- exact flatten/re-expansion to the faithful converted graph for all 15.

The generated artifact includes the Observation source, an illustrative
Observation Result, three consumer samples, and a machine-readable proof.

## Counterexample: shared runtime collection is not automatically an Observation

The representative source-fanout census found one OVAL Object reused by **42**
Windows Server 2025 Rules and **43** Windows 11 Rules:

`oval:mil.disa.stig.win:obj:20000000`

It is an empty `auditeventpolicysubcategories_object`.

The reviewed native capability mapping already models
`windows.auditeventpolicysubcategories` with:

```text
test_source.kind = none
```

because the OVAL Object carries no selector or other authored acquisition
semantics. Native content therefore removes the meaningless Object and the Test
directly evaluates the current system's audit-policy subcategories.

This is **not** a good Observation artifact candidate merely because its source
Object had high fanout.

A scanner may still collect the underlying system data once and reuse that
collection internally across compatible Tests. That is runtime collection
execution reuse (#44), not an author-visible Observation dependency.

This establishes an important extraction rule:

> Source fanout is evidence to inspect, not sufficient evidence to create an
> Observation.

An Observation is justified when reusable authored acquisition/derivation has
meaningful identity and a useful explicit export boundary. Capability-intrinsic
singleton acquisition should remain intrinsic to the capability.

A better source-fanout proving case is a shared Object with meaningful
selection/dataflow, such as the Windows `DomainRole` WMI query reused by four
Server 2025 Rules.

## Remaining proof before 65-benchmark modernization census

1. Add negative fixtures for unknown export, ID/version mismatch, and private
   implementation access.
2. Decide whether Observation source may consume Organizational Inputs and, if
   so, make those bindings part of execution identity.
3. Define the minimal value-export provenance record.
4. Align Item exports with the existing Item materialization contract.
5. Add consumer-result provenance for reused Observation execution.
6. Validate the contract against at least one source-ID-fanout family in
   addition to Apache's publisher-clone family.

These are research gates, not blockers to documenting the candidate syntax.
