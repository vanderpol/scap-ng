# 0.4.0 — Making complex Variables understandable

**Research checkpoint · informational only · no 0.3 specification changes · no Board vote requested**

This project is evaluating readability of OVAL-derived multi-stage calculations in the **six published 0.3 sample STIGs**, using the original standalone OVAL Rule closures beside the unchanged 0.3 Assessments.

**[Download the complete current evidence ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-variable-research-beb6c404dde0/scap-ng-0.4-variable-research.zip)** (includes `BOARD-RESEARCH-PREVIEW.md`, 20 OVAL+NG case directories, per-example Variable-flow views, `STATS.json`, `APACHE-DATAFLOW-PATTERNS.json`, and all-instance CSV classifications). [Tracking issue #223](https://github.com/vanderpol/scap-ng/issues/223).

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
- The actual released 0.3 authoring has already localized the older shared Objects. A new source-only import prototype therefore reuses the surviving **11-Variable graph**, leaving source collection Objects Assessment-local.
- **15 of 15** Apache Assessments imported that graph and independently expanded to exactly their original parsed 0.3 content. That removes **154 duplicate Variable declarations** from experimental source authoring while retaining two typed public outputs and all existing runtime semantics.
- Debugging complexity is measurable: **18 of 22** Apache Assessments containing Variables have dependency chains at least four stages deep; maximum and median longest chain per Assessment are **nine stages**. The other five STIGs have maximum Variable dependency depth of two or less.
- Common authoring graph shape does **not** by itself prove two evaluations can safely share runtime Items or derived values; target context, error status, completeness and lineage remain requirements.

The biggest readability problem is therefore often **seeing and reusing the same dataflow graph across Assessments**, not simply eliminating one-off names.

## Recommendations, in order

1. **Explain and diagnose existing graphs first.** Generate a concise dependency view showing collected inputs → Variable stages → typed outputs → consuming checks. Produce an optional diagnostic trace with per-stage status, input/output counts, bounded redacted samples, completeness and source Item lineage. The archive now includes `VARIABLE-FLOW.md` and `VARIABLE-DEBUG-PLAN.yaml`; the latter is an authoring-time plan, **not** scanner evidence.
2. **Generalize the proven build-time Apache reuse.** A source-only import of the surviving 11-Variable graph compiles back to all 15 original 0.3 Assessments. Formalize source identity, hash, explicit exported values, local Object dependencies, namespace/collision checks and cycle rejection. This does not introduce cross-Assessment runtime status, scheduling or caching.
3. **Treat runtime shared producers as a separate decision.** A scanner-side Observation/provider may later collect once and reuse evidence, but only after proving target binding, collection identity, status/completeness, provenance, redaction and result behavior. **Authoring reuse does not grant runtime reuse.**
4. **Prototype ordered derived-value stages as an *authoring view*, not a replacement evaluator.** A left-to-right pipeline or SQL-like named stages may communicate intent better than scattered Variable references, but it needs exact lowering into current typed Variable operations without altering multiple values, error handling, correlation or Cartesian products.
5. **Allow bounded private inlining only where it actually reads better.** The experimental exact-lowering proof works, but widespread full-definition nesting adds lines and depth. Do not generalize from "possible" to "desirable".
6. **Do not import another expression evaluator implicitly.** JSONata's [chaining](https://docs.jsonata.org/other-operators) offers a readability idea; its [sequence-flattening behavior](https://docs.jsonata.org/1.8.0/processing) and CEL's [collection/error macros](https://github.com/cel-expr/cel-spec/blob/master/doc/langdef.md) require explicit semantic comparison with OVAL. Borrow presentation patterns, not unproven truth semantics.

## Human review path

For a short review of *different* semantic situations, start with these directories inside the evidence archive:

- **RHEL 9 SV-258020:** dynamic dconf path construction
- **RHEL 9 and Oracle Linux 9:** standalone OVAL plus real `for_each` source-Object nesting examples
- **Windows Server 2025 SV-278043:** multi-source registry/event-log calculation **retained** as a counterexample
- **Apache SV-214228 and SV-214268:** shared discovery chain vs genuine named computation
- **Windows Server DNS SV-259374:** derived path

Every sample retains the full source `original-1.4.oval.xml` next to the unmodified `current-0.3.assessment.yaml` and any experimental alternatives. Research syntax is visibly identified as **not adopted**.

For a concise technical choice set, read [Board design options](BOARD-DESIGN-OPTIONS.md). The archive's `BUILD-TIME-IMPORT/consumer-samples/` places each source-only imported example beside its original standalone OVAL definition, unmodified 0.3 Assessment, and compiler-expanded output.

## Gate before proposing 0.4 normative text

A proposal SHALL demonstrate both:

1. **Safe lowering:** complete, independent expansion back to the validated canonical 0.3 dataflow graph, with explicit types, cardinality, dependencies and provenance; then adversarial missing/empty/duplicate/incomplete/error cases and live scanner/OVAL parity where semantics can diverge.
2. **Real readability gain:** fewer cross-references, understandable names, concise worked examples, no excessive nesting, and a consistent way to inspect the full graph.

**Current judgment:** The most promising specification-light avenue is **build-time reuse with canonical expansion**, complemented by generated dataflow views. The study is suitable for an informal OVAL Board **research preview** once the owner has reviewed representative examples. It is **not ready for a ratification vote**, a new generic pipeline primitive, or a blanket automatic conversion rewrite. Keep #223 open for the measured follow-on experiments.

For a shorter Board email, use `BOARD-RESEARCH-PREVIEW.md` inside the ZIP; this page is the research status landing page.
