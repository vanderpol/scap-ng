# 0.4-C hybrid experiment: `must` over original OVAL Set/Filter/Variable dataflow

**19 October 2026 · Refs #245 · Experimental, not adopted 0.4-C or a scanner-conformance claim.**

## The question tested

Should we rebuild the complete 0.3/0.4-A Object/Set/Filter/Variable execution graph to obtain clearer 0.4-C authoring, or retain the proven graph and improve the human-facing requirement vocabulary independently?

**Bounded result: the second route works for a real complex source Definition.** The compiler reconstructs the *exact original source-compatible A Assessment* after presenting existence/matching as `must` and criteria as `and` / `or`. This is a genuinely executable, independent C-to-A requirements adapter; it is **not yet** proof that the remaining A dataflow representation is pleasant to author, nor that live source OVAL scanner outcomes agree.

Source: [OVAL Community Self-Assertion `unix/oval-def_set-unix.xml`, pinned](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/unix/oval-def_set-unix.xml), **Definition `oval:org.mitre.oval.test:def:276`**. The pinned v003 semantic round-trip is already verified. CI now independently regenerates the authored C overlay, lowers it without loading the original source as compiler input, and checks complete deep equality against the original v003 A graph.

## Meaningful change in what the author sees

The original source-compatible Test contains separate `check` and `check_existence` fields:

```yaml
check: all
check_existence: only_one_exists
states:
  - state-this-file-state-represents-a-file-object-with-a-path-equ
```

The generated C *author-facing check* uses a single `must` contract:

```yaml
checks:
  complement:
    description: Test that the set construct is supported with the COMPLEMENT operation.
    observation: this-object-represents-file-object-that-set-b-c-complement-object
    must:
      items_exist: exactly_one
      items_match: every
      states:
        - state-this-file-state-represents-a-file-object-with-a-path-equ
require:
  and:
    - check: complement
    - check: intersection
    - check: union
    - check: exclude_filter
    - check: one_level_sets
    - check: two_level_sets
    - check: three_level_sets
```

The full generated C document also carries each original Test `source_id` and all original descriptions plus a `compatibility` section containing the **unmodified, explicitly typed A Object/Set/Filter/State/Variable graph**. Nothing is silently turned into a simpler Set, an invented filter order, or a scalar constant. This deliberate separation is the key hybrid design point; **the full document remains more verbose than we ultimately want**.

## Verified proof

[CI original-source hybrid proof, run 39333725911](https://github.com/vanderpol/scap-ng/actions/runs/39333725911):

| Original source graph | Preserved |
| --- | ---: |
| OVAL Tests / C checks | **7 / 7** |
| Original Objects | **11** |
| Set Objects (nested union, intersection, complement and exclusion filters) | **7** |
| Source States | **4** |
| Original Variables, including multi-valued constants | **3** |
| Original criteria | Explicit AND containing all seven Tests |

All eleven Objects, Set ordering and operand nesting, Filters, all three constant-Variable values/quantifiers, four typed States, original source Test IDs, Test titles, and exact semantics-preserving criteria survive a **byte-neutral structured deep-equality check** against the source-compatible representation. Changing the source Test's cardinality, the Filter action, or the constant-Variable values causes source-equivalence proof failure.

[298 focused C tests passed](https://github.com/vanderpol/scap-ng/actions/runs/39333725713), including eight hybrid positive/adversarial tests. [Source-independent hybrid requirement adapter](../../../tools/research_c_hybrid_must_overlay.py) and [negative-test suite](../../../tools/test_research_c_hybrid_must_overlay.py). The full proof JSON and generated C overlay are included in the [source-backed GitHub Actions artifact](https://github.com/vanderpol/scap-ng/actions/runs/39333725911), under `c-hybrid/`; this artifact is temporary, while this summary and its source/CI are permanent.

**Scope caveat:** A semantic round-trip, structural deep equality and synthetic negative tests are not a six-state scanner run. The module has not replaced the native Self-Assertion C compiler; that converter remains at **20 of 162** supported Definitions. Call this **one independently validated hybrid authoring experiment**, not 21 C-native Definitions and not a completed Set/Filter/Variable simplification.

## Independent engineering assessment: go/no-go

**GO: investigate the hybrid architecture further.** Existing native OVAL-compatible graph semantics are sophisticated and have already survived real roundtrips. Rewriting them simply to gain shorter syntax creates risk and delay without demonstrated benefit.

**NOT YET GO: accept the present authored format as satisfactory.** Replacing `check`/`check_existence` with `must` and `all` with `and` is useful but insufficient. A human author still confronts long legacy State/Object identifiers and a large typed execution graph. The next material gains must be demonstrable rather than cosmetic:

1. **Inline fixed literal values at the consumer** while keeping exact multi-value `var_check`, datatype, provenance and sharing. Do not remove real runtime derived inputs or mixed acquisition/comparison uses.
2. **Separate reusable observations from per-check requirements** without losing Set population, filter order, Items or collection behavior. Show dependency arrows and source comments in a graphical/editor view.
3. **Keep true derived-data dependencies explicit**, including downstream commands/selector parameterization, without redeclaring intermediary Variables only for presentation.
4. **Measure before/after authoring burden** on this seven-Test UNIX source and the nineteen-Variable Apache source: number of declarations authors must edit, number of cross-references, and whether a non-OVAL expert correctly interprets empty/error/unknown paths. Less YAML alone is not semantic clarity.
5. **Prove status boundaries**, source OVAL Set complement/filters and multi-valued matching, independently with expected outcomes. Structural source preservation does not establish scanner parity.

Do **not** promote a second proprietary Set/Filter evaluator or alter the normative 0.3 design on the strength of this research result. Formal comparison with David Solins' SLANG still needs a human-readable **full** complex example and independent status outcomes; this proof is a real step toward that threshold but **does not alone satisfy it**.

The high-level architecture preference is recorded in [#245](https://github.com/vanderpol/scap-ng/issues/245), subject to owner review of the semantic-language change before acceptance.
