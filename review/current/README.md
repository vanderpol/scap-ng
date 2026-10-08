# Current SCAP-NG 0.3 review

**0.3.0 is pre-alpha, pending final release validation and owner acceptance.**
This is the only current human-review entry point; historical research and
0.2.0 review pages are not competing specifications.

## Read in this order

1. [Benchmark → Rule examples](../../specification/examples/README.md):
   actual STIG policy, identifiers, remediation, and publisher Profiles.
2. [Automated and Manual Assessment examples](../../specification/examples/assessments.md):
   concise Rule → Assessment checks, modernizations, and **synthetic** result
   illustrations (not observed scanner results).
3. [Modernization review guide](REVIEW-GUIDE.md): where each production
   example lives and why unproven automatic rewrites remain fail-closed.
4. [Verified six-benchmark artifact](https://github.com/vanderpol/scap-ng/actions/runs/37849528026):
   download **`scap-ng-board-representative-review`** under *Artifacts*.
   Browse `authoring/` (RHEL 9, Oracle Linux 9, Windows 11, Windows Server
   2025, DNS, Apache), `packages/`, and `REVIEW.json`. The artifact was
   built from SCAP-NG commit `9095a1983bbd60be2bdd65655fa40f5c428cb9f9`
   and passed conversion, native 0.3 schema/semantic/graph checks,
   normalization, and compilation.

## Evidence boundary

- [The first active-0.3 full-corpus release run](https://github.com/vanderpol/scap-ng/actions/runs/37838382899)
  **succeeded** at code commit `799d083119b3d0506e552616b22e62076db8337e`,
  including signed test compilation. It accounts for 61 supported native
  benchmark packages and four explicit nonstandard `independent.sqlext`
  source blockers.
- [The follow-up full-corpus run](https://github.com/vanderpol/scap-ng/actions/runs/37846666574)
  validates later Organizational Input/result contracts at code commit
  `38ac339e7818c662dabbf100b34584c3e5fd6eb1`.
  Its outcome must be checked independently before calling 0.3 complete.
  Later commits through `9095a198` change documentation and audit tooling,
  not the content evaluation contract.
- These runs establish source-conversion and build gates, **not** live scanner
  or cross-vendor runtime equivalence. The
  [0.3 release issue](https://github.com/vanderpol/scap-ng/issues/191) and
  [full-corpus gate](https://github.com/vanderpol/scap-ng/issues/202) track
  final acceptance.

For detailed language semantics use the [draft specification](../../specification/README.md)
and [0.3 schema](../../schema/v0.3.0/README.md).
[Deferred/out-of-scope topics](../../specification/deferred-after-0.3.md)
are not normative 0.3. Published [Board votes](../../board/VOTES.md)
and the preserved [0.2 schema](../../schema/v0.2.0/README.md)
remain historical governance/evidence, not current authoring guidance.
