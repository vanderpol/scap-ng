# Foreach v1 production proof

**Date:** 2026-10-06  
**Transformation:** `foreach.direct-object-component.at-least-one.v1`  
**Status:** production-candidate semantic proof, 0.3.0 authoring/validation
integration, and opt-in converter modernization proof passed. Automatic
converter rewrite remains disabled by default.

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

The first production-lowering run used a `source-compatible` placeholder.
The follow-on context-aware compiler and verifier now resolve the source and
target Object capabilities against the maintained 0.2.0 capability mappings,
map the projected/selector fields into native vocabulary, and require exactly
one compatible native datatype before lowering. The five eligible production
candidates all satisfy that type gate.

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

It does not establish scanner execution conformance or Board approval.
The 0.3.0 authoring/validation integration is now implemented, including
capability-mapping datatype compatibility. Automatic SCAP 1.4 converter
modernization remains a separate gate.

## Gate conclusion

The narrow v1 semantic design has passed:

- algebraic population proof;
- downstream Test aggregation proof;
- ObjectComponent error-boundary proof;
- result/evidence canonicalization proof;
- fail-closed eligibility proof;
- production-candidate lowering proof.

The research lowerer, context-aware compiler, production candidate verifier,
0.3.0 authoring/deep-schema validation, semantic validator, and real authoring
fixture now pass together. The complete independent 0.3.0 release tree is open;
frozen 0.2.0 remains unchanged.

The production converter now includes a fail-closed, explicitly opt-in 0.3.0
post-mapping modernization pass. A regression built from the pinned
SV-257889 OVAL source exercises the real path:

```
OVAL source
  -> faithful semantic lowering
  -> native capability mapping
  -> opt-in foreach v1 modernization
  -> 0.3 semantic validation
```

That source produces the two expected home-directory foreach rewrites and
passes semantic validation. The focused workflow run
https://github.com/vanderpol/scap-ng/actions/runs/37522441963 passed.

Automatic modernization remains disabled by default. This is now a stable
technical checkpoint for the narrow v1 construct; broader authoring-language
design should be reviewed before extending foreach into additional proof
classes.
