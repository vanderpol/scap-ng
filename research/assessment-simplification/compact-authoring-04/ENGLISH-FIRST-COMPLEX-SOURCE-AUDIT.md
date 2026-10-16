# SCAP-NG 0.4 — English-first grammar tested against complex real Assessments

**Research only; no 0.4 grammar decision.** The proposals below are **readability sketches**, not schema-valid content, verified conversions, working Test operators, or scanner results. They are compared against exact [six-STIG r3 source-backed files](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/manifests/pinned-real-stig-fixtures.json). Original source semantics are **mandatory**, even when they seem less obvious than the rule title.

**Design goal:** A security administrator should understand the Assessment's intent without knowing OVAL, while an implementer should determine its precise meaning without guessing.

## What survives the first complexity test

- **Individual checks:** `check` (purpose) → `inspect` (typed capability) → `where` or explicit acquisition (collection) → `require` (measurable result) is a promising human reading order.
- **Already collected Items:** `every_collected_item` reads more clearly than `all_found`; it represents **Test matching across collected Items**, NOT a new collection loop or independent Test per Item.
- **Existence:** `at_least_one_item_exists: true` is more self-explanatory than `at_least_one_found: true`. But a Boolean **does not** mean a failed or incomplete collector is ordinary false, and one `true` key for each rare existence mode may become unwieldy.
- **Multi-value fields:** `includes_value: nosuid` is appealing where it is precisely defined as OVAL field `existence=one_or_more` + `match=one_or_more` + typed equality, **not substring search**. It needs explicit support for uncommon value cardinalities.
- **Combined requirements:** real source `evaluate` trees need **named checks plus explicit `all_of` / `any_of`**. Procedural `if/else` does not generally replace OVAL six-result Boolean composition.
- **Runtime dependency graphs:** `for_each` collection expansion, Set filters, shared Objects, Variables and actual shell commands must remain visible or losslessly lowerable. The word `every_collected_item` must never mean `for_each`.

## 1. Windows 11 — role-dependent Remote Desktop user rights

Source: [SV-253495](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml). **Seven real Tests.** The source reads the Windows `DomainRole` WMI record (values `1`/`3` for a non-DC domain-joined machine, `0`/`2` for a standalone machine); inspects the shared `SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME` user-right collection; and accepts **one of three distinct OR branches**: domain-joined + four named principals, standalone + Guests, or Everyone. Guest/principal checks use **some collected user-right Item** matching rather than every Item matching.

**English reading:** “Accept the Everyone assignment; or, on a standalone machine, the Guests assignment; or, on a non-DC domain-joined machine, all four specified principal assignments.”

```yaml
# Illustrative structure ONLY; names/actions are NOT approved grammar
checks:
  domain_joined:
    check: Machine is a non-DC domain-joined computer
    inspect: windows.wmi.query
    collect:
      namespace: root\cimv2
      query: SELECT DomainRole FROM win32_computersystem
    require:
      at_least_one_item_exists: true
      every_collected_item:
        result:
          record:
            domainrole:
              one_of: ['1', '3']  # UNPROVEN: original has two distinct State alternatives
  guests_denied:
    check: Guests are assigned the deny-Remote-Desktop user right
    inspect: windows.userright
    where:
      userright:
        equals: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME
    expect:
      trustee_name:
        case_insensitive_equals: Guests
        observed_values:
          exist: at_least_one
          matching: all
    require:
      collected_items:
        exist: at_least_one
        satisfying: at_least_one
# Additional named checks: standalone, local_account, domain_admins,
# enterprise_admins, everyone; their full source must be preserved.
evaluate:
  any_of:
    - all_of: [domain_joined, local_account, guests_denied, domain_admins, enterprise_admins]
    - all_of: [standalone, guests_denied]
    - everyone
```

