# OVAL Board review of SCAP-NG

**Status:** SCAP-NG 0.2.0 is a versioned pre-alpha working design for human/OVAL Board review. The 0.2.0 label is retained across corrective review changes; reviewers should use the current `main` content. Nothing is Board-approved merely because code, schema, examples, or CI are green.

## Start here

1. Read **[SCAP 1.4 → SCAP-NG: key changes](SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md)**, including the new **Results: less volume, more useful information** section covering Benchmark summaries, Rule messages/reasons, bounded evidence, maximum returned samples, and explicit completeness.
2. Open the **[SCAP-NG 0.2.0 schema](../schema/v0.2.0/README.md)** — the current versioned schema set on `main`, capability mappings, validation commands, and newcomer guide are all there.
3. Review the **[0.2.0 Board review content](review-content/0.2.0/README.md)** — this now includes the six source-to-NG converter pilot cases, frequency-oriented examples, focused New NG feature samples, and supporting/stress examples. For a feature-by-feature inventory, use **[FEATURE-SAMPLES.md](review-content/0.2.0/FEATURE-SAMPLES.md)**.
4. Review the **[OVAL 5.12.3 → SCAP-NG capability crosswalk](../specification/migration/oval-5.12.3-capability-crosswalk.md)** — this is the direct Test-type/capability mapping and a critical part of the Board review.
5. Download the compact **[representative OVAL Board review artifact](https://github.com/vanderpol/scap-ng/actions/runs/37321474460/artifacts/11350651969)** (`scap-ng-board-representative-review`). It contains only the primary review surfaces: maintainable normalized `authoring/` and compiled `packages/` for six representative benchmarks.
6. Review the **[Board proposals and votes](VOTES.md)** — one maintained index for proposal records, Discussion vote links, and the small set of current design decisions that still need new proposals.
7. Try the **[human-runnable SCAP 1.4 → NG conversion tools](../tools/HUMAN-RUNNABLE-SCRIPTS.md)**. The normal one-package entry point is **[`generate_niwc_current_review.py`](../tools/generate_niwc_current_review.py)**, which runs the checked-in rule splitter and current converter from an original pinned SCAP 1.4 ZIP. The exact-deduplication step is **[`scap_ng_repo_normalizer.py`](../tools/scap_ng_repo_normalizer.py)**.

## Current working direction

- Benchmark → Rule → Assessment; no separate Policy object.
- Preserve used, non-deprecated OVAL semantics without reproducing OVAL XML structure.
- Keep Test, Object, State, Variable, and Item concepts where their semantics remain useful.
- Keep applicability explicit and authored.
- Keep manual assessment first-class.
- Keep migration provenance separate from executable native content.
- Produce smaller, explainable Results with bounded evidence and explicit completeness.
- Use a self-contained manifest-based package for compiled content.

## Review boundary

SCAP-NG remains versioned as **0.2.0** for this Board review, but the current 0.2.0 baseline includes post-freeze corrective changes that made previously implicit/defaulted semantics explicit. Reviewers SHALL use the current `schema/v0.2.0/` content on `main` together with its regression evidence rather than treating the earlier six-case publication SHA as the final technical schema baseline.

The six converter-produced Board cases remain **pending human acceptance**, but they are no longer the whole review surface. The 0.2.0 Board corpus now also includes frequency-oriented examples from the pinned Self-Assertion source, supporting/stress examples for non-trivial Variable/Set/filter/dependency logic, and focused samples for newer or newly explicit NG concepts such as conditional evaluation, a candidate Assessment-result dependency analog for OVAL `extend_definition`, intrinsic and standalone applicability, explicit `not_applicable`, reporting projection, redaction, Organizational Input, manual Assessment, and the collected-Item reuse proposal.

The maintained entry point for that corpus is [`review-content/0.2.0/README.md`](review-content/0.2.0/README.md); the authoritative feature inventory is [`FEATURE-SAMPLES.md`](review-content/0.2.0/FEATURE-SAMPLES.md). The sample corpus is intentionally broader than the six converter-pilot cases, while keeping converter-fidelity evidence separate from native feature-demonstration content.

These checks establish structural, conversion, schema/semantic, and known-result evidence. They do **not** establish independent scanner equivalence, complete collector coverage, or live-target conformance. ESX/VMware and Kubernetes semantics that still need upstream guidance remain deferred rather than being guessed into the current design.

## Representative Board conversion build

The primary OVAL Board artifact is intentionally small and optimized for human review rather than exhaustive corpus coverage.

It contains six representative benchmarks:

- RHEL 9;
- Windows 11;
- Apple macOS 15;
- Apache 2.4 UNIX Server;
- Apache Tomcat 9;
- Google Chrome.

No Solaris benchmark is present in the pinned NIWC source repository. Solaris can be added later when a pinned SCAP 1.4 source is available.

The artifact contains only:

- `authoring/` — normalized native SCAP-NG source intended for ongoing human editing and maintenance;
- `packages/` — compiled `.scapng` packages built from those same source trees.

The `authoring/` tree is the form NG content developers would maintain after mechanical SCAP 1.4 translation and normalization. Exact duplicate Assessments are factored into `authoring/shared/assessments/` and use meaningful human-readable names derived from their semantics. Opaque hash-only shared names are prohibited by repository policy.

- **[Download `scap-ng-board-representative-review`](https://github.com/vanderpol/scap-ng/actions/runs/37321474460/artifacts/11350651969)**
- **[GitHub Actions run 37321474460](https://github.com/vanderpol/scap-ng/actions/runs/37321474460)**
- Artifact SHA-256: `58ac641937067546c632a177308eff34ab5253c26d0067a6d8ab836ea4373cb9`
- Approximate artifact size: **5.4 MB**
- SCAP-NG source revision used by the build: `390fe5f6b44bfe2a1a12600fc481e8e638f35aa3`
- Pinned NIWC source revision: `8c8e5dff860af6b1290ee9273a282db24278f8d5`

The representative set passed schema validation, Assessment-semantic validation, package-graph validation, exact-duplicate normalization, validation of the normalized source, and package compilation.

### Exhaustive corpus evidence

The separate 65-package NIWC Current build remains useful as broad migration/regression evidence, but it is **not** the primary human-review artifact.

That exhaustive run accounts for all 65 pinned source packages: 61 supported native conversions, four expected `independent.sqlext` publisher-extension blockers, and zero unexpected blockers. It is retained as supporting evidence that the converter handles the broader published corpus, not as something Board reviewers are expected to download and inspect file-by-file.

Supporting exhaustive run: [GitHub Actions run 37309124830](https://github.com/vanderpol/scap-ng/actions/runs/37309124830).

## Reproduce the conversion

The review builds are generated from checked-in tools and pinned source packages; they are not hand-edited exports. A reviewer can run the same pipeline locally:

- **Convert one pinned SCAP 1.4 package:** [`tools/generate_niwc_current_review.py`](../tools/generate_niwc_current_review.py)
- **See complete commands and prerequisites:** [Human-runnable SCAP-NG tools](../tools/HUMAN-RUNNABLE-SCRIPTS.md)
- **Normalize only proven exact duplicate Assessments:** [`tools/scap_ng_repo_normalizer.py`](../tools/scap_ng_repo_normalizer.py)
- **Inspect the exhaustive 65-package CI pipeline:** [`.github/workflows/scap-ng-full-current-native-normalize-compile.yml`](../.github/workflows/scap-ng-full-current-native-normalize-compile.yml)

The conversion goal is **semantic losslessness for supported SCAP 1.4 paths, with a normalized native representation**. Exact duplicate Assessment definitions may be replaced by one shared Assessment only when semantic equivalence is proven; Rule/check bindings and source provenance remain represented. Similar or near-duplicate Assessments are not merged automatically.

## Open design discussions

- **[Native representation of OVAL `extend_definition`](discussions/EXTEND-DEFINITION-NATIVE-MODEL.md)** — current conversion preserves the semantic by recursive inlining; the Board still needs to decide whether native NG should preserve an explicit Assessment-result reference and, if so, where that binding belongs.

## Voting

See **[Board proposals and votes](VOTES.md)** for the complete maintained proposal index, individual immutable proposal records, Discussion vote links, current proposal gaps, and voting-governance caveats.
