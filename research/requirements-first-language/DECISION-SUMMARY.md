# SCAP-NG auditor authoring — current direction

**17 October 2026. Research, not a Board vote, approved schema or scanner release.** [Track #235](https://github.com/vanderpol/scap-ng/issues/235).

**New Apache proof (17 October):** [full source audit](APACHE-SOURCE-PROVIDER-AUDIT-2026-10-17.md) establishes four at-least-one shellcommand Tests, 18 Variables, separate primary Include versus loaded-file discovery, and different optional field conditions. [Read-only static Apache provider](../../tools/research_provider_apache_directives.py) now preserves individual raw directive sources and reports incomplete unsupported contexts, macros, glob limits, cycles, and missing required Includes. **Do not conflate this with Apache effective configuration or proven conversion.**

**New validated Linux proof (17 October):** [source-backed initialization-file audit](LINUX-INIT-FILES-AUDIT-2026-10-17.md) found a global-root-file count regression in the earlier nested example and confirmed across all 4,096 POSIX modes that the original eight flag constraints mean **allowed-bit subset of octal 0740**, not numeric mode <=0740. A [revised native sketch](experiments/linux-init-global-population.yaml) and read-only [streaming files-from-account-homes provider](../../tools/research_provider_linux_account_files.py) with its [contract](providers/linux.files_from_account_homes.v0.1.yaml) were added; this provider is test-fixture-backed and not old OVAL source-compatible. The existing WMI grouping test suite is also now run in CI. These are material semantic findings, not another vocabulary vote.

**Direction:** typed-resource-first for ordinary auditor checks, with one explicit collection form for genuinely multi-resource policies. This is no longer an author-facing OVAL Object/Test/State grammar. Leave OVAL-like structural compatibility to the converter/evaluator when source semantics require it.

**Why:** independently provided Gemini blind-read and context-aware ChatGPT first-read both identified good comprehension of simple selection/expectation checks but ambiguity about required versus optional resource existence, missing evidence, and nested provider identity. We caught a further source-fidelity failure in WMI: raw [1,3] is not the same as membership in either 1 or 3. We must not use English-like fields to hide that difference.

**Better vocabulary:** native, uniquely identifiable facts can use a named typed resource; population policy can use each + where + must, with a positive minimum only when existence is required. This is still **experimental**; the old if_empty language remains only in pre-existing prototype examples. [See all readable design samples](IDEAL-AUDITOR-AUTHORING-THIRD-PASS.md).

**New technical evidence:** a [real read-only Linux mountinfo collector](../../tools/research_provider_linux_mounts.py) exposes IDs by mount namespace, typed VFS mount options and completeness/diagnostics under a [versioned prototype contract](providers/linux.mounts.v0.1.yaml). A [synthetic evidence model](../../tools/research_requirements_first_evidence.py) shows complete/partial, missing selector, duplicate/singleton, selected-vs-compliant and related counterexamples. [CI](https://github.com/vanderpol/scap-ng/actions/workflows/research-requirements-first-04.yml) checks the grammar, negative cases and real runner collection.

**What is NOT proven:** Linux provider equivalence to OVAL linux.partition; a Windows WMI role provider; an Apache loaded-directive provider; Windows DNS per-zone/key semantics; the full six-state native runtime; or lossless six-STIG conversion. Short snippets are not substitutes for those proofs.

**Next owner-free technical gate:** finish one genuinely complex typed provider with fixture-level semantic traces (Windows WMI first), and test a native policy against the unchanged original source before choosing a normative grammar. A later novice-author exercise should test writing requirements, not just reading YAML.

**Gemini needed now? No.** Use another independent model only after WMI and Apache provider contracts and counterexample packs exist; otherwise it will be asked to invent missing semantics again.
