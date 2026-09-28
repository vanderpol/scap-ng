# SCAP-NG Format Comparison Criteria

Iteration 001 now compares the same canonical assessment semantics in three
human-facing YAML representations. The early seven-rule prototypes remain useful
for controlled feature experiments, but the primary format evidence is now
generated from published SCAP 1.4 benchmarks.

## Candidate A — Combined rule with shared-rule overlays

A resolved combined rule keeps policy text, Check Content, applicability, and
automation together.

Cross-STIG reuse is represented as:

- one reusable technical/shared rule base;
- policy-specific overlays;
- build-time resolution into complete scanner-facing rules.

The overlay may specialize policy identity/content and declared parameter
values, but it must not silently mutate the shared assessment semantics.

The central design question is whether the convenience of a complete rule view
justifies normative inheritance/overlay semantics at high reuse fan-out.

## Candidate B — Split policy / assessment / binding

Policy rules, technical assessment definitions, and mappings are separate
authored objects.

Cross-STIG reuse is represented as:

- one shared technical assessment;
- independent policy rules;
- explicit bindings from each policy rule to the assessment;
- typed parameters where reviewed parameterization is permitted.

The central design question is whether explicit composition and provenance
outweigh the additional navigation between policy, assessment, and binding
objects.

## Candidate C — Ansible-inspired authoring

The Ansible-inspired form uses familiar ordered concepts such as steps,
register, variables/bindings, and assert/that while preserving SCAP-NG's typed
assessment semantics.

It has **no Ansible, Jinja, Python, inventory, plugin, or mutable-task runtime
dependency**.

It is an authoring syntax over the same canonical semantics, not a third scanner
execution model.

The central design question is whether Ansible familiarity materially improves
authoring/review comprehension without adding unnecessary ceremony or inviting
incorrect assumptions about Ansible execution behavior.

## One semantic source for all candidates

The comparison pipeline is:

    published SCAP 1.4
      -> faithful XCCDF + OVAL semantic IR
      -> canonical SCAP-NG benchmark semantics
         -> combined-rule YAML
         -> split policy/assessment/binding YAML
         -> Ansible-inspired YAML

The automated verifier reconstructs the rendered semantics and compares them
against the canonical benchmark. A syntax is not allowed to gain apparent
simplicity by discarding source behavior.

## Production benchmark demonstration

The three renderings have been generated and equivalence-checked for:

| Benchmark | Rules | Supported automated | Manual/external | Automated source blockers |
| --- | ---: | ---: | ---: | ---: |
| RHEL 9 | 445 | 418 | 27 | 0 |
| Oracle Linux 9 | 448 | 408 | 40 | 0 |
| Windows 11 | 257 | 245 | 11 | 1 |
| Windows Server 2025 | 291 | 260 | 30 | 1 |

RHEL 9 and Oracle Linux 9 provide the Linux reuse axis. Windows 11 and Windows
Server 2025 provide the client/server Windows reuse axis and expose
Windows-specific migration issues.

## Measured exact reuse in the four anchors

The four published anchors contain 1,331 supported generic automated assessment
instances but only 804 unique exact technical assessments.

Therefore:

- exact duplicate assessment definitions avoidable: **527**;
- exact assessment-definition maintenance reduction: **39.59%**;
- cross-benchmark exact-reuse groups: **525**.

Directional pair coverage is:

- Oracle Linux 9 reusable with RHEL 9: **368 / 408 = 90.2%**;
- RHEL 9 reusable with Oracle Linux 9: **368 / 418 = 88.04%**;
- Windows 11 reusable with Server 2025: **158 / 245 = 64.49%**;
- Server 2025 reusable with Windows 11: **158 / 260 = 60.77%**.

The same exact reuse groups are available to all three candidate formats. No
format receives credit for a larger hand-picked reuse set.

## Reuse at published-corpus scale

The compact reuse survey covers all 65 individual signed benchmark ZIPs in the
pinned NIWC `Current/` corpus:

- **8,892** XCCDF rules;
- **7,084** supported automated assessments;
- **3,413** unique exact technical assessments;
- **3,671** duplicate assessment definitions avoidable;
- **51.82%** exact maintenance-unit reduction;
- **1,701** cross-benchmark exact-reuse groups;
- **5,340** assessment instances participating in cross-benchmark exact reuse.

This makes reuse a first-class architectural concern rather than a convenience
for a few closely related STIGs.

### High-fan-out examples

