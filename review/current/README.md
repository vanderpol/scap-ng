# Current SCAP-NG review

This is the single active human-review entry point.

## Start here — one review path

1. **Start with the policy:** [Benchmark and Rule examples](../../specification/examples/README.md), with actual STIG titles, discussion, identifiers, fixes and publisher Profiles.
2. **Then inspect the checks:** [automated and manual Assessment examples](../../specification/examples/assessments.md), including readable results and 0.3 modernizations.
3. **Compare before and after:** [0.3 modernization review guide](REVIEW-GUIDE.md), including boundaries for conversions that remain fail-closed.
4. **Inspect all six actual benchmark trees:** open [the latest verified end-to-end six-anchor build](https://github.com/vanderpol/scap-ng/actions/runs/37839525823) and download the **`scap-ng-board-representative-review`** artifact under *Artifacts*. Its `authoring/` tree includes two Linux, two Windows, DNS and Apache STIGs; the build also produced normalized and compiled packages.

For source examples and suggested searches in that ZIP (including `for_each:`, `shared_objects:`, Set/Filter and typed arrays), see the [exact-key feature index](../../specification/examples/assessments.md#where-to-find-real-source-files).

**Evidence status (October 8, 2026):** The linked six-benchmark artifact was built at source commit `072f849e73f5e605bbc1a9f6262f5ad8a75b8b26` (verified [full run 37839525823](https://github.com/vanderpol/scap-ng/actions/runs/37839525823)); later exact-head regression and 65-source gates remain separate. The six-benchmark build linked above passed conversion, native 0.3 schema/semantic validation, graph validation, normalization and compilation. The separate [65-source active-0.3 release gate](https://github.com/vanderpol/scap-ng/issues/202) has not yet been certified green. Four `independent.sqlext` packages are acknowledged blockers; pending compilation/runtime-equivalence issues are not resolved by a successful six-anchor build. 0.3 remains a **pre-alpha review candidate**, and OVAL Board release awaits owner acceptance.

**Results examples:** [0.3 Scan, Benchmark and Assessment Result fixtures](../../specification/examples/0.3.0/results/README.md) are clearly labeled **synthetic**; they explain summary, provenance, bounded evidence and manual attribution but are not real scanner output.

The earlier [deterministic human-review snapshot](https://github.com/vanderpol/scap-ng/actions/runs/37755622654) remains available for historical comparison with source commit `138c1d2f7695f1c1fe73ceb4f49de16e509dcfde`; it is **not** the latest regression build. The full-corpus modernization research measurements are kept separate from the active [full-corpus release checkpoint](https://github.com/vanderpol/scap-ng/actions/workflows/scap-ng-full-current-v03-release.yml).

For further detail, use the [0.3 schema](../../schema/v0.3.0/README.md), [core objectives](../../specification/objectives.md), [current draft specification](../../specification/README.md) and [0.3 Board release issue](https://github.com/vanderpol/scap-ng/issues/191). The showcase and review guide above are the primary reader-facing entry points.

## Explicitly deferred beyond 0.3

See the concise [deferred/out-of-scope list](../../specification/deferred-after-0.3.md). Deferred research is not part of the normative 0.3 review package.

## Historical 0.2.0 baseline — review closed

The 0.2.0 package is preserved as historical reference. The 0.3 candidate is the active review target.

- [0.2.0 schema](../../schema/v0.2.0/README.md)
- [0.2.0 source samples](../../board/review-content/0.2.0/README.md)
- [Published votes](../../board/VOTES.md)

Earlier completed review states are preserved under
[review/iterations/](../iterations/README.md).
