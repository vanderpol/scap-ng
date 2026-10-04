# UNIX file: explain the outcome from concrete evidence

Compare [selected source](../sources/unix-file.xml), [Assessment](../content/unix-file.assessment.yaml),
[provenance](../provenance/unix-file.json), [cases](../expected/unix-file.json), and
the [linked 0.2.0 result](../expected/unix-file.result-set.json).
Human status: **pending-review**. Provenance: Inherited selected criterion.

Scope: criterion `oval:navy.navwar.niwcatlantic.scc.test:tst:9` within Definition
`oval:navy.navwar.niwcatlantic.scc.test:def:1`, revision 3. This is not the entire
UNIX file Self-Assertion Definition and not a hardening policy.

Before: `tst:9 → obj:9 → ste:9`. After: `test-path → file → path`.
The reviewed `filepath → full_path` mapping preserves the exact path
`/opt/support/txt/txtfile/build.win32.txt`. Native `check_existence: some` retains
`at_least_one_exists`; `check: all` retains all-Item State satisfaction.
The Object selects one full path. There is no traversal or shellcommand.

Why true in the supplied result:

1. Object `file` reports complete collection and Item `source-file` exists.
2. Its typed `full_path` observation equals the State's authored path.
3. Existence succeeds and every collected Item satisfies the State.
4. The expression consumes `test-path`; logical, population, and evidence
   completeness are explicitly recorded as true.

The result links the Assessment identity/revision, execution, Test, Object, Item,
State, compared typed values, field-use lineage and synthetic target provenance.
Truth/comparison evidence was specified independently; the existing helper
serialized the scheduling envelope. The snapshot is not the sole oracle.

Confirmed absence gives false before State comparison. Permission failure gives
error; not-collected gives unknown. Incomplete population plus one matching Item
does not establish `check: all`, so remains unknown. An explicit platform N/A
collection status gives not_applicable. No collector was run; these are synthetic
collection-control-flow cases, not filesystem or permission acquisition proof.
