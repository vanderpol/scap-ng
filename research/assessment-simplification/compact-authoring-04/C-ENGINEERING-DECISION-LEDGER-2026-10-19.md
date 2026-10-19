# SCAP-NG 0.4-C research: evidence and next decision gates

**19 October 2026 · owner priority #1 · [issue #245](https://github.com/vanderpol/scap-ng/issues/245). This is a research handoff, NOT an adopted specification.**

## Architecture conclusion so far

**Continue C:** a human-oriented authoring frontend can reuse A's capability mappings, typed Objects/Items, source-compatibility adapters, six-state Boolean/existence tables, and eventually one execution IR. Do not rebuild B providers or fork a second scanner. C's strongest improvement is in **shared observations, explicit Item scope and a requirement tree that uses checks instead of OVAL structures**.

**One research language shape:** a check chooses **exactly one** of direct *from* or a named *observation*. It then has an explicit *must* Item/record/field requirement; independent named checks combine in *require* with Boolean operators. Named observations each specify a *from* acquisition. The [single-frontend normalizer](../../../tools/research_c_one_frontend.py) accepts the already-tested direct Linux/Windows/DNS and the seven-check shared Windows case as one static shape; it does not yet execute, validate arbitrary A capabilities, compile arbitrary Variables or establish scanner parity.

## Confirmed bounded engineering gates

| Proof | Evidence | Result classification |
| --- | --- | --- |
| Linux /home selector and mount_options | [C/A proof](C-SHARED-ENGINE-PROOF-2026-10-19.md) | Structural source identity + synthetic collection outcomes |
| Windows WDigest DWORD=0 + WMI absence | [composed research sample](c-two-windows-checks.research.yaml) | Both inputs compile through A/source adapters; 36 independent six-state pairs |
| DNS response limiting | [DNS source example](c-short-windows-dns-rrl.research.yaml) | Exact shell collection arguments + selected result fixtures |
| RHEL mode 0740 eight source bits | [permission macro](../../../tools/research_c_permissions_macro.py) | All 4,096 POSIX bit combinations; full source account/Filter parity unproven |
| Apache limited Variable fusions | [shared-engine analysis](C-APACHE-SHARED-OBSERVATIONS-2026-10-19.md) | Pinned acquisition and bounded differential fixtures, NOT complete 19-Variable source conversion |
| Real Windows 11 SV-253495 | [7-check C reviewer sample](c-source-exact-windows-rdp-rights.research.yaml) | Two shared observations, seven Checks, full original AND/OR structure and 0.3 source read-only inverse |
| Source-independent Windows authoring | [C native research compiler](../../../tools/research_c_windows_shared_native.py) | Generates version-pinned A Test/State structures without reading original source document; schema/focused real-source regressions; NOT generalized or scanned |
| Same-record requirement scope | [adversarial record evidence](../../../tools/test_research_c_same_record_evidence.py) | Two partial parent records cannot form a false matching whole; six-state/partial cases, synthetic |
| Guided view feasibility | [shared projection](../../../tools/research_c_guided_observations.py) | 2 source cards + 7 check cards + one requirement tree, no existing A editor changes; still an adapter, not a deployed GUI |
| YAML portability | [strict C loader](../../../tools/research_c_require_language.py) | Rejects unquoted YAML 1.1 on/off/yes/no mapping keys; use explicit observation reference instead of on |
 
