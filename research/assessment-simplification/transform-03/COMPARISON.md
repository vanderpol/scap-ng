# Where an authoring transform helps, and where execution still matters

**Experimental findings.** “Compilable” requires a meaning-preserving lowering to
available primitives, not merely acceptance by an open generic JSON schema. A
method can be simpler to author yet still need a new acquisition/evaluation
contract. Complete Check Text, source versions and graph closures remain in the
linked dossiers; none is superseded by a miniature DSL example.

Owner clarification: [existing SCAP 1.4 and shellcommand](EXISTING-CAPABILITIES.md)
SHOULD be evaluated before new features. Typed DNS/configuration providers below
are possible alternatives, not required additions. The pinned enhanced corpus
already includes seven shellcommand-bearing cases and five SCAP 1.4 packages;
upgrade savings from original DISA 1.3 content require a separate paired comparison.

## Across the selected cases

| Rule / source | Easier author-facing concept | Compiler versus execution evidence |
| --- | --- | --- |
| [SV-257889 RHEL9](../dossiers/SV-257889.md) | Every initialization file fits a permissions allowance | **Compiler demonstrated** for the permission predicate and fixed native file selectors. Original full account/Variable/Set/Filter scope not compiled. No need for a new numeric-mode field or comparison operation. |
| [SV-258236 RHEL9](../dossiers/SV-258236.md) | Each named crypto backend has its required target/type | Finite compile-time rows already have bounded source-contract evidence in refinement-01. Keep each backend's existence Test; full deep symlink mapping/scanner comparison remains unproven. No new runtime table is needed. |
| [SV-258179 RHEL9](../dossiers/SV-258179.md) | Audit rules cover these operations, architectures and actor domains | Existing regex requirements can be expanded from publisher rows, but ordered semantic coverage is a **different method**. Method-02's symbolic domain prototype is promising, not equivalent to the original persisted-text checks. Runtime/kernel/loaded scope and b32 anomalies remain material. |
| [SV-278028 Windows2025](../dossiers/SV-278028.md) | Each selected FTP site points at an existing permitted directory | A named site/path relationship could hide path Variable chains. No accurate lowering/provider contract is demonstrated. Never let site inputs inject a command or treat missing/error discovery as an empty inventory. |
| [SV-278138 Windows2025](../dossiers/SV-278138.md) | These principals have these effective rights on each AD data directory | Publisher role/rights tables could expand existing comparisons; role-aware allowlists need a complete effective-right universe, inheritance/token/deny semantics and per-directory existence. No ACL-to-effective-access substitution or target proof. |
| [SV-278001 Windows2025](../dossiers/SV-278001.md) | Each registry ACL meets the stated principal/right policy | A front end could expand literal source ACE constraints; that does not prove the complete ACL or effective access is restricted. Empty/null DACL and omitted rights need target investigation. No implemented transform here. |
| [SV-259350 Windows DNS](../dossiers/SV-259350.md) | Every relevant zone owns the required DNSSEC record types, retaining the integrated-zone exception | Typed parent relationships simplify authoring and the synthetic model, but need correct acquisition/variable-instance/error semantics. No demonstrated compilation to current primitives; no allegation that the original source loses correlation. See #122. |
| [SV-259345 Windows DNS](../dossiers/SV-259345.md) | Each selected key's signature duration is within the threshold | Units can be an author abbreviation over known comparisons. Exact seconds versus source whole-hour truncation/errorcatch-zero is a method change. Neither target semantics nor a faithful complete compiler is proved. |
| [SV-259374 Windows DNS](../dossiers/SV-259374.md) | Each selected Up interface meets the specified addressing constraint | Requires preserving interface/address keys, empty bypass and actual SuffixOrigin conditions. Compiler hiding shell/array details is possible only after its acquisition contract is proved. PrefixOrigin/DHCP is not a substitute. |
| [SV-214228 Apache](../dossiers/SV-214228.md) | Every explicit KeepAlive/limit occurrence meets the rule; presence differs for main/loaded groups | Author predicate is clearer; a validated occurrence provider is the hard part. Restricted parser over native snapshots exists, not a full native collector. Last-value-wins/default inference changes the original all-occurrence check. |
| [SV-214268 Apache](../dossiers/SV-214268.md) | Each selected cookie setting carries the required flags | Original source already correlates flags within an Item. Named setting syntax may remove script/Variable overhead after acquisition is established; a general join is not demonstrated as necessary. |
| [SV-214292 Apache site](../dossiers/SV-214292.md) | Selected roots have no prohibited default document | Native file selection should carry traversal, mount/link/status behavior. Discovery/config scope still needs validation. Broad shell scanning and whole-tree searches change the task; source root-level index.html is not effective DirectoryIndex. |

The DNS package targets Windows Server2022; these cases SHALL NOT be presented as
Server2025-specific evidence. No new platform was needed for this compiler proof.

## Practical comparison

| Approach | Author readability / reduction | Scanner implementation cost | Compatibility risk / evidence |
| --- | --- | --- | --- |
| Current explicit native form | Familiar explicit Objects/States/Tests; repeats simple predicate machinery | Existing intended backend contract | Current target contract; no released scanner equivalence claim |
| Existing SCAP 1.4 / focused shellcommand | Can replace indirect acquisition with a fixed service/utility query | Existing command capability; query/error/output verification still costs work | Seven selected cases already use it. Specific simpler replacements and paired DISA upgrade savings remain unproven. |
| Publisher table/template only | Reduces repeated nodes but leaves regex/graph reasoning | No new runtime operation | Prior 36-row bounded source contracts; useful, insufficient for the clarified author goal |
| Requirement-oriented **compiler** | Author names the allowance and empty behavior; 36 versus 242 lines for this identical fixed fixture | No new scanner primitive; modest compiler/diagnostic mapping work | Independent Boolean source predicate and bounded status tests; account/discovery/target scope unproved |
| Requirement-oriented **domain methods** | Named settings, scoped DNS relationships, symbolic audit coverage remove more conceptual overhead | Provider/parser/type/version/error contracts; audit algorithm is substantial | Previous synthetic evidence; potentially changed requirement/source semantics; target investigation required |
| Unconstrained prose / inferred command generation | Short to type, ambiguous to review | Unstable inferred execution | Rejected: ambiguity, missing error/scope contracts, unbounded command generation |

No author-time, comprehension, collector-performance or false-pass measurement
was performed. Fewer lines are evidence of representational reduction only.

## Refinement decisions and rejected shortcuts

The best next direction starts with existing SCAP 1.4 capabilities, including
suitable fixed shellcommand queries, then a small typed authoring layer/compiler
where it helps. Domain-method research is justified where those existing methods
cannot express the desired method clearly/accurately. It is unnecessary to standardize every convenience
as a new scanner operation. The permission experiment retains independently
observable booleans, solving the earlier mode-only model's partial-value weakness.

Reject numerical `mode <= 0740`; omitting unknown/error semantics; accepting scope
fields without implementing them; emitting unreviewed provider names and calling
schema acceptance compatibility; flattening all backend existence into one global
Test; suppressing collection errors into absence; defaults/last-value-wins Apache
interpretation; unconstrained organizational inputs; universal shellcommand or
behavioral-probe substitution. Focused fixed shell queries remain legitimate
future candidates; native acquisition retains all filesystem scanning.

Unproven next steps are full source-scope compiler closure, independent target
comparison, author trials, provider versioning, and compatibility across uncommon
supported features. Rarity is not grounds for removing an advanced feature. No
deprecated Test becomes supported by a shorter authoring form.
