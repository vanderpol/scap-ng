# Assessment simplification research

Latest corpus reading: [all RHEL 9 and Windows Server 2025 Check Texts, requirements 05](requirements-05/README.md).
All 736 requirements were read, with pinned original text, interpretation notes,
twelve expanded problem families and source discrepancies. Coverage verification
does not establish scanner equivalence; additional samples' full OVAL closures and
target validation remain follow-up work.

Latest concepts: [ten authoring/assessment alternatives, concepts 04](concepts-04/README.md),
including native editing without a second language, reusable observation recipes,
acceptance cases and directly evaluated domain contracts. Concepts only; no new
execution/equivalence claim. The compiler's implementation risk remains explicit.

Latest continuation: [requirement-oriented authoring compiler, transform 03](transform-03/README.md).
A readable permission allowance compiles to current independent Boolean States,
with exhaustive source-predicate and partial-result evidence. Its
[comparison](transform-03/COMPARISON.md) distinguishes compiler conveniences from
new DNS/Apache/audit execution contracts. Experimental research only; the current
schema/converter and single external review surface are unchanged.

Owner-corrected direction: [new assessment methods, method 02](method-02/README.md).
This explores direct Object requirements, semantic permission allowances,
configuration constraints and symbolic audit coverage. The earlier graph/table
work below remains evidence; it is not the main authoring-method goal.

Previous continuation: [refinement 01](refinement-01/README.md) adds finite-table
expansion with full bounded source-contract comparison, typed DNS acquisition
experiments, an Apache occurrence library, adversarial tests and a new handoff.
The initial study below is preserved as the baseline.

**Research checkpoint, 2026-10-03: all 12 packet cases investigated. Experimental proposals only; no schema/converter changes or scanner-equivalence claim.**

Start with the [findings and limits](FINDINGS.md), [comparison](COMPARISON.md), [experimental execution contracts](FEATURES.md), [versioned yes/no decision candidates](DECISIONS.md), and [resumption handoff](HANDOFF.md). This is development research, not a parallel external review surface.

| Source | Dossiers |
| --- | --- |
| RHEL 9 | [Audit syscalls](dossiers/SV-258179.md), [home initialization files](dossiers/SV-257889.md), [crypto back ends](dossiers/SV-258236.md) |
| Windows Server 2025 | [FTP paths](dossiers/SV-278028.md), [AD effective rights](dossiers/SV-278138.md), [registry ACEs](dossiers/SV-278001.md) |
| Windows DNS | [RR completeness](dossiers/SV-259350.md), [key durations](dossiers/SV-259345.md), [interface addressing](dossiers/SV-259374.md) |
| Apache server/site | [KeepAlive](dossiers/SV-214228.md), [cookie flags](dossiers/SV-214268.md), [default documents](dossiers/SV-214292.md) |

Each dossier links unchanged before content, pinned original Rule/OVAL XML, dependency edges, a proposed after sketch, alternatives and a concrete result matrix. `evidence/` retains legacy provenance separately from `proposals/`. Applicability source closures are separate per-family evidence. All proposal files are labeled experimental and remain outside the established schema.

Reproduce from repository root (Python 3.12, PyYAML, lxml and jsonschema):

```bash
python research/assessment-simplification/experiments/extract_evidence.py /path/to/pinned/niwc-checkout
python research/assessment-simplification/experiments/build_dossiers.py
python research/assessment-simplification/experiments/verify_study.py
python -m unittest discover -s research/assessment-simplification/experiments -p test_semantics.py -v
python -m unittest discover -s tools -p 'test_oval_result_truth_tables*.py' -v
python tools/check_current_authoring_contract.py research/assessment-simplification/samples
python tools/validate_native_json_schemas.py research/assessment-simplification/samples --schema-dir schema/v0.1.0
```

