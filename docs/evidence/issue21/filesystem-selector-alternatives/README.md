# Issue #21 filesystem selector naming evidence

These are representative source-equivalent native Assessments for the pinned
OVAL 5.12.3 `unix.file/file_object` full-path alternative. They are evidence
for owner review, not new approved examples or scanner proofs.

| File | Meaning | Current 0.4 validation expectation |
|---|---|---|
| `alternative-a.assessment.yaml` | Candidate A: `filepath` / `path` / `filename` | Valid under the current public resolved overlay (`filepath` is used). |
| `alternative-b.assessment.yaml` | Candidate B: `full_path` / `directory` / `filename` | Proposal only; currently rejected because the public overlay does not expose `full_path`. |
| `tools-emission.assessment.yaml` | Exact observed tools mapping shape: `full_path` / `directory` / `name` | Currently rejected by the public overlay; this is the concrete nine-selector mismatch. |

## Compatibility and migration consequences

Candidate A matches the current SCAP-NG `native-selector-contracts.json` and
the existing author-facing tests. It would require the converter to map its
internal OVAL/native acquisition names (`full_path`, `directory`, `name`) to
`filepath`, `path`, `filename`, or require an explicit converter migration
layer. Existing converted YAML using the tools keys would need a mechanical
key migration and regenerated source crosswalk/provenance.

Candidate B better matches the converter's path-level internal names for
`full_path` and `directory`, but still requires a decision about `name` versus
`filename` and a coordinated mapping/schema change. Existing Candidate-A
content would need key migration. It must not be introduced as a permissive
alias: accepting both vocabularies would blur source crosswalks and make
round-trip provenance ambiguous.

The tools emission is verified statically from
`scap-ng-tools@1f4f74d`,
`src/scap_ng_tools/converter/_v04_runtime/v04_direct_converter.py:296-339`,
and the SCAP-NG mappings' `native.selector_map`. Direct end-to-end conversion
against this checkout remains blocked by the tools frozen snapshot pin. No
naming option is selected by this evidence.