**Readability correction:** The first draft mixed `at_least_one_item_exists: true` (Boolean) and `at_least_one_collected_item: {trustee_name: ...}` (a predicate map). That looked like a missing `true` value and concealed the original field-value requirement. This corrected **research-only** sketch gives each part one job: `expect` describes which fields match; `require.collected_items.exist` counts collected user-right Items; `require.collected_items.satisfying` counts how many Items satisfy `expect`; `observed_values` separately requires at least one `trustee_name` value and all observed values to equal Guests ignoring case. It corresponds structurally to original `collected_items_require: at_least_one_exists_and_some_match` and field `require: at_least_one_exists_and_all_match`. All six-state behavior still requires independent proof. **No Boolean is missing**, and no new normative schema has been adopted.

**Works for people:** typed data source, purpose, alternatives, and referenced checks are in one reading flow. **New challenges:** `one_of: ['1','3']` must not casually collapse two record State alternatives or alter `value_match`/six-state semantics. The user-right collection may contain many principals; `at_least_one_collected_item` is essential and must not become `every_collected_item`. Need separate record and nested-field cardinality and a clear way to define/reuse a named Object once.

## 2. RHEL 9 — account-derived initialization-file collection

Source: [SV-257889 shared Assessment](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml). **Two real Tests plus three named shared Objects.** Both use `unix.password` account Sets and Filters, project `user.home_dir` through Object-level `for_each`, discover dotfiles while filtering out directories, and check eight permission/flag fields. The non-system-user Test uses `collected_items_require: may_be_absent_and_all_match`; the root-user Test instead uses `at_least_one_exists_and_all_match`. The Assessment `evaluate` requires both.

**English reading:** “For the selected non-system-user home directories, check all initialization files if any exist. For root's selected home directories, at least one initialization file must exist, and every file must satisfy the permission restrictions. Both checks must hold.”

```yaml
# Illustrative structure ONLY
checks:
  non_system_files:
    check: Non-system users' local initialization files have safe permissions
    inspect: unix.file
    collect:
      for_each:
        item: user
        in: non_system_users  # named unix.password Set + Filters
      where:
        directory: {from: user.home_dir}
        name: {matches_regex: '^\.[^\s\.]+'}
      exclude:
        type: directory
      traversal: {max_depth: 1, recurse: symlinks}
    require:
      items_may_be_absent: true
      every_collected_item:
        setuid: {equals: false}
        setgid: {equals: false}
        group_write: {equals: false}
        # five more source fields omitted: see real Assessment
  root_files:
    check: Root's local initialization files have safe permissions
    inspect: unix.file
    collect:
      for_each:
        item: user
        in: root_users  # different named password Set and Filters
    require:
      at_least_one_item_exists: true
      every_collected_item: {permission_predicates: use_original_eight_fields}
evaluate: {all_of: [non_system_files, root_files]}
```

**Works for people:** explains account→file projection and two different existence conditions. **New challenges:** `for_each` here **collects a combined target File population**; `every_collected_item` then checks that already collected population. These are separate stages. The placeholders above are *explicit*, not invented built-in operators. Shared account Sets/Filters, union aggregation, zero-source-Item errors and exact traversal must be retained. `items_may_be_absent` and `at_least_one_item_exists` are parallel phrases, but extending this style to all original existence modes may require too many Boolean keys.

## 3. Windows Server DNS — dynamic zone selection and alternative ways to pass

Source: [SV-259345](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml). **Five real Tests, three command-building Variables and one named zone collection.** Its `evaluate` is **OR** of: caching-only (no zones), all forward zones AD-integrated, or **all three** of DNSSEC-signed, zone-signing key period, and key-signing key period. Commands interpolate the observed forward-zone names and check `stdout_line` results; the period checks enforce both `>=48` and `<=168` hours.

**English reading:** “Pass if there are no relevant zones, or no forward zone is outside AD integration, or the DNSSEC signing and both key-period checks pass together.” This sentence deliberately **does not** assert that zone-by-zone correlation is already proven by the source.

