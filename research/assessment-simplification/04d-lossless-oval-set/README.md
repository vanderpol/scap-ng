# 0.4-D original OVAL 5.12.3 nested Set/Filter/Variable — complete source-backed review

**20 October 2026 · Research #246 · experimental authoring, not scanner runtime-parity or a normative 0.4 specification.**

This is a real **OVAL 5.12.3 Self-Assertion Definition**, NOT a DISA STIG Rule: original [unix/oval-def_set-unix.xml, Definition 276](https://github.com/OVAL-Community/SCAP-Self-Assertion/blob/e3538595c5083b9c34d937a81d319234df9bbfaa/SCAP_1.4/OVAL_Test_Content/unix/oval-def_set-unix.xml), source revision e3538595c5083b9c34d937a81d319234df9bbfaa. It has **7 Tests, 11 Objects, 7 nested Set Objects, 4 States, 3 multi-valued constant Variables, an exclude Filter and explicit union/intersection/complement operators**.

## Permanent direct GitHub YAML for human review

- [Best current complete D compact authoring YAML — 224 editable lines](unix-set-seven-tests.0.4-D-compact-author.yaml)
- [Required separately managed source provenance — 78 lines](unix-set-seven-tests.0.4-D-compact-provenance.yaml)
- [Complete D unfactored YAML — 283 editable lines](unix-set-seven-tests.0.4-D-author.yaml)
- [D exact nested Set subtree reuse, before selector compaction — 271 editable lines](unix-set-seven-tests.0.4-D-reused-sets.yaml)
- [Original pinned source-compatible A graph as readable JSON](original-source-compatible-a.json). **This is v003-derived source-compatible intermediate representation, not an independently schema-validated full 0.4-A authored Assessment.**
- [Compact exact-source proof](compact-proof.json) and [Set-factoring exact-source proof](factoring-proof.json).

For a real operational STIG with five Tests and 19 dynamic Variables, compare the separate [Apache SV-214268 D authoring packet](../04d-lossless-apache/README.md). The UNIX Self-Assertion adds nested Set/Filter complexity not covered by that Apache check.

## Concrete simplification and actual source-equivalence boundary

| Authoring stage | Editable YAML lines | Graph proof |
| --- | ---: | --- |
| Earlier full C inline-constant hybrid artifact | 328 including source-compatibility metadata | Verified source reconstruction |
| First complete D Test/Set representation | 283 | Verified |
| D with exact named nested Set reuse | 271 | Verified |
| **D compact: source-pinned four literal path selectors and source titles managed separately** | **224** | **Verified** |
| **Required D managed source provenance** | **78** | Mandatory compiler input |

The 224-line D authoring file is **104 lines (~31.7%) shorter** than C's full hybrid YAML; the combined D authored and provenance material is about **302 lines**. Separating managed metadata from edited content is not elimination of source requirements. C and D have differently structured files, and line counts alone do not establish novice comprehension.

Specific source-proven reductions:
- **3 redundant authored constant Variable declarations eliminated**, while original value arrays, State references and value-match quantifiers are reconstructed exactly.
- **3 identical nested Set subexpressions** are replaced by explicit named Set reuse; compiler expands original operand order, complement direction and filter semantics. This is authoring-time factoring, **not** a live scan execution cache.
- **4 source-known unix.file literal path selectors** omit redundant string datatype/equality boilerplate. Explicit filename nil semantics are retained. Unknown shapes fail closed.
- **11 legacy source Object descriptions** remain in a required provenance sidecar, not in the author-edited file; meaningful author-facing collection names remain.
- Test quantifiers retain distinctions among absence, exactly-one-exists-and-match, and at-least-one-and-all-match; there is no C fields_join or split items_exist/items_match construct.

## Verified gates and limitations

[Focused green CI run 39424863621](https://github.com/vanderpol/scap-ng/actions/runs/39424863621): **28 regression tests passed**. Tests cover full original graph equality, source Set/Filter/State/Variable/criteria identities, alias cycles and incorrect aliases, filter action changes, altered path/nil fields, Value quantifiers, Test cardinalities, missing source identities and source titles, and YAML roundtrips. The source graph is exactly reconstructed by the [D Test/Set adapter](../../../tools/research_d_oval_sets.py), [safe named Set factoring](../../../tools/research_d_set_factoring.py), and [safe typed selector compact authoring](../../../tools/research_d_compact_collections.py).

**Not verified:** original scanner runtime behavior across complete-empty/partial/error/unknown/NA outcomes, a complete version-pinned native 0.4-A Assessment, generalized D capability conversion, the six-STIG corpus, or comprehension by non-OVAL authors. The unchanged A schema, converter and scanner were not modified.

**Decision:** retain this as an independent, source-verified D research candidate, not an adopted replacement for A. Next challenge is a genuinely complex DISA STIG Set/Filter/record example, independently tested expected statuses, and a complete native A/D comparison. Stop on semantic uncertainty; do not silently weaken the original test. Compatibility-relaxing [E plan #247](https://github.com/vanderpol/scap-ng/issues/247) remains planning only.
