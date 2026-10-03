# More ways to make STIG automation easier

**Experimental concepts, 2026-10-03. No accepted schema changes or new execution
claims.** Owner requested ideas beyond the allowance compiler, including new
assessment methods, with no preference for novelty over existing accurate methods.
This is development research; `review/current/` remains the sole external review
surface. Checkout: `main`, receiving SHA
`d9ab1f3bd9eb52d03ec669a7eff14c626d7ca862`, clean/equal to upstream.

The opportunity is to separate three jobs: identify the right Objects, obtain
trustworthy observations, and state the requirement. Most content authors should
work on the last job and explicitly choose the first. Repeated acquisition/parsing
expertise should be tested once and reused, without hiding policy or errors.

This wave develops **concepts**, not executable experiments. Examples are human
views or hypothetical notation, not currently accepted/compilable native syntax.
Earlier executable evidence is linked where relevant. No new tests or target scans
were performed; documentation/link checks do not establish semantic equivalence.

## 1. A form that edits native NG directly

An author selects a named Object and edits a form representing actual native
fields, comparisons and quantifiers:

```text
Object: selected initialization files
Check: all Items
If no files exist: allowed
group_write: must equal false
group_execute: must equal false
other_read: must equal false
...
```

The persisted source is ordinary native NG. The form displays and edits that same
Object/State/Test graph; it does not require a second authoring language or a
semantic lowering compiler. An advanced view exposes the native source. Distinguish
this simple display/edit operation from a macro that expands an allowance into
eight comparisons. Convenience expansions would still need separate verification.

**Benefit:** writers need not learn node-reference syntax/type boilerplate; they
can inspect/fix the actual saved content. **Cost/risk:** UI defects still exist,
and it does not itself remove the conceptual complexity of a difficult check.
Named/embedded components, Variables, Sets and Filters remain available. Validate
round-trip edits, reference sharing, independent capability declarations and all
supported advanced forms; never normalize a graph invisibly during display.

## 2. Reusable observation helpers, with the requirement visible

An author chooses a versioned observation recipe, not a black-box “STIG passes”
function. Examples: forward-zone records, loaded audit rules, Apache explicit
directive occurrences, AD data paths and effective rights.

```text
Observe: Apache explicit directives
Group: main configuration
Require presence of KeepAlive
Require every observed KeepAlive value to be On
```

The recipe owns mechanics; the author owns the expected values, scope and presence.
Implement it with existing native Objects, reviewed capability interfaces or an
existing fixed shellcommand query as appropriate. Do not invent a provider first.
For Apache, file/include searching and acquisition SHALL remain in the native
scanner. A parser may interpret scanner-acquired content; it must not search the
filesystem through shellcommand. For DNS, a bounded administrative query may be
the simplest existing shellcommand solution.

**Benefit:** many Rules share one tested observation implementation. **Cost/risk:**
helper defects have a large fan-out; supported product versions, identity, complete
scope, errors and consistency need contracts. Resolve/version/hash/bundle helpers
with the self-contained package; no silent runtime downloads or upgrades. Allow
an explicit native implementation escape route. No opaque compliance verdicts or
organizational command injection. The Apache snapshot parser/DNS query sketch in
[refinement-01](../refinement-01/README.md) are partial research evidence, not mature
helpers or target conformance.

## 3. Requirements over explicit relationships

Instead of asking an author to build parallel lists and correlate their indexes:

```text
For every selected DNS zone:
  Its records contain RRSIG, DNSKEY and NSEC3.

For every selected FTP site:
  Its configured directory exists.
```

The important word is **its**: references/keys preserve the parent, including
installation/site/zone identity. Multiple matches need an explicit one/all/any
requirement; missing or duplicate identities cannot arbitrarily select a winner.
The DNS server-wide all-integrated/empty exceptions remain explicit outside this
illustrative per-zone assertion, with platform applicability evaluated separately.

**Benefit:** the writer states the relationship rather than a join algorithm.
**Cost/risk:** selection, child completeness and collection failure remain hard;
an incomplete child list does not prove absence. Try existing Object/Variable/
record relationships or a fixed query first. A new typed relationship primitive
is justified only by an evidenced gap. [Method-02](../method-02/README.md) has
synthetic scoped-relation cases; original Variable-instance and target behavior
remain unexecuted. Do not claim original OVAL loses correlation.

## 4. Decision tables for applicability and exceptions

Authors often understand a small matrix better than nested Boolean expressions:

| Condition | Applicability outcome | Configuration requirement |
| --- | --- | --- |
| Domain-controller condition true | Applicable | Check selected AD file effective rights |
| Domain-controller condition false | Not applicable | No AD configuration invocation |
| Domain-controller condition unknown/error | Unresolved/error | No invented platform classification or assumed exemption |

This is an author/editor view of the existing Rule/applicability/Assessment split,
not an inline platform check mixed into the compliance Test. Configuration-specific
exceptions can have a separate table, preserving their own semantics. Define
whether rows are exclusive, cumulative or prioritized; unspecified overlap is an
authoring error. Do not use unknown as “otherwise.” Do not let Organizational Input
select Tests. Publisher-owned choices remain fixed and explicit.

