# SCAP-NG 0.3 — quick sample review

**Audience:** project owner and repository visitors seeking a roughly 10-minute readability preview. **This is not a formal request for OVAL Board review, 0.3 release approval, or runtime-conformance certification.**

**Download:** [direct six-STIG native authoring ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-99e8faf09771/scap-ng-0.3-six-stig-source-preview.zip) · [six individual ZIPs in the repository README](https://github.com/vanderpol/scap-ng#full-stig-conversion-downloads) · [checksum file](https://github.com/vanderpol/scap-ng/releases/download/v0.3.0-six-stig-preview-99e8faf09771/SHA256SUMS.txt).

These are durable **GitHub Release attachments**, not expiring Actions artifacts. The combined ZIP contains the complete `scap-ng-0.3-human-review/benchmarks/<name>/candidate-authoring/` trees, matching `faithful-authoring/` trees, and per-benchmark `SCORECARD.md` files. It **does not** contain compiled scanner packages or observed scan results.

## Read just these three real conversions

| Time | Focus | Look inside the downloaded ZIP |
| --- | --- | --- |
| 3 min | **An ordinary Rule and its direct predicate** | `benchmarks/rhel9/candidate-authoring/` → find `home-is-mounted-with-the-nosuid-option.assessment.yaml`. Compare its local `states:` entries with the same name under `faithful-authoring/` |
| 3 min | **An embedded Filter on observed Items** | `benchmarks/windows11/candidate-authoring/ms_windows_11/assessments/applicability/condition.bluetooth-installation.yaml`; compare to `faithful-authoring/`. Look for `filters:` and the absence of an artificial `state:`, capability, or State title inside each Filter |
| 3 min | **Genuine multi-Test logic** | `benchmarks/windows-server-2025/candidate-authoring/ms_windows_server_2025/assessments/automated/SV-278001.automated.yaml`. Confirm the `evaluate:` tree still conveys an understandable requirement |

If a named path has been deduplicated to `shared/` by the candidate renderer,
search the ZIP for the Assessment basename rather than assuming a fixed directory.

## Four things to tell us

Does an ordinary Test read naturally without chasing State references?
Does `select` (what to acquire) versus `filters` (which observed Items to
keep) make sense? Do comparisons still convey their typed requirements without
repeated capability/title wrappers? Is anything now **harder** to understand
than the faithful conversion?

**What does not need your review:** proving filter cardinality, regex matching,
unknown/error propagation, OVAL source identity, 65-source conversion, or
package signing. Those are engineering conformance gates in
[issue #208](https://github.com/vanderpol/scap-ng/issues/208), not owner
manual-verification work.

For a short in-page introduction without downloading a ZIP, read the
[Rule → Assessment walkthrough](../../specification/examples/assessments.md)
and the [select/filter/state contract](../../specification/assessment/selection-and-filters.md).

**Release boundary:** The six-STIG artifact is suitable for a *readability*
preview, but 0.3 freeze waits for a successful exact-head
[65-source gate](https://github.com/vanderpol/scap-ng/actions/workflows/scap-ng-full-current-v03-release.yml)
and differential six-state runtime checks.
