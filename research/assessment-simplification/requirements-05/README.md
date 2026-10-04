# Full RHEL 9 and Windows Server 2025 requirement reading

**Experimental development research, 2026-10-03.** This continues the owner's
request for easier, equally accurate ways to automate STIG requirements. All
**445 RHEL 9 and 291 Windows Server 2025** complete Check Texts were read in
source order, including exceptions and procedural requirements. This is broader
requirements interpretation, not another XML-to-JSON assessment conversion.

Receiving checkout: `vanderpol/scap-ng`, `main`,
`c802b9dac9a0b7c846e18389c24ea417d15d7b74`, initially clean/equal to upstream.
Current AGENTS/design/requirements/glossary/provenance instructions were consulted. No established schema, converter or review-build
content was changed. `review/current/` remains the sole external review surface.

## Read the results

- [Reading notes](READING-NOTES.md): interpretation recorded after each complete
  batch, specific rule anchors, exceptions, source inconsistencies and implications.
- [Expanded examples and recommendations](RECOMMENDATIONS.md): twelve problem
  families, readable requirement sketches, adversarial acceptance cases and costs.
- [Decision candidates](DECISIONS.md): unpublished versioned yes/no questions.
- Exact original requirements: [RHEL 9](evidence/rhel_9.json) and
  [Windows Server 2025](evidence/ms_windows_server_2025.json). Search `id` for a
  cited SV number; `checks[].content` retains the full original Check Text.
- [Extraction pins/counts](evidence/extraction.json) and
  [independent coverage verification](evidence/verification.json), with
  [six negative coverage controls](evidence/coverage-controls.json).

Reading logs cover every ordinal, not just interesting examples. Notes summarize
related rules; they are not a written security analysis or a resolved complete
OVAL graph for each of 736 rules. Existing [twelve source dossiers](../dossiers/)
retain the earlier detailed graphs. No source commands in Check Text were executed.

## Pinned sources

Both are published NIWC enhanced **SCAP 1.4** packages at
[`8c8e5dff860af6b1290ee9273a282db24278f8d5`](https://github.com/niwc-atlantic/scap-content-library/tree/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current).
They retain much DISA 1.3-derived content, per owner context; package version alone
does not show that a particular assessment method has been modernized.

| Source | Pinned filename under Current | Benchmark version | Rules |
| --- | --- | --- | ---: |
| RHEL 9 | U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip | 002.009.013 | 445 |
| Windows Server 2025 | U_MS_Windows_Server_2025_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV1-signed.zip | 001.001.001 | 291 |

RHEL ZIP SHA-256:
`70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5`.
Windows ZIP SHA-256:
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0`.
Datastream and extracted evidence hashes are in extraction.json. Source files
were available locally; no requested source gap for these two benchmarks.
This wave does not broaden the earlier DNS/Apache sources or claim to have read
their entire STIGs. NIWC production evidence remains separate from OVAL
Self-Assertion conformance evidence.

## What changed in the recommendation

Use several authoring methods rather than one universal high-level language:

1. A direct native editor or optional table recipe for straightforward typed
   registry, service and finite resource checks. Keep each row's absence behavior.
2. Versioned observations with explicit scope, parent identity and actual
   configured/running/enforced meaning; reuse existing supported capabilities.
3. Existing fixed shellcommand queries for suitable administrative APIs. DeviceGuard,
   AuditPol and certificate-store queries are candidates, not tested target adapters.
4. Separate investigation of typed relationship/ordering predicates for the
   checks that remain complex. Do not require new scanner features until existing
   Object/Variable/State/Test methods demonstrably fall short.
5. Explicitly mixed automated/manual evidence for approvals, deadlines, personnel
   events and alternate implementations. Do not convert missing process evidence
   into an invented automatic pass.

New counterexamples matter: HKCU cannot mean only the scanner service user;
Windows ACL inheritance is not a POSIX permission mask; the running Credential
Guard/VBS checks explicitly reject registry-only evidence; a '$' suffix does not
identify every system share; and terminal-rule requirements cannot use token
presence anywhere in a file. The RHEL crypto manual check lists **13** backend
paths while the earlier selected automated graph has **12**. The earlier model
remains bounded to that graph and needs reconciliation before reuse for the full
manual requirement. Source anomalies are documented, never silently repaired.

## Reproduce and interpret verification

Use the configured environment's Python with lxml, or another equivalent Python:

```sh
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/scap-ng/bin/python research/assessment-simplification/requirements-05/extract_requirements.py /workspace/scratch/simplification-sources
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/scap-ng/bin/python research/assessment-simplification/requirements-05/read_requirements.py rhel_9 --start 1 --count 40
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/scap-ng/bin/python research/assessment-simplification/requirements-05/verify_coverage.py /workspace/scratch/simplification-sources
PYTHONDONTWRITEBYTECODE=1 /workspace/.venvs/scap-ng/bin/python research/assessment-simplification/requirements-05/exercise_coverage_guards.py /workspace/scratch/simplification-sources
```

The source root contains `Current/<pinned filename>`. The extractor reuses the
maintained source parser, not a historical whole-benchmark generator. Verification
uses an independent namespace-aware ZIP/XML traversal to compare every Rule,
check, complete text, reference and recorded text hash, plus ordinal coverage of
the reading log. It detects extraction loss; it cannot prove a human understood
every detail. Re-extraction is deterministic.

Six deliberately corrupted temporary copies test detection of omitted Rules,
truncated Check Text, changed references/selectors/text hashes and a reading gap,
even after refreshing the extracted file digest. These are evidence-preservation
checks, not assessment semantic tests. No target scans, new evaluator
implementation, compiler, author trial or equivalence test is claimed. Acceptance
cases in the recommendations are specified examples, **not executed tests**.

Provenance: **Inherited** pinned NIWC source text/current project requirements;
**Adapted** earlier research ideas refined against all 736 check requirements;
**Common** new relationship/sequence examples and follow-up recommendations;
**Evidence/Audit** coverage scripts, hashes, reading notes, anomalies and limits.
Legacy serialization/IDs occur only in research provenance, not native executable
authoring. Full reading provides requirement evidence, not proof of scanner
equivalence or completeness of the OVAL dependency graph.