One exact technical assessment for limiting concurrent sessions to ten is used
by **13 different Linux benchmarks**: Amazon Linux 2023, four Ubuntu releases,
Oracle Linux 7/8/9, RHEL 7/8/9, and SLES 12/15.

Several password-complexity assessments are exact matches across **12
benchmarks**.

Windows exact reuse also persists across generations. Secure Boot, for example,
uses the same exact assessment across Windows 10, Windows 11, and Windows Server
2016/2019/2022/2025. Multiple PowerShell and audit-policy assessments have the
same six-benchmark fan-out.

A candidate format must therefore remain understandable when one assessment is
bound to many independent policy rules, not merely two.

## Rule mapping versus automation reuse

Two independent mapping signals are used:

1. identical normalized XCCDF Check Text;
2. equivalent complete normalized OVAL semantics.

Same Check Text establishes that policy rules correspond; it does not prove
their automated implementations are identical.

Equivalent complete OVAL semantics establishes technical assessment identity
under the migration model and therefore exact automation-reuse evidence.

The four-anchor corpus contains a useful control: RHEL 9 and Oracle Linux 9
"library files must be owned by root" have identical Check Text but different
OVAL filename/filter semantics. They are policy-aligned but are intentionally
not counted as exact automation reuse.

## Parameterized reuse remains a separate question

Literal abstraction identifies possible parameterized assessments, but those
groups are only review candidates.

Four-anchor upper bound:

- 1,331 instances -> 400 shapes;
- **69.95%** candidate reduction.

Full-corpus upper bound:

- 7,084 instances -> 1,593 shapes;
- **77.51%** candidate reduction.

Neither percentage is proven parameterized reuse. Paths, thresholds, registry
values, package names, users, and other literals can be policy-significant.
Typed parameterization requires review and conformance evidence.

## Architectural tensions to evaluate

The format decision is no longer "reuse versus no reuse." All three forms can
represent the same measured reuse.

The useful questions are:

- Is reuse explicit enough that reviewers can identify every affected policy?
- Is a complete resolved rule easy to inspect?
- Can policy identity and assessment identity evolve independently?
- Is shared-assessment provenance/versioning clear?
- Can tools prevent overlays from modifying technical semantics?
- Are parameter values typed and reviewable?
- Is change impact obvious in Git review?
- Can source organization be resolved into a simple, self-contained scanner
  package?
- Does the syntax faithfully accept converted SCAP 1.4 without special semantic
  exceptions?
- Does high fan-out remain manageable when one assessment serves 6, 12, or 13
  benchmarks?

## Review matrix

| Area | Combined rule + overlays | Split policy / assessment / binding | Ansible-inspired | Evidence / notes |
|---|---|---|---|---|
| Understand one resolved rule | TBD | TBD | TBD | Same converted examples |
| Understand source dependencies | TBD | TBD | TBD | Six committed reuse groups |
| DISA policy-only authoring burden | TBD | TBD | TBD | Win11 policy-only packages |
| Add automation without repeating policy | TBD | TBD | TBD | Four-anchor conversion |
| Reuse across separate STIGs | TBD | TBD | TBD | 525 four-anchor groups / 1,701 corpus groups |
| High-fan-out reuse | TBD | TBD | TBD | Up to 13 benchmarks |
| Parameterize safely | TBD | TBD | TBD | Candidates only; not yet proven |
| Prevent semantic mutation | Overlay contract required | Explicit assessment identity | Explicit assessment identity | Canonical verifier |
| Preserve independent policy identities | TBD | TBD | TBD | Mapping/binding provenance |
| Avoid duplicated assessment logic | Supported | Supported | Supported | Same measured reuse set |
| Maintain provenance/version lineage | TBD | TBD | TBD | Exact fingerprint + source provenance |
| Review shared changes in Git | TBD | TBD | TBD | High-fan-out impact |
| Convert XCCDF + OVAL faithfully | Verified on four anchors | Verified on four anchors | Verified on four anchors | Same canonical IR |
| Render complete resolved view | Native source shape | Tooling/view required | Tooling/view required | |
| Scanner package complexity | TBD | TBD | Same canonical package target | |
| Policy-only/manual scan support | Demonstrated | Demonstrated | Authoring view | |
| Long-term version management | TBD | TBD | TBD | |
| Avoid misleading runtime assumptions | N/A | N/A | Must make no-Ansible-runtime rule explicit | |

No architecture decision should be made solely because one representation is
shorter, has fewer files, or resembles a familiar tool. The decision should be
grounded in readability, provenance, safe reuse, migration fidelity,
implementation burden, and long-term maintenance at the reuse scale actually
measured in published content.
