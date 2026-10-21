# SCAP-NG 0.4.0 examples — Assessments

**Current source-backed YAML/JSON authoring samples:** [immutable October 21 canonical source-only release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-canonical-flat-authoring-20261021). The [October 20 pre-release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) is immutable and uses the preceding authoring revision. Begin with [Benchmarks and Rules](README.md) for the policy context.

A **Test** states what information to collect using `capability` and `object`, then what must be true using `require`. `evaluate` combines Test results. SCAP-NG retains these familiar OVAL concepts while reducing indirection in ordinary checks.

## 1. A simple automated Test

**0.4.0 flat-Object grammar update (2026-10-21):** Native selectors and acquisition parameters live directly in `object`, without generic `select` or `collect` wrappers. Short complete comparisons may use one-line flow mappings; longer or complex Objects may be multiline. The current October 21 regenerated six-STIG candidate has passed strict native schema, exact source inverse, and independent package CI; the October 20 tagged pre-release remains the older baseline. No compiled or signed scanner bundle is claimed.

This small **syntax illustration** is deliberately shortened. It is *not a verbatim STIG Assessment*. For source-backed rule logic, use the complete, source-verified files in the current immutable authoring release.

```yaml
tests:
  home-mount-requires-nosuid-test:
    test_title: The /home mount must use nosuid
    capability: linux.partition
    object: {mount_point: {equals: /home}}
    require:
      items: one_or_more
      all_items_must:
        - mount_options:
            require: at_least_one_exists_and_all_match
            equals: nosuid

evaluate:
  test: home-mount-requires-nosuid-test
```

Read this in order: the Test collects partition Items with `linux.partition`; `object` selects the `/home` mount; `items: one_or_more` requires at least one match; and `all_items_must` requires each selected Item to have the expected mount option. **Item existence and matching are separate requirements.** The inline Object inherits the Test's capability, so repeating `object.capability` is unnecessary.

For simpler State-free Tests, the source-backed 0.4 syntax can express explicit existence, for example:

```yaml
require:
  items: none
```

This means the corresponding collected Item population must be empty; it is not permission to treat collection errors as an empty result.

## 2. Multiple Tests and Boolean logic

When an Assessment needs several Tests, leave **one blank line between Test declarations** and **one blank line before `evaluate`** in the YAML. Indent list entries beneath their parent key. No decorative separator comments or redundant Test-title comments are necessary.

```yaml
tests:
  domain-member-test:
    test_title: The system is a domain member
    capability: windows.wmi.query
    object: domain-membership-query
    require:
      items: one_or_more

  remote-logon-local-account-test:
    test_title: Remote logon restriction includes local accounts
    capability: windows.userright
    object: remote-logon-deny-right
    require:
      items: one_or_more

evaluate:
  all:
    - test: domain-member-test
    - test: remote-logon-local-account-test
```

This is **illustrative structure**, not the original Windows STIG logic. The source-backed Windows examples have additional record and trustee matching requirements that must not be dropped when editing or simplifying. The `and`/`or` and `any`/`all` meaning must be taken from the versioned `evaluate` contract, not guessed from indentation.

**Name Tests and Objects by their purpose or selected data**, not solely the collection technology. For example, `domain-membership-query` is more informative in demonstration material than `windows-wmi57-object`. The 0.4 capability name should come from the schema, such as `windows.wmi.query`; a legacy OVAL identifier like `wmi57` belongs in source provenance, not an invented new capability. **Existing converted logical IDs are not renamed merely for presentation**: renaming demands complete reference/provenance validation.

## 3. Manual alternatives and exceptional Assessments

Rules may offer both automated and manual Assessment choices. A Rule's explicit `default_assessment_choice` does not remove the other choice or its provenance. All **2,958 Rule choice links** in the six-STIG authoring set are retained.

Of the **1,375 distinct automated Tests**, 816 use canonical `all_items_must`, 387 have structured presence-only requirements, and **172 retain source-exact uncommon requirement forms**. The latter are not silently rewritten into attractive shortcuts.

## 4. What validation proves

The 4,001 authored documents validate against the current version-local schema in both YAML and JSON, and the typed-source graph roundtrips; **25,628 generic OVAL result comparisons** have also passed. These checks do *not* prove collection-capability behavior, signed-bundle compilation, scanner execution, or final OVAL equivalence. Four zero-Item/empty-aggregate reference scenarios remain explicitly unresolved.

See [release gates](../../review/current/0.4.0-FINALIZATION-GATES.md) for the exact evidence. **Archived 0.3.0 examples and synthetic results** are available from [the 0.3.0 archive](../../archive/0.3.0/README.md); they must not be mistaken for actual 0.4 scan output.
