# Direct 0.4.0 authoring acceptance — 2026-10-25

Owner course correction under [#251](https://github.com/vanderpol/scap-ng/issues/251)
and the [engineering directive](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271):
Objects are local by default, genuinely shared identity remains named, and readable
YAML is an acceptance requirement. No schema or language meaning changed.

| Required field | Verified result |
| --- | --- |
| BASE_SHA | `9c48e684f6b7bb1b6d40a124b19ec32966cdd85d` |
| RESULT_SHA | `da227c462d83d735709077963e8accba9da6d427` |
| SCHEMA_VERSION | **0.4.0**, approved schema tree unchanged |
| INLINE_OBJECT_COUNT | **95 Tests** |
| SHARED_OBJECT_COUNT | **1 named Object**, referenced by **7 Tests** |
| NO_OBJECT_COUNT | **71 Tests**, intentional system audit acquisitions |
| ONE_LINE_OBJECT_COUNT | **101**: 79 Test Objects, 21 Set operands, 1 Variable Object |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **130 / 0 / 161** of 291 original Rules; unchanged |
| TESTS | **3,021**, zero failures/errors, one unchanged skip; final style **9/9** |
| CI | **4/4 implementation checks PASS; 2/2 example-publication checks PASS** |
| REGRESSIONS | **0**; 130 Assessments / 173 Tests preserved |
| KNOWN_LIMITATIONS | Automated subset; no original nonempty Filter proved; remaining freeze/runtime/trust gates below |
| NEXT_ENGINEERING_OBJECTIVE | Closed-domain Registry hive selector proof, then bounded generic admission |

**What changed.** A small reachable dependency walk counts each actual consumer's
Object edges within one Assessment, including Variables, Sets and Filter-State
dependencies. Repeated Test/Variable references do not duplicate their acquisition;
equal-valued distinct source Objects are not merged. Private Test/Set Objects
inherit capability; Variable acquisitions retain it. Shared titles use source
comments or concrete selector facts, never invented purposes. The real seven-use
“Legal notice text” Object and its stable ID remain. **Zero avoidable shared Objects
existed in this pin**; source-backed controlled graph regressions catch the
source-wide-count defect without fabricating a corpus improvement.

The separate 68-line YAML presentation module uses safe serialization hints, not
text replacements. It quotes literal backslashes correctly, keeps simple Objects
on one line and complex acquisition/`require` structures multiline. All **262 JSON
and 262 parsed YAML documents** validate with current Object capability checks;
deprecated grammar occurrences are **zero**. Twenty-eight redundant capability
fields disappear from nested private Set Objects. All 130 original-source proofs
and exact compiled-operand checks pass. **127 program hashes are unchanged**;
three Set programs change their source/operand hashes for the explicit-capability
omissions, with their original collection semantics independently re-proved.

**Browse actual output** ([navigation and provenance manifest](../examples/direct-v04/README.md)):

- [Inline Registry: SV-278080](../examples/direct-v04/windows-server-2025-must-prevent-the-display-of-slide-shows-on-the-loc-da1e140a.assessment.yaml).
- [Genuine shared Object: SV-278207](../examples/direct-v04/the-windows-server-2025-required-legal-notice-must-be-configured-to-di-c6314f08.assessment.yaml).
- [No-Object audit policy: SV-278047](../examples/direct-v04/windows-server-2025-must-be-configured-to-audit-account-logon-credenti-7a4eb1d5.assessment.yaml).
- [Multiple Tests/evaluate: SV-277998](../examples/direct-v04/windows-server-2025-permissions-for-the-system-drive-root-directory-us-40e5f4bd.assessment.yaml).
- [Original nested Sets: SV-278192](../examples/direct-v04/windows-server-2025-must-have-the-dow-root-certificate-authority-ca-ce-acebd595.assessment.yaml).
- [Registry/Variables/shellcommand: SV-278139](../examples/direct-v04/windows-server-2025-active-directory-sysvol-directory-must-have-the-pr-1ec1fc0c.assessment.yaml).

These six files have JSON peers, original Benchmark/Rule/Definition/dependency IDs,
ZIP/XML hashes and converter SHA in the manifest. Their closed selected wrapper
also compiles and independently proves; the public directory validator checks
**6/6**, zero unclassified files. The regeneration command and safe extension
instructions are in the [developer guide](../developer/DIRECT-V04-CONVERTER.md).
The [machine report](v04-direct-authoring-acceptance.json) records exact commands,
dependencies, counts, hashes, test classifications and CI. No performance gain or
increase in original-source coverage is claimed for this correction.

**Acceptance answers.** (1) Yes: Assessment-local, inline by default. (2) Yes:
compact simple Objects, verified at every eligible YAML syntax node. (3) Yes:
legitimate sharing and meaningful stable references remain. (4) Yes: structured
inline `require` and current `evaluate` grammar only. (5) No source-proof,
compilation or supported-Rule coverage regression. (6) Yes: documented commands
and focused tests run in the minimal Python/PyYAML/jsonschema environment without
AI. (7) **GO for the next bounded, independently proved increment; NO-GO for
production promotion.**

The old non-mandatory authoring guard still reports 16 historical `test-` prefix
assertions, versus 17 baseline findings including the now-corrected Variable
presentation order. It was run and left unchanged; its prefix convention is not
the current schema's meaningful `-test` suffix contract. The documentation audit
retains three pre-existing current and 39 historical missing links, with no new
broken links. Arbitrary authored capability enum/cross-field hardening, complete
policy coverage, production signing/trust and actual scanner acceptance remain
separate gates. No production converter, compiler, schema, release gate or
six-STIG package was changed.

Exact-head implementation CI: [rebaseline](https://github.com/vanderpol/scap-ng/actions/runs/40233665204), [canonical](https://github.com/vanderpol/scap-ng/actions/runs/40233665182), [current regression](https://github.com/vanderpol/scap-ng/actions/runs/40233665210), [issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40233665161). Documentation did not trigger for the code-only head; [example documentation](https://github.com/vanderpol/scap-ng/actions/runs/40233836115) and its [issue-reference check](https://github.com/vanderpol/scap-ng/actions/runs/40233836037) passed on `1f8098a95`.

One final issue-comment attempt failed exactly: `Post "https://api.github.com/graphql": Forbidden`. It was not retried; this committed report is the authorized handoff.
