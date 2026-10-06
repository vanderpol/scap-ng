# Straw-man authoring syntax

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**

This file defines no normative vocabulary. It records the smallest syntax that
appears sufficient for the first real RHEL 9 examples.

## Working idea

Use a module/capability-like block for acquisition and keep expectations beside
it:

```yaml
check:
  file:
    path: /etc/example.conf

  expect:
    exists: at_least_one
    all:
      owner_id: 0
```

The words are provisional. The important experiment is **locality**, not whether
the final key is named `file`, `collect`, `expect`, or something else.

## Semantic rules that are not optional

A compiler for any simplified form must still make these explicit in the typed
semantic IR when they matter:

- collection capability;
- selector operation and datatype;
- collection status and errors;
- existence requirement;
- item aggregation;
- state/entity comparison;
- entity existence/check;
- Boolean `all / any / not`;
- evidence/reporting behavior;
- source provenance.

The authoring layer MAY infer a value only where the syntax has exactly one
defined meaning. If two meanings are possible, the author must choose.

## Locality rule

Inline a collection or expectation when it is private to one check.

Name it only when at least one of these is true:

1. it is intentionally reused;
2. another check depends on one of its collected fields;
3. the author needs a stable reusable abstraction;
4. readability is genuinely improved by naming it.

This is a research hypothesis, not a schema rule.

## Composition

Multiple local checks should read as normal Boolean composition:

```yaml
check:
  all:
    - systemd:
        unit: example.service
        property: LoadState
      expect:
        value: masked

    - systemd:
        unit: example.service
        property: UnitFileState
      expect:
        value: masked
```

The compiler remains responsible for lowering this to typed Test/Object/State
semantics with the original existence/check rules.

## Local derived values

When a value is genuinely needed by several operations, prefer a local
`let`-style binding over a distant top-level Variable:

```yaml
check:
  let:
    audit_dir:
      from:
        text:
          path: /etc/audit/auditd.conf
          pattern: ...
        field: capture[1]

  all:
    - ...
```

This does not mean SCAP-NG should literally adopt Jinja, Ansible expressions, or
this exact syntax. The experiment is testing whether the dataflow can remain
near the security requirement instead of requiring the author to reconstruct a
global dependency graph.

## Commands

Command checks should be concise when the requirement is inherently
command-oriented:

```yaml
check:
  command:
    shell: bash
    run: rpm -Va --noconfig | ...
  expect:
    stdout: empty
```

Native typed collectors remain preferred where scanner-aware collection
semantics matter.


## Organizational input

Organizational input is a first-class part of this authoring experiment.

The simplified authoring layer should make a policy-dependent check read like
the requirement itself, for example:

```yaml
inputs:
  approved_time_sources:
    type: string_list
    required: true
    provenance: organization

check:
  chrony:
    servers: discovered

  expect:
    every:
      server:
        in: approved_time_sources
```

or:

```yaml
inputs:
  approved_local_accounts:
    type: string_list
    required: true
    provenance: organization

check:
  users:
    local: true
    interactive: true

  expect:
    every:
      username:
        in: approved_local_accounts
```

The exact syntax is provisional. The important semantic requirements are:

- organizational input supplies **state values / policy facts**, not new
  collection or execution logic;
- the scanner MUST NOT rewrite or mutate the authored assessment based on input;
- provenance is mandatory for supplied organizational values;
- missing required input must produce a defined non-pass outcome rather than
  silently substituting a default;
- input values must be typed and constrained by the target field/domain;
- the same authored assessment should remain portable between organizations,
  with local policy supplied separately;
- results must record which organizational input values materially affected the
  decision, subject to redaction policy.

This should be tested as part of the simplified-authoring feasibility study,
especially for currently manual RHEL 9 Rules whose host evidence is measurable
but whose pass/fail decision depends on approval or local policy.