**Benefit:** reviewers can inspect the exception matrix. **Cost/risk:** overlapping
rows, unresolved conditions and hidden precedence can change results. This remains
a sketch, not a decision-table compiler/evaluator. The AD original graph, manual
requirement and principal semantics are in [SV-278138](../dossiers/SV-278138.md).

## 5. Expected-state manifests instead of repeated check construction

Some Rules simply describe an expected resource map:

| Selected resource | Required kind | Required canonical destination |
| --- | --- | --- |
| bind.config | symlink | /usr/share/crypto-policies/FIPS/bind.txt |
| gnutls.config | symlink | /usr/share/crypto-policies/FIPS/gnutls.txt |
| nss.config | regular file | No symlink destination requirement |

The complete crypto manifest needs all twelve source resources, not these three
illustrative rows. Each expected resource retains its own existence obligation;
one observed match cannot cover a missing different resource. A directly evaluated
manifest is a distinct proposal from compiling rows into existing Tests. Try the
existing finite publisher expansion or a validated utility method first.

**Benefit:** easy additions/review; policy lives in the table. **Cost/risk:** map
identity, optionality, extra resources, duplicates, type differences and statuses
must be explicit. [Refinement-01](../refinement-01/README.md) already has bounded
36-row source-contract evidence; that does not establish a native manifest engine
or complete deep-capability/target equivalence. Tables SHALL be publisher content,
not Organizational Input changing the Test population.

## 6. Assess configured meaning, rather than prescribed text spelling

For audit, the author could state:

```text
For the required architectures and extended-attribute operations:
  Audit events attributed to root login.
  Audit events attributed to user logins with auid >= 1000, excluding unset.
```

Grouped syscalls or several ranges may satisfy the same requirement even when
their text differs. The execution must examine rule ordering, exclusions and the
complete symbolic actor domain, not sample one user. Similar opportunities may
exist for firewall or authentication rules, but each domain requires its own
semantics; no generic parser can infer security equivalence.

