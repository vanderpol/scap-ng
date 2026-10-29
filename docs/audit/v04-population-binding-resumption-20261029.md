# Population and catalog investigation after interrupted DRAFT publication

Task: [#251](https://github.com/vanderpol/scap-ng/issues/251).
Pending population/source-compatibility decisions:
[#255](https://github.com/vanderpol/scap-ng/issues/255).
Investigation date: 2026-10-29. No normative change is accepted by this packet.

## Inputs and method

Recovered GitHub `main` was `0b2fdb2d392c5d80a4128d73ae4ac5ada573cf26`.
The previous local DRAFT payload/recovery directories had not survived the
workspace replacement. Recovered the published 4,206-proof floor from the six
source archive, five proof batches and the four guard receipts; checked all
65 original ZIP sizes, SHA-256 and Git blob IDs against NIWC
`8c8e5dff860af6b1290ee9273a282db24278f8d5`. The frozen previous archive remains
byte-identical. One necessary reconstruction uses the existing DRAFT builder;
it is a publication deliverable, never a routine all-corpus regression.

The read-only investigation walks the 1,184 primary `all_exist` and 992 primary
catalog-blocked original closures from the frozen ledger. It performs no
conversion, reference repair, source rewriting or runtime execution.
Raw per-Rule identities, source pins, hashes, boundary vectors and reproduction
scripts accompany the evidence publication. Counts are primary blockers;
secondary blockers overlap and prevent treating any count as guaranteed coverage.

## all_exist: measured populations and complete-case equivalence

Of 1,184 primary blocked Rules, 589 have a State-bearing affected Test, 115 have
Variables in their dependency closure and 136 have a Set/Filter on an affected
Object. These counts overlap. 577 have only State-free affected Tests without
Variables anywhere in the closure or affected-Object Sets/Filters. This last
number is a triage population, **not** an admitted or independently proved set.
Every affected original token, Test/Object identity and structural hash remains
in the original evidence. Field-level `all_exist` remains separate.

The pinned OVAL `oval-common-schema.xsd` contains an internal tension:
its `ExistenceEnumeration/all_exist` prose calls Test-level `all_exist`
equivalent to `at_least_one_exists`, while its evaluation charts distinguish
their absent/error/not-collected populations. Neither text is silently discarded.
The current native schema explicitly maps both spellings to `one_or_more`;
the earlier approved normalization and its exact-source admission remain intact.

With a complete population consisting only of actual, successfully collected
Items, both source charts return false for zero Items and true for one or more.
The conditional converter mapping is therefore:

```yaml
# Original Test check_existence=all_exist retained in provenance
require: {items_found: one_or_more}
```

That equivalence does not settle the surrounding collection contract. Eleven
independently specified boundary vectors reproduce the existing OVAL reference
helper's results:

| Original collection evidence | all_exist | at_least_one_exists |
| --- | --- | --- |
| Complete, zero actual Items | false | false |
| Complete, one actual Item | true | true |
| Complete, three actual Items | true | true |
| Complete, one existing + one absent expected target | false | true |
| Complete, one existing + material Item error | error | true |
| Complete, one existing + material Item not-collected | unknown | true |
| Collection error, with an existing Item | error | error |
| Collection not collected, with an existing Item | unknown | unknown |
| Incomplete, zero Items | unknown | unknown |
| Incomplete, one Item, no State | unknown | unknown |
| Incomplete, one passing Item, State check="at least one" | unknown | true |

These are OVAL reference results, **not native scanner-runtime evidence**.
The absent-target row describes OVAL evidence; it does not propose creating
nonexistent native Items. Discarding a diagnostic or labeling an incompletely
accounted target population complete would not establish equivalence.

Concrete variable-population source: Amazon Linux 2023
`SV-274101r1120291`, `unix.file` Object
`oval:mil.disa.stig.unix:obj:23047200`, selects `filepath` through constant
Variable `oval:mil.disa.stig.defs:var:23047200`, `var_check="at least one"`.
The seven original paths are `/sbin/auditctl`, `/sbin/aureport`, `/sbin/ausearch`,
`/sbin/autrace`, `/sbin/auditd`, `/sbin/rsyslogd`, `/sbin/augenrules`.
Finding one actual file does not demonstrate complete accounting for the seven
selection targets. No live collection of these paths was performed.

Owner decision requested under #255: specify how an actual-Items collection
represents a missing expected target and how material Item error/not-collected
and incomplete collection affect Test existence. In particular, an observed
passing Item must not by itself erase the distinction above. Can the existing
grammar/approved collection contract enforce these obligations for the proposed
new admission population, or is an explicit contract/schema correction required?
Only if the latter is needed should a normative change be proposed. This packet
does not change schema, compiler, oracle, collector or prior normalization.

After that decision: admit source-pinned complete-case classes incrementally,
preserve original tokens and normalization conditions in provenance, prove
each new class independently, and retain dynamic/Set/filter contexts until their
population obligations are covered. Global replacement remains inappropriate.

## Catalog: all 992 dependencies are embedded, with foreign URI entries

All 992 primary failures span 21 ZIPs. Each requested Definition exists in
exactly one embedded OVAL component. The corresponding source entry is
`{http://scap.nist.gov/schema/scap/source/1.2}uri` (`ds:uri`), whose `uri`
attribute points to an existing component-ref and then the component containing
the exact Definition. The resolver correctly recognizes XML Catalog `cat:uri`
entries in `urn:oasis:names:tc:entity:xmlns:xml:catalog`; it does not interpret
the foreign `ds:uri` extension as a catalog binding.

Representative: Active Directory Domain V3R6, original Rule
`SV-243466r959010`, points to the V3R6 `-oval2.xml` href. The checklist retains
an older V3R5 `cat:uri` pointing to an absent old component, while the new,
fully connected V3R6 `-oval2.xml` entry uses `ds:uri`. Source identities and
both entries are retained in the evidence.

Classification of the 992 observed failures:

| Cause | Rules | Disposition |
| --- | ---: | --- |
| Foreign-namespace URI entry, complete embedded target chain | 992 | Source packaging/producer-compatibility issue |
| Genuinely absent requested Definition | 0 | No missing Definition in this primary cohort |
| Relative-path normalization needed | 0 | Exact source names already agree |
| Valid standard catalog entry mishandled by converter | 0 | No resolver defect demonstrated |

The catalog XSD allows foreign children with `xs:any namespace="##other"
processContents="skip"`. The representative original catalog therefore passes
that XSD: structural validity does not give the foreign element standard URI
resolution semantics. Do not describe these 992 as XSD-invalid, genuinely
missing content, successfully converted, or proven unlocks.

Recommendation: obtain corrected, pinned upstream catalog entries. Alternatively,
the owner may explicitly authorize a narrowly pinned NIWC producer-extension
adapter with separate provenance and source-validity labels. Such authorization
must specify treatment of stale broken standard entries and distinguish the
adapter from standard reference resolution. No namespace rewrite, basename
guess, component search fallback or automatic repair is implemented here.

## Independent existing-mapping progress

The IOS XE line/global source reader previously had no frozen field crosswalks,
so all 38 new IOS XE DRAFT candidates were initially UNVERIFIABLE/UNSUPPORTED.
Adding explicit identity crosswalks for the two **unchanged approved mappings**
and activating them in the direct converter proves all 38 original Rule closures
without changing their DRAFT program hashes. Three pinned original component
fixtures contain all 66 Tests used by those Rules. Six focused regressions check
source validity/deprecation, every original node hash, independent source/native
terms, schema/compiled operands, selector/State/count mutations, namespace/nil/
attribute rejection, separate existence/matching and continued all_exist rejection.
The changed DRAFT regression still proves diagnostic mapping separation using
the unactivated `ios.line` capability. Other IOS/IOS XE capabilities stay excluded.

No original invalid/deprecated closure, count function, #255 population/binding
contract, scanner/editor or 0.5 work is admitted. Publication, exact-commit CI
and the latest recovery state are recorded in
[AUTONOMOUS-PROGRESS](../developer/AUTONOMOUS-PROGRESS.md).
