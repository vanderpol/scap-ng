# Native link resolution with negated existence leaves

Status: **pending-review**. [Native Assessment](../content/symlink-resolution.assessment.yaml),
[mechanical conversion](../mechanical/symlink-resolution.assessment.yaml),
[source closure](../sources/symlink-resolution.xml),
[provenance](../provenance/symlink-resolution.json),
[independent synthetic cases](../expected/symlink-resolution.json).

Complete Self-Assertion `unix/unix-def_symlink_test.xml`, Definition
`oval:navy.navwar.niwcatlantic.scc.unix.test:def:1`. Definition 2, containing
additional erroneous-link cases, is outside this selected complete Definition.

| Source Test / Object | Native role | Required source result |
| --- | --- | --- |
| `tst:1` / `obj:1` | `test-link-chain-exists` / `link-chain-object` | true: a resolvable chain is a symlink population |
| `tst:3` / `obj:3` | `test-regular-file-is-link` / `regular-file-object` | false, then negated: a regular file is not a symlink Item |
| `tst:5` / `obj:5` | `test-missing-link-exists` / `missing-link-object` | false, then negated: the path does not exist |
| `tst:6` / `obj:6` / `ste:6` | `test-working-link-target` / `working-link-object` / `canonical-target-state` | true: canonical path equals the source target |

The original criteria are `AND(tst:1, NOT tst:3, NOT tst:5, tst:6)`.
The first three Tests have **no State**; existence is meaningful without a
comparison. Only the final Test compares the resolved canonical path to
`/opt/support/symlinks/symlinks_dir1/targetfile.txt`.

On the independently described positive fixture, Test results are
`true, false, false, true`. Both negations become `true`, producing Assessment
`true`. A wrong final target or missing working link produces `false`. An error
collecting the chain propagates `error`; an uncollected chain propagates `unknown`
when the remaining criteria are true. A file must not be fabricated as an existing
symlink Item merely because the regular file itself exists.

The native file replaces generated placeholder/truncated labels and source
comments with meaningful local identities and titles. Exact original IDs/comments
remain separately traceable. The mechanical file receives the same stable ID
plan, and native title refinement preserves the complete executable graph.

All Items and collection flags are synthetic. The helper does not resolve links,
inspect real files, or prove broken/circular-link acquisition behavior. Resolution
belongs to the scanner-native `unix.symlink` collector; shell filesystem searches
are not used. This example preserves the source's meaningful dependency graph
without recreating XML serialization layers.
