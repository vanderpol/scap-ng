# SCAP-NG 0.3 architecture and complexity audit

**Status:** in progress; initial source-level pass, **not** a completed corpus audit or release approval.
**Objective:** maximum useful capability with minimum authored surface, while preserving type safety, provenance, collection behavior, and OVAL six-state semantics.
**Board gate:** do not describe an architectural decision as stable if a near-term breaking redesign is already anticipated.

## Decision rubric

Classify each candidate **keep / simplify / consolidate / remove / research**. Compare authoring token/line count, number of independent concepts/IDs, implementation burden, result clarity, and compiled bytes **separately**. Require a paired real-content example, counterexample, exact conversion mapping and conformance tests before any normative simplification. A shorter YAML example alone is insufficient.

## Initial findings

| Component | Evidence in current main | Preliminary disposition | Board gate / required proof |
| --- | --- | --- | --- |
| `select` inside Object | An Object can use direct `select`, `set` composition, `filters`, `for_each`, and capability-specific acquisition behavior | **Keep**: distinguishes direct selector from acquisition composition, avoids property collisions | Confirm schema closure and interactions, especially Set/Filter semantics |
| Repeated inline `capability` | `capability-common.schema.json` requires it on `inline_object` and `inline_state`; `CURRENT-DESIGN.md` says capabilities are independently typed | **Research simplification**: explicit Test capability could determine capability for private Object/State, with specified override policy | Count equal vs differing Test/Object/State capabilities in actual converted corpus; test cross-capability usages and validator; never silently change referenced/shared component capability |
| Rule `organizational_input_requirements` | `rule.schema.json` requires it; Rule already binds Benchmark Parameter to Assessment input; Assessment explicitly identifies its input consumers | **Consolidate candidate**: derive a discoverability index during compilation rather than author a second copy | Verify multi-Assessment choices, multiple consumers, cross-file reuse, validation error paths and provenance |
| `variable_match` / `value_match` and membership `in` | Current shared comparison enum lacks `in`/`not_in`; shared Object entity quantifier still `variable_match`. README marks membership as proposed only | **Research**: clearer membership expression may help common cases, but must not replace general quantification | #194/#195: exact OVAL var_check/entity_check truth mapping, empty/incomplete values, all/none/one, scalar versus collection |
| `value: {input: ...}` | Current research Organizational Input fixture uses direct State input, avoiding pass-through Variable; README explicitly says conformance incomplete | **Keep conceptual direction, block readiness until tested** | #193 typed input contract, resolver, evaluator, results, invalid/expired/missing input, provenance |
| `evaluate` | Current design deliberately keeps explicit expression tree; multi-Test real examples exist in review guide | **Keep pending evidence** | Measure trivial one-Test overhead against complex nested trees, NOT/AND/OR semantics; avoid inferred implicit root evaluation |
| `shared_objects` vs private Object | `review/current/REVIEW-GUIDE.md` identifies real RHEL9 SV-258029 with shared dconf Object, and other private inlined Objects | **Keep separation** | Check true reuse, item/result dependence, graph cycles and output explainability |
| Complex Sets/Filters/`for_each` | `set_expression` supports union/intersection/difference; foreach bindings preserve correlated Item lineage; residual-pattern measurement tool exists | **Keep capability, minimize ceremony** | Use residual-pattern data; never replace correlated foreach with Cartesian or assume OVAL parity from a short snippet |
| Results, reported elements, provenance | Multiple normative specifications and derived constraints; broad audit not completed | **Pending** | Check thin/full payload, redaction semantics, capped samples, human root causes, manual attribution, signatures |
| Generated examples vs actual conformance | `native-schema-validation-triage.md` documents historical fixture drift; guide distinguishes mechanically converted versus production-derived native authoring | **Readiness risk** | Regenerate and validate *current* trees, separate design-only research fixtures, ensure README does not imply unsupported syntax is executable |

## Evidence examined in this initial pass

- `research/iterations/003/design/CURRENT-DESIGN.md`: architecture, independent capabilities, scope, collections, runtime.
- `schema/v0.3.0/capability-common.schema.json`: inline component requirements; comparison enum; `object_entity_base`; set/filter/foreach primitives.
- `schema/v0.3.0/rule.schema.json`: mandatory Rule-level Organizational Input discovery map.
- `specification/assessment/assessment-method.md`: independent capability compatibility, policy bindings, semantic graph closure.
- `specification/examples/README.md`: Board-facing examples, proposed `in`, explicit stated conformance limitations.
- `review/current/REVIEW-GUIDE.md`: real Rule IDs and provenance qualification for showcase.
- `research/iterations/003/review/native-schema-validation-triage.md`: historical generator/schema/content drift.
- `tools/measure_post_modernization_residual_patterns.py`, `tools/test_research_inline_private_components.py`: audit/rewrite research already implemented; **not executed during this pass**.

## Work remaining before a design freeze / Board release

1. Build a reproducible, pinned baseline from fresh 0.3 conversion and normalization, then run JSON Schema and semantic validators. Count files, failures and provenance classifications.
2. Mine the six review STIGs, then all 65 benchmark archives, for capability mismatches, inline-component repetition, structural wrappers, dangling/redundant identifiers, quantifier/Variable patterns, and outstanding complex Sets/Filters.
3. For every candidate simplification, test (a) a representative success, (b) a counterexample where it is **not** allowed, and (c) six-state/collection-completeness parity. Report actual authored and packaged size independently.
4. Audit results, packaging, applicability, Profiles/Tailoring, manual STIG conversion and full vocabulary; reconcile normative specs/schema/converter/README.
5. Produce a short recommendation matrix separating **pre-Board blockers** from consciously deferred post-0.3 features. Present major design choices to owner before adopting them; reserve 0.3 freeze until current tests and review content agree.

**No automatic design/schema changes are authorized by this research report.**
