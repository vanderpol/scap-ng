# SCAP-NG 0.4-C sample review — simple and complex

**19 October 2026 · #245 · Research samples only; C is not normative or production-executable.**  
These examples use the **existing A collection/dataflow** backend or source-compatible fixture adapters. They illustrate the **authoring experience**, not a new platform collector or scanner.

## 1. Simple Linux — /home must have nosuid

[Independent C source fixture](c-source-exact-home-nosuid.research.yaml) · [Original A source](runtime-slice/home-nosuid.assessment.json) · [C/A structural test](../../../tools/test_research_c_shared_engine.py).

**Native 0.4-A Test excerpt:**

\`\`\`yaml
capability: linux.partition
object:
  capability: linux.partition
  select:
    mount_point:
      matches_regex: '.*\/home'
states:
  - mount_options:
      require: at_least_one_exists_and_some_match
      equals: nosuid
require: at_least_one_exists_and_all_match
\`\`\`

**Research C requirement (independently authored; compiles to exact same A Test on this fixture):**

\`\`\`yaml
require:
  each: linux.partition
  where:
    mount_point: {matches_regex: '.*\/home'}
  minimum_items: 1
  all_found_items:
    mount_options: {contains: nosuid}
\`\`\`

**Status: SOURCE-STRUCTURE-PRESERVING FOR THIS ONE FIXTURE.** This C input currently lowers to the same A Object selector, field State, Item requirement and evaluate reference. Exact \`equals: /home\` is *not* source-equivalent to the imported \`matches_regex\`; our negative test blocks it. The C \`contains\` wording is a presentation of the original multi-valued State \`at_least_one_exists_and_some_match\` for this exact source, not a general-value operator implementation.

## 2. Windows 11 — WDigest must be disabled (same Item)

[Independent C witness](c-source-exact-wdigest.research.yaml) · [Windows 11 source](../../requirements-first-language/contract-candidate/corpus/source-specimens/windows-registry-state-all-0fef40d33c90.source.yaml) · [Windows/evaluation tests](../../../tools/test_research_c_common_evaluation.py).

**Research C — source-preserving fields, explicit no-hidden-defaults:**

\`\`\`yaml
require:
  each: windows.registry
  where:
    hive: local_machine
    key:
      equals: 'SYSTEM\CurrentControlSet\Control\SecurityProviders\Wdigest'
    name: {equals: UseLogonCredential}
  registry_view: unspecified_requires_xml_parity
  collected_items:
    exists: one_or_more
    match: all
  on_same_item:
    all:
      - type: {equals: dword, field_exists: one_or_more, field_match: all}
      - value: {equals: 0, field_exists: one_or_more, field_match: all}
\`\`\`

**Status: BOUNDED SOURCE-COMPATIBILITY BRIDGE / FIXTURE EVALUATION.** The source is a converted **0.3** Assessment, not a pinned valid 0.4-A authored Registry Assessment. The C requirement compiles to the existing compatibility IR for the same source Test and State; the existing typed offline Registry evaluator tests correct DWORD value, wrong type/value, zero Items, incomplete and error, and conflicting views. No arbitrary Windows Registry view is assigned. A real scanner must still validate original XML view semantics and datatypes. Crucially, **the type and value must match on the same Registry Item**; unrelated Items cannot satisfy opposite halves.

## 3. Apache — command discovery with a real Variable-operation change

[Two-Variable source specimen](../../requirements-first-language/contract-candidate/corpus/source-specimens/independent-shellcommand-apache-small-575d1e0ee9d2.source.yaml) · [Fused compiler](../../../tools/research_c_fused_apache.py) · [Differential tests](../../../tools/test_research_c_fused_apache.py).

**Existing source expressions:** one \`regex_capture\` Variable collects Apache process command lines using \`independent.shellcommand\` and derives the httpd/apache2 executable path. A second \`concat\` Variable adds the literal \` -V\` to build a version-check command. Neither source collector nor its shell arguments are replaced.

**Potential human C view (illustrative only, not yet a parsed C grammar):**

\`\`\`yaml
steps:
  apache_version_command:
    from: independent.shellcommand
    collect: existing_apache_process_command_lines
    extract_first: '(^\/.+\/httpd|^\/.+\/apache2) '
    append: ' -V'
\`\`\`

**Implemented research compiler IR:** a single \`c-research-fused-typed-value-pipeline\` with the original A/source collection request, exact regex capture, \`append_literal: " -V"\`, original Variable fingerprints, and two provenance-bearing original Variable IDs. It is **a genuinely different evaluation implementation**, not just the same source AST with nicer names. Its output is compared both against the existing source-Variable evaluator and independently authored expected results. One Apache process, an Apache2 alternative, two distinct executable paths, absent/missing evidence, incomplete evidence and malformed evidence are tested.

**Status: FOCUSED DIFFERENTIAL FIXTURE PASS.** OVAL regex dialect and source Item order are not yet independently verified, so we cannot certify fully lossless SCAP 1.4 conversion.

## 4. Complex Apache — 19 Variables and five checks

[Real source specimen SV-214268](../../requirements-first-language/contract-candidate/corpus/source-specimens/independent-shellcommand-1-3d964d126ca8.source.yaml) · [C read-only Variable steps](../../../tools/research_c_shared_engine.py) · [source DAG regression](../../../tools/test_research_c_shared_engine.py).

**Human-readable logical outline of original source graph (NOT an executable C translation):**

\`\`\`yaml
assessment: Secure Apache session cookies
collect:
  discover_apache_executables: independent.shellcommand
  find_apache_root: derived_from_discovered_executables
  find_main_configuration: derived_from_apache_root
  expand_include_files: derived_from_main_configuration
  find_all_loaded_configuration_files: derived_from_apache_includes
check:
  all:
    - session_enabled_in_main_and_included_configuration
    - session_enabled_in_other_loaded_configuration
    - session_cookie_httponly_and_secure_in_main_and_included_configuration
    - session_cookie_httponly_and_secure_in_other_loaded_configuration
    - session_cookie_module_enabled
\`\`\`

These labels are merely a **narrative preview**. In the original source there are five named Tests and a 19-node Variable dependency graph, including regex capture, concat, \`unique\` and \`merge\`. The previously tested C **read-only graph presentation** uses \`extract\`, \`combine\`, \`distinct\`, and \`merge_values\`, and reconstructs the exact source graph, preserving acquisition identities and parameters. That **does not mean** we can replace this entire graph with five hypothetical native collection calls: all 19 original dependencies, source cardinalities, provenance, conditional errors and path identities remain necessary until a verified transformation exists.

**Status: SOURCE DAG RECONSTRUCTION PASS; COMPLETE HUMAN-FACING C COMPILER NOT BUILT.** This is the complex fixture we should use to check that an attractive C design is genuinely simpler rather than concealing OVAL mechanics or losing precise results.

## 5. Universal C truth and no-data behavior

The [common C evaluator](../../../tools/research_c_common_evaluation.py) maps a single explicit existence/Item-match interface into A's OVAL-derived generic Test semantics. The six-state logical operators are lowered to A's typed expression engine and checked against an independent source evaluator. These cases are shared across Unix/Windows capability IDs:

| Observation | For “at least one Item must exist, all observed Items match” | Why |
| --- | --- | --- |
| Complete, 0 Items | Fail | Required Item is definitely absent |
| Incomplete, 0 Items | Unknown | The collection might be incomplete |
| Complete, 1 good Item | Pass | Complete and expected field matched |
| Incomplete, 1 good Item | Unknown | A later Item could fail |
| Incomplete, 1 bad Item | Fail | Already decisive for an all-match condition |
| Collection error | Error | Not interchangeable with an empty successful collection |
| Not collected | Unknown | No justified truth outcome |
| Not applicable | Not applicable | Not a fabricated pass |

**Known unresolved boundary:** a complete, empty **State-bearing** Test with an existence setting that itself passes (\`none_exist\` or \`any_exist\`) has no validated zero-item State aggregation in the existing generic helper; the C adapter deliberately refuses to invent a default. This must be separately resolved against normative source behavior. Likewise, actual OVAL Registry default-view and regex compatibility remain open.

## 6. Evidence and decision

[**Focused 21-test CI PASS**](https://github.com/vanderpol/scap-ng/actions/runs/39251766907): Linux source-identity; typed Registry/partial/view conflict; full 6×6 combinations for each of four Boolean operators; nested logic; universal missing/empty/incomplete semantics; Apache 2/19 Variable graph preservation; and **actual Apache two-step capture/concat fusion** with negative cases.

**Result:** These three relatively independent probes support a **GO for C feasibility engineering**, using **A-derived collectors** and a **single capability-neutral evaluator**. They **do not** establish the complete six-STIG, source/OVAL/XSD, six-state scanner or general C Variable-rewrite parity gates. C remains a research candidate; no normative A schema or pinned Guided editor was changed.