`extract_evidence.py` verifies all five ZIP hashes before reading them and uses the maintained splitter's resolver and closure code. Preserve the NIWC `Current/` filenames in the pinned checkout. No source shell commands execute. `build_dossiers.py` is a research presenter, not a production converter. The 22 new test methods include 4096 exhaustive modes and 294 regex text fixtures; subcases are not counted as separate unittest methods. The 63 inherited tests are schema-derived evaluator unit regressions, not target scans or a fresh upstream Self-Assertion run.

The original receiving-session brief and packet descriptions follow unchanged below.

---

# Original assessment simplification research handoff

**Status: research inputs and instructions; no redesign is accepted by this packet.**

Owner request, 2026-10-02: investigate unknown methods or future features that make complex OVAL/SCAP-NG assessments easier for humans to write and understand, while preserving testing accuracy. Shellcommand may help focused queries; native scanners retain filesystem traversal and exclusion responsibility.

## Start here

Give Codex the prompt below with access to `vanderpol/scap-ng`. Read [the complete task](CODEX-TASK.md) before starting. This packet intentionally uses 12 selected automated Assessments with their Rules and manual Check Text, not an entire 65-package corpus.

## Selected cases

| Family | Rule | Objects / Variables / States / Tests | Research focus |
| --- | --- | --- | --- |
| rhel_9 | [SV-258179](samples/rhel_9/rules/SV-258179.rule.yaml) | 24 / 17 / 0 / 24 | Audit-rule parsing; regex repetition; running versus persisted rules |
| rhel_9 | [SV-257889](samples/rhel_9/rules/SV-257889.rule.yaml) | 5 / 2 / 5 / 2 | Native file traversal; user/home selection; Sets/Filters; permission bits |
| rhel_9 | [SV-258236](samples/rhel_9/rules/SV-258236.rule.yaml) | 12 / 0 / 12 / 12 | Repeated symlink/target checks; policy-wide reuse |
| ms_windows_server_2025 | [SV-278028](samples/ms_windows_server_2025/rules/SV-278028.rule.yaml) | 9 / 8 / 5 / 4 | FTP site records; environment paths; dynamic command construction |
| ms_windows_server_2025 | [SV-278138](samples/ms_windows_server_2025/rules/SV-278138.rule.yaml) | 12 / 3 / 4 / 9 | AD data paths and effective Windows rights |
| ms_windows_server_2025 | [SV-278001](samples/ms_windows_server_2025/rules/SV-278001.rule.yaml) | 4 / 3 / 5 / 5 | Registry permissions; WMI records and shell query interpretation |
| ms_windows_server_dns | [SV-259350](samples/ms_windows_server_dns/rules/SV-259350.rule.yaml) | 7 / 4 / 6 / 6 | Per-zone DNSSEC record completeness and applicability |
| ms_windows_server_dns | [SV-259374](samples/ms_windows_server_dns/rules/SV-259374.rule.yaml) | 6 / 5 / 3 / 5 | Interface/address correlation and static addressing |
| ms_windows_server_dns | [SV-259345](samples/ms_windows_server_dns/rules/SV-259345.rule.yaml) | 6 / 3 / 5 / 5 | Per-zone signature duration, units and boundaries |
| apache_server_2-4_unix_server | [SV-214228](samples/apache_server_2-4_unix_server/rules/SV-214228.rule.yaml) | 9 / 18 / 4 / 4 | Apache discovery/includes; configuration predicates; script overhead |
| apache_server_2-4_unix_server | [SV-214268](samples/apache_server_2-4_unix_server/rules/SV-214268.rule.yaml) | 10 / 19 / 7 / 5 | Cookie HttpOnly policy across scoped configuration |
| apache_server_2-4_unix_site | [SV-214292](samples/apache_server_2-4_unix_site/rules/SV-214292.rule.yaml) | 9 / 18 / 0 / 2 | Default page/directory listing; native file selection versus config intent |

Counts describe authored top-level nodes only, not semantic complexity or runtime cost. Selection is purposive, not a statistically representative census. Apache examples already use shellcommand heavily: studying them can identify how to remove opaque script/dataflow overhead, not merely add more shell commands.

## What is included

