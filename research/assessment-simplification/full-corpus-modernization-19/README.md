# Full-corpus 0.3 modernization census

**Status:** post-freeze 0.3 research/evidence checkpoint. The transformations counted as applied below match the accepted 0.3 modernization direction; deferred Observation is measured but not applied.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37691979118

Pinned NIWC revision:
`8c8e5dff860af6b1290ee9273a282db24278f8d5`

The run regenerated all 65 individual NIWC Current packages from source:

- **61** generated native content;
- **4** expected `independent.sqlext` source blockers;
- **0** unexpected blockers.

## Result

Measured automated Assessments: **7,165** total, including **6,916 Rule
Assessments** and **249 applicability Assessments**.

Exact/reversible modernization produced:

| Measure | Faithful | 0.3 research view | Reduction |
| --- | ---: | ---: | ---: |
| Top-level Objects | 13,402 | 544 | **95.94%** |
| Top-level States | 9,121 | 435 | **95.23%** |
| Named Variables | 2,250 | 864 | **61.60%** |
| Named component references | 23,883 | 1,326 | **94.45%** |

Rule Assessment classifications:

| Class | Count | Percent |
| --- | ---: | ---: |
| local/simple | **5,283** | **76.39%** |
| bounded dataflow (`for_each`) | 22 | 0.32% |
| meaningfully complex | **1,611** | **23.29%** |

The exact automatic `for_each` v1 rewrite class remains narrow: **22** rewrites
across 6,916 Rules. DNS research separately shows additional nested runtime
iteration hidden inside PowerShell; that evidence drives the accepted nested
`for_each` authoring requirement rather than inflating this automatic-rewrite
count.

## Static Variable folding

The accepted bounded static-literal pass removed **509 constant Variables** across
**332 Assessments** and replaced **1,071 constant-Variable references** with
direct scalar/typed-array literals.

The transform is atomic and fail-closed per Variable:

- every reference must be in a proven literal-replacement shape;
- datatype, operation, and source-equivalent `variable_match` remain explicit;
- unsupported shapes stay as named Variables rather than blocking the package or
  being partially rewritten.

This is why all **61** normally convertible packages still generate successfully
and the known **4** SQL-extension blockers remain the only blocked packages.

## Deferred Observation opportunity

Observation is **not applied** to the 0.3 research view.

The census still measures the proven opportunity so the research is not lost:

- **9** package-local candidate Observation artifacts;
- **69** candidate consumers;
- Apache discovery, Windows DomainRole, and RHEL/Oracle Linux dconf families.

Observation is deferred beyond normative 0.3 because its typed export,
execution/result provenance, binding, manifest dependency/cycle, and cache/reuse
contracts need to be completed as one interoperable design.

## Retained Object boundary

After locality, top-level Objects remain only where identity/referenceability is
meaningful.

Retained reason counts:

- multiple Tests: **330**
- graph-only: **110**
- Test + graph: **98**
- multiple Tests + graph: **6**

The apparent **17** single-consumer `object_graph:1` cases are the proven
`for_each` source population cases. They intentionally retain a named,
referenceable collection identity rather than representing missed locality.

This is the evidence basis for the 0.3 authoring rule:

- private Object → local/inline with its consumer;
- reusable/referenceable acquisition → named under `shared_objects:`.

## Residual complexity

Among the **1,611** meaningfully complex Rule Assessments, overlapping causes are:

- real multi-Test composition: **1,052**
- Set/Filter semantics: **636**
- nested evaluation: **587**
- shared acquisition: **332**
- named State reuse: **214**
- derived Variable graph: **166**
- repeated Test reference: **147**
- named Object graph: **72**
- constant binding: **44**
- external input binding: **21**

These residuals are not targets to eliminate merely to make the percentage
smaller. Existing evaluate, Set/Filter, and runtime Variable semantics remain
when the complexity is real.

## Evaluate checkpoint

The corpus confirms that real composition remains important: more than one
thousand Rule Assessments require multi-Test composition, with nested trees and
repeated Test references present in production.

0.3 therefore keeps the existing named-Test + explicit `evaluate` model.
**Redesign of evaluate is deferred**: no implicit one-Test root, nested Test
definition model, or new shorthand is added for this checkpoint.

## Applied scope

Applied only where the transform is exact/reversible:

- consumer-local Object/State presentation;
- private Set-operand locality;
- Variable-local Object locality;
- recursive private Object-graph locality;
- single-use external/constant/leaf-derived Variable locality where proven;
- bounded `for_each` v1.

Measured but not applied:

- deferred shared Observation extraction;
- single-Test evaluate-root authoring ceremony.

Not rewritten merely to reduce complexity:

- broader conditional/case syntax;
- typed `linux.fstab`;
- violation-query positive spelling;
- general unproven multi-source `for_each`;
- domain-specific semantic changes.

The detailed 61-package reports and logs remain in the workflow artifact rather
than this repository.

## Human-review package

The 0.3 review set uses:

- RHEL 9;
- Oracle Linux 9;
- Windows Server 2025;
- Windows 11;
- Apache 2.4 UNIX Server;
- Windows Server DNS.

Each benchmark carries a compact modernization scorecard. Observation opportunity
may appear as deferred research evidence, but **no Observation artifact or
consumer rewrite belongs in the normative 0.3 candidate tree**.

Final IN / DEFER / OUT requirements are maintained in
[#174](https://github.com/vanderpol/scap-ng/issues/174).
