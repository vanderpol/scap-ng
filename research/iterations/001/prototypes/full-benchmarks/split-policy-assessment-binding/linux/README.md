# Linux full benchmark — split-policy-assessment-binding

**Iteration:** 001  
**Rules:** 7 total: 6 automated in the automated package + 1 manual-only

The policy source contains seven rules once. Automation is a separate collection of six assessments plus six bindings. The manual-only rule has no binding. The policy source is used unchanged to build both policy-only and automated packages.

`source/` is the authoring/review form. `dist/` contains the real `.scapng` package prototypes. The ZIP members remain individually addressable even though the source is aggregated here for concise iteration review.

`results/` contains complete seven-rule scan examples. The automated scan deliberately includes Pass, Fail, Not Applicable, Error, and Manual results.

The prototype Ed25519 signature uses a public RFC 8032 test key and demonstrates mechanics only; it provides no publisher trust.