```yaml
# Illustrative references to real Tests; no new collector semantics implied
checks:
  caching_only:
    check: No relevant forward or reverse lookup zones
    inspect: independent.shellcommand
    collect: {command: "Get-DnsServerZone ... [full source command]"}
    require:
      at_least_one_item_exists: true  # command-result Items, not DNS zones
      every_collected_item:
        stdout_line:
          no_values_exist: true
  zone_signed:
    check: Forward lookup zones report DNSSEC signing enabled
    inspect: independent.shellcommand
    collect: {command_from: command-get-issigned-setting-each-forward-lookup-zone-variable}
    require:
      at_least_one_item_exists: true
      every_collected_item:
        stdout_line:
          exactly_one_value_exists: true
          every_value: {equals: 'True'}
  # Additional real Tests: all_AD_integrated, zone_period, key_period
evaluate:
  any_of:
    - caching_only
    - all_AD_integrated
    - all_of: [zone_signed, zone_period, key_period]
```

**Works for people:** alternatives and their dependencies are easier to spot. **New challenges:** `no_values_exist` and the presence of command-result Items are different; a command returning no lines is not necessarily zero collected Items. The three native Variables build commands from actual zone-name observations; replacing them with an unverified `for_each: zones` could change per-zone aggregation, command execution, status, provenance, or error behavior. The English summary must **not** invent new DNS policy rules.

## 4. Apache 2.4 UNIX — included configuration and optional settings

Source: [SV-214228](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml). **Four real Tests, 18 local Variables and a shared Apache installation collection.** The Variables build the active config path, discover Include/IncludeOptional files and loaded configs, and compose command arguments. `evaluate: all` requires four checks: `KeepAlive On` in primary/include files; any directive in other loaded files must also be On; `MaxKeepAliveRequests >= 100` in primary/include files; optional occurrences elsewhere must also meet the limit.

**English reading:** “Find Apache's actual configuration. Check KeepAlive and MaxKeepAliveRequests in the main/included files; if those directives occur in other loaded files, check all those occurrences as well.”

```yaml
# Illustrative structure ONLY; actual Variable graph intentionally NOT erased
checks:
  primary_keepalive:
    check: Main/included configuration requires KeepAlive On
    inspect: independent.shellcommand
    collect: {command_from: shell-command-check-keepalive-in-httpd-conf-all-include-conf-variable}
    require:
      at_least_one_item_exists: true
      every_collected_item:
        stdout_line:
          every_value: {matches_regex: '\s*KeepAlive On'}
          at_least_one_value_exists: true
  other_keepalive:
    check: If any other loaded configuration defines KeepAlive, it must be On
    inspect: independent.shellcommand
    collect: {command_from: shell-command-check-keepalive-in-all-loaded-conf-files-variable}
    require:
      at_least_one_item_exists: true
      every_collected_item:
        stdout_line:
          values_may_be_absent: true
          every_value: {matches_regex: '\s*KeepAlive On'}
  # The two MaxKeepAliveRequests tests use the same structure with
  # a typed subexpression >= 100 and separate requirement scopes.
evaluate: {all_of: [primary_keepalive, other_keepalive, primary_max_requests, other_max_requests]}
```

**Works for people:** “required here; optional but constrained there” is readable and inspectable. **New challenges:** readers need to see where `command_from` comes from; a named `collect`/discovery graph or shared source module may be better than 18 generated Variable names, but is **not yet proven lossless**. Optional field presence must not become optional command-result Items, and shell exit/stderr error settings still matter.

## 5. Windows registry alternatives — a clean intermediate case

Source: [SV-253254](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/main/focused-fixtures/source-backed/authoring/ms_windows_11/assessments/automated/SV-253254.automated.yaml). One collected registry Item tests `EditionId` with two allowed **State combinations**, each requiring the field `type=string` and either `value=Enterprise` or `value=EnterpriseS`.

