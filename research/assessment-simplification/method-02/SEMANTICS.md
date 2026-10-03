# Proposed execution and accuracy contract

Every SHALL/SHOULD/MAY statement here is an **experimental proposal**, not an
amendment of current SCAP-NG. This is a bounded executable model, not a complete
assessment specification.

## Objects, Tests and States

An Object SHALL identify a typed population with stable Item identities and
collection status. Its fields MAY contain scalar observations or typed child
populations. A child relation SHALL retain its parent's identity. Providers
SHALL report facts, not publisher-policy compliance decisions.

A Test MAY express `every` plus an inline State in `require`, instead of naming
separate State wrappers that are not reused. Named reusable Objects, States and
Variables SHALL remain possible in the larger language. This prototype supports
only the inline subset. Existing supported Set/Filter/function/record semantics
SHALL NOT be removed because the examples do not need them.

The author SHALL state whether a complete empty population is allowed or a
violation. A partial empty population cannot prove either absence or universal
success. For a nonempty population, every selected Item must satisfy the State.
Unknown selection SHALL NOT silently discard an Item; an unknown/error predicate
is retained in the Test's uncertainty. Independent Objects SHALL NOT share an
implicit Item binding. Shadowed Item names SHALL be rejected.

The complete predicate AST SHALL be checked before acquisition/evaluation,
including branches excluded by an exception. Unknown fields, incompatible
operations and ambiguous multi-operator comparisons SHALL be rejected. The
prototype checks its three fixed record contracts; it does not validate/execute
the illustrative Object `scope` plans. A production compiler additionally SHALL
validate/implement every source-plan field and reject duplicate YAML keys. The
current prototype loads known checked examples with PyYAML; it is not such a
source compiler.

Expected types SHALL be explicit in provider/operation contracts. No Boolean/
integer/string coercion occurs. The proposed author view avoids repeated type
declarations on every comparison; a future compiler would need an explicit,
validated typed execution plan. This is a deliberate proposed departure from
the current independently declared capability shape, not permission to change
the accepted schema or infer incompatible capabilities silently.

## Result and proof rules

The bounded model evaluates true/false/error/unknown. `all` preserves a confirmed
false even beside uncertainty; `any` preserves a confirmed true. Otherwise error
precedes unknown. It does not implement not-evaluated/not-applicable source
behavior. The full language SHALL preserve required six-state behavior and
applicability semantics; the bounded four-state subset SHALL NOT become a
capability-retirement or result-domain-removal argument.

`unless` means exception OR requirement. A proven exception skips the body and
is explained as satisfied; unknown exceptions do not automatically skip it.
A proven body may establish true even if the exception is uncertain. This is a
configuration-level exemption; platform/classification applicability SHALL remain
a separate Assessment and SHALL NOT be inferred from a CPE label.

Collection errors SHALL NOT become successful empty populations. Malformed
population shape or duplicate Item identity is error before predicate evaluation.
Missing required scalar evidence, unknown value and collection error are distinct.
The models use `Value(missing)` for confirmed absence and `Value(unknown)` for
unresolved values; a missing schema field is error, not absence.

## Domain operations

**Permissions `at_most`:** let A be allowed right names and O be observed rights.
The predicate is O ⊆ A. All four Unix categories are explicit. No special bit is
ignored, and no octal numeric ordering is used. Invalid mode types/domain are
error; unresolved modes remain unknown. Permission rights in another platform
require that platform's own typed universe and acquisition semantics.

**Records `include`:** each requested type needs a confirmed witness in this
parent's relation. Duplicate types do not cover a missing different type. A
complete relation with no witness is false. An incomplete relation with a missing
witness is unknown. Confirmed witnesses for all requested types can prove this
monotone containment even if additional relation Items remain uncollected; this
is a proposed proof rule, not a claim that legacy OVAL always gives that result.
Aggregate error/not-collected relation status cannot certify it. A partial outer
zone inventory still cannot prove `every zone`, even when known zones are good.

**Configuration `settings`:** for each named setting, gather explicit occurrences
inside this acquisition group and Item. Required means a confirmed occurrence
must exist; optional permits complete absence. Every occurrence must satisfy the
typed comparison. Unknown setting names might belong to the selection and keep
it unresolved. Explicit `Off` followed by `On` fails this method. No effective
default or last-value collapse is performed. The provider must canonicalize
Apache's valid spellings and numeric syntax with supported version semantics;
that provider is not implemented here.

**Audit coverage:** the required space is a finite product of architecture,
syscall and symbolic actor intervals. First-match order is significant. Integer
predicate boundaries yield finite exact cells for the restricted conjunction
grammar. A preceding matching never action blocks that cell. Positive coverage
requires a complete ordered program because missing earlier rules can alter the
answer. A partial program is unknown even if all observed rules appear favorable.

The textual sketch SHALL require arch before syscall-name lookup. Auditctl
documentation confirms that a later arch can select the wrong lookup table;
normalizing that order as cosmetic would be unsafe. Numeric syscall mapping,
unsupported fields, other filter lists, prepend/delete/control commands and
global audit state are outside the prototype. Unknown semantics return unknown;
resource exhaustion is error. No unsupported condition is silently dropped.
Loaded and persisted sources SHALL remain distinct and evidence-labelled.

## Accuracy versus source compatibility

Same policy question does not guarantee identical published implementation.
This study distinguishes: exact source predicate equivalence, agreement with
stated intent over known observations, and unsupported target assumptions.

- Permission containment equals the original eight source predicates over all
  valid observed modes; collection/traversal equality is not proved.
- DNS typed scoped containment follows the selected per-zone intent, retaining
  server-wide exceptions, but source Variable-instance/status behavior is not
  independently executed. New monotone proof rules need explicit review.
- Apache constraints agree with the isolated explicit-occurrence policy formulas;
  original discovery/scripts/error suppression and native canonicalization remain
  unexecuted. Declared/loaded grouping is preserved as a stated contract.
- Audit coverage deliberately differs from regex spelling, duplicate source
  anomalies and persisted collection. It is an intended-policy method hypothesis
  with a proved bounded algorithm, not a lossless converter replacement.

A changed assessment method SHALL have its own identity/provenance and be offered
as an explicit Rule choice if adopted. It SHALL NOT silently replace migrated
behavior. Model truth and structural validation alone SHALL NOT establish scanner
equivalence; same-target independent execution is required for that claim.

## Acquisition and organizational boundaries

Native scanners SHALL handle filesystem traversal, mount exclusions, permissions,
symlinks/junctions and collection status. Fixed administrative queries MAY provide
typed observations for suitable domains, including auditctl/DNS APIs; they SHALL
NOT scan directories or become a universal fallback. No commands execute here.

Organizational Input MAY occupy a publisher-declared constrained value slot. It
SHALL NOT inject a predicate, command, capability, Object declaration or Test
selection. The publisher owns structural requirements. Per-Item evaluation does
not create new authored Tests. The prototype accepts no input-binding structure;
the complete standard must retain supported external-input semantics safely.

No effectively deprecated Test SHALL become a supported operation under a friendly
name. The established `accesstoken`→`userright` source replacement remains an
example; native effective-file rights are not an implementation of accesstoken.
Governance reinstatements and supported rare validation features remain respected.
