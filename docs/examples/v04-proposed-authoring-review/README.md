# SCAP-NG 0.4.0 — 40 proposed human-authoring examples

**Proposed authoring presentation; October 30, 2026; NOT a release.**

**Start here to review the proposed form**, not the older as-generated
[40-Rule audit](../v04-expanded-authoring-review/README.md).
These 20 Windows 11 and 20 RHEL 9 pairs use a Test-wide
`require.field_requirement` wherever comparison-bearing scalar fields
are safely traceable. Field pairs remain local only as genuine overrides.
A source-pinned one-State Windows Registry AND is a single `fields` mapping.

Some Item-presence/record-absence cases do not have a meaningful
field-comparison default. Boolean group boundaries and record aggregation
are deliberately preserved where a source-justified rewrite is unavailable.
**Record member fields are a separate current-schema boundary**:
their explicit per-member value policies remain until record-scope
inheritance is designed and accepted. They have not been silently folded
into the Test-wide scalar policy.
No datatype is inferred or discarded in this review. The current
schema still requires Assessment-root `purpose` and long logical IDs;
those separately approved authoring cleanups have **not** been
silently applied to these examples.

**Verification boundary:** 84 YAML documents validated against the current
0.4.0 schema; two 20-Rule excerpt packages compiled separately. This does
**not** reprove OVAL semantics, scanner evaluation, source-to-source
equivalence, publisher applicability, or six-state behavior.
**NOT SCANNER-VERIFIED — RESULT UNAVAILABLE.**
The sample Benchmarks are incomplete review wrappers with placeholder
applicability and deliberately omitted full Profiles/manual Rules.

All Rule YAML is byte-identical to the source-pinned as-generated gallery;
Assessment edits have SHA256 provenance and an exact preimage in
[the edit receipt](REVIEW-RECEIPT.json). No immutable 65-stream artifact
or original proof baseline was changed. Track schema/converter standardization
in [#264](https://github.com/vanderpol/scap-ng/issues/264) and content
completion in [#265](https://github.com/vanderpol/scap-ng/issues/265).
**32 Assessments changed.** The unchanged Assessments check only
whether Items exist or do not exist; they contain no fields to match,
so adding a field policy to them would be incorrect.

## Windows 11 — 20 proposed-format pairs

[Review Benchmark](ms_windows_11/benchmark.yaml) · [Applicability placeholder](ms_windows_11/applicability.yaml)

| Rule | Proposed Assessment | Policy edits | Original generated |
| --- | --- | --- | --- |
| [SV-253475](ms_windows_11/rules/SV-253475.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253475.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253475.automated.yaml) |
| [SV-253276](ms_windows_11/rules/SV-253276.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253276.automated.yaml) | Item presence only; unchanged | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253276.automated.yaml) |
| [SV-253433](ms_windows_11/rules/SV-253433.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253433.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253433.automated.yaml) |
| [SV-253363](ms_windows_11/rules/SV-253363.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253363.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253363.automated.yaml) |
| [SV-268318](ms_windows_11/rules/SV-268318.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-268318.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-268318.automated.yaml) |
| [SV-253435](ms_windows_11/rules/SV-253435.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253435.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253435.automated.yaml) |
| [SV-253340](ms_windows_11/rules/SV-253340.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253340.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253340.automated.yaml) |
| [SV-253298](ms_windows_11/rules/SV-253298.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253298.automated.yaml) | 2 Tests refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253298.automated.yaml) |
| [SV-253491](ms_windows_11/rules/SV-253491.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253491.automated.yaml) | 4 Tests refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253491.automated.yaml) |
| [SV-253293](ms_windows_11/rules/SV-253293.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253293.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253293.automated.yaml) |
| [SV-253302](ms_windows_11/rules/SV-253302.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253302.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253302.automated.yaml) |
| [SV-253308](ms_windows_11/rules/SV-253308.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253308.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253308.automated.yaml) |
| [SV-253265](ms_windows_11/rules/SV-253265.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253265.automated.yaml) | Item presence only; unchanged | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253265.automated.yaml) |
| [SV-253479](ms_windows_11/rules/SV-253479.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253479.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253479.automated.yaml) |
| [SV-253301](ms_windows_11/rules/SV-253301.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253301.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253301.automated.yaml) |
| [SV-253257](ms_windows_11/rules/SV-253257.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253257.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253257.automated.yaml) |
| [SV-253273](ms_windows_11/rules/SV-253273.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253273.automated.yaml) | Item presence only; unchanged | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253273.automated.yaml) |
| [SV-253306](ms_windows_11/rules/SV-253306.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253306.automated.yaml) | 2 Tests refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253306.automated.yaml) |
| [SV-253297](ms_windows_11/rules/SV-253297.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253297.automated.yaml) | 3 Tests refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253297.automated.yaml) |
| [SV-253291](ms_windows_11/rules/SV-253291.rule.yaml) | [YAML](ms_windows_11/assessments/automated/SV-253291.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/ms_windows_11/assessments/automated/SV-253291.automated.yaml) |

