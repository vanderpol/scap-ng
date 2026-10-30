# Windows 11 — SCAP-NG 0.4.0 authoring review

This is a **historical six-STIG file-layout walkthrough**. For the [current human-readable 65-stream authoring ZIP](https://github.com/vanderpol/scap-ng-evidence/releases/download/v04-human-readable-review-20261030-ab5cddd/scap-ng-0.4.0-human-readable-authoring-review.zip), full original-source DRAFT, archived internal layout experiment, and smaller current examples, start at the [0.4.0 downloads and samples index](../../../docs/releases/0.4.0-downloads-and-samples.md).

Open the [earlier approved six-STIG sample release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) and inspect `authoring/ms_windows_11/` from the [YAML](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-six-stig-authoring-approved-20261020/scap-ng-0.4.0-six-stigs.yaml.zip) or [JSON](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-six-stig-authoring-approved-20261020/scap-ng-0.4.0-six-stigs.json.zip) ZIP. It contains source-backed Rules, Assessments, and shared Assessments in one verified cross-reference graph.

Start with [the current review guide](../REVIEW-GUIDE.md), then read [Assessment examples](../../../specification/examples/assessments.md). For complex Windows Tests, keep `windows.wmi.query` capability separate from older OVAL-derived Object IDs such as `wmi57`; the latter are source provenance, not alternate SCAP-NG collection capabilities. Do not rename compiled Object IDs unless every reference and source mapping is preserved.

These are authoring samples, **not observed Windows scan results**. Historic 0.3 comparison trees and illustrative 0.3 result files remain under [archived 0.3 content](../../../archive/0.3.0/README.md).
