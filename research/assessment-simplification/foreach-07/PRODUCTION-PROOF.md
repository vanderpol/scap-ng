# Foreach v1 production proof

**Date:** 2026-10-06  
**Transformation:** `foreach.direct-object-component.at-least-one.v1`  
**Status:** production-candidate semantic proof passed; automatic rewrite remains disabled.

## Pinned sources

The proof uses the same pinned production packages and checksums recorded in
[CENSUS-2026-10-06.md](CENSUS-2026-10-06.md):

- RHEL 9 V2R9 enhanced V13;
- Solaris 11 x86 V3R5 enhanced V18;
- NIWC content revision
  `8c8e5dff860af6b1290ee9273a282db24278f8d5`.

## Method

For each analyzer candidate satisfying the conservative v1 proof preconditions:

1. generate the simplified authoring binding:
   ```yaml
   for_each:
     item: item
     in: <source-object>

   select:
     <target-entity>:
       from: item.<source-field>
   ```
2. lower that syntax through the research v1 lowerer;
3. compare the lowered graph to the faithful analyzer-described graph;
4. require exact agreement for:
   - rewrite identity;
   - source Object;
   - projected source field;
   - target Object;
   - target selector entity;
   - equality comparison family;
   - `var_check="at least one"`;
   - target Object aggregation boundary;
   - union population semantics;
   - presence of the faithful target datatype;
5. fail the workflow if any eligible candidate differs.

The prototype deliberately marks the bound selector datatype as
`source-compatible`; full capability-schema type inference belongs to the
0.3.0 compiler prototype and is not claimed by this bounded proof.

## Result

| Benchmark | Eligible | Equivalent | Failed |
| --- | ---: | ---: | ---: |
| RHEL 9 | 4 | 4 | 0 |
| Solaris 11 x86 | 1 | 1 | 0 |
| **Total** | **5** | **5** | **0** |

All eligible production candidates lowered to the same proven semantic graph.

Focused workflow:

https://github.com/vanderpol/scap-ng/actions/runs/37505388013

Artifact from the preceding equivalent production run:

`foreach-modernization-candidate-reports`

The workflow emits separate RHEL and Solaris v1 proof JSON files along with the
candidate reports.

## What this proves

For the current narrow v1 class, the simplified authoring syntax is not merely a
synthetic example. It represents real current DISA/NIWC production graph shapes
and lowers back to the same source Object projection, target selector
quantification, and Test aggregation boundary.

## What this does not prove

This result does not extend v1 to:

- fan-out Variables;
- helper/intermediate target Objects;
- `record_field`;
- `var_check=all` or mixed quantification;
- derived/function expressions;
- multiple independent projected sources;
- evaluation iteration.

It also does not yet establish production capability-schema datatype inference,
a finalized 0.3.0 JSON Schema, scanner execution conformance, or Board approval.

## Gate conclusion

The narrow v1 semantic design has passed:

- algebraic population proof;
- downstream Test aggregation proof;
- ObjectComponent error-boundary proof;
- result/evidence canonicalization proof;
- fail-closed eligibility proof;
- production-candidate lowering proof.

The next gate is the **0.3.0 authoring-schema/compiler prototype**, still kept
separate from frozen 0.2.0.
