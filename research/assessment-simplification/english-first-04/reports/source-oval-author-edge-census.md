# Original-source OVAL rare-feature ownership vs six-STIG native authoring

**Research only.** Input pinned NIWC `scap-content-library` revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5` and exact native six-STIG r3 SHA-256 `03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d`.

Direct original OVAL source: **2140** Test identities in six original STIG archives.
Curated native authoring: **1375** Tests in **872** automated Assessments.
They are different populations: source archives contain OVAL content not necessarily selected into native authoring.

## Original OVAL Test origin and existence usage

| Original ID namespace | at_least_one_exists | all_exist | any_exist | none_exist | only_one_exists |
| --- | ---: | ---: | ---: | ---: | ---: |
| DISA | 1237 | 356 | 116 | 101 | 8 |
| NIWC/NAVWAR | 268 | 5 | 5 | 40 | 4 |

## Selected native authoring modes (different denominator)

| Existence mode | Native Test occurrences |
| --- | ---: |
| `all_exist` | 201 |
| `any_exist` | 71 |
| `at_least_one_exists` | 993 |
| `none_exist` | 103 |
| `only_one_exists` | 7 |

## Native Test source-ID linkage check

Original OVAL Test comments and original existence modes can provide
candidate matches, **not verified source identities**.
| Candidate quality | Native Test count |
| --- | ---: |
| `mixed_author_candidates` | 14 |
| `multiple_same_author_candidates` | 112 |
| `single_original_test_id_candidate` | 1249 |

## Source attribution for 201 native all_exist cases

The JSON contains each native Test with **source-ID candidates**, not proven
lineage. Cases where several original IDs share a comment, or none match,
require XCCDF Rule/Definition/source Test ID mapping. Do not infer author
statistics for those from filenames or NIWC packaging.

## Limitations and decision policy

- Counts of all original OVAL Tests include Tests not selected in the 0.4 native six-STIG authoring; never divide one source count by the other denominator.
- Source namespace establishes *identity prefix*, not a verified DISA 1.3 release byte-for-byte comparison.
- A native descriptive Test name can match several different source IDs; title-and-mode joins are candidates only; do not call them provenance-confirmed.
- Original XCCDF Rule→OVAL Definition→Test ID closure is required for a provable native assessment linkage; mixed-source dependencies must be reported independently.
- No OVAL feature is dropped in this report and no schema, runtime, importer or source benchmark was modified.

Any rare OVAL feature needs a separate human-value/semantic review:
retaining the capability to convert a source construct does not require
giving native content writers a corresponding new keyword. Mark unused
source features as candidates, not automatically obsolete.
