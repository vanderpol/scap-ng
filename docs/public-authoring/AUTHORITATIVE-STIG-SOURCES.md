# STIG source authority for public agents and editors

**Authoring source-trust policy · 18 October 2026 · [curation issue #242](https://github.com/vanderpol/scap-ng/issues/242).** This guide defines how the agent decides whether an STIG Rule, check text, revision, or OVAL source is publisher-authenticated. It is not a comprehensive public STIG-source allowlist and does not change the normative SCAP-NG schema.

## The core distinction

**A discovery or convenience mirror is not the issuing authority.** A Rule shown on [STIGViewer.com](https://stigviewer.com) may be useful for finding identifiers or reading an informal mirror, but **STIGViewer.com is not DISA's authoritative publication source**. Do not confuse that site with DISA's distinct *STIG Viewer* application.

For authoritative public STIG content and release identity, use the [DISA Cyber Exchange STIG Document Library](https://www.cyber.mil/stigs/downloads/) and [official STIG release announcements](https://www.cyber.mil/stigs/stig-announcements), with relevant source files, metadata, revision and release dates. Cyber Exchange's [SRG/STIG compilation library](https://www.cyber.mil/stigs/compilations/) is an official alternative for a pinned quarterly snapshot; an out-of-cycle update may be individually published earlier. **Verify the actual payload version**, not merely the compilation date.

The earlier project rule to download DISA STIG manuals **only from cyber.mil** remains in force. The agent is allowed to use external sites to locate a title/Rule ID, but they do not confer source authority.

## Source categories for the agent

| Class | Examples | Allowed use | Label |
| --- | --- | --- | --- |
| **Publisher-official** | DISA STIG XML/ZIP/manual published by Cyber Exchange `cyber.mil`; an authenticated exact copy of that official artifact | Establish official Rule/check/fix/version provenance once original payload/revision verified | `AUTHORITATIVE: DISA` |
| **Verified local/archived official payload** | Offline STIG ZIP or source checked against a pinned official hash/signature and publisher release identity | Same for an explicitly pinned older release; not automatically *latest* | `VERIFIED OFFICIAL COPY`, with release date |
| **Project source or reviewed conversion** | Version-pinned `vanderpol/scap-ng` and SCAP-NG examples with documented input lineage | Existing implementation, modernization/reference comparison; **not automatically the original publisher text** | `PROJECT-DERIVED` |
| **Third-party discovery/reference** | STIGViewer.com, blogs, search snippets, other public STIG mirrors | Find a likely Rule ID, title, secondary interpretation or lead to original publisher | `THIRD-PARTY — UNVERIFIED` |
| **User-provided** | Pasted Check text, uploaded benchmark/Assessment, local repository files | Draft from user-provided material; use source claims only as supplied, until origin/revision are independently established | `USER-SUPPLIED` or `VERIFIED OFFICIAL COPY` when justified |

**Avoid blanket distrust of all third-party engineering material:** third-party OVAL implementations, OS vendor manuals and compliance code may be helpful when redesigning checks, but they are **comparison evidence**, not proof of the exact official STIG Rule/revision.

## Default resolution policy

1. Resolve an **exact Rule ID + revision/version** where available. If a mirror is the first search hit, use it as a *locator only* and continue to Cyber Exchange or a verified local official copy before saying the requirement is official or current.
2. Record the **publisher, downloaded artifact URL or local origin, exact version/release, retrieval timestamp when available and original payload hash**. Retain the provenance of copied/reviewed project content separately from the publisher payload.
3. For an *authoritative-source-required* workflow, **fail closed** if official content cannot be obtained or verified: do not silently promote STIGViewer.com or another mirror. Display `OFFICIAL SOURCE NOT VERIFIED`; the author may upload an official benchmark instead.
4. For a **draft-only exploratory workflow**, if the user requests proceeding from unofficial/user text, explicitly show `DRAFT FROM UNVERIFIED TEXT`. Do not assert revision/currentness, scanner validity or OVAL parity.
5. A source version mismatch is a **review item**: comparing RHEL 9 and RHEL 10 may help reuse logic, but platform applicability, selectors and requirement text still need verification.
6. On disconnected networks, prioritize locally provided signed/hash-verified official content and pinned packs. Do not make Internet access an editor requirement.

## Future configurable source allowlist

Maintain a small versioned **source policy** separate from the authoring schema and grammar profile: `official_publishers`, `allowed_discovery_sites`, `approved_mirrors_with_verified_hashes`, `blocked_sites`, `local_source_policy`, and exceptions approved by a trusted organization administrator. Its meaning must never be inferred solely from URL substring matching; validate hostnames, redirects, artifact identities and provenance.

**Design decision deferred:** how centrally to manage organizations' specific source allowlists, override permissions, release updates, cache hashes and disconnected policies. The curated public default is deliberately conservative. This page is guidance, not a security-certified source verifier or implemented automated URL enforcement.

## What to show the human

```text
Rule: SV-... · version/revision ...
Publisher source: AUTHORITATIVE: DISA — cyber.mil ZIP [release identifier]
Compared with: PROJECT-DERIVED RHEL 9 Assessment [commit/hash]
Third-party discovery: STIGViewer.com [not used as authority]
Target authoring language: SCAP-NG 0.4 experimental profile [exact tag/overlay]
Draft status: AI-generated; not schema-validated or scanner-verified
```

**Key rule:** publisher authenticity, SCAP-NG source provenance, syntax/schema validity, and actual scanner Assessment results are four different trust claims. Don't substitute one for another.
