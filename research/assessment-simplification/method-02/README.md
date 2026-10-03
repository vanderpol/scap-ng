# New assessment methods: Objects and direct requirements

**Experimental research; no accepted language/schema/converter change.**

Owner clarification, 2026-10-03: discover new, equally accurate ways to perform
the compliance check, imagining a new assessment specification an ordinary author
can understand. OVAL concepts may help; the author should not need OVAL machinery.
The previous [refinement](../refinement-01/README.md) mainly reduced scaffolding
and preserved migration contracts. It remains useful evidence but does not meet
this clarified goal by itself.

Verified receiving checkout: clean `main`,
`d510a92b47507f2d8f5a3ad2d610363cdf487f35`, equal to upstream main.
Current architecture, requirements, glossary, transition records and previous
source/handoff evidence were reread. This direction changes research emphasis,
not the accepted Benchmark → Rule → Assessment architecture or authoring grammar.

## What an author would write

Name the **Objects**, then say what each must satisfy. Let domain-aware operations
answer the security question directly. Keep Test, Object, State, Variable and
Item meanings where appropriate. Here `require` is an inline State/predicate;
`every` is a Test quantifier with the current Item kept in scope.

```yaml
# EXPERIMENTAL excerpt; Object selection and exceptions are in the full example.
tests:
  DNSSEC records:
    every: zones
    as: zone
    empty: allowed
    require:
      signed: {equals: true}
      records: {include: [RRSIG, DNSKEY, NSEC3]}
```

Read it as: "Every selected zone must be signed and contain these three record
types." A DNS query should provide facts with identity/status, not a compliant
Boolean. The author writes neither commands nor counts projected through Variables.
The [full example](examples/dns.yaml) keeps the server-wide all-integrated/empty
exception. Classified-network and platform applicability stay separate.

A different permission method uses a **set of allowed rights**:

```yaml
require:
  permissions:
    at_most:
      owner: [read, write, execute]
      group: [read]
      other: []
      special: []
```

"At most" permits fewer rights; it does not demand every listed right. The
engine checks set containment, not numeric mode ordering. This reproduces the
sample's eight forbidden-bit predicates for all 4,096 Unix modes, including
special bits. It rejects 0604 because `other.read` is outside the allowance.
See [home files](examples/home-files.yaml); source selection/traversal remains
explicit and is **not implemented** by this predicate experiment.

For Apache, an author names settings and presence:

```yaml
require:
  main:
    settings:
      KeepAlive: {equals: 'On', presence: required}
      MaxKeepAliveRequests: {at_least: 100, presence: required}
```

The engine examines explicit occurrences in that installation's main group.
Off then On fails an all-occurrence requirement; a default does not prove an
explicit declaration. The [full example](examples/apache.yaml) also checks the
source's optional other-loaded group. A different effective-setting method is
possible, but is not equivalent to these explicit checks.

For audit, ask a **coverage question**, rather than match 24 text patterns:

```yaml
source: loaded
architectures: [b32, b64]
syscalls: [setxattr, fsetxattr, lsetxattr, removexattr, fremovexattr, lremovexattr]
actors: [root-logins, user-logins]
```

"Do configured exit rules cover every listed operation for these architectures
and login identities?" The engine reasons over parsed predicates and their
order. It can combine two disjoint user-ID ranges, detect a gap and account for
a preceding never rule. This is a different assessment method, not expansion into
24 OVAL Tests. It checks configured exit-rule coverage, not delivery of audit
logs or all global audit/task/exclusion behavior.

## Evidence and honest boundaries

**34 new test methods passed:** exhaustive 4,096-mode comparison against the
pinned original permission State; 256 two-zone combinations; 36 Apache occurrence
cases; 500 generated audit programs checked against independent exhaustive small-
domain evaluation; missing/partial/error/unknown, duplicate identity, empty,
boundary, ordering and unsupported-condition cases. Subcases are not unittest
methods. [Logs](evidence/test-results.txt), [machine-readable verification](evidence/verification.json).

Permission-predicate equivalence is established for supplied valid mode values.
Apache/DNS predicates agree with independently written intent formulas over
supplied typed observations. Audit interval reasoning agrees within its bounded
grammar/domain model. **None establishes full source scanner equivalence.**

This session did not run the earlier 114 methods again: their results remain in
refinement-01. No target systems, kernel/auditctl execution, Windows queries,
Apache acquisition, source-plan execution, complete Self-Assertion corpus or
author usability trial was run. New examples intentionally do not target the
accepted schema. No scanner or converter code changed.

Read [method comparison and all-case application](METHODS.md),
[execution/accuracy contract](SEMANTICS.md),
[unpublished yes/no candidates](DECISIONS.md), and [handoff](HANDOFF.md).

## Reproduce

From the repository root with the configured Python3.12 environment:

```bash
source /workspace/.venvs/scap-ng/bin/activate
export PYTHONDONTWRITEBYTECODE=1
python -m unittest discover -s research/assessment-simplification/method-02 -p test_methods.py -v
python research/assessment-simplification/method-02/demo.py
```

The [demo evidence](evidence/demo.json) contains four synthetic failures with
readable explanations and witnesses/gaps. It is not a target scan. The grammar
experiment consumes externally supplied typed snapshots; it does not implement
Object source plans, package compilation or production syntax parsing.

## Sources and provenance

The same five packages and complete 12-case original Check Text/OVAL closures
remain pinned in the [parent study](../README.md). Source reproduction/hashes are
in [refinement-01](../refinement-01/evidence/source-reproduction.json); no new
production platform or source substitution was needed. Permission evidence uses
RHEL9 V2R9 enhancedV13, SV-257889; audit uses SV-258179; DNS uses V2R3 enhancedV8,
SV-259350; Apache server uses V3R2 enhancedV2, SV-214228. DNS's source Benchmark is
Server2022, not asserted to be a Server2025-specific revision.

[Pinned upstream audit documentation](evidence/audit-reference.json) confirms
first-match ordering and arch-before-syscall-name lookup. It is current upstream
documentation, not proof of the RHEL target's kernel/audit version. Apache/DNS
official references from the preceding refinement remain relevant.

Inherited: pinned requirement/source facts, existing research and current project
contracts. Adapted: new examples guided by original policy predicates. Common:
new requirement evaluator, interval coverage model and independent synthetic
oracles. Evidence/Audit: owner correction, comparisons, counterexamples, logs and
limitations. No external scanner implementation copied. Legacy provenance stays
outside executable examples. No capability is retired; effectively deprecated
Tests remain unsupported.
