# Maintaining SCAP-NG

This page defines the single development/review process. The
[specification](specification/README.md) defines language meaning,
[BRANCH-MANAGEMENT.md](BRANCH-MANAGEMENT.md) defines Git operations, and
[AGENTS.md](AGENTS.md) defines agent-specific working rules.

## Core rule

**Machine-green is not human-accepted.** Schema validity, faithful source
conversion, compiler success, actual scanner execution, and OVAL Board
ratification are distinct states. Never assert one from another.

## Work and issue traceability

Every new commit **SHALL** cite a GitHub issue (`Refs #NNN` or `#NNN`).
Use an existing coherent workstream issue rather than opening trivial
issue-per-commit placeholders. Start from current `main` and follow
[trunk-based branch rules](BRANCH-MANAGEMENT.md).

For each **semantic** change, include in the issue/review packet:
the problem and objective; a small real source-backed before/after example;
the exact effect on evaluation, compatibility and provenance; rejected
alternatives; relevant OVAL/SCAP source; positive/negative boundary tests;
workflow evidence; and a dated human decision. A large generated diff is not
a review packet. Do not promote undecided research into normative pages.

## Validation ladder

1. **Focused checks** on a minimal reproducible fixture: schemas, semantic
   validators, results, converter or Self-Assertion tests as appropriate.
   Record independently justified expected behavior, especially for unknown,
   error, incomplete population and input provenance.
2. **Representative integration:** the maintained
   [six-benchmark conversion regression](.github/workflows/scap-ng-fast-conversion-regression.yml)
   covers RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025, Windows
   Server DNS, and Apache 2.4 UNIX. Validate converted authoring,
   normalization, graph references and compiled packages. A separate fast
   five-benchmark suite may exist for narrower regression work; do not
   confuse it with the Board's six-anchor review deliverable.
3. **Release checkpoint only:** the
   [65-source active-0.3 gate](.github/workflows/scap-ng-full-current-v03-release.yml)
   intentionally accounts for 61 supported candidates and four
   `independent.sqlext` blockers. It can be dispatched intentionally
   or triggered by the explicitly maintained release-trigger file.
   It **shall not** run as a routine edit/test loop.
   Do not stop an already-running full validation merely to launch another;
   queue subsequent checkpoints and verify each exact source SHA.

Never weaken semantic validation to manufacture a green run. When a new
failure occurs, isolate a minimum reproducible case, fix it, add a regression,
and rerun the appropriate gates.

## One current review and one authority per topic

- [Current review](review/current/README.md) is the sole active reviewer
  entry point. Completed checkpoints belong in `review/iterations/`;
  historical 0.2 source and schemas are retained but not rebuilt as 0.3 gates.
- [Specification](specification/README.md) states accepted normative rules.
  [Examples](specification/examples/README.md) illustrate them with short,
  production-grounded excerpts; they do not independently redefine the model.
- [Board records](board/README.md) contain decisions and votes, not a
  competing language overview. [Research](research/) and
  [deferred features](specification/deferred-after-0.3.md) remain explicitly
  non-normative until accepted.
- [CHANGELOG.md](CHANGELOG.md) records material issue-linked changes;
  [ROADMAP.md](ROADMAP.md) states only current checkpoint and future phases.
- [Human-run tools](tools/HUMAN-RUNNABLE-SCRIPTS.md) is the operator catalog.
  All repository Markdown links are checked by
  [documentation audit](tools/audit_markdown_links.py) and its workflow.

## Release and evidence discipline

A version checkpoint identifies the exact schema/source SHA, pinned legacy
source, validation runs, test artifacts and SHA-256. Store large generated
content/logs in GitHub Actions or the evidence repository instead of committing
bulk output. Do not republish expiring artifacts as permanent releases.

Semantic changes require reviewer acceptance, and distribution/publication
is distinct from that acceptance. After the owner accepts a candidate,
publish a durable versioned GitHub prerelease with compact reader-facing
content and externally linked raw engineering evidence. Historic votes,
accepted designs and release artifacts shall not be silently rewritten.
