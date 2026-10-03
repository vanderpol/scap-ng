# Write the requirement; compile its mechanics

**Experimental research, 2026-10-03.** This wave follows the owner's permission to
use a different authoring form that compiles to the current specification. It
extends [new-method research](../method-02/README.md), keeping the question about
human comprehension separate from the choice of scanner implementation.
Development research only; `review/current/` remains the sole external review
surface. No schema, converter, supported capability or policy architecture changed.

The recommendation is an optional requirement-oriented authoring language over
named Objects. Authors state what must hold, exceptions and absence behavior;
the compiler emits the current Object/State/Test graph whenever that is accurate.
Domain operations needing new execution remain separately labeled proposals.
The [existing-capability baseline](EXISTING-CAPABILITIES.md) includes SCAP 1.4 and
existing shellcommand as possible final solutions; new runtime features require
an evidenced gap. Seven selected checks already use shellcommand in enhanced
SCAP 1.4 packages, so a version upgrade and remaining complexity are separate claims.
YAML is the inspectable prototype, not the claimed readability benefit. A sentence
editor could expose the same typed operations without interpreting free prose.

## A concrete example that actually compiles

An author writes:

```yaml
protect-user-files:
  every: alice-initialization-files
  missing: allowed
  permissions_at_most:
    owner: [read, write, execute]
    group: [read]
    other: []
    special: []
```

Read this as: check every selected file; an empty selection is allowed; each file
may give the owner read/write/execute and the group read, with no other or special
permissions. It need not grant all the permitted rights. An unreadable allowed
bit does not affect this restriction. Collection failures are still failures of
observation, never permission to assume compliance. Root's analogous Test says
`missing: violation`, preserving the original distinction.

The compiler emits eight independently typed Boolean States and one native Test
with `states_match: all`, `match: all`, and `existence: optional`. **It does not
introduce a native octal mode field.** This improves the earlier method-02 design:
complete numeric-mode acquisition is unnecessary for this allowance and could
lose independent partial observations. The existing Boolean design remains intact.

Browse [author source](examples/initialization-files.author.yaml),
[compiled native source](compiled/initialization-files.assessment.yaml),
[separate source map](evidence/source-map.json), and
[synthetic diagnostic](evidence/diagnostic-demo.txt). The latter turns a failing
`other_read` State into “other read is outside the allowed permissions,” pointing
back to the author's requirement instead of requiring graph reconstruction.

This example uses two **fixed illustrative home directories**. It does not replace
the complete RHEL account discovery, Variables, Sets, Filters or directory-type
exclusion. [SV-257889](../dossiers/SV-257889.md) retains that graph, original Check
Text, exceptions and applicability. Only the permission predicate is compared
against the original XML; do not deploy the fixed example as the full STIG check.

## Evidence and practical cost

**18 new test methods and 63 existing six-state regression methods passed.**
The new tests include all 4,096 modes against the original permission State,
4,095 nontrivial allowances with four mode cases each, 65,536 eight-comparison
true/false/error/unknown combinations, and 36 two-comparison six-state cases.
Missing resources, incomplete collection, multiple matches, forbidden/missing
entities, invalid selectors, duplicate YAML keys, unsupported methods and runtime
input injection are covered. Some Tests reuse repository schema-derived control
flow; they are explicitly not an independent scanner comparison.

The author fixture has 36 lines versus 242 emitted native lines, including comments,
for the **same fixed fixture**: two Objects, sixteen States, two Tests. This is an
85% reduction in source lines, not runtime work or measured comprehension. The
compiler cost is modest: one allowance expansion, strict literal/type checking,
stable IDs and a diagnostic map. The scanner gets its existing shape; target
execution, author trials and full source-scope compilation remain unproven.

Generic schema and presentation guards pass. More substantially, the prototype
generates the deep `unix.file` schema from the reviewed mapping and validates each
Object, State and Test, then cross-node semantics and reference closure. The first
attempt omitted the automated Assessment's required `specification` metadata;
generic validation rejected it. That was a prototype omission, corrected here;
the backend schema was not relaxed. No new semantic guarantee follows from schema
validation alone.

## Continue reading or reproduce

- [Transform versus new runtime methods, across all 12 cases](COMPARISON.md).
- [Existing SCAP 1.4/shellcommand options before new features](EXISTING-CAPABILITIES.md).
- [Experimental normative semantics and supported subset](SEMANTICS.md).
- [Versioned yes/no decision candidates](DECISIONS.md).
- [Source/version/provenance ledger](PROVENANCE.md).
- [Exact checks, hashes and limits](evidence/verification.json).
- [Resumption handoff](HANDOFF.md).

From repository root, with the configured Python 3.12 environment:

```bash
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/scap-ng/bin/python research/assessment-simplification/transform-03/verify.py
```

The command regenerates the fixed native example and source map, runs semantic
tests, deep capability validation (inside those tests), generic schema checks,
the presentation guard, diagnostic demonstration and existing result regressions.
It writes actual logs and exit statuses, and exits nonzero if a check fails. It
does not collect files or run inherited sample commands. This standalone compiler
experiment is not a general-purpose maintained converter; promotion would require
a bounded production task under repository-level tooling.