**Benefit:** authors specify the security property. **Cost/risk:** high evaluator
complexity, product/version dependence and source-versus-manual-intent differences.
The existing shellcommand collector may suffice; correct domain evaluation may be
a tested publisher query or a new native operation only if necessary.
[Method-02's audit prototype](../method-02/README.md) has restricted ordered-model
evidence, not kernel proof, full filter-list/global-state coverage or source regex
equivalence. This idea is a method change until that distinction is resolved.

## 7. Make the observation layer explicit: configured, effective or running

The author chooses which fact the STIG actually requires:

```text
Audit source: loaded rules
Apache source: every explicit configuration occurrence
Windows permissions: effective rights for the specified principal
```

No silent substitution of persisted for loaded, effective last value for explicit
occurrences, or ACE entries for effective access. A helper with a precise name and
version makes this choice understandable without revealing its complete mechanics.
Defaults count only where the requirement actually permits them. Existing native
capabilities/query methods may already supply the required view.

**Benefit:** fewer plausible checks of the wrong fact. **Cost/risk:** product
parsers/defaults and Windows token/deny/inheritance semantics must be validated.
A daemon reporting an effective setting is useful when that is the security
question; it is not an automatic replacement for [SV-214228's explicit occurrence
conditions](../dossiers/SV-214228.md). This is primarily a contract/authoring idea,
not necessarily a new language feature.

## 8. Typed policy concepts: duration, access allowance and resource containment

Authors should express “at most 48 hours,” “no rights beyond this allowance,” or
“this resolved directory is outside the prohibited area” using reviewed typed
operations, instead of hand-building conversions, numeric bit masks or unsafe path
prefix tests. These are illustrations, not statements that every sampled STIG
contains those exact values or semantics.

**Benefit:** fewer unit, boundary and lexical errors. **Cost/risk:** typed hours
may mean exact seconds or source-truncated hours; effective rights are not an ACE
allowlist; path containment needs filesystem/case/link/junction identity supplied
by the native scanner. A compiler must preserve the chosen contract or reject it.
Existing primitives are preferred where adequate. The allowance transform has
exhaustive predicate evidence; duration/containment/Windows generalization does
not. See [transform-03](../transform-03/README.md), [DNS duration](../dossiers/SV-259345.md)
and [FTP](../dossiers/SV-278028.md).

## 9. Write acceptance cases alongside each automated requirement

An author supplies small observation scenarios with expected outcomes:

| Permission scenario | Expected |
| --- | --- |
| Complete observation, mode 0600 | true |
| Complete observation, mode 0604 | false |
| Forbidden bit unresolved, other required comparisons true | unknown |
| Object collection fails | error |
| Confirmed empty population | Follows this Test's explicit existence requirement |

A preview runner explains which clause was decisive and which observations were
needed. It should accept realistic typed collection snapshots, not only numeric
happy-path values. For relationships, include a witness in the wrong parent; for
settings, include duplicates/conflicts; for boundaries, include values just outside
the threshold. Review and expected cases are independent of generated comparator
code. Compare source and candidate on identical snapshots where acquisition is
actually the same, and eventually run independent target comparisons.

**Benefit:** authors can communicate intent and report a compiler/helper defect
without rewriting correct policy. **Cost/risk:** finite examples are not a complete
proof, and shared implementation assumptions can make two broken paths agree.
No new native runtime syntax is required to store separate author/test evidence.
Prototype semantic tests exist in earlier waves; an author-facing runner/editor
has not been implemented or usability-tested.

## 10. Explain results in the same terms used to write the requirement

```text
Test: protect-user-files
File: /home/alice/.bashrc
Finding: other read is outside the allowed permissions
Observation: other_read = true
```

For more complex checks, report the parent key, setting occurrence, missing
expected resource or uncovered audit interval. Keep concrete witnesses and provider/
source locations; identify incomplete inventories and errors separately. Retain
bounded evidence and exact native Test identity, allowing reviewers to traverse
into the saved graph when needed. Do not replace detailed runtime provenance with
a friendly summary or infer pass from a truncated evidence list.

**Benefit:** content debugging/review becomes about policy clauses. **Cost/risk:**
maps must remain accurate across revisions, and collection/result semantics remain
authoritative. [Transform-03](../transform-03/README.md) demonstrates one synthetic
State-to-author-clause finding; a complete result/editor pipeline is unimplemented.

## Three implementation routes, rather than one mandatory compiler

| Route | Strongest opportunity | Where complexity/risk lives |
| --- | --- | --- |
| Native NG plus direct editor and reusable existing Assessments/Objects | Reduce authoring mechanics without a second language | UI, observation helpers, native validators/scanner |
| Optional requirement syntax/compiler | Compact repetitive typed predicates/expected maps | Compiler plus helpers/scanner; inspectible output, native escape route and pinned version needed |
| New directly evaluated requirement operations | Security properties existing methods cannot express adequately | Portable operation/provider contracts and scanner conformance; no compilation is not no implementation risk |

The author's compiler-defect concern applies equally to helpers and new scanner
operations: correct content can be blocked by implementation bugs. Avoid a mandatory
opaque layer. Retain ordinary native content, explicit alternative Assessment
choices and a reviewable local workaround route. Neither direct interpretation nor
a GUI eliminates software defects. These are recommendations, not claims that an
escape-route product/editor has been implemented.

## Recommendation and boundaries

Start with a **native editor + reusable observation recipes + author acceptance
cases**. This offers concrete usability improvements while retaining existing
semantics. Use focused existing shellcommand where it is the simplest accurate
method. Add optional authoring abbreviations proven for bounded transformations.
Treat semantic audit coverage and novel relationship/domain operators as separate
research until existing-method limitations and equivalence evidence justify them.

Most NIWC 1.4 content retains DISA 1.3 tests, per owner context; package version
does not prove modernization. Shellcommand SHALL NOT perform any filesystem
searches, including include discovery. Native acquisition retains remote filesystem
scope/exclusions, permissions, links/junctions, completeness and scanner efficiencies.
Organizational Input SHALL remain constrained expected values, not commands,
provider selection or Test selection. Applicability SHALL remain separately authored
Assessment logic in Benchmark → Rule → Assessment. No effectively deprecated Test
becomes supported, and no rare supported capability is removed.

Rejected: arbitrary natural language interpreted into execution without review;
generic “is compliant” helpers; choosing a favorable source automatically;
unsupported source fields silently ignored; broad shell scanning; sampled probes
claiming universal compliance; changed policy/source semantics hidden as cleanup.
AI MAY suggest draft content/tests, but its inference SHALL NOT decide runtime
semantics. Every executable artifact needs deterministic reviewed meaning.

## Evidence and next work

Established evidence: the original twelve source dossiers/closures, prior bounded
permission/relationship/configuration/audit experiments, source capability inventory
and current native contracts. New inference: reusable observations/editor/testing
may reduce author effort. Unresolved: actual author comprehension, target agreement,
helper completeness/version portability, conformance cost and time saved. No
measured advantage or new executable result is claimed by this concept wave.

See [decision candidates](DECISIONS.md) and [handoff](HANDOFF.md). An initial author
trial SHOULD measure ability to write a new check, explain absent/error behavior,
spot wrong-parent/duplicate/boundary cases and repair a policy error. Do not measure
only source line counts. No source/schema stabilization or review-build work was
changed, and no new Board vote/duplicate backlog issue was opened.

Provenance: **Inherited** current design/requirements/glossary, twelve pinned NIWC
dossiers and prior research; **Adapted** direct requirements/relationship/decision
table/manifest ideas, explicitly refined for native editing and existing-method
choices; **Common** new author-trial, recipe/editor and acceptance-case concepts;
**Evidence/Audit** tradeoffs, links, limitations and resumption guidance. Source
package pins remain in parent dossiers and sample-manifest. No external implementation
or private target data was copied.
