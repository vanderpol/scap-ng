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
SHAs, source hashes, proof cases and CI links. [Audit-policy packet](v04-audit-policy-direct.md) records the next completed
increment. The next bounded objective is original closed-domain Registry hive
selection equivalence (19 candidate Rules), with whole-closure proof, error
evidence, native enum contract and negative tests required before admission.
SID/user-right (39) and WMI (26) remain ranked source censuses; counts overlap
and never constitute admission. These are queued engineering objectives, not
observed scheduled or automatically resumed jobs. Existing historical evidence and mandatory gates remain
intact. Issue commenting was previously Forbidden; committed reports are the
authorized GitHub handoff if that restriction persists.
