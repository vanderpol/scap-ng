# OVAL Board review of SCAP-NG

**Status:** pre-alpha working design for review. No proposal is Board-approved merely because its code, schema or CI exists.

## Review in about 20 minutes

1. Read the [visitor overview](../START-HERE.md) and [current working design](../research/iterations/003/design/CURRENT-DESIGN.md).
2. Browse a [RHEL 9 Rule and its manual/automated Assessments](../docs/rhel9-review.md), then the [Windows 11 guide](../research/iterations/003/review/windows11-current-full/README.md).
3. Compare the [draft specification](../specification/README.md) and [OVAL-to-NG crosswalk](../specification/migration/oval-5.12.3-capability-crosswalk.md). Reviewed mappings take precedence over provisional suffix-preserving inventory rows.
4. Read the [individual yes/no proposals](proposals/README.md) and use the [published Discussion links](VOTES.md) to vote with reactions.
5. Consult [decision reconciliation](../docs/decision-reconciliation.md) for original questions and [archives](../archive/README.md) for evidence behind earlier experiments.

## Current direction

- Benchmark → Rule → selected Assessment; no separate Policy object.
- Authored Tests, Objects, States and Variables preserve required semantics; native capabilities share clear primitives rather than reproduce OVAL XML in JSON.
- Publisher Profiles only disable Rules. External Tailoring may select published choices and enable/disable Rules, but cannot override publisher Parameter values. Organizational Input supplies delegated values.
- Manual checks remain essential. Informational policy use retains Rule role while technical truth remains separate.
- Compiled content uses logical manifest bindings and a self-contained ZIP prototype. Migration evidence stays outside executable native source.
- Results separate policy context from Assessment execution details, with bounded evidence and explicit completeness.

These are working requirements proposed for ratification, not announcements of a finished standard.

## What is demonstrated

The [fresh pinned-corpus normalization/compiler run](https://github.com/vanderpol/scap-ng/actions/runs/37004465863) passes: 65 source packages, 25,147 documents schema-valid before normalization, 19,655 afterward, and 65 compiled bundles. Self-signed CMS experiments demonstrate mechanics, not publisher trust. Current regression CI passes on Windows and Linux; Self-Assertion evidence remains separate from production migration.

Representation/round-trip comparisons, structural schemas and packaging do not establish target-runtime evaluator equivalence. Full-review examples include explicit warnings, exclusions and older generic capability shapes. Final grammar, broad capability normalization, cryptographic profiles and runtime conformance remain work in progress.

## How voting works

Each decision has one versioned yes/no proposition in its own GitHub Discussion. React to the opening post: 👍 Yes, 👎 No. Comments explain or clarify votes. A substantial change requires a new version and fresh votes; automation does not rewrite existing voting text or create duplicate versions.

Eligibility, quorum, voting duration, abstention/conflict handling and official disposition must be approved before votes are binding. The earlier TEST-VOTE-001 connectivity topic is a test, and the historical canonical-JSON research discussion is not a vote. New concrete proposals address those directions without deleting their history.

The [publication index](discussion-index.json) records Discussion URLs, proposal versions and body hashes. Its absence or a missing row means an item has not yet been successfully published. [Proposal source manifest](proposals/manifest.json).
