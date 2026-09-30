<!-- scap-ng-discussion-id: CANONICAL-JSON-AUTHORING-RESEARCH -->

**Status: Research / prototype — NOT an OVAL Board voting question.**

This discussion captures an architectural research idea that should be tested before any formal Board proposal.

## Question

Can the full Rule / Policy / Assessment presentation, a compact Rule / Assessment presentation, and a restricted Ansible-inspired assessment presentation compile to one canonical, versioned SCAP-NG execution JSON representation without losing assessment or policy semantics?

## Two different propositions

### A. Multiple source layouts for the same native assessment language

The full split source has an explicit Policy object. A compact Rule / Assessment source could synthesize an explicit, validated Policy/check-selector representation during compilation.

This is primarily a source-layout, reference-resolution, and normalization problem.

### B. A distinct Ansible-inspired source language

This is materially riskier because it introduces genuine semantic translation. The compiler itself becomes part of the compliance trust boundary.

No general-purpose Ansible interpreter, arbitrary module execution, shell execution, or command-injection-capable mechanism should be assumed. Unsupported or ambiguous constructs should fail closed rather than be approximated.

## Critical failure mode

A STIG requirement can be correct, an author can express that requirement correctly, and a scanner can correctly execute the compiled JSON — yet the compliance result can still be wrong because the compiler changed the author's intended semantics.

Therefore syntax-valid JSON, successful source-to-JSON compilation, or even round-trip reconstruction are necessary but insufficient evidence.

## Bounded prototype before any Board vote

1. Define a candidate canonical JSON IR representing named check selections/default selector, applicability, parameters, manual checks, automated assessment graphs, variable dependencies, statuses, evidence limits, reuse, and provenance without source file-path coupling.
2. Start with 5–10 independently hand-reviewed cases, including existence/nonexistence, Test vs State entity existence, `var_check`, repeated entities, recursive sets/filters, manual assessments, applicability, tailored/default/alternate selectors, and multi-rule assessment reuse.
3. Author equivalent behavior in full Rule / Policy / Assessment and compact Rule / Assessment forms, then demonstrate equivalent canonical JSON after deterministic normalization.
4. Evaluate a restricted Ansible-inspired representation separately rather than assuming it is simply another layout.
5. Test against independent expected outcomes and, where practical, differential execution. Do not rely only on the compiler comparing its own output.
6. Preserve debug traceability from source file/line → expanded construct → canonical JSON node/ID → compiler version/hash → scanner result/evidence.
7. Measure implementation complexity, unsupported feature rate, diagnostics quality, conversion defects, and long-term maintenance burden.

## Board-readiness gate

This topic should remain non-voting until tested examples, scope boundaries, assurance evidence, and unresolved semantic differences are available.

A later voting Discussion should be a separate topic with a narrowly phrased proposal such as: **“Do you agree that SCAP-NG SHALL define a canonical compiled execution representation independent of authoring presentation?”**

## Success criterion

Success is not that three formats compile without errors.

Success is independent evidence that equivalent author intent produces equivalent scanner behavior, and that translation defects can be localized and explained.