```yaml
# Illustrative, not approved; preserves two explicit conjunction branches
check: Windows EditionId is Enterprise or EnterpriseS
inspect: windows.registry
where:
  hive: {equals: local_machine}
  key: {equals: 'SOFTWARE\Microsoft\Windows NT\CurrentVersion'}
  name: {equals: EditionId}
require:
  at_least_one_item_exists: true
  every_collected_item:
    satisfy_any_of:
      - all_of: [{type: {equals: string}}, {value: {equals: Enterprise}}]
      - all_of: [{type: {equals: string}}, {value: {equals: EnterpriseS}}]
```

**Works for people:** field names are local to the collection; two alternatives are easy to scan. **New challenges:** the shorthand still needs explicit presence/matching requirements for each `type` and `value` field (or a single clear, explicit `state_fields_require` scope); it must preserve `states_match: any` and missing/unknown/error propagation. `satisfy_any_of` is an illustration of the aggregation, not automatically ordinary two-valued OR.

## Where the idea holds — and where it breaks

| Tested source pattern | English-first readability | Current proof boundary |
| --- | --- | --- |
| Simple Linux `/home nosuid` | **Strong:** purpose, selector, item/option populations immediately visible | Membership operator needs precise type and source semantic lowering |
| Registry alternatives | **Good:** two accepted State branches | Field requirements and alternative-State semantics still explicit |
| Windows user-right + WMI | **Moderate:** domain alternatives readable as named checks | Multi-valued principals, nested records, `some` vs `every` matching |
| RHEL user→file `for_each` | **Moderate:** source/target projection visible | Zero Item and ObjectComponent errors, filter/Set and union semantics |
| DNS zone-sourced commands | **Mixed:** top-level OR logic clear | Dynamic command-building and per-zone provenance not simplified safely |
| Apache multi-file configuration | **Mixed:** compliance intent clear | Deep Variable/command graph remains extensive |
| State-free absence; rare `none`, `one`, `odd`, `all_exist` | **Not yet exercised here** | Must support full original scope/quantifier matrix before 0.4 |

## Four lessons for the next 0.4 candidate

1. **Treat the two stages separately:** first collect/expand the Item population (`inspect`, `where`, `for_each` as needed), then evaluate the already collected Items (`every_collected_item`, `at_least_one_collected_item`, etc.). Do **not** call these both `for_each`.
2. **Explicit, readable existence:** `at_least_one_item_exists: true` is easier to guess than `at_least_one_found`, but the Boolean-per-mode family may become too large. Compare with `items_exist: at_least_one` across *all five* original existence modes. Do not treat `all_exist` as simple non-emptiness.
3. **Reuse readable named checks and collections:** high-level `any_of`/`all_of` (if formally lowered to original six-state operators) is readable and scales; resource acquisition, Variables and shared Objects need independently understood descriptions and provenance. Avoid unsupported `if/else` normalization.
4. **Require source-backed counterexamples before grammar freeze:** no missing statuses, unproven typed field aliases, or invented filters. Formally prove the five existence × four match cardinality combinations, State-free special cases, nested records, array/Variable `value_match`, partial collection, and evidence.

**Preliminary verdict:** English-first is a real improvement for **what** an Assessment checks, and for small-to-medium explicit check trees. It cannot yet replace the underlying complex collection/evaluation model for DNS, Apache and user-derived files. To become **THE** 0.4 grammar rather than a second façade, it needs one complete, precise way to express unusual quantifiers, typed dynamic dependencies and six-state results. That is the remaining technical work, not a reason to abandon the readability goal.

Decision tracking: [#227](https://github.com/vanderpol/scap-ng/issues/227) · [#229](https://github.com/vanderpol/scap-ng/issues/229) · [cardinality wording options](CARDINALITY-READABILITY-OPTIONS.md) · [actual 0.4 r3 complex examples](COMPLEX-REAL-WORLD-EXAMPLES.md).