Green [C source-independent compiler CI](https://github.com/vanderpol/scap-ng/actions/runs/39276658341) and [C record correlation CI](https://github.com/vanderpol/scap-ng/actions/runs/39277075573). Later focused C tests are only to be called green after the exact-head run is inspected.

## What is NOT earned yet

- No production-grade C authoring compiler for **all** A capabilities; the source-independent Windows compiler is deliberately bounded to the pinned seven-check family and exact source aliases.
- No complete forward migration of all six representative STIGs into independently authored C. The original A source-envelope census is not C coverage.
- No independent OVAL 5.12.3 XML/SCAP runtime oracle confirming collected real Items, regex dialect, WMI namespace/registry view, or Variable/record semantics.
- No general source-preserving nested Variable composition, per-parent foreach, filters, unknown/error source propagation, scope-dependent optional records or full shared observation caching.
- No tested production scanner, platform collection parity, signed C compiled package or authoritative evaluator; fixture Pass/Fail never becomes an editor compliance result.
- No blind auditor usability acceptance. A read-only source view can be more pleasant without genuinely removing concepts; shared observations must not hide Item correlations.

## Highest-value non-Apache next gate

RHEL9 **SV-257889** (initialization files under account-derived home directories): retain TWO original Tests with DIFFERENT existence requirements and distinct dynamically derived populations, one State with eight independent forbidden permission-bit comparisons, source Variables/Objects/Sets/Filters, and global versus per-parent correlation. An author should see clear named observations for regular users versus root without a single merged union. It must refuse a shorter representation if the source population or optional/required existence changes. Confirm matching against pinned original source Items and independently expected six-state outcomes; do not invent a faster full collector or claim success from the already-verified 0740 bit macro alone.

## Vocabulary still open to falsification

- Prefer explicit *any_item*, *every_item*, *absent*, etc.; do not approve bare *must* as hidden some-match without blind reviewer evidence.
- Preserve a visible distinction between **Item population**, **field values within one Item**, **whole record-state alternatives**, and **logic over separate Tests**.
- A single shared observation exposes data, not a policy outcome; every check retains independent requirements.
- Do not use implicit IF/ELSE for multi-branch six-state source expressions when the original is OR-of-AND.
- Do not use a superficially shorter record *in* comparator unless its full cardinality and missing/incomplete behavior is independently shown equivalent.

**State:** GO for continued C feasibility work. NO-GO for language freeze or "as capable as A" claim. Keep trunk-based issue-linked changes in research only.

## Shared A objectless capabilities (C-only research checkpoint)

The unified C compiler now handles one named `observations:` source for multiple checks on A capabilities whose versioned `test_source.kind` is `none`, e.g. `windows.passwordpolicy`, **without introducing a fake Object**. See [review sample](c-shared-objectless-policy.research.yaml) and [targeted negative and six-state tests](../../../tools/test_research_c_objectless.py). `shared_singletons` is authoring/provenance metadata for direct native Test checks, not a physical A collection Object or a verified runtime cache. This also exposes an important compiler invariant: shared evidence does not imply the same policy result for multiple checks.

The new focused CI run must be verified against its exact commit SHA before calling this checkpoint green. It does not demonstrate live collection or full six-STIG parity.

## Same frontend compiles the complex Windows record family

The seven-check Windows 11 source-backed C sample is now routed through the **same** `compile_c_unified` entrypoint as inline direct, named shared-Object and objectless singleton C. This is a narrowly pinned record-family backend, not a general WMI implementation. It reuses the already reviewed original ID and multi-valued record-State guards, produces native 0.4-A Tests/Objects, and uses the same six-state expression engine. The additional [integrated tests](../../../tools/test_research_c_unified_complex_windows.py) assert source-independent compilation, schema shape, 128 Boolean and mixed six-state source expression outcomes, and negative unsupported-record mutations. Native collection and original SCAP XML parity remain unverified.

## Local-first C testing and superseded CI reduction

- [Local C runner](../../../tools/run_research_c_locally.py) parses the **same** focused unittest list as the maintained GitHub workflow. Run `python tools/run_research_c_locally.py --quick` for the six key compiler/source tests or `--all` for the entire source regression gate. Requires a local repository checkout and PyYAML/jsonschema dependencies, but no GitHub clone and no network per run.
- The dedicated [C workflow](../../../.github/workflows/research-c-shared-engine.yml) now uses a C-specific GitHub Actions concurrency group, so a superseding main-branch C run cancels earlier C runs. It **does not** affect other workflows.
- In the available isolated Python environment, normalizing one shared C authoring example 10,000 times took about 0.25 seconds. Twelve structural compiler tests ran in about 0.05 seconds with explicitly **stubbed** native-A and Boolean evaluation dependencies. These verify authoring graph relationships and local control flow, **not** the full pinned A compiler or source parity. The prior completed Actions run executed 164 C tests in roughly 1.3 seconds once scheduled; CI wait time, not raw Python execution, was the primary throughput blocker.

The bundled workflow revision must independently pass at its exact SHA before declaring this checkpoint verified.
