# Assessment simplification research

**Status:** experimental research only. Nothing in this tree changes the accepted SCAP-NG schema, converter, scanner, or Board decisions unless promoted through the normal specification/review process.

This work explores ways to make accurate assessments easier for humans to author and understand while preserving required semantics and explicit error/completeness behavior.

## Research progression

| Phase | Focus | Durable outputs |
| --- | --- | --- |
| Initial study | Representative complex STIG/OVAL cases and simplification opportunities | [findings](FINDINGS.md), [comparison](COMPARISON.md), [feature inventory](FEATURES.md), [decision candidates](DECISIONS.md), [case dossiers](dossiers/) |
| [refinement-01](refinement-01/README.md) | Finite-table authoring, acquisition contracts, adversarial refinements | samples, contracts, backlog, evidence, decision candidates |
| [method-02](method-02/README.md) | Requirement-oriented methods over typed Objects | methods, semantics, examples/evidence, decision candidates |
| [transform-03](transform-03/README.md) | Compile readable requirements to established native Assessment mechanics where semantics are exact | comparison, semantics, provenance, capability analysis, decision candidates |
| [concepts-04](concepts-04/README.md) | Broader authoring/assessment concepts | concept review and decision candidates |
| [requirements-05](requirements-05/README.md) | Full RHEL 9 + Windows Server 2025 Check Text reading | reading notes, recommendations, evidence, decision candidates |
| [editor-06](editor-06/README.md) | Open authoring workbench/editor direction | full-coverage obligations, implementation options, decision candidates |
| [foreach-07](foreach-07/README.md) | Post-conversion iteration modernization with provable OVAL equivalence | collection-vs-evaluation semantics, automatic rewrite boundary, rejection rules, conformance plan |
| [authoring-language-08](authoring-language-08/OVAL-USAGE-CENSUS-2026-10-06.md) | Production OVAL feature/locality census | feature frequencies, reuse/locality evidence, coverage implications |
| [ansible-authoring-09](ansible-authoring-09/README.md) | Research-only Ansible-inspired authoring sketches | RHEL/Windows examples, manual automation review, organizational-input sketches |
| [conditional-10](conditional-10/README.md) | Conditional-shaped OVAL Boolean trees | branch-shape census, six-state caveats, applicability/case research |
| [locality-11](locality-11/README.md) | Inline private Object/State layout over the existing semantic model | 20-rule examples, full RHEL/Server 2025 census, structural round-trip evidence |
| [residual-patterns-12](residual-patterns-12/README.md) | Recurring residual complexity after known simplification opportunities | RHEL/Windows motif census, prioritized modernization/capability candidates |
| [fstab-13](fstab-13/README.md) | Typed persistent Linux mount configuration | 23-rule `/etc/fstab` census, OVAL 5.12.3 boundary, before/after example, fail-closed proof requirements |

The 12 case dossiers preserve source-specific analysis and are intentionally separate records rather than repeated project-status documentation.

For current SCAP-NG authority use [the specification](../../specification/README.md), [CURRENT-DESIGN](../iterations/003/design/CURRENT-DESIGN.md), and [the Board review page](../../board/README.md). Research success does not imply runtime equivalence, feature adoption, or Board approval.
