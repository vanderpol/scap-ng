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
