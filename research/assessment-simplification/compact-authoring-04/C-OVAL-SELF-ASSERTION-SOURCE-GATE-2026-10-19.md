# 0.4-C original OVAL Self-Assertion: verified imported baseline and new authoring experiments

**19 October 2026 · [issue #245](https://github.com/vanderpol/scap-ng/issues/245) · Working research, not release or complete 0.4-C.**

## The new reproducible full original source gate

The [full original-source CI job](../../../.github/workflows/research-c-self-assertion-compatibility.yml) now checks out:
- `OVAL-Community/SCAP-Self-Assertion@e3538595c5083b9c34d937a81d319234df9bbfaa` (original SCAP 1.4 OVAL Test Content, **not** converted samples),
- `OVAL-Community/OVAL@v5.12.3` (source schema checkout),
- current `vanderpol/scap-ng@main`, including the maintained 0.3 source lowering/OVAL round-trip engine.

CI executes the full old-format compatibility pipeline and [the new 0.4-C source-backed export adapter](../../../tools/research_c_oval_self_assertion_bridge.py), which cross-references original source Tests/criteria, preserves native Test titles and original Test comments, copies the complete source-compatible A/0.3 Assessment in a typed fallback, and creates explicit per-Definition reviews plus a manifest.

**Reproduced original corpus counts:** **144 XML source files, 785 declared OVAL Tests, 167 Definitions**, of which **162 have semantically equal v003 OVAL round-trips** and **five are explicitly source-deprecated or source-invalid**. The exact five blocker identities and reasons are regression-gated. [Verified full CI run, 2026-10-19](https://github.com/vanderpol/scap-ng/actions/runs/39323282663).

Five exception cases (do not silently repair content):
1. `ios/ios-def_version55_test.xml` — deprecated OVAL Test.
2. `junos/junos-def_xml_config_test.xml` — deprecated OVAL Test.
3. `macos/ind-def_environmentvariable58_test_mac.xml` — original Variable-reference datatype mismatch.
4. `solaris/sol-def_package511_test.xml` — original Variable-reference datatype mismatch.
5. `windows/win-def_wuaupdatesearcher_test.xml` — original Variable-reference datatype mismatch.

This is **162 source-compatible A fallback Assessments**, NOT 162 native C authoring conversions and NOT 162 independently executed OVAL scanner results. The C review manifest explicitly counts **zero native C-converted Definitions**, and refuses any missing Definition/report entry. The earlier local-only 291/785 C Test and 51/167 C Definition figures are not reproducible here; **do not combine** those historical numbers with this 0.3/A baseline.

The generated review package currently uses a **GitHub Actions artifact with finite retention**, not a persistent release/commit. Before asking for human review of native C output, publish an independently verified complete C authoring converter and corresponding GitHub-hosted source-linked content, plus real semantic boundary outcomes rather than read-only views.

## One original OVAL constant Variable can already disappear from authored C values

The [original Self-Assertion filter closure](../../../board/review-content/0.2.0/sources/filter.xml) uses OVAL `var:134`, two fixed string paths, and source `var_check="only one"`. The new [source-independent C literal-array lowering](../../../tools/research_c_inline_source_constants.py) and [tests](../../../tools/test_research_c_inline_source_constants.py) express this consumer as:

```yaml
field: path
equals:
  - /opt/support/txt/txtfile
  - /opt/support/txt/txtfile/subtxtfile
value_match: one
```

No authored constant Variable declaration is needed. The compiler can recreate **one typed constant Variable** with the same original source ID, both values in order (including duplicates if present), and the exact original `only one` quantifier as internal compatibility provenance. The small adapter explicitly rejects shared constant references, unknown types, non-equality operations, empty values, and implicit/missing quantifiers. This is **one real OVAL source-backed field-predicate experiment**, not a whole converted Set/Filter Definition. It neither evaluates nor silently changes the original Set membership.

[Verified 271 focused unit tests including six source-backed constant tests](https://github.com/vanderpol/scap-ng/actions/runs/39323600742).

## Variable origin versus Variable use — evidence, not new syntax

The [read-only C Variable role audit](../../../tools/research_c_variable_roles.py) distinguishes:
- **Origins**: static publisher constant; value derived from observed Items/other calculations; external OVAL Variable (which **is not automatically** an authorized Organizational Input).
- **Consumers**: command/selector acquisition parameter; filter/set population selection; a Test's expected-State comparator; input to another transformation; other explicit Object/Test dependency.

In the original full Apache SV-214268 source, 19/19 Variables are derived, **nine** Variables are consumed at least once by further acquisition parameters and **ten** by other value transformations. These are **consumer-role counts, not exhaustive distinct authoring constructs or proof that a Variable cannot be reused**. A source graph can have multiple consumers, including one Variable used for collection and Test comparison; regression fixtures prove such mixing must remain representable.

A promising **design hypothesis**, not accepted C grammar, is:
- keep static scalar/array literals inline;
- keep policy authority and Organizational Inputs separate from system observations;
- author genuine runtime computations as `derived_values`, with typed field extraction and pure transforms;
- reference those derived values directly from observation acquisition parameters, filters, or comparisons, without inventing duplicated Variables or claiming a new evaluation phase;
- retain the full typed graph (and its statuses, scopes, provenance and original test documentation) in the internal A-compatible IR.

The real design criterion is **stage/causal role and evidence lineage**, not a superficial renaming of OVAL Variable. Do not force an artificial two-way exclusive split because a real derived value may serve several roles.

## Next source gates

1. Compile complete, original Definition closures from human-authored C to the existing A source IR, starting with common direct Tests; no duplicate execution model.
2. Preserve original source Test comments/metadata and meaningful authored check identities, even for complex Sets/Filters and nested Variable chains.
3. Demonstrate Set/Filter/Variable/foreach and datatype semantics from the original 785 Tests with independently reviewed expected populations and six-state outcomes.
4. Produce source-ID → compiled C output/unsupported-reason crosswalk for **every** original source Test/Definition and ship the complete content directly on GitHub.
5. Keep actual original OVAL collector/scanner conformance as a separate later gate.

**The original OVAL corpus is not yet converted to readable 0.4-C. Its compatibility foundation is now reproducible and regression-gated; this distinction is important.**
