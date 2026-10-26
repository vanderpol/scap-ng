# SCAP-NG 0.4 engineering execution ledger

Authority: [owner directive](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271).
This ledger records bounded engineering outcomes; it grants no production-release,
signing/trust or scanner acceptance authority. No paid capacity is purchased or
assumed available. No Goal/schedule/auto-resume state is claimed from unobserved UI.

| Checkpoint | BASE_SHA / RESULT_SHA | IMPLEMENTED | SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | REGRESSIONS / TESTS / CI | PERF / NEXT |
| --- | --- | --- | --- | --- | --- |
| Architecture acceptance — complete | `284705ee6` / `840242a14` | Common Set proof; integer GT/GTE/LTE; public validation profiler | 87 / 0 / 204 of 291 | Zero; 3,008 tests, one unchanged skip; all five implementation checks PASS | Validation branching dominates; no optimization claimed. GO audit-policy source increment. |
| Audit policy — complete | `02b50ec57` / `ad6df4f71` | Approved implicit-system source; audit enum/field proof | 130 / 0 / 161 of 291 | Zero; 3,012 tests, one unchanged skip; all five implementation checks PASS | 262-doc validation 11.532 s (32.178 s profiled), no speedup claim. GO closed-domain Registry selector proof. |

The [authoring acceptance checkpoint](v04-direct-authoring-acceptance.md) is complete:
`9c48e684f` → `da227c462`, with examples published in `1f8098a95`.
Assessment-local sharing, safe YAML presentation and capability inheritance are
verified: 95 inline Test Objects, one named Object/seven Test references, 71
no-Object Tests and 101 compact Registry Object sites. Coverage remains
130 source-proved / zero compiled-unproved / 161 blocked. There were no avoidable
shared declarations in this pin; controlled source-backed graphs establish the
corrected policy. Mandatory regressions: 3,021 tests, zero failures/errors, one
unchanged skip; final style checks 9/9. All four triggered implementation CI checks
and both example-publication checks passed. No speedup/coverage gain is claimed.
The one final issue-comment attempt returned `Post "https://api.github.com/graphql": Forbidden`;
the linked committed report is the fallback, with no retry.

[Architecture packet and evidence](v04-architecture-acceptance.md) contains exact
SHAs, source hashes, proof cases and CI links. [Audit-policy packet](v04-audit-policy-direct.md)
records its completed increment.

The [closed-domain Registry hive checkpoint](v04-direct-registry-hive.md) is now
complete: `cef742119` → `2c850a36b`. All 19 additional original Rule closures
independently prove and compile; the 49-pair original Object/Item enum relation
is explicit and source tokens remain in provenance. Current coverage is
**149 proved / zero compiled-unproved / 142 blocked** of 291. All prior 130 program
hashes are unchanged. Mandatory regressions: **3,026 tests**, zero failures/errors,
one unchanged skip; all five exact implementation-head workflows PASS. Authoring
remains local by default: 114 inline Test Objects, one named Object/seven references,
71 intentional no-Object Tests and 120 compact Registry Object sites. Public gates
validate 300 JSON/300 YAML documents and independently verify 149 programs.
Empty/dynamic hives, State-level enum comparator changes and extra `all_exist`
normalizations remain blocked. No unmatched-workload speedup is claimed.

The [user-rights checkpoint](v04-direct-userright.md) is complete:
`a2ce5fd94` → `c80f84c0a`, with actual examples in `718b10df1`.
Of 39 original candidate closures, 34 independently prove and compile; five
remain atomically blocked by WMI record dependencies. Global coverage advances
to **183 proved / zero compiled-unproved / 108 blocked** of 291; all prior 149
program hashes are preserved. **3,032** maintained tests pass with zero
failures/errors and one unchanged skip; all five implementation-head workflows
PASS. The published Variable/Filter case retains original `var_check: all` as
`value_match: every`; it is never changed to match an apparent policy intent.
Public gates validate 368 JSON/368 YAML documents and verify 183 programs.
Authoring: 147 inline Test Objects, nine shared references to two named Objects,
71 intentional no-Object Tests and 120 compact Registry Object sites. No schema,
production converter/compiler or release gate changed. One issue-comment attempt
returned `Post "https://api.github.com/graphql": Forbidden`; no retry was made.

The [WMI record checkpoint](v04-direct-wmi-records.md) is complete:
`f9e3b0978` → `4087e4309`, with [actual WMI examples](../examples/direct-wmi/README.md)
published in `e5bd741f9`. All **18** supported WMI closures independently prove
and compile, completing all **39** user-rights candidates. Eight WMI closures
remain blocked by unsupported capabilities or unapproved `all_exist`. Current
coverage is **201 proved / zero compiled-unproved / 90 blocked** of 291; all
183 prior program hashes are unchanged. **3,037 tests**, zero failures/errors,
one unchanged skip; all five exact implementation-head hosted workflows PASS.
Public paired gates validate 404 JSON/404 YAML documents and independently verify
201 programs. Authoring remains local by default: 165 inline Test Objects, 36
references to 12 genuinely shared Objects, 71 no-Object Tests and 120 compact
Registry Object sites. Named record boundaries, original datatype distinctions
and missing-member errors remain intact. No schema or release-gate changes.

