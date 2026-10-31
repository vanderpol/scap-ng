# Source-backed producer compatibility (#255/#268)

This implements approved Decisions 1–3, 6, 10, 13 and 14 on the draft branch.
It does not promote the existing 65-stream library or change scanner semantics.

The direct converter now emits zero_or_more, a complete comparison Test field
policy, explicit reported_elements, bounded readable native names, and no
Assessment purpose. Class/mode and original source identities remain intact.
Redundant local field pairs equal to the nearest inherited pair are omitted;
exceptions retain both members. Boolean arrays, State boundaries, record
correlation and record aggregation remain distinct. Missing source counts are
errors, never filled from editor metadata. Existence-only Tests are exempt.
Explicit field absence retains values_found:none; the mandatory shared policy
on an all-absence Test is nonoperative because every leaf overrides absence.

The record schema now permits member inheritance only in an inherited native
condition. Unscoped historical record predicates retain explicit counts.
Source comparison and the compiler field-scope index now carry the nearest
complete pair into record members. Positive/negative coverage retains exceptions
and exactly_one record matching. This is an implementation of Decision 2, not
a change to the source cardinality algebra.

Long native names remove grammatical boilerplate and retain beginning/end
content within 64 characters including suffix. No random hash is appended.
Different original source identities that still collide are rejected, including
cross-Rule filename collisions; no dictionary overwrite is accepted as success.
The migration ledger records original-to-native identities and requires fresh
proof. Source identifiers, ZIPs and previously accepted native/proof hashes
are not changed. Shared-library promotion and naming remain separate gates.

Empty optional Rule discussion/rationale/extensions/warnings/identifiers/
references/remediation are omitted. Data affecting evaluation/applicability
remain required. No schema default annotations were added.

Usage is supplied to the independent static proof as invocation_purpose
(assessment/applicability), with standalone absence remaining None. The proof
checks source Definition class independently. Historical witness purpose is
read explicitly as archival metadata; current authoring still rejects it.
Historical may_be_absent witnesses are decoded to the canonical zero_or_more
term only at that archival/source-comparison boundary. Neither allowance is a
compiler or schema acceptance alias. No all_exist/incomplete/error/unknown
reference-oracle rule was changed.

## Observed gates

35 targeted tests PASS (9.721s): new source-backed producer suite, Windows
cmdlet/remaining primitive regressions, owner schema lock and schema registry.
This includes two pinned Windows Server 2025 Rules (SV-278139, SV-278080) and
pinned RHEL 9 SV-257851. Generated capability validation, whole-authoring schema,
compilation and fresh static source proof pass; invocation contexts can reuse
the Linux Assessment without changing its class. Additional original Windows
cmdlet/IIS/NTUSER closures retain fresh source proof and compilation.

The wider initial probe also exposed pre-existing historical fixture/compiler
incompatibility and a schema-anchor pin changed by the input PR. Those are not
passing results and are not repaired by rebaselining evidence. In particular,
this checkpoint is not maintained-suite green or a scanner-runtime proof.

Exact initial CI at 31b7ee859033a9b489a4e8458ae763ac2381533d completed:
Board, current-design, Markdown and issue-reference checks PASS; canonical-fast,
contract-sync, clean-extract and draft-schema FAIL. Contract-sync failed on
old producer purpose; canonical-fast first failed on its old synthetic purpose.
The producer and that current test factory are corrected here. Further gates
must be observed after publication; no active gate was canceled.
