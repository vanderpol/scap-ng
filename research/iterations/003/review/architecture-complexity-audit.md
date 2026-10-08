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

## Second pass: capability contract and authoring overhead

**Confirmed implementation constraint:** `tools/validate_generated_capability_semantics.py` currently rejects Test → Object and Test → State mismatches **for both referenced and inline uses** (`test.object_capability`, `test.inline_object_capability`, `test.state_capability`, `test.inline_state_capability`). It also checks parent Object vs nested Set Object and filter State capabilities. Thus the hypothetical "inline Object with a different compatible capability" is **not currently supported**, notwithstanding generic prose about independently typed nodes. There is a stronger simplification argument for eliminating identical inline declarations **if** each containment parent is explicitly typed and resolved deterministically.

**Important exception:** An inline Object used in Variable-local or nested Object/Set contexts does not necessarily have a Test as lexical parent. A safe rule cannot simply say "all inline Objects inherit from Test"; it must identify the nearest semantically typed parent, require explicit capability when none exists, and reject conflicts. A referenced/shared Object remains explicit and cannot be silently retyped. Filter-local State might inherit from its containing Object rather than a Test. Exact rules still require tests.

**Potential gap in validator structure:** `validate_native_semantics.py` is an entrypoint that delegates to `validate_assessment_capability_semantics`. Its advertised validation scope is within one Assessment and its local graph, so **do not assume** it validates Benchmark → Rule → Assessment Parameter wiring or a completed Organizational Input Set merely because this command passes. The full compilation/policy resolver must be checked separately.

**Confirmed authoring overhead:** `schema/v0.3.0/rule.schema.json` requires `organizational_input_requirements` on **every Rule**, including those with none, and its `uses` entries require repeated Test/State/State-slot references. This is potentially derivable from the selected Assessment's declared input consumers and the Rule's binding, which would reduce duplication and prevent drift. Whether it can be entirely omitted or generated as a manifest/index is an open policy and implementation decision.

**No schema or validator changes made.** These are implementation-backed findings, not corpus statistics or conformance proof.

## Third pass: confirmed schema/example drift and redundant contract surface

### Confirmed Board-showcase inconsistency — action required

`schema/v0.3.0/assessment.schema.json` requires keys in `assessment.inputs` to match `^[a-z0-9]+(?:-[a-z0-9]+)*-input$` (lowercase kebab-case and `-input` suffix). `specification/assessment/component-naming.md` affirms the same rule. However, `research/iterations/003/examples/organizational-input/time-source.assessment.yaml`, its Rule binding, and `specification/examples/README.md` use `required_time_sources`. **This is a verifiable mismatch**, independently of the still-incomplete direct State-input implementation. A consistent rename, such as `required-time-sources-input`, needs to propagate through Assessment contract, State reference, Rule binding, and the README identifier crosswalk; it is not just a cosmetic fix. Apply with regression checks to avoid wrong references. **Pre-Board blocker for examples.**

### Mandatory discovery metadata

`schema/v0.3.0/rule.schema.json` requires `organizational_input_requirements` for **all** Rules (even those without any required input), while `assessment_choices.*.inputs` already captures Parameter → Assessment-input binding. The authored `uses` list then repeats exact Test/State/slot consumer locations. This is mechanically derivable only if input-consumer references and all choice-resolution paths are statically discoverable; no proof yet of sufficiency for dynamic bindings. Test against multiple consumers, manual choices and nested semantic references before removing. Strongest authoring simplification candidate, but **do not assume generation is trivial**.

### Validation boundaries

`tools/validate_native_semantics.py` delegates to `validate_assessment_capability_semantics`; that function validates a local Assessment graph, not the full bundle-level cross-document parameter resolution. A green Assessment validator is necessary but insufficient to establish end-to-end Organizational Input conformance. An integrated test must verify publisher Parameter identity, Rule binding, Assessment contract and State usage, input set eligibility and provenance, and result treatment for missing values.

## Work remaining before a design freeze / Board release

1. Build a reproducible, pinned baseline from fresh 0.3 conversion and normalization, then run JSON Schema and semantic validators. Count files, failures and provenance classifications.
2. Mine the six review STIGs, then all 65 benchmark archives, for capability mismatches, inline-component repetition, structural wrappers, dangling/redundant identifiers, quantifier/Variable patterns, and outstanding complex Sets/Filters.
3. For every candidate simplification, test (a) a representative success, (b) a counterexample where it is **not** allowed, and (c) six-state/collection-completeness parity. Report actual authored and packaged size independently.
4. Audit results, packaging, applicability, Profiles/Tailoring, manual STIG conversion and full vocabulary; reconcile normative specs/schema/converter/README.
5. Produce a short recommendation matrix separating **pre-Board blockers** from consciously deferred post-0.3 features. Present major design choices to owner before adopting them; reserve 0.3 freeze until current tests and review content agree.

**No automatic design/schema changes are authorized by this research report.**

## Fourth pass: Board example repaired in part; conformance blocked

- **Fixed naming drift** on main: renamed Assessment input `required_time_sources` → `required-time-sources-input` consistently in the worked Assessment, Rule fragment, resolved-context fixture, and examples README. Confirmed against `assessment.schema.json`'s required `-input` suffix. **This does not validate the whole example.**
- **Additional concrete schema drift remains:** the same worked Assessment retains old `objects:` and `states:` layouts, nonconforming names (`object-configured-time-sources`, `state-source-approved`, `test-time-sources`), legacy Test `check`/`check_existence`, and no required `reported_elements` in that Test. Current 0.3 format instead uses `shared_objects` for genuinely reused Objects and suffix IDs. Do not mechanically rename until proper selection, collection, and matching semantics are established.
- **Illustrative capability unresolved:** worked NTP Assessment names `linux.chrony`; code search only found it in this fixture and README, not an implemented capability mapping. Treat the example as **conceptual only**, not an executable conformance demonstration. A real supported capability/collected Item example should replace it before labeling it validated. Existing README describes it as a design fixture but its placement alongside valid samples risks reader confusion.
- **Scope of verification performed:** JSON parsing of the two relevant 0.3 schema files and static inspection of their requirements; no end-to-end YAML schema validation, scanner evaluation, 65-benchmark corpus run or proof of correct runtime collection in this pass.
