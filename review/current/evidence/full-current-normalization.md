# Full-current normalization review

This is the stable reviewer-facing summary for the full-current native normalization/compiler experiment.

## Scope

The generated tree contained 3,192 files and approximately 121 MB of payload. It demonstrated current-corpus normalization, shared Assessment reuse, schema validation, and compilation experiments.

That complete generated tree is evidence, not normative SCAP-NG source.

## Rebaseline disposition

Compact compiler, experiment, and validation summaries are being retained in `vanderpol/scap-ng-evidence` under:

`runs/niwc-current/2026-10-02-native-normalize-compile/`

The largest raw generated reports remain recoverable from the original repository history while a durable non-history storage decision is made:

- `normalizer-report.json` — ~78 MB;
- `native-schema-census.json` — ~29 MB;
- one remaining multi-megabyte validation payload is also source-retained pending the large-evidence storage path.

Original generated tree:

`research/iterations/003/review/full-current-native-normalized/`

Original tree identity:

`0cdc64a649d768fc9874757f3f508282f696baf8`

The pre-rebaseline Git tag/history remains the recovery source for the complete original tree.
