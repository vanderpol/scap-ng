# Shared observation artifact research

**Status:** research only; no accepted schema or source-layout change.

## Working conclusion

A file whose sole purpose is to gather or derive reusable observations should
not be called an Assessment if it has no Tests/evaluate truth.

The current Assessment contract answers a technical question and produces the
Assessment result domain. A truthless reusable producer has a different role:
it gathers Items and/or derives typed values for other Assessments.

Working term: **observation** artifact / **observation provider**.

Avoid using `collection` as the authored artifact name because current SCAP-NG
terminology reserves collection for the runtime act of evaluating an Object.

## Proposed authoring layout

A separate source file exists only when reuse justifies independent identity.
Therefore the preferred research layout is:

```text
<benchmark>/
  benchmark.yaml
  rules/
  assessments/
    automated/
    manual/
    applicability/
  shared/
    observations/
      apache-httpd-discovery.observation.yaml
```

If reusable Assessments are later moved into the already anticipated shared
subtree, the shape can remain coherent:

```text
shared/
  assessments/
  observations/
```

A provider used by only one Assessment should normally remain local rather than
be extracted merely to create another file.

## Proposed file identity

Example:

```yaml
observation:
  id: shared.apache.httpd.discovery
  version: 1

  objects:
    ...

  variables:
    ...

  exports:
    httpd_executable:
      value:
        variable: apache-path-httpd-or-apache2-variable
      datatype: string
      cardinality: zero_or_more

    primary_and_included_configs:
      value:
        variable: primary-and-included-configs
      datatype: string
      cardinality: zero_or_more
```

Suggested source suffix:

`*.observation.yaml`

Do not use `*.assessment.yaml` for a document with no Assessment truth.

## Why an intentional shared directory helps

The directory communicates author intent without becoming semantic identity:

- content under `assessments/` evaluates technical truth;
- content under `shared/observations/` exists because multiple consumers reuse
  acquisition/dataflow;
- private Object/State/Variable plumbing remains colocated with its sole
  consumer.

The package compiler still resolves explicit references and logical IDs. Runtime
identity comes from the document and manifest, not from the source path.

## Compiled package

The package manifest should treat the provider as a distinct logical object
type, conceptually:

```json
{
  "shared.apache.httpd.discovery": {
    "type": "observation",
    "version": 1,
    "path": "o/o/...",
    "sha256": "..."
  }
}
```

The physical package path remains non-semantic, consistent with the existing
manifest design.

## Result distinction

An observation execution produces status-bearing gathered/derived observations,
not an Assessment pass/fail result.

It may expose:

- Object-produced Items;
- Variable-produced typed value streams;
- status/completeness;
- provenance;
- target/binding identity.

Consumers perform their own Tests/States/evaluate logic.

## Apache proving case

The current Apache proof class contains 15 Rule Assessments sharing an exact
4-Object + 11-Variable discovery subgraph. Only two public outputs are required:

- `httpd_executable`;
- `primary_and_included_configs`.

That is a strong candidate for:

`shared/observations/apache-httpd-discovery.observation.yaml`

rather than either:

- copying the graph into every Rule Assessment; or
- creating a testless file named `*.assessment.yaml`.

## Apache executable prototype

The research prototype now emits a real source artifact:

`shared/observations/apache-httpd-discovery.observation.yaml`

and three representative rewritten consumer Assessments.

For the pinned Apache 2.4 corpus:

- **15** Rule Assessments match the exact shared discovery graph;
- **4 Objects + 11 Variables** move behind the Observation boundary;
- public export surface: **2 typed value streams**;
- `httpd_executable`: **21** consumer references;
- `primary_and_included_configs`: **18** consumer references;
- rejected eligible consumers: **0**;
- flatten/re-expansion to every faithful converted Assessment: **passed**.

Focused negative coverage rejects private Observation-node access.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37619423430

This proves source extraction and exact flattening for the publisher-clone
family. Windows Server 2025 separately proves a shared `kind: items` WMI
export across 12 consumers.

RHEL 9 now supplies the source-ID-fanout proof: SV-258013, SV-258020, and
SV-258026 share one dconf acquisition Object and its derived lock-directory
Variable. A single Observation exports both `databases` Items and
`lock_directories` values; all **3/3** consumers flatten exactly back to the
faithful conversion with **0 rejected**.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37628881725

Together the three proofs cover publisher-cloned value graphs, source-shared
Item acquisition, and source-shared mixed Item/value dataflow. Runtime
result/provenance details remain research before normative promotion.

## Open naming decision

The final standard term is intentionally unresolved. Candidates include:

- Observation;
- Observation Provider;
- Data Provider;
- Fact Provider.

Current research preference is **Observation** for the artifact and
**observation execution/result** for runtime output because it covers both
collected Items and derived typed values without colliding with existing Object,
Collection, Test, State, Variable, or Assessment terminology.
