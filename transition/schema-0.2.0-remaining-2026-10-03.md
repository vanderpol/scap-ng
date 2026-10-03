# 0.2.0 remaining work excluding ESX — 2026-10-03

Owner direction at 18:50 America/New_York: assume ESX is out of scope for now.
Baseline inspected: main 9c729604509e80c7e66bc663a668ab9152fd8ce9.
This is a working-draft stabilization checklist, not a stable release declaration.

## Implemented draft foundation

Conditional expressions, explicit N/A/intrinsic applicability, dependency packaging
and execution traces; optional readable Item names/locators; reported_elements;
canonical Assessment Results; all/consumed Item materialization and verified
observation imports; unsigned Scan/Benchmark/Rule/Assessment result-package linkage.
PRs #129/#130/#132/#134/#135/#136 are merged. These provide representation,
controlled scheduling and integrity evidence; they are not a complete scanner.

## Remaining bounded work

1. Resolve and document direct variable.value zero-value execution behavior with
   source-backed expected results. Distinguish correctly computed zero values,
   empty strings, resolution failures, Test existence and quantifier semantics.
2. Resolve native authored literal/datatype/operation validation boundaries,
   beginning with Boolean strings versus Boolean JSON values. The current issue
   record explicitly notes that a boolean State can accept the string "false";
   do not infer runtime comparator behavior from schema acceptance. Add focused
   valid/invalid and distinguishing cases without weakening 5.12.3 baseline.
3. Review the two remaining in-scope new OVAL 6.0 capabilities:
   kubernetes.kubectl and kubernetes.kubepsp. Specify target/resource/query/record
   semantics, version prerequisites, statuses and native binding validation.
   #137's dormant upstream binding assertions must not be inherited. Preserve
   source bytes and record source defects separately. Adopt with focused fixtures
   or explicitly defer with rationale; unresolved adoption cannot be hidden.
4. Reconcile current schemas, normative shared Markdown, capability references,
   implementation and examples. Several dated guides still list features already
   implemented as remaining work. Establish exact version inheritance and a
   portable feature-to-test coverage/acceptance inventory for the post-checkpoint
   Codex expansion. Complete exhaustive corpus/catalog expansion remains #128;
   it is not a reason to postpone declaring a bounded, honest draft checkpoint.
5. Run the final applicable regression, schema, source/reference, compiler/result
   integration and preservation gates on one pinned commit, including Windows and
   Linux CI. Preserve stable 0.1.0 behavior and test the maintained migration
   paths at their supported versions. Record exact evidence, unresolved/deferred
   items and the ready-to-paste bounded Codex content-expansion task.

## Explicit exclusions and limitations

ESX is deferred pending original-implementer guidance. Four ESX draft mappings
already merged through #140/#141 remain provisional; do not delete them or
retroactively claim they were finalized. Five further drafts are isolated at
hold-esx-upstream-guidance-20261003 and are not merged release coverage.

Automatic conditional normalization is not planned (#126). Live acquisition,
a complete reference scanner, exhaustive vendor/target conformance, full
capability documentation/content expansion and signed-result trust profiles
are separate workstreams. The current package is explicitly unsigned, not
authenticated. Record these limits in the final draft checkpoint; do not treat
them as secretly completed or silently change their future project requirements.

#128/#131/#125 are broader than this bounded draft checkpoint and may remain
open with traceable dispositions. Do not equate issue-open status with missing
implementation of every item originally listed.

Provenance: owner scope correction; Evidence/Audit of schema/v0.2.0/README.md,
latest transition checkpoints, capability references, and live issue/PR records.
