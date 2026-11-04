# Issue #21 filesystem selector naming evidence

These are representative source-equivalent native Assessments for the pinned
OVAL 5.12.3 `unix.file/file_object` full-path alternative. They are evidence
for owner review, not scanner proofs.

| File | Meaning | Validation expectation |
|---|---|---|
| `alternative-a.assessment.yaml` | Owner-approved Candidate A: `filepath` / `path` / `filename` | Valid under the current public resolved overlay. |
| `alternative-b.assessment.yaml` | Candidate B: `full_path` / `directory` / `filename` | Proposal only; rejected because Candidate B is not the grammar. |
| `tools-emission.assessment.yaml` | Pre-change tools shape: `full_path` / `directory` / `name` | Rejected by the public overlay; retained to show the resolved GAP-SEL-01 input. |

## Compatibility and migration consequences

Candidate A matches the current SCAP-NG `native-selector-contracts.json`,
authoring tests, and the updated canonical mappings. The separate tools PR
updates its snapshot/mappings so converter output uses Candidate A. Existing
converted YAML produced by the pre-change tools keys requires a mechanical key
migration with its source crosswalk/provenance regenerated; no alias is used.

Candidate B remains rejected. It must not be introduced as a permissive alias:
accepting both vocabularies would blur source crosswalks and make round-trip
provenance ambiguous.

The pre-change tools emission is verified statically from
`scap-ng-tools@1f4f74d`,
`src/scap_ng_tools/converter/_v04_runtime/v04_direct_converter.py:296-339`,
and the SCAP-NG mappings' `native.selector_map`. Candidate A is now selected by
the owner; updated output is covered in the separate tools PR.
