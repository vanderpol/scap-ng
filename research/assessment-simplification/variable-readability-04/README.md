# 0.4.0 — Making complex Variables understandable

**Research checkpoint · informational only · no 0.3 specification changes · no Board vote requested**

This project is evaluating readability of OVAL-derived multi-stage calculations in the **six published 0.3 sample STIGs**, using the original standalone OVAL Rule closures beside the unchanged 0.3 Assessments.

**[Download the complete current evidence ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-variable-research-efaefb283961/scap-ng-0.4-variable-research.zip)** (includes `BOARD-RESEARCH-PREVIEW.md`, 20 OVAL+NG case directories, per-example Variable-flow views, `STATS.json`, `APACHE-DATAFLOW-PATTERNS.json`, and all-instance CSV classifications). [Tracking issue #223](https://github.com/vanderpol/scap-ng/issues/223).

## What the corpus actually says

| Six-STIG findings | Measured |
|---|---:|
| Named Variable uses across benchmark scopes | **407** |
| Unique named Variable definitions after deduplicating shared Assessments | **376** |
| Initial research candidates for inline/folding | **123** |
| Remain explicit pending evidence | **263** |
| Unreferenced and needing provenance audit | **21** |
| Private Object nesting candidates | **14** |
| Self-contained, exact-structure lowering proofs | **137/137** |
| Individual inline experiments that grew in YAML lines | **113/137** |
| Individual inline experiments that grew nesting depth | **97/137** |

These are **independent one-component experiments**, not a claim of scanner/OVAL runtime equivalence or the impact of one simultaneous rewrite.

### Apache is the outlier

Among 22 Apache automated Assessments containing 282 Variable occurrences:

- **20 repeated named-Variable definition groups** cover **248 occurrences**.
- A stricter transitive fingerprint that includes referenced Variables **and** source Object definitions finds **24 complete repeated graph groups** spanning **238 occurrences**. There were **no missing dependencies** in this closure census.
- Earlier research separately proved one precise **15-assessment, 4-Object + 11-Variable** shared Apache discovery graph with two typed outputs and exact flattening.
- Common authoring graph shape does **not** by itself prove two evaluations can safely share runtime Items or derived values; target context, error status, completeness and lineage remain requirements.

The biggest readability problem is therefore often **seeing and reusing the same dataflow graph across Assessments**, not simply eliminating one-off names.

## Recommendations, in order

1. **Explain existing graphs first (no new standard feature).** Generate a concise, collapsible dependency view showing collected inputs → transformation stages → typed outputs → consuming Objects/States/Tests, with the complete unabridged graph and standalone OVAL available on demand. The evidence ZIP includes `VARIABLE-FLOW.md` beside applicable examples.
2. **Investigate reusable typed derived-data producers.** Apache's recurring discovery graph is a stronger research case for a shared Observation/data provider than arbitrary Object nesting. Preserve explicit exported types, cardinalities, status/completeness, collection lineage, provenance and target scoping; do not hide an Assessment verdict inside a data provider.
3. **Prototype ordered derived-value stages as an *authoring view*, not a replacement evaluator.** A left-to-right pipeline or SQL-like named stages may communicate intent better than scattered Variable references, but it needs exact lowering into current typed Variable operations without altering multiple values, error handling, correlation or Cartesian products.
4. **Allow bounded private inlining only where it actually reads better.** The experimental exact-lowering proof works, but widespread full-definition nesting adds lines and depth. Do not generalize from "possible" to "desirable".
5. **Do not import another expression evaluator implicitly.** JSONata's [chaining](https://docs.jsonata.org/other-operators) offers a readability idea; its [sequence-flattening behavior](https://docs.jsonata.org/1.8.0/processing) and CEL's [collection/error macros](https://github.com/cel-expr/cel-spec/blob/master/doc/langdef.md) require explicit semantic comparison with OVAL. Borrow presentation patterns, not unproven truth semantics.

## Human review path

For a short review of *different* semantic situations, start with these directories inside the evidence archive:

- **RHEL 9 SV-258020:** dynamic dconf path construction
- **RHEL 9 and Oracle Linux 9:** standalone OVAL plus real `for_each` source-Object nesting examples
- **Windows Server 2025 SV-278043:** multi-source registry/event-log calculation **retained** as a counterexample
- **Apache SV-214228 and SV-214268:** shared discovery chain vs genuine named computation
- **Windows Server DNS SV-259374:** derived path

Every sample retains the full source `original-1.4.oval.xml` next to the unmodified `current-0.3.assessment.yaml` and any experimental alternatives. Research syntax is visibly identified as **not adopted**.

## Gate before proposing 0.4 normative text

A proposal SHALL demonstrate both:

1. **Safe lowering:** complete, independent expansion back to the validated canonical 0.3 dataflow graph, with explicit types, cardinality, dependencies and provenance; then adversarial missing/empty/duplicate/incomplete/error cases and live scanner/OVAL parity where semantics can diverge.
2. **Real readability gain:** fewer cross-references, understandable names, concise worked examples, no excessive nesting, and a consistent way to inspect the full graph.

**Current judgment:** The study is suitable for an informal OVAL Board **research preview** once the owner has reviewed representative examples. It is **not ready for a ratification vote**, a new generic pipeline primitive, or a blanket automatic conversion rewrite. Keep #223 open for the measured follow-on experiments.

For a shorter Board email, use `BOARD-RESEARCH-PREVIEW.md` inside the ZIP; this page is the research status landing page.