## RHEL 9 — 20 proposed-format pairs

[Review Benchmark](rhel_9/benchmark.yaml) · [Applicability placeholder](rhel_9/applicability.yaml)

| Rule | Proposed Assessment | Policy edits | Original generated |
| --- | --- | --- | --- |
| [SV-257851](rhel_9/rules/SV-257851.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257851.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257851.automated.yaml) |
| [SV-258080](rhel_9/rules/SV-258080.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-258080.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-258080.automated.yaml) |
| [SV-258042](rhel_9/rules/SV-258042.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-258042.automated.yaml) | 2 Tests refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-258042.automated.yaml) |
| [SV-257941](rhel_9/rules/SV-257941.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257941.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257941.automated.yaml) |
| [SV-258236](rhel_9/rules/SV-258236.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-258236.automated.yaml) | 12 Tests refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-258236.automated.yaml) |
| [SV-258046](rhel_9/rules/SV-258046.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-258046.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-258046.automated.yaml) |
| [SV-257948](rhel_9/rules/SV-257948.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257948.automated.yaml) | 2 Tests refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257948.automated.yaml) |
| [SV-257782](rhel_9/rules/SV-257782.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257782.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257782.automated.yaml) |
| [SV-257823](rhel_9/rules/SV-257823.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257823.automated.yaml) | Item presence only; unchanged | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257823.automated.yaml) |
| [SV-257800](rhel_9/rules/SV-257800.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257800.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257800.automated.yaml) |
| [SV-257825](rhel_9/rules/SV-257825.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257825.automated.yaml) | Item presence only; unchanged | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257825.automated.yaml) |
| [SV-257848](rhel_9/rules/SV-257848.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257848.automated.yaml) | Item presence only; unchanged | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257848.automated.yaml) |
| [SV-257828](rhel_9/rules/SV-257828.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257828.automated.yaml) | Item presence only; unchanged | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257828.automated.yaml) |
| [SV-257785](rhel_9/rules/SV-257785.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257785.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257785.automated.yaml) |
| [SV-257790](rhel_9/rules/SV-257790.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257790.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257790.automated.yaml) |
| [SV-258059](rhel_9/rules/SV-258059.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-258059.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-258059.automated.yaml) |
| [SV-258021](rhel_9/rules/SV-258021.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-258021.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-258021.automated.yaml) |
| [SV-257786](rhel_9/rules/SV-257786.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257786.automated.yaml) | 2 Tests refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257786.automated.yaml) |
| [SV-258045](rhel_9/rules/SV-258045.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-258045.automated.yaml) | 1 Test refactored | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-258045.automated.yaml) |
| [SV-257955](rhel_9/rules/SV-257955.rule.yaml) | [YAML](rhel_9/assessments/automated/SV-257955.automated.yaml) | Item presence only; unchanged | [Before](../v04-expanded-authoring-review/rhel_9/assessments/automated/SV-257955.automated.yaml) |

## Human review checklist

- Can you understand a simple scalar comparison without an AND tree?
- Are shared field counts at the Test scope, with local overrides only when needed?
- Does every meaningful AND/OR/ONE/XOR distinction remain apparent?
- Are record count policies distinct from scalar field count policies?
- Which datatypes or required-empty metadata add unnecessary author burden?

Reproduce from the pinned as-generated gallery:

```bash
python tools/build_v04_proposed_authoring_review.py \
  --baseline docs/examples/v04-expanded-authoring-review \
  --source-trace-root <human-v2-export-root>/records/streams \
  --output <new-nonexistent-directory>
```
