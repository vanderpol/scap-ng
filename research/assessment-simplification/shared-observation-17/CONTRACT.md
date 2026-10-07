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

Item exports are now also proven in production conversion, both alone and
alongside a derived value export:

```yaml
exports:
  databases:
    kind: items
    object: dconf-user-databases-object
    capability: independent.textfilecontent54

  lock_directories:
    kind: values
    variable: dconf-user-database-locks-directories-variable
    datatype: string
    cardinality: zero_or_more
```

The Item representation should still reuse the existing Item/materialization
contract rather than invent an Observation-specific format.

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

A `kind: items` export should reuse:

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

## Second production proof: Windows DomainRole Item export

A second production proof now covers `kind: items`.

The shared Observation is:

```yaml
observation:
  id: shared.windows.computer-system-role
  version: 1

  objects:
    computer-system-role:
      capability: windows.wmi.query
      collect:
        namespace: root\\cimv2
        query: SELECT DomainRole FROM win32_computersystem

  exports:
    computer_system:
      kind: items
      object: computer-system-role
      capability: windows.wmi.query
```

Pinned Windows Server 2025 conversion results:

- **12 eligible Assessments**;
- **0 rejected**;
- 5 applicability Assessments;
- 7 automated Rule Assessments;
- local Tests/States/evaluate trees remain in each consumer;
- exact flatten/re-expansion to the faithful converted Assessment: **passed for
  all 12**.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37620448238

This is the complementary proof to Apache:

| Proof | Export kind | Shared content | Consumers |
| --- | --- | --- | ---: |
| Apache discovery | `values` | 4 Objects + 11 Variables | 15 |
| Windows DomainRole | `items` | 1 meaningful WMI Object | 12 |

Together they show Observation is not tied to one dataflow style.

The Windows proof also reinforces separation from Assessment-result
dependencies: consumers still own the policy predicates that interpret
`DomainRole`; the Observation exports gathered data, not "domain member=true"
or another policy truth.

## Third production proof: RHEL dconf mixed exports

The RHEL 9 source-level reuse case proves one Observation can expose gathered
Items and a derived value stream without owning policy truth.

Source nodes shared by SV-258013, SV-258020, and SV-258026:

- Object: `dconf user databases` from `/etc/dconf/profile/user`;
- Variable: `dconf user database locks directories`.

Observation exports:

- `databases`: `kind: items`;
- `lock_directories`: `kind: values`, string, `zero_or_more`.

Pinned RHEL 9 result:

- **3 eligible Rule Assessments**;
- **0 rejected**;
- each consumer uses both exports once;
- exact flatten/re-expansion: **passed for all 3**.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37628881725

This is the source-ID-fanout counterpart to Apache's publisher-clone proof and
closes the source-side proof needed for the modernization census.

## Runtime/result checkpoint

The executable prototypes now establish these candidate requirements:

- binding fails closed on unknown export and Observation ID/version mismatch;
- private Observation nodes are not consumer-addressable;
- execution identity includes Observation ID, version, content digest, target
  identity, and effective input/binding identity;
- top-level status characterizes execution, not Assessment truth;
- authored export cardinality and observed runtime cardinality remain distinct;
- Item and value exports carry provenance back to the Observation execution and
  source Object/Variable;
- consumers retain the Test/State/evaluate logic that maps data/status into the
  six-state Assessment result.

The dconf artifact includes an illustrative result with execution ID, digest,
target/binding identity, completeness, diagnostics, per-export status, Item
references, runtime value cardinality, and provenance. It is a research
contract, not an accepted result schema.

## Remaining before normative 0.3 promotion

These no longer block the **source-modernization census**, but they do block
normative Observation promotion:

1. decide whether Observation source may consume Organizational Inputs and make
   any such bindings part of execution identity;
2. align the exact Item-export result fields with the existing Item
   materialization/import schema rather than only the current conceptual match;
3. add executable consumer-result provenance/reuse fixtures, including
   incomplete/error propagation;
4. define package-manifest typing, dependency-cycle rejection, and runtime cache
   freshness rules.

No schema change is implied by the successful research proofs.
