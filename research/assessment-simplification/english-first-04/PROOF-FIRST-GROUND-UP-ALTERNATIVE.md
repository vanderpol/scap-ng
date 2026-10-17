# Last ground-up alternative: evidence, claims, and ways to pass

**October 17, 2026 — radical design exploration / NO ADOPTION.** Issue [#235](https://github.com/vanderpol/scap-ng/issues/235). This is neither an approved 0.4 authoring grammar nor a source-reversible whole-corpus conversion, and it does not supersede the pinned source evidence. **The purpose is to decide whether a different mental model is more understandable**, not to invent more aliases.

## Review disposition — reject the YAML redesign, retain the explanation concept

The owner identified unnecessary nesting, particularly `claims.<id>.valid.all`, on October 17, 2026. **Disposition: do not pursue `observe/claims/pass_if` as a replacement 0.4 YAML language in its current form.** It renames existing concepts and introduces wrappers without a corresponding new semantic distinction. The illustrations below are a retained historical thought experiment, **not the recommended authoring syntax**.

Every author-facing wrapper must supply a distinct, necessary semantic boundary. In this experiment:

- `valid` does not define one; its child quantifier already expresses the required matching scope. **Remove.**
- `observed` describes Item existence ambiguously; `items` expresses it more precisely. **Do not rename.**
- `on` merely renames `from`; `using` merely renames `inspect`. **Do not rename without proven benefit.**
- `claims` is substantially a rename for named `checks`; `observe` renames typed `sources`; `pass_if` renames `evaluate`, and could falsely imply only Boolean pass/fail rather than the six-state technical result model. **Do not change the normative vocabulary for aesthetic reasons.**
- **Keep** the useful *reader model*—facts collected, requirements checked, and acceptable decision paths—as a generated auditor preview of the **single existing Assessment**. Named passing routes may be editor/presentation labels that preserve the original `evaluate` expression.

The following is the shorter, source-backed **current research candidate**, not newly approved normative 0.4:

```yaml
checks:
  home_uses_nosuid:
    from: home_mounts
    require:
      items: at_least_one
      match: all
      mount_options:
        at_least_one_value_equals: nosuid
```

Do not silently omit `require`: it currently distinguishes the predicate's technical requirements from acquisition and descriptive metadata. Its removal needs a separate reserved-name and compiler proof. Do not redefine `all` as both Item matching and field-value matching; the latter may be `at_least_one_value_equals` (e.g., the `rw,nosuid` case).

**Design check before proposing new nesting:** if deleting a key changes neither scope, cardinality, acquisition, evaluation order, reference identity nor error propagation, the key is a strong removal candidate. Field absence and legacy `all_exist` semantics still require independent work, not hidden defaults.

---

## The underlying diagnosis

People do not think in OVAL Tests/Objects/States and their implementation-scoped check/existence operators. They think: **what facts did we observe → what assertions can we make about those facts → which complete combination constitutes compliance?** Changing `require` vocabulary does not simplify the Apache 18-Variable dependency chain, a seven-Test Windows Boolean tree, or a Linux account-dependent file search.

This proposal starts with those three concepts as the **only top-level technical constructs**:

1. **`observe`**: named, typed facts and discovery graphs, including selectors, Sets, dependent collection, variables, and provenance.
2. **`claims`**: atomic assertions about one population. Each names separately *the existence criterion* and *which observed Items must satisfy what*. A claim is evaluated as a single technical operation; its clauses must **not** be lowered to independent Boolean tests without OVAL six-state proof. The same grammar nests into records and field values.
3. **`pass_if`**: named, explicit **alternatives** combining complete claims via original OVAL-equivalent `and`/`or`; no procedural `if/then/else` or first-match priority.

This is proposed as **one replacement authoring grammar**, not a second dialect used alongside `checks/evaluate` in a normative 0.4 package. During evaluation it remains an isolated research sketch. The compiled scanner representation would be generated and signed, never an extra independently maintained prose rule.

## Example 1 — RHEL 9 /home nosuid (real converted Assessment)

Existing best split candidate, stripped of surrounding metadata:

```yaml
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\/home'}
require:
  items: at_least_one
  match: all
  mount_options: {at_least_one_value_equals: nosuid}
```

Alternative:

```yaml
observe:
  home_mounts:
    using: linux.partition
    where:
      mount_point: {matches_regex: '.*\/home'}
claims:
  home_uses_nosuid:
    on: home_mounts
    observed: at_least_one
    valid:
      all:
        mount_options:
          any_value: {equals: nosuid}
pass_if: home_uses_nosuid
```

The claim reads: *observe /home mounts; require at least one such Item; all observed Items must have at least one `nosuid` mount-option value*. `any_value` is an explicit field-value quantifier, not a replacement for Item-level `valid.all`. The selector's original regex remains unchanged.

**Immediate candid result: this is LONGER and not convincingly better for a single simple Test.** A design that wins only on formal elegance but loses the simplest example may not be worth adopting. The rest of this experiment asks whether complex readability outweighs that cost.

## Example 2 — Windows WMI records and independently scoped matching (real SV-253495)

```yaml
observe:
  computer_role:
    using: windows.wmi.query
    collect:
      namespace: 'root\cimv2'
      query: SELECT DomainRole FROM win32_computersystem
claims:
  domain_member:
    on: computer_role
    observed: at_least_one
    valid:
      all:
        states:
          or:
            - result:
                records:
                  observed: at_least_one
                  valid:
                    all:
                      domainrole: {equals: '1'}
            - result:
                records:
                  observed: at_least_one
                  valid:
                    all:
                      domainrole: {equals: '3'}
```

Interpretation: Every computer Item must satisfy **one whole alternative**. In the first, every record must have role 1; in the second, every record must have role 3. If one Item has records `[1,3]`, **neither alternative is true**. A general `domainrole in ['1','3']` transformation would falsely pass. This candidate is longer than the current one but gives the same visible pattern of `observed`+`valid` for both Items and records. The source has a seven-claim decision tree, not just this fragment.

### The improvement that may matter most — name the complete passing routes

The original SV-253495 contains seven checks and a final `or` of three branches. An auditor-first authoring structure could retain all seven claims and display the alternatives as:

```yaml
pass_if:
  or:
    - case: domain_joined
      and:
        - domain_member
        - deny_local_account
        - deny_guests
        - deny_domain_admins
        - deny_enterprise_admins
    - case: standalone
      and:
        - standalone_computer
        - deny_guests
    - case: deny_everyone
      claim: deny_everyone
```

The names above are **proposed editor aliases**, not original Test IDs; a converter must preserve a one-to-one mapping to each source check and the original `or(and(...),and(...),...)` graph. `case` is a label on an OR branch, NOT a procedural conditional. No reordering or short-circuit execution semantics should be invented. The full source also has two named WMI/userright collectors and five userright comparisons.

## Example 3 — dependent Linux account → file permissions (real SV-257889)

Keep the original ordered observation graph: selected user account Sets, separate source exclusions, `for_each` of users' home directories, actual path/name selector, filesystem traversal, one-operand union and exclusion of directory Items. These **cannot** be replaced by an invented `non_system_users` primitive without an actual collector contract and source-status proof.

Once observed, the claims are understandable:

```yaml
claims:
  non_system_init_files_safe:
    on: non_system_init_files
    observed: if_present
    valid:
      all:
        fields:
          presence: all
          and:
            - setuid: {equals: false}
            - setgid: {equals: false}
            - sticky: {equals: false}
            - group_write: {equals: false}
            - group_execute: {equals: false}
            - other_read: {equals: false}
            - other_write: {equals: false}
            - other_execute: {equals: false}
  root_init_files_safe:
    on: root_init_files
    observed: at_least_one
    valid:
      all:
        fields:
          presence: all
          and:
            - setuid: {equals: false}
            # Seven other exact source fields as above
pass_if:
  and:
    - non_system_init_files_safe
    - root_init_files_safe
```

**Critical detail:** zero non-system-user files is allowed by that claim, while zero root files is not. The eight field existence checks apply to returned Items in either branch. The observation graph remains essential; a pleasant claim cannot excuse deleting it. Literal `equals: false` tests are real data comparisons and should not be removed.

## Examples 4 and 5 — DNS / Apache patterns

**DNS signature-validity requirements** involve separate zone/key-signing collectors, three dynamically composed PowerShell commands, and a multi-State `and` of `stdout_line >= 48` and `stdout_line <= 168`. A proof-first claim could be:

```yaml
claims:
  zone_signing_validity:
    on: zone_signing_hours
    observed: at_least_one
    field_policy: required     # Inherited State-field scope, not record scope
    valid:
      all:
        states:
          and:
            - stdout_line: {greater_than_or_equal: 48}
            - stdout_line: {less_than_or_equal: 168}
```

`field_policy: required` above is **only a proposed place** for the original Test-level `all_state_fields_exist` semantics; a six-state proof must determine the exact typed meaning and whether it is redundant. It is not a settled addition.

**Apache's optional KeepAlive field** proves why a claim's Item population must be independent of field-value presence:

```yaml
claims:
  optional_keepalive_overrides_safe:
    on: loaded_apache_config_directives
    observed: at_least_one
    valid:
      all:
        stdout_line:
          if_present: {matches_regex: '\s*KeepAlive On'}
```

The surrounding Apache real Assessment has FOUR checks and an **18-variable dependency graph**. This sketch does not magically shorten that graph. A typed `apache.loaded_config` collector could, but would be a **new capability** requiring its own acquisition/error/completeness tests, not merely a syntax rename.

## Source-preservation and error boundaries

- `observed` and `valid` are different, explicitly typed quantities. `observed: exactly_one` means one Item *exists*; `valid: exactly_one` means exactly one collected Item *matches*. They cannot be collapsed into one label.
- Root Items, repeated field values, records, record members, expected-value arrays and named source Sets are **different population types**; the grammar can recurse but must not let a quantity silently change its target.
- Preserve all distinct OVAL existence/cardinality pairs, including source-legacy `all_exist` as an explicitly labeled import compatibility case until proven redundant. No implicit `at_least_one` when source is optional or unknown.
- Missing/error/unknown/not-applicable and incomplete collection are first-class six-valued outcomes. `claims.observed` + `claims.valid` are **atomic Test-style assertions** with source evaluation order. They are NOT separately evaluated booleans combined by ordinary AND.
- `states.or` combines **whole States**, not independent membership tests over a record collection. `pass_if.or` combines **whole claim outcomes**, not priority conditions.
- No generic complement/`not` rewrite, regex inversion, heuristic fallback to shell/manual, implicit resource identity, inferred typed-variable input, or invented source selectors.
- Evidence reporting and original Test/source IDs remain metadata tied to claims. A human-friendly `case` name never replaces provenance.
- The one known bootloader source `none_exist`+State inconsistency remains a rejected source, not an opportunity to invent undefined semantics.

## What changes relative to the existing 0.4 research

| Aspect | Existing `sources` / `checks` / `evaluate` | Proposed `observe` / `claims` / `pass_if` |
| --- | --- | --- |
| Normal simple Assessment | Very compact (advantage) | More setup and IDs (disadvantage) |
| Complete seven-Test Windows decision | OR/AND references require mental reconstruction | Named **passing cases**, still OR of AND (potential advantage) |
| Nested Items / States / records | Correct but specialist terminology | Repeating `observed` / `valid` at each typed population (potential advantage; more lines) |
| Deep Linux/Apache discovery | Separate named collectors/Variables and recursive Sets | Explicit named observation graph; **no inherent complexity reduction** |
| Exceptional field existence | Unfinished legacy flags | **Still unfinished**; needs one formally proven policy |
| Audit explanation | Human author writes Test titles; notes external | Render a typed **proof sheet automatically from the parsed assertions and pass routes** |
| Standardization cost | Extensive existing schema/compiler work | Major new parser, schema, migration and interoperability risk |

## Recommendation, even if the new idea is rejected

**Do not promote this as v0.4 merely because it looks different.** The core three-part *mental model* is a stronger way to explain assessments, but its literal YAML is **not clearly superior** to our current split-requirement candidate. It increases lines in easy cases and retains unavoidable OVAL cardinalities in difficult cases. The genuine gains are (a) named observations in dependency order, (b) named atomic claims with their populations, and (c) visible, named passing paths.

The test that should decide is a **deterministic auditor proof sheet** generated from the **existing single authoritative Assessment AST**, not separate hand-written Markdown. It should show for each claim: source, Items required, matched Items required, required/missing fields, nested record contract, pass/fail/unknown behavior, and precisely which `pass_if` route combines it. Use a guided editor to create the same authoritative syntax. If a readability study proves the radically reorganized syntax itself is better, revisit the normative grammar; otherwise keep the current split requirement semantics and stop renaming.

## Hard gates for changing the one normative language

1. Create typed AST and exact invertible lowerer for all 871 supported six-STIG automated Assessments. The current sketches are **not** that proof.
2. Run a differential six-state fixture suite, covering incomplete/error Items, field absence, WMI mixed records, duplicate Items and expected-value lists. The lack of an independent scanner does not prevent a specification-level reference evaluator; do not claim scanner conformance.
3. Test **blind**, with 0.3 vs current split vs proposed proof-first views: can unfamiliar auditors predict empty, duplicate, mixed, missing and error cases and identify the three Windows pass routes? Assess accuracy and time, not YAML line count.
4. Prove that editor guidance can construct a new ordinary Assessment without undocumented defaults or synthetic provenance, and can edit a complex Assessment with byte-stable unrelated source.
5. Preserve 0.3 releases and the working 0.4 draft. No Board or owner approval is inferred from a source-inversion test. Existing issues: [research #235](https://github.com/vanderpol/scap-ng/issues/235), [semantics #229](https://github.com/vanderpol/scap-ng/issues/229), [editor MVP #2](https://github.com/vanderpol/scap-ng-editor/issues/2).

## Exact source anchors

- [Current source-exact RHEL home assessment](canonical-operators/linux-home.canonical.research.yaml)
- [Current complete Windows 11 seven-Test assessment](canonical-operators/windows-wmi-rights.canonical.research.yaml)
- [Current account-derived Linux file assessment](canonical-operators/linux-files.canonical.research.yaml)
- [Current DNS assessment](canonical-operators/dns.canonical.research.yaml)
- [Current Apache assessment](canonical-operators/apache.canonical.research.yaml)
- [Baseline source inversion coverage](canonical-operators/report.md)
- [Previous full grammar complexity stress tests](COMPLEXITY-STRESS-TEST-ITERATIONS.md)