The [password/lockout-policy checkpoint](v04-direct-system-policy.md) is complete:
`e5bd741f9` → `88eaa0133` → corrected `740bc8039`. All seven password-policy and
three lockout-policy original closures prove and compile; coverage advances to
**211 proved / zero compiled-unproved / 80 blocked**. All prior 201 program hashes
are unchanged. Public gates validate 424 JSON/424 YAML documents and verify 211
programs. Initial local mandatory tests: **3,043**, zero failures/errors, one
unchanged skip; corrected targeted tests 6/6; all five exact corrected-head hosted
checks PASS. Internal review caught and corrected required fixed datatype
attributes being mistaken for defaults; both readers now reject omissions. The
actual original source already has explicit valid attributes, so all 424 generated
documents are unchanged. No source normalization or schema modification.

The [Windows service checkpoint](v04-direct-service.md) is complete:
`740bc8039` → `fefbcc3a9`. Both actual source closures prove and compile; coverage
advances to **213 proved / zero compiled-unproved / 78 blocked**. All previous
211 program hashes are unchanged. Public gates validate 428 JSON/428 YAML
documents and independently verify 213 programs. **3,047** maintained tests,
zero failures/errors, one existing skip; 52 related tests and 15 final focused
tests pass. All five exact implementation-head hosted workflows PASS. Source
selector case semantics, API enum names and relative-COMPLEMENT/Filter boundaries
remain exact. Authoring: 167 inline Test Objects, 36 references to 12 genuinely
shared Objects, 85 no-Object Tests, 120 compact Registry Objects; deprecated keys
zero. The final trace qualifies unsupported record constructs accurately.

The [OpenSSH text-file checkpoint](v04-direct-textfile.md) is complete:
`ca1ee36f3` → `4adfdbad9`; [actual YAML/JSON](../examples/direct-textfile/README.md)
is pinned in `fd66890da`. All seven original candidate closures prove and compile;
coverage advances to **220 proved / zero compiled-unproved / 71 blocked**. All
213 previous program hashes remain unchanged. Public gates validate 442 JSON/442
YAML documents and independently verify 220 programs. **3,052** maintained tests,
zero failures/errors, one existing skip; 57 related tests pass; all five exact
implementation-head workflows PASS. Regex flags/defaults, item creation,
filesystem scope, capture types and original patterns remain exact. Unsupported
Windows-view/traversal attributes fail closed. Authoring: 174 inline Test Objects,
36 references to 12 genuinely shared Objects, 85 no-Object Tests and 120 compact
Registry Objects; deprecated grammar zero.

The [file-effective-rights checkpoint](v04-direct-file-rights.md) is complete:
`95ce4e721` → `6d7fdc039`; [actual Set/Filter/Variable samples](../examples/direct-file-rights/README.md)
are pinned in `97a151f08`. All eight original closures prove and compile;
coverage advances to **228 proved / zero compiled-unproved / 63 blocked**. All
220 previous program hashes remain unchanged. Public gates validate 458 JSON/458
YAML documents and independently verify 228 programs. **3,057** maintained tests,
zero failures/errors, one existing skip; 62 related tests and 20 final publication
checks pass. All five exact implementation-head workflows PASS. SID selection,
permission Booleans, Variables, path forms, Filters and relative-complement
boundaries remain exact. Unsupported group expansion/view/traversal/nilled
selection stays blocked. Authoring: 200 inline Test Objects, 39 references to
15 genuinely shared Objects, 85 no-Object Tests, 127 compact Registry sites;
deprecated grammar zero. The sample helper now handles complex-only selections
and distinct roles without inventing ordinary examples or repeating a Rule.

The [command collection-error checkpoint](v04-direct-command-behaviors.md) is complete:
`083ec0e3e` → `fab566b2a`; [actual error-flag YAML/JSON](../examples/direct-command-behaviors/README.md)
is pinned in `b9e6a7af3`. All ten actual closures prove and compile; coverage is
**238 proved / zero compiled-unproved / 53 blocked**. All 228 previous program
hashes remain unchanged. Public gates validate 478 JSON/478 YAML documents and
verify 238 programs. **3,061** maintained tests, zero failures/errors, one existing
skip; 66 related tests pass; all five exact implementation-head workflows PASS.
True error flags remain collection controls; neighboring default flags stay false.
Historical fixed case windows-14/SV-278146 now proves without changing its fixture
or old manifest; the original reader remains unverifiable and a false-flag mutant
mismatches. The 883-Assessment ledger is unchanged. Authoring: 211 inline Test
Objects, 39 references to 15 shared Objects, 85 no-Object Tests, 127 compact Registry
sites; deprecated grammar zero.

The next bounded objective is cmdlet nullable/input-record source proof. Seven
original candidates include two WMI dependencies. The approved capability-specific
select parameter, null module constraints, selection_match and value_match scopes,
record results and unsupported wildcards must remain distinct from generic
wrappers or Test requirements. Deprecated scalar WMI remains blocked; it is not
silently aliased to record-producing wmi57.
These are queued engineering objectives, not
observed scheduled or automatically resumed jobs. Existing historical evidence and mandatory gates remain
intact. Issue commenting was previously Forbidden; committed reports are the
authorized GitHub handoff if that restriction persists.
