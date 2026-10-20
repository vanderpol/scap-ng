# 0.4-C original-OVAL Variable blockers: what actually needs redesign

**19–20 October 2026 · research #245 · not normative, no scanner parity.**

## Verified source accounting

Independent [pinned original OVAL Self-Assertion source CI](https://github.com/vanderpol/scap-ng/actions/runs/39347643315) inspected the **68** currently Variable-blocked, A-compatible Definitions (out of **162** A-compatible original Definitions). They contain **245 original Variable declarations**.

| Actual role of original Variable | Variables | Definitions containing at least one |
| --- | ---: | ---: |
| Runtime-derived local expression (nonliteral computation) | **102** | 17 |
| Source `local` Variable with typed literal-only expression | **24** | 9 |
| Constant used in Object/collection selection | **84** | 40 |
| Constant used as one State expectation | **17** | 10 |
| Constant used by more than one State expectation | **4** | 4 |
| Constant feeding a derived Variable | **14** | 7 |
| **Total distinct original Variables** | **245** | **68 source Definitions overall** |

Definition columns **overlap**. The 245 Variable rows do **not** mean 245 independent blocked Definitions. Seven Variables also have mixed Object/State consumers; the classification prioritizes collection identity in such mixed cases and records multi-context use separately. Full reproducible inventory: [source-graph census](../../../tools/research_c_oval_variable_usage_census.py), [negative tests](../../../tools/test_research_c_oval_variable_usage_census.py), and the Actions artifact `c-native/original-oval-variable-usage-census.json`.

This is a *First-blocker census*, not a complete feature-frequency profile: some of the 68 Definitions have additional unsupported Tests, Sets, Filters, or evaluators. The Self-Assertion corpus exercises edge cases intentionally and is not a frequency model for deployed STIGs.

## Measurable safe authoring improvement, not coverage inflation

The [single-consumer C constant adapter](../../../tools/research_c_constant_state_source.py) and [adversarial regression tests](../../../tools/test_research_c_constant_state_source.py) independently rebuilt the **full exact typed A source graph** for **14 distinct string constants in eight original Definitions**. Their source Variable IDs/typed metadata live in a mandatory provenance companion; the editable C representation contains the field, comparison operation, explicit value quantifier and actual scalar/list of values. Nested arrays preserve order and duplicates; changed, missing, aliased, or conflicting values fail source-identity/roundtrip checks. The compiler accepts the authoring document plus companion, **without rereading source A or original OVAL XML**. [Actual original family example](c-original-family-fixed-pattern.research.yaml) is pinned and checked against generated source in CI.

**Limits:** this is a *narrow editable value facet*, not a full native C Definition compiler, a generalized datatype transformation or a separately executed evaluator. It does not increase the separately proven **36/162 native-C** Definition conversions. The three remaining nominal single-State constants do not satisfy all current safe-inlining conditions; never count them as converted. Existing full UNIX Set and Apache Variable hybrid examples remain separate source graph proofs.

## Independent authoring design consequence

There is more than one kind of OVAL Variable work:

1. **Fixed expected requirement values** should be inline where single-use, exact typed comparison/cardinality/source identity survives. Shared constants should be named once rather than copied into several checks.
2. **Collection or acquisition inputs** may look like constants but **select data**. A Variable used by a source Object's `var_ref` or collector is not automatically replaceable by a normal State literal. Preserve request identity, multiplicity, parent/host scope, and provenance.
3. **Computed runtime values** are the genuinely complex part: a typed DAG of transforms, selectors, and downstream collection arguments. Avoid pretending these are static inputs or merely different `must` syntax.

One original Variable can feed multiple roles: these are **authoring/use-site concepts**, not mutually exclusive declarations or a requirement for three separate execution engines. Keep one A-compatible typed execution graph. The **24 typed literal-only local Variables** are an important negative result for the historical assumption that every OVAL local Variable requires runtime computation. They still may be collection inputs and are **not automatically safe to inline** without preserving acquisition identity.

## Next genuinely valuable gates

- Source-driven collection bindings: demonstrate authored values or derivations feeding an original Object/command selector **without changing collection identity or value multiplicity**; reject shared/dynamic cases until proven.
- Multi-State reuse of one constant: author a named shared expected value, retaining one original source Variable identity and exact `var_check` per State.
- General derived expression DAG: preserve joins, object component sources, failures/unknown and per-parent identity; use true six-state and independently expected outcomes, not only typed-source graph equality.
- Measure on real STIG Apache/Linux/Windows content as well as Self-Assertion. This corpus overrepresents standalone datatype/function tests, including `time_difference` and `glob_to_regex`.

**No decision or external SLANG review request yet:** the separate Set/Filter/dynamic-command and runtime-status acceptance gates remain open. Do not adopt a normative 0.4-C grammar on these statistics.