- Original bytes from the successful build: selected Rules, each automated and manual Assessment, the five applicability catalogs and their Assessment files, and source-generation provenance.
- A non-executable `benchmark-context.json` metadata extract per family. Complete Benchmark/Profile/group membership remains in the full pinned artifact. These are partial research families, not deployable full benchmarks.
- `sample-manifest.json` with original build and NIWC pins, case counts and SHA-256 for all 83 sample/context files.
- Full research instructions, iterative deliverables, proof requirements and shellcommand boundaries in `CODEX-TASK.md`.

Rule-relative selected automated/manual paths and catalog-relative applicability paths are preserved. The full packet is roughly 300 KB of sample payload. Commands in the snapshots are content data; do not execute them during inspection.

## Pins and source acquisition

- Successful build: https://github.com/vanderpol/scap-ng/actions/runs/37083265100
- Full review artifact: https://github.com/vanderpol/scap-ng/actions/runs/37083265100/artifacts/11260426828
- Build commit: `5acbd67af155668440615b0d6b1f6412805caa10`
- NIWC revision: `8c8e5dff860af6b1290ee9273a282db24278f8d5`
- Original package name, SHA-256 and source Benchmark identity: each family's `source-generation.json`.
- Origin batches: `native-current-batch-0/1/2/3` from this same run. Original generated source was used, rather than duplicate-normalized content, to retain baseline authoring complexity.

Retrieve original pinned NIWC ZIPs for XCCDF/OVAL closure using the maintained splitter and semantic parser documented under `tools/`. This packet does not contain the original ZIPs or target-system scan results. Do not use the snapshots as normative authority if current design/schema has evolved.

## Known interpretation hazards

- RHEL9 SV-258179 Check Text examines loaded audit rules via auditctl, while the selected automated graph selects `/etc/audit/audit.rules`. Compare both contracts explicitly.
- DNS SV-259350 Rule/manual title concerns DNSSEC RRs, while its automated Assessment title names the RRSet authorization requirement. Treat title/binding reuse as a research question; a title mismatch alone does not prove incorrect logic.
- Sample schema/graph validation and round-trip evidence establish structural/fidelity checks, not target runtime equivalence. Proposed methods need explicit semantic counterexamples and eventually execution evidence.

## Ready-to-paste Codex prompt

```text
Work in vanderpol/scap-ng on main. Read AGENTS.md and current design/transition records, then research/assessment-simplification/CODEX-TASK.md and sample-manifest.json. This is a potentially expensive staged research task to discover clearer, equally accurate assessment methods, not a production rewrite. Start with RHEL9 SV-258179 and Apache UNIX Server SV-214228; compare STIG intent, original pinned OVAL and complete NG graphs before proposing small mockups. Keep filesystem scanning in native scanner capabilities; shellcommand is allowed only where its acquisition/error/scope contract is justified. Follow the brief through counterexamples, equivalence limits, portable semantic contracts and coherent research checkpoints. Preserve existing designs and samples; commit completed research to main. Begin with the preflight/baseline checkpoint, then continue through the pilot and remaining cases unless a substantive semantic decision needs owner input.
```

## Provenance and verification

Inherited: unchanged selected NIWC-derived generated Rule/Assessment and applicability content from the pinned same-run batches. Generated snapshots derive from NIWC XCCDF/OVAL and current original converter work; see source-generation records. Evidence/Audit: purposive selection, counts, byte hashes, context extracts and interpretation hazards. Common: original research instructions and file-integrity checking. No coworker private code, sensitive SCC target results or external implementation has been copied.

Verified locally: 12 Rules, 12 automated and 12 manual Assessments; sample manifest hashes; YAML/JSON parsing; selected Rule choice paths and applicability reference closure. The current authoring vocabulary/presentation guard also passed on 73 YAML files, with zero violations. See `packet-verification.json`. This is packet integrity and a vocabulary guard, not a full schema or runtime conformance pass. The originating build passed structural and graph gates; receiving Codex must reproduce appropriate baseline checks on its checkout.
