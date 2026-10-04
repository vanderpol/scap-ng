# Converter-first Board pilot handoff — stop for human review

Date: 2026-10-04. Status: **pending-review**. Six mechanically converted review
cases, plus four earlier supporting seeds retained separately. All ten native
files remain pending; Codex accepts none of them.

Start: `/workspace/scap-ng`, clean `main`,
`345d8de7436adbba15cf0fe546684dbc4ba8ef5d`. Frozen technical SHA:
`7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`. Existing checkout and later maintenance
commits were kept; no reset, clone or alternate SCAP-NG repository was created.
The final publication SHA is supplied in the user report and exact-commit CI
receipt. `git log` identifies this handoff's commit without a self-referential SHA.

Entry points: [README](README.md), [manifest](manifest.json),
[conversion plan](conversion-plan.json), [coverage](coverage.json),
[validation](validation.md), [findings](questions.md).
The next action is human review of these six cases, not the next conversion batch.

Preflight read root AGENTS, BRANCH-MANAGEMENT, MAINTAINING, START-HERE,
CURRENT-DESIGN, repository map/policy, versioned schema/capability documentation,
Board checkpoint/sample instructions, maintained content-development task/handoff,
October 4 freeze record, requirements index, terminology/glossary, Assessment
specification and current provenance/conversion references. Existing test-content
findings and Issues #50/#128/#131 scope were reviewed in this session; historical
manual output was not treated as proof of the current conversion path.

Pinned Self-Assertion `e3538595c5083b9c34d937a81d319234df9bbfaa` is accessible;
local checkout `/workspace/scratch/self-assertion-e353` and GitHub commit API agree.
The adapter verifies original whole-file hashes and complete extracted closures.
Source tree SHA: `d0b680aa781cde9e55ad8778b71ee82da37ebab3`.

Current work replaces the earlier manual family/file/registry transcriptions with
actual converter-generated native content, retaining their meaningful identities
and independent oracle cases. Directory filtering, WMI records and symlink criteria
are added. Four previous constant/concat/owner-filter/dependency examples remain
supporting seeds, not mechanically converted successes. No preserved research or
source identity was deleted.

The adapter calls the existing lower/roundtrip/align/mapping libraries. It does
not reimplement source predicates or add a converter. UNIX file and registry use
explicit case-scoped existing mapping calls; their automatic readiness remains
unchanged. Local presentation names are keyed by exact source IDs. Mechanical and
native files differ only in titles and supported Constant literal presentation.
The exact pipeline/components, paths, scope and crosswalks are recorded durably.

There are 31 independently reasoned primary-case outcomes and 17 supporting
outcomes, including native edge variants. The bounded helper handles correlated
records in addition to the previous scalar/Variable/Set slice; missing expected
record fields follow the inherited OVAL error rule. It acquires nothing. The
linked UNIX result remains a source-aware evidence example. Green schemas,
roundtrips or model checks are not a claim of independent scanner equivalence.

Four minimal reproducer groups remain under `tests/focused-regressions/board-pilot/`:
binary/Boolean source disagreement, direct-Variable converter limitation, native
Variable cycle missing a shared diagnostic, and the new uncommented-State naming
limitation. Directory-filter executable/comment inconsistency is independently
reviewable in the already minimal source closure. No schema semantics were changed.

Validation commands are in validation.md. Both platform CI jobs additionally
checkout the pinned Self-Assertion revision, reproduce only these six conversions,
check committed bytes and run focused regression tests. No 65-benchmark workflow
was launched. Smoke/fast-five regression do not expand this pilot's source scope.

If interrupted before publication, run the two focused test modules and
`convert_board_pilot_v02.py --source-root <pinned-checkout> --check`, verify manifest
hashes and the intended diff, commit/push on main per branch policy, then await the
Ubuntu/Windows contract, smoke and fast-five results. Do not recreate source oracles
from implementation output. Do not change the frozen schema to fix a fixture.

After human acceptance only, a sensible next bounded task is the direct-Variable
converter gap plus source-backed Object-component/function chains and directional
Set difference. That work is not authorized by this handoff. The immediate next
step remains review, with no editor or broad corpus conversion.

History: initial manual/native pilot started at `6ba41d4e9e34a88ced8d930d9f3126738350b65d`
and appeared in `d720d2c4103450f48574bf7f8adf2f2539cdfb68`. Owner feedback produced
meaningful local identities in `345d8de7436adbba15cf0fe546684dbc4ba8ef5d`; the present
converter-first task starts from that preserved result. Earlier validation is
historical evidence, not certification of this new adapter.
