# Representative Windows SCC Result Observations

**Purpose:** Preserve sanitized structural measurements from a representative SCAP 1.4 Windows 11 SCC scan supplied during iteration 001.

The raw result archive is intentionally **not** committed because endpoint results may contain host-specific or sensitive evidence.

## Size measurements

The supplied ZIP archive was **817,012 bytes compressed** and **14,097,194 bytes expanded**.

| Artifact | Uncompressed bytes |
|---|---:|
| ARF | 8,805,768 |
| XCCDF results | 2,457,653 |
| OVAL results stream 1 | 1,467,420 |
| OCIL results | 925,763 |
| OVAL results stream 2 | 419,856 |
| OVAL CPE results | 18,540 |
| OVAL variables stream 1 | 1,097 |
| OVAL variables stream 2 | 1,097 |

This is one endpoint and one benchmark. It should not be treated as a universal size ratio, but it demonstrates why SCAP-NG must treat result volume as an architectural concern.

At the same approximate expanded size, 100,000 endpoint assessments would represent roughly 1.4 TB before database/index overhead.

## XCCDF observation

The XCCDF result contained **257 rule-result elements** and **257 message elements**.

The SCC-generated messages were among the most immediately useful human-facing portions because they attempted to explain observed versus required conditions. This supports making structured explanation a normative NG result rather than relying on implementation-specific message prose.

## OVAL observation

For the two principal OVAL result files:

- stream 1 was 1,467,420 bytes, of which approximately 827,093 bytes were embedded OVAL definitions;
- stream 2 was 419,856 bytes, of which approximately 129,390 bytes were embedded OVAL definitions.

The result consumer must also traverse tested criteria/items and system characteristics to reconstruct why a definition passed or failed.

SCAP-NG should not require static assessment definitions to be repeated in every endpoint result. Results should reference the exact installed benchmark/assessment digest and contain only necessary runtime observations, reasons, and evidence.

## OCIL observation

The OCIL result was 925,763 bytes. It contained definitions for 257 questionnaires, 257 choice-question actions, and 257 choice questions, while only 11 questionnaire-result and 11 test-action-result elements were present in this particular output.

This illustrates the cost of coupling manual-assessment definitions and result instances in one result document.

SCAP-NG policy Check Content should be independently stored with policy. A manual result should contain the outcome and assessor evidence, referencing the policy procedure rather than reproducing an entire questionnaire language.

## ARF observation

The ARF was the largest result artifact at 8,805,768 bytes.

SCAP-NG should preserve the useful concept of associating asset identity, content identity, and results, but should avoid an aggregation format that requires embedding copies of multiple complete source/result languages.

## Design consequences

Iteration 001 carries forward these result principles:

1. static content is stored once and referenced by digest;
2. a rule result directly exposes actual, expected, operator, outcome, and decisive reason;
3. evidence can be shared by multiple rule results;
4. large populations return bounded examples and completeness/count-quality metadata;
5. full traces are optional forensic data, not the normal enterprise result;
6. manual and automated results share a common result envelope.
