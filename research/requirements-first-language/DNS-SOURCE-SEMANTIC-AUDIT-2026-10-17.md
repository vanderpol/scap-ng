# Windows DNS source audit: empty population and signing-key cardinality

Research #235 (authoring) and #229 (source semantics), 17 October 2026. Based on the complete [SCAP 1.4-derived source](../assessment-simplification/english-first-04/canonical-operators/dns.canonical.research.yaml), compared with the [prior native sketch](examples/06-windows-dns.yaml). Not a scanner run, an adopted schema or proven lossless conversion.

## Exact source structure

Five independent shellcommand Tests combine as three OR alternatives:

1. **Caching-only:** the command must produce at least one Item, and its stdout_line field must have **no values** for nonexcluded forward or reverse zones.
2. **AD integration:** the command must produce at least one Item, and its stdout_line field must have **no values for forward zones that violate AD integration**. The original title explicitly says all forward zones **if any**.
3. **Signed zones:** three Tests combined with AND: each Item must have exactly one stdout_line string True for IsSigned, and the two distinct ZoneSigningKey and KeySigningKey derived commands must report signature-validity hours satisfying **two whole-State comparisons**: at least 48 and at most 168, both with mandatory State field presence.

All five source Tests have an at_least_one Item requirement; absent stdout values in an existing command Item are a **different** condition from an absent shellcommand Item.

All direct shellcommand objects disable the automatic error flags for nonzero exit status and stderr. Key-validity derived commands catch some errors by emitting string 0; a native typed provider must not silently reinterpret those source outcomes as ordinary exceptions. Source zone selection omits Forwarder, TrustAnchors, auto-created and (for forward-only source) reverse zones. Those selectors and the source command's Item status are part of semantics.

## The reverse-only DNS counterexample

Assume **one reverse lookup zone exists and zero forward lookup zones**, and all relevant source command collections return a complete shellcommand **Item** with appropriate stdout value presence.

- Source caching-only alternative need not pass: reverse lookup zone exists.
- Source AD-integrated alternative can **Pass**: no forward zones violating AD integration were reported. The requirement is "if any".
- The original top-level OR can consequently Pass.
- The [old native sample](examples/06-windows-dns.yaml) incorrectly requires a forward zone to exist by writing an explicit empty-population failure on the AD branch. Its other alternatives would not rescue this reverse-only case. This can change the result.

This is a **controlled counterexample conditional on the stated shell Item behavior**. It does not establish how every real PowerShell probe behaves. The [source-backed regression test](../../tools/test_research_dns_source_contract.py) pins the relevant source fields and the candidate's imposed minimum.

The better native formulation for the AD branch is: "Every relevant forward zone, if any, must be integrated with Active Directory." A complete confirmed zero forward-zone population is acceptable for that branch. A zero observed because collection is incomplete is NOT confirmed absence.

## The signed branch is still not a one-line numeric range

The original signed check requires exactly one string True rather than an arbitrary per-item true value. The two signing-key kinds are acquired through distinct commands using DNSKEY signature validity period Days * 24 + Hours. The two lower/upper original States must be evaluated independently; repeated stdout fields and missing values require source-specific tests before they can be lowered to one typed between predicate.

Even if a native provider supplies a value in hours, it must preserve key type, zone association, data origin, collection status, zero-on-exception behavior when converting, and appropriate numeric types. A normalized native DNS policy may be easier to write, but that alone is not evidence of source equivalence.

## Design decision

Retain typed, reusable zones and signing-key providers as the leading **native authoring direction**, but do not require forward zones to exist merely to make the YAML less ambiguous. Count selected resources only when the actual requirement demands existence. Treat missing shell Items, missing fields, duplicate values and incomplete evidence as distinct.

The [source test](../../tools/test_research_dns_source_contract.py) verifies five checks, three alternatives, five Item-existence obligations, two no-output predicates, typed/State structure, original zone exclusions and separate key commands. No production DNS service or scanner has been invoked.

**New fixture evidence contract:** [typed DNS zone/key normalizer](../../tools/research_dns_zone_key_evidence.py), [versioned schema sketch](providers/windows.dns.zone_signing_evidence.v0.1.yaml), and [negative tests](../../tools/test_research_dns_zone_key_evidence.py) preserve forward vs reverse, ZoneSigningKey vs KeySigningKey, source days/hours, duplicate identities, per-zone correlation, missing fields and incomplete/error collection. This is STRUCTURED SYNTHETIC input, **not** Get-DnsServerZone or DNSKEY PowerShell collection, and cannot establish source conversion parity. It intentionally does not mimic the original catch-output-zero, shell Item/value separation or OVAL record/State evaluation.

**Next step:** source-aware synthetic provider fixtures and a formal native evidence/status contract; independent Gemini review will be useful only with those explicit counterexamples rather than another keyword poll.
