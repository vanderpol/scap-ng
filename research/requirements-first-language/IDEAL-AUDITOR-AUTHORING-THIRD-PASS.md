# Third-pass auditor authoring candidate — typed facts, not OVAL-shaped predicates

**Research only. 17 October 2026. NOT adopted 0.4 and NOT implemented executable YAML.** Designed after two naive-review transcripts, internal cardinality counterexamples, a synthetic evaluation experiment, and a real read-only Linux mounts provider smoke test. None of these prototypes independently proves the SCAP 1.4 migration or the ability to implement all typed facts.

## What is different this time?

The earlier proposal still made the author start with quantified collections even when the requirement was simply "the registry setting" or "the service". That is the last remnant of OVAL's universal Object/Test/State machinery.

A better authoring interface may need **two complementary ways to express policy**, not one universal expression forcing everything into an iterator:

- **Named fact / resource:** when a capability has a uniquely identifiable subject, author the subject plus expected value. The provider contract declares identity and missing behavior.
- **Population rule:** when the requirement is genuinely about a set of resources, author a constrained collection. The requirement visibly states whether a population is mandatory and how its members are checked.

These are two syntactic shapes in one language with one evidence/result model, not two competing dialects. A guided editor can offer the natural shape for each typed capability.

## 1. Named resource: no false collection drama

**Illustrative new native check (NOT valid current prototype):**

~~~yaml
require:
  windows.registry_value:
    hive: HKLM
    key: 'SOFTWARE\Policies\Microsoft\Windows\Installer'
    name: AlwaysInstallElevated
    view: 64bit
    equals: 0
~~~

A real registry provider must specify key identity and view, whether the value can be absent, types and access errors. This does not authorize implicit coercion from a string "0" to integer 0.

## 2. Required population: the resource has to exist

~~~yaml
require:
  each: linux.mounts
  where:
    mount_point: {equals: /home}
  minimum_resources: 1
  must:
    mount_options: {contains: nosuid}
~~~

This is valid design *only if* the desired policy permits multiple selected mounts. A fully identified singleton mount provider cannot be substituted without explicit namespace/identity semantics. The earlier authored if_empty: fail is no longer favored for native policy; it expresses an evaluator outcome rather than the actual required population.

## 3. Optional population: no forced existence

~~~yaml
require:
  each: windows.accounts
  where:
    category: {equals: guest}
  must:
    enabled: {equals: false}
~~~

Zero **confirmed** guest accounts passes. Zero **observed in an incomplete scan** cannot pass. The positive minimum is absent because the policy does not require guest accounts to exist.

## 4. The real Windows 11 user-rights example: facts and alternatives

The source-faithful research Assessment has seven named checks and eight evaluation leaf references, including two distinct Windows WMI whole-State alternatives. A future **native** language might read:

~~~yaml
require:
  or:
    - and:
        - windows.computer_role: domain_joined_member
        - windows.deny_remote_logon:
            includes: [LocalAccount, Guests, DomainAdmins, EnterpriseAdmins]
    - and:
        - windows.computer_role: standalone
        - windows.deny_remote_logon:
            includes: [Guests]
    - windows.deny_remote_logon:
        includes: [Everyone]
~~~

This is intentionally an aspirational **native** policy, not source-equivalent executable code. A typed denied-rights provider can expose the complete configured trustee set and make list inclusion a *known cardinality* operation, avoiding four repeated userright collection blocks.

**Big source-compatibility danger:** a normalized domain_joined_member fact must preserve the original WMI behavior. The records [1,3] are a confirmed failure for the two original whole-State alternatives despite naive each-value membership in {1,3}. Native source mapping cannot casually redefine that as true; record status/error semantics still need proof.

## 5. Apache: typed facts make intent obvious, providers remain expensive

~~~yaml
require:
  and:
    - apache.directive:
        name: KeepAlive
        equals: 'On'
    - apache.directive:
        name: MaxKeepAliveRequests
        at_least: 100
~~~

A genuine apache.directive provider must expose instance identification, loaded Include hierarchy, source-file and line provenance, duplicate/effective settings, command exit/error conditions, and ambiguity. The four original source command checks cannot automatically be replaced by two native facts without evidence; if the data cannot be reconstructed, the converter must refuse lossless migration.

## 6. Nested Linux account-derived files: when collections really belong

~~~yaml
require:
  each: linux.accounts
  as: user
  where:
    uid: {at_least: 1000}
  must:
    each: linux.files
    using:
      under: '$user.home_dir'
      recursive: true
      max_depth: 5
    must:
      owner: {equals: '$user.username'}
~~~

This is a native **policy example**, not the source permissions rule. The collection model is the right tool here because users and files genuinely constitute sets. Lexical binding must preserve each user-to-file relationship when multiple users share a directory; missing user or file observations cannot be quietly dropped. The document must define the complete-zero semantics, even if each treats it as vacuous by explicit language contract.

## 7. Windows DNS: complexity remains legitimately present

~~~yaml
require:
  or:
    - windows.dns.mode: caching_only
    - each: windows.dns.forward_zones
      minimum_resources: 1
      must:
        directory_integration: {equals: active_directory}
    - each: windows.dns.forward_zones
      as: zone
      minimum_resources: 1
      must:
        and:
          - signed: {equals: true}
          - each: '$zone.signing_keys'
            minimum_resources: 1
            must:
              validity_hours: {between: [48, 168]}
~~~

This compresses away some source mechanics but **also leaves out** the original distinction between zone-signing and key-signing keys, the original four command-derived variables, and the separate test/state field semantics. It must NOT be called losslessly equivalent. It demonstrates that complex domain policies cannot always become one-liners without losing content.

## Strongest internal design conclusion so far

**Recommend a typed-resource-first authoring language with a visible collection escape hatch.** That is materially different from OVAL-in-YAML: simple checks do not require a generic Object, State, Test, existence check and evaluator graph; complex native checks use named, reusable platform facts and explicit population relationships.

Yet we must resist two failure modes:

1. **Magic providers:** a one-line windows.deny_remote_logon primitive cannot become an opaque, rule-specific compliant/not-compliant function. It should expose reusable raw configuration facts and source/field statuses.
2. **Fake conversion fidelity:** if a short source replacement cannot preserve original group cardinality, missing status or command failure behavior, it is a **new native policy**, not an automatic faithful conversion. The conversion pipeline may need a separate compatibility representation that ordinary auditors rarely author.

## Next evidence to collect before a normative choice

- A real Windows roles provider with per-record grouping, and synthetic WMI [1], [3], [1,3] and partial/error fixture outcomes.
- A reusable Apache config provider tested across Include topology and conflicting directives without hiding the source-file provenance.
- A real direct-authoring exercise with an unfamiliar auditor, starting with *writing* three new requirements rather than simply explaining these examples.
- A formal six-state native result and provider status contract, compatible with migrated result reporting but not copied blindly from legacy OVAL objects.
- Source-conversion reports listing native mappings, compatible fallbacks and unconvertible cases per benchmark.

**Gemini:** no external review required at this stage. The next useful independent critique is not "which keywords look nicer?" but "given actual provider contracts, can a novice author and correctly reason about a Windows WMI mixed-record check and Apache multi-file directive case?" Send only when those provider contracts and evidence fixtures are ready.
