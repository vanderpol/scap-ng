# Linux full benchmark — combined-rule

**Iteration:** 001  
**Rules:** 7 total: 6 automated in the automated package + 1 manual-only

The policy-only source contains seven policy rules. The automated source contains the same seven rules, with six assessments embedded directly in their rule objects and one manual-only rule. The repeated policy material is intentional so the lifecycle cost of the combined design is visible.

`source/` is the authoring/review form. `dist/` contains the real `.scapng` package prototypes. The ZIP members remain individually addressable even though the source is aggregated here for concise iteration review.

`results/` contains complete seven-rule scan examples. The automated scan deliberately includes Pass, Fail, Not Applicable, Error, and Manual results.

The prototype Ed25519 signature uses a public RFC 8032 test key and demonstrates mechanics only; it provides no publisher trust.
