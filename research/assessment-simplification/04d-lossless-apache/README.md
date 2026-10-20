# 0.4-D first source-backed review: Apache SV-214268

**20 October 2026 — Research #246; NOT an adopted 0.4.0 grammar, released scanner, or OVAL runtime-parity proof.** The intent is to explore a clearer, lossless authoring model **without editing 0.4-A**.

## Review the actual YAML — directly in GitHub

- [Complete 0.4-D author-edited YAML](apache-sv214268.0.4-D-author.yaml)
- [Required but non-author-edited source provenance](apache-sv214268.0.4-D-provenance.yaml)
- [Machine-readable count and reconstruction proof](proof.json)
- [Original converted Apache Assessment (0.3-derived source, NOT a validated 0.4-A authoring file)](../samples/apache_server_2-4_unix_server/assessments/automated/niwc.apache_server_2-4_unix_server.SV-214268.automated.assessment.yaml)
- [Exact source OVAL for SV-214268](../evidence/apache_server_2-4_unix_server/SV-214268/source-oval.xml)
- [0.4-C full Apache experiment and measured sidecar split](../compact-authoring-04/C-APACHE-FULL-HYBRID-2026-10-19.md)

The complete source includes **five Tests, nineteen chained computed Variables, one named shared Object and four private acquisitions**. Two distinct populations of Apache configuration files must remain distinct. The generated 0.4-D editor-facing Assessment uses C's proven explicit observation/derived-value model and source provenance separation, but its Test/State syntax deliberately returns to A-style paired `require` with explicit `states_match: all`.

## Specific Test/State readability change

Here is the actual D portion for the optional loaded-file SessionCookieName requirement (not a replacement of the complete file):

```yaml
require: at_least_one_exists_and_all_match
states:
  - stdout_line:
      require: may_be_absent_and_all_match
      matches_regex: '(?i)HttpOnly'
  - stdout_line:
      require: may_be_absent_and_all_match
      matches_regex: '(?i)Secure'
states_match: all
```

C used an extra `must.items_exist` / `must.items_match` split, repeated `field: stdout_line` and `fields_join: and`; D drops those wrappers while retaining the exact same scope: the two State predicates are evaluated against each **single collected Item**, with no false cross-Item matching. The field-level `may_be_absent` wording is still difficult, and is **not** hidden or renamed until its precise semantics and vocabulary are reviewed. Likewise the original Test title mentions only HttpOnly even though the original source also evaluates Secure; D retains that source description pending review rather than silently changing source parity.

## What is verified, and what is not

[Successful focused Actions test run 39421024237](https://github.com/vanderpol/scap-ng/actions/runs/39421024237): **10 tests passed**. The checked-in [research adapter](../../../tools/research_d_apache_native_states.py) reconstructs the complete existing converted native **0.3 source-compatible** Apache Assessment from D source plus a required SHA-pinned provenance sidecar, *without loading the original Assessment as compiler input*. Tests compare complete source graphs: five original Tests, 19 Variable definitions, shared Object identity and AND result topology. They reject changed regexes, collector commands, cardinality, missing same-Item AND, missing provenance and unreviewed source drift. Explicit author edit mode changes the generated graph but makes **no source parity claim**.

| Actual version / authoring surface | YAML lines | Status |
| --- | ---: | --- |
| Original converted 0.3 Assessment, full authoring representation | 554 | Existing source-compatible baseline; **not native valid 0.4-A** |
| Complete C hybrid, provenance still inline | 428 | Verified 0.3 source reconstruction |
| C author-edited only, required separate provenance | 354 | Verified 0.3 source reconstruction |
| **D author-edited only, required separate provenance** | **335** | **Verified 0.3 source reconstruction** |
| D required provenance sidecar | 98 | Must accompany authoring; combined D is 433 lines versus 428 full C lines |

The metrics are **not** evidence that execution operations are reduced: D still authors **nineteen derived computations**. Compared with the already-proven C split, the direct syntax saving is just 19 author-edited lines (~5.4%). D has **not** proven independent 0.4-A typed native-schema validation, scanner runtime parity, cross-platform converter coverage, or blinded auditor readability. Avoid calling 0.3 deep equality an OVAL scanner conformance result.

## Low-compute next gates before owner review

1. **A/4D native parity:** produce a first-class complete **valid version-pinned 0.4-A** Apache Assessment or a clearly specified base-A Test projection from the same source, prove D→A mechanically and report all 0.3-to-A transformation differences. Preserve the frozen A files.
2. **Actual author burden:** reduce the *nineteen* author-edited derived steps safely by factoring common source discovery or inlining only independently proven pure transformations. Don't simply hide downstream command dependencies.
3. **Second hostile source:** a non-Apache, real OVAL nested **Set/Filter/multivalued Variable** or Windows WMI/record composition. Publish full A/D examples here with tested empty/partial/error/unknown/NA outcomes and explain any blocked operators.
4. **Comprehension comparison:** give unfamiliar reviewers same source intent and complete A/D YAML; ask precisely which Item is assessed, whether States share one Item, what happens if none are found, how requirements combine and where evidence came from.
5. **Stop/go:** if D offers only cosmetic improvement on two real complex assessments, keep 0.4-A as the primary design and don't promote D vocabulary.

## 0.4-E remains planning only

[Separate staged E research plan #247](https://github.com/vanderpol/scap-ng/issues/247) breaks work into independently resumable sub-10-minute Codex slices because the advertised five-hour-per-day usage limit may correspond to roughly ten minutes of actual daily coding-agent compute. No claim that an agent is currently running; Actions is used here for fast targeted checks. E may intentionally diverge from original OVAL mechanics **only after** D lossless research and an explicit human-reviewed source-intent/behavior change.
