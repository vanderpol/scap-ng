# 0.4-C Windows 11: seven checks, two observations, one readable policy

**19 October 2026 — research [#245](https://github.com/vanderpol/scap-ng/issues/245), NOT accepted C authoring grammar, source scanner, or normative specification.**

[Source-compatible C research reviewer sample](c-source-exact-windows-rdp-rights.research.yaml) · [Real Windows 11 SV-253495 source](../../requirements-first-language/contract-candidate/corpus/source-specimens/windows-userright-1-39dad4df5336.source.yaml) · [bounded adapter](../../../tools/research_c_windows_shared_observations.py) · [tests](../../../tools/test_research_c_windows_shared_observations.py).

## Why this is a stronger test than one Registry check

Real Windows 11 SV-253495 denies Remote Desktop logon for different trustees depending on domain role. Its original Assessment has **seven Tests**, **two shared Objects**, and an **OR of three branches** (two contain AND groups). C presents two typed observations and seven named requirements rather than a separate collector configuration in each check.

| Shared observation | Original source | Consumers |
| --- | --- | --- |
| System role | WMI: SELECT DomainRole FROM win32_computersystem | Domain-joined non-DC; standalone |
| Denied Remote Desktop trustees | Windows userright: SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME | Local accounts, Guests, Domain Admins, Enterprise Admins, Everyone |

The original content already reuses two Objects. C's first improvement is **auditor organization**, NOT yet fewer runtime acquisitions, smaller compiled evidence or measured scanner performance.

## First-read auditor view

Observations: **System domain role** and **accounts denied Remote Desktop logon**.

Checks: **domain-joined non-DC**, **standalone**, **Local Accounts denied**, **Guests denied**, **Domain Admins denied**, **Enterprise Admins denied** and **Everyone denied**.

~~~
Accept when ANY branch is true:
  1. Domain-joined non-DC AND Local Accounts denied
     AND Guests denied AND Domain Admins denied
     AND Enterprise Admins denied
  2. Standalone workstation/server AND Guests denied
  3. Everyone denied
~~~

This is **not** an IF/ELSE chain: errors, unknown, not-evaluated and not-applicable outcomes remain six-state results. The Test checks on the same source may also be evaluated independently.

## Hidden ambiguity we must avoid

The WMI Test's two alternative **whole-record** States are combined by any-state; within each record State, all collected DomainRole values must equal a particular literal, and the field must exist. It is NOT proven equivalent to a generic "some DomainRole belongs to 1 or 3" when a record has multiple values.

The precise C research view therefore retains all of the scopes:

~~~yaml
must:
  items: every_item
  record: result
  record_requirement: at_least_one_exists_and_all_match
  field: domainrole
  field_requirement: at_least_one_exists_and_all_match
  any_record_state_every_value_equals: ['1', '3']
~~~

This is too verbose for an *initial* editor card, but useful in Expert details. A Guided editor can present the security meaning while retaining the original Item/record/field distinctions and exact expansion. The source trustee Tests require at least one matching Item with exact source regex/case-insensitive predicates. One shared observation is not one combined outcome.

## Executable gates

- Extract all seven Test requirements, both exact source collection requests and the original three-branch expression; refuse source predicate, selector, nested-record, cardinality and logic mutations.
- Compare the entire checked-in reviewer sample against the source-generated C view and reconstruct the original 0.3 source without changes.
- Compare 128 Boolean leaf assignments and mixed six-state scenarios against the independent source-expression oracle. These are **supplied Test results**, not actual Windows collection or a complete C language compiler.
- A concrete YAML portability defect was found by regression: PyYAML interpreted bare *on:* as Boolean key true. The view now uses *observation:* and the C strict loader rejects boolean-coerced keys rather than silently accepting them. A concise word is not worth an ambiguous parser contract.

## Graphical editor hypothesis — remain within C research

A desktop editor could provide three clear panes or sections: **Observations** (named acquisitions with provenance), **Checks** (one observation and explicit Item/field predicates per card), and **Requirement** (an AND/OR tree over the checks). Advanced record/cardinality, raw selectors and source identity remain expandable; the first-read view remains short. Never let GUI display strings independently redefine evaluation semantics. C will feed the editor only after the grammar and compiler are independently verified.

## Open decision gates

The pinned witness is a converted **0.3** source, not a fully executable 0.4-A authored Assessment, and no live WMI/userright collection is demonstrated. A real C authoring compiler must accept a source-independent C document, use reviewed A provider contracts, compile into one execution IR, and independently validate nested multi-field records, errors, provenance, complete six-STIG coverage and auditor comprehension. Short review aliases alone are not a reduction in underlying acquisition mechanics.

**Recommendation: continue C**, particularly shared observations and compiler-supported Guided authoring, but do not freeze it or declare A equivalence.
