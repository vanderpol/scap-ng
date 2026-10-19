# C shared-engine first executable proof — 19 October 2026

**Research #245 · bounded engineering checkpoint, NOT accepted SCAP-NG 0.4-C syntax, native compiler, working scanner, or verified SCAP 1.4 source-result parity.**

## What passed

[**Exact-head CI 39249073388 — PASS**](https://github.com/vanderpol/scap-ng/actions/runs/39249073388): **8 source-backed focused tests**, Python 3.12/PyYAML, no new host/OS collectors. [The test implementation](../../../tools/test_research_c_shared_engine.py) and [small bridge](../../../tools/research_c_shared_engine.py) are in the existing tools tree, not a new scanner.

1. **Linux RHEL9 source check:** An independently written [C-shaped /home sample](c-source-exact-home-nosuid.research.yaml) compiles to the same immutable **0.4-A** `linux.partition` Object selector, field State and evaluation requirements as the [pinned A source](runtime-slice/home-nosuid.assessment.json). This includes `matches_regex: '.*\/home'`, `at_least_one_exists_and_all_match` over selected Items, and `at_least_one_exists_and_some_match` over the multi-valued `mount_options` field. An intuitive `equals: /home` selector, a changed presence minimum, a switched field operator, or a changed Item requirement **fails closed** rather than being passed off as faithful conversion.
2. **Apache real source Variable graphs:** The [two-Variable Apache source](../../requirements-first-language/contract-candidate/corpus/source-specimens/independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml) and the [19-Variable Apache source](../../requirements-first-language/contract-candidate/corpus/source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml) (published **0.3-derived** source specimens, not native valid 0.4-A authored Assessments) are processed through **the existing A source dataflow index**. They can be represented as named C-friendly derived steps (`extract`, `combine`, `merge_values`, `distinct`) and reconstructed to the **exact original source expression graph** and acquisition definitions, including variable identities, operator parameters and shared Objects. Unsupported operators do not get guessed.
3. **Same evidence, same fixture outputs:** The existing research Apache Variable fixture evaluator receives the original and reconstructed source plans with precollected shell Items. The resulting typed values, reported statuses and trace agree for a single `httpd`, alternate `apache2`, two observed paths and incomplete acquisition. The test is **same-evaluator fixture equality**, not an independent semantics oracle.
4. **Adversarial safeguards:** The bridge refuses changed patterns and requirements, missing/duplicate Variable identities, an unrecognized reference alias, altered step expressions, missing steps, changed source fingerprints and changed shared acquisition graphs.

## Side by side: authored source vs bounded C sample

Existing 0.4-A source-backed Test (only relevant nested fields shown; full source linked above):

```yaml
object:
  capability: linux.partition
  select:
    mount_point:
      matches_regex: '.*\/home'
states:
  - mount_options:
      require: at_least_one_exists_and_some_match
      equals: nosuid
require: at_least_one_exists_and_all_match
```

Independently authored C test shape (experimental):

```yaml
require:
  each: linux.partition
  where:
    mount_point:
      matches_regex: '.*\/home'
  minimum_items: 1
  all_found_items:
    mount_options:
      contains: nosuid
```

The C syntax is more requirement-oriented, but this test only proves a **small, exactly mapped subset**. The selector syntax remains source-exact on purpose: shortening it to `equals: /home` may change assessed Items and outcomes. More radical improvement must never hide that tradeoff. The compiled output is still A's original Object/State contract.

## Do not overclaim

| Boundary | Actual status |
| --- | --- |
| C authored Linux sample roundtrips to same A collection/State shape | **PASS** (structural identity) |
| Existing A dataflow indexes original and C-presented Apache graphs identically | **PASS** (static structure) |
| Existing fixture evaluator yields identical values/statuses for same Apache evidence | **PASS** (same evaluator; selected test inputs) |
| Source evaluator independently verified against OVAL 5.12.3/SCAP 1.4 runtime | **NOT PROVEN** |
| Runtime collector compatibility, OS call behavior, caching, performance | **NOT PROVEN** |
| New losslessly rewritten Variable *algorithms*, instead of re-presenting original expressions | **NOT PROVEN** |
| All six STIGs expressible as C/compatible fallback, source and result preservation | **NOT PROVEN** |
| User-unfamiliar auditor authors and understands complex new C content correctly | **NOT TESTED** |

**Conclusion:** The shared-front-end/shared-A-backend architecture has its first *working structural seam*. It does **not** demonstrate that replacing Variable implementation is cheap, that collection and evaluation are fully independent, or that C has functional parity with A.

## Next focused gate, without restarting B

Take **one real 0.4-A Registry or Windows WMI State** and make its typed selector, Item/field/record requirements and evidence status survive the same C authoring boundary, including missing/incomplete/error. Separately test **one actual Variable-expression optimization**, with *independent* expected values and status, under pinned source identities. Anything with changed output or lost parent identity must fall back to original compatibility IR. Do not let a visually shorter rule count as source-preserving until those independently verified gates pass.
