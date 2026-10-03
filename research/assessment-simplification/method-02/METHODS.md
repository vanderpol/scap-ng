# Competing methods and why these are different

All methods are experimental. The question is whether someone who understands
the requirement can author/review the check without learning OVAL graph mechanics.
There is no measured author study yet.

## Three competing designs

| Design | What the author thinks about | Accurate execution burden | Disposition |
| --- | --- | --- | --- |
| Objects plus direct requirements | The population, exceptions and allowed/required facts | Typed observations, scoped quantifiers, domain comparison/coverage, evidence | Prototype recommended for further author trials |
| Condition/requirement decision table | "On a domain controller require X; on a member server require Y" | Complete ordered/unordered condition semantics, unknown applicability, mutually exclusive or cumulative rows | Useful companion for Windows role exceptions; specified only, not implemented |
| Behavioral probes | "Try the operation and observe what happens" | Safe representative action, identity/environment control, timing and complete scenario coverage | Reject as universal replacement in these samples; a successful/failed sampled action cannot prove all users/paths/events |

Free natural-language execution is rejected: "restrict access" is too ambiguous.
A controlled sentence editor could emit the same typed requirement AST and show
"Every selected zone contains these types," without an LLM deciding semantics.
Such an editor is not implemented. YAML here makes the experiment inspectable;
YAML itself is not the discovery.

The earlier finite templates remain a useful migration/maintenance tool, but
leave the author responsible for regex and execution graph details. They do not
provide the principal method sought by the clarified research direction.

## New methods with actual execution models

### Permissions as an allowance, not eight Boolean comparisons

Before: Object → eight permission-bit State entities → Test. Proposed method:
collect a native mode value, form the set of observed rights, and ask whether it
is a subset of the publisher's allowance. This is not `mode <= 0740` and not
`mode == 0740`: 0604 fails containment; 0000 passes this particular restriction.
Source selection/Filters/Sets, special bits and root/user existence stay intact.

The common set-containment operation generalizes to typed rights/method/algorithm
allowances. **Windows rights do not use Unix bit positions.** An explicit ACE
allowlist is not an effective-access allowance. The native Windows collector must
resolve the same token/group/inheritance/deny semantics and right universe first.

### Named configuration assertions, not script/stdout comparisons

Before: discover roots, concatenate paths/commands, grep, parse output, States.
Proposed method: query an Object representing an installation's configuration
and state named setting constraints with required/optional presence. Execution
operates over explicit occurrences, retaining installation/group/occurrence keys.
The author needs the service's setting vocabulary, not command interpolation.

Shared mechanics work for other parsed configuration formats. A grammar/provider
still needs version, scope and status contracts. The prototype accepts already
canonicalized On/Off and integer values; it does not establish that normalization
or acquisition from real Apache files. Explicit, effective and live runtime
settings SHALL be separate source kinds rather than a hidden scanner choice.

### Audit coverage of a symbolic event population, not regex presence

Before: 24 regex predicates and 17 constant/concat Variables. Proposed method:
an ordered parsed rule program is assessed against architecture × operation ×
actor requirements. Actors are **symbolic domains**, not one sampled user:
root-login auid 0 and user-login auid 1000..4294967294 (unset excluded).

For this prototype, all auid comparisons are conjunctions. Partition each required
interval at each rule comparison boundary and adjacent integer. Predicate truth
is constant in each cell. The first matching exit rule determines always/never
for that cell. Every required cell must select always. Two ranges can jointly
cover all users; a rule only for user 1000 cannot. Output identifies the uncovered
operation/architecture/user-ID interval and decisive rule line.

This is a real change in assessment method: accept semantically covering grouped
or split rules without matching a particular text spelling. It can also detect
coverage hidden by an earlier never rule. It is **not** equivalent to the source's
persisted regex checks: loaded/persisted scope, two b32 anomalies, spelling,
suppression and unsupported extra conditions distinguish them. No silent source
repair or automatic migration is authorized.

The algorithm proves configured exit-rule coverage inside the supported model.
Global audit enablement, other filter lists, architecture syscall mapping,
include/load commands, kernel versions, scheduling and record delivery are not
implemented. Full native acquisition must establish those assumptions or the
Test cannot certify actual event auditing. A generic universal coverage primitive
would additionally need domain-specific matching/ordering semantics; no untyped
general join is implied.

### Relationships belonging to each Object, not parallel arrays

Before: separate zone/record/interface arrays linked by Variables/commands.
Proposed method: `zone.records` or `installation.main` is a typed relationship
owned by the current Item. It cannot borrow a favorable record from another
parent. `every` supplies scope; `include` asks for witnesses inside that scope.
Nested Tests remain available for requirements that need deeper relationships.

This is more than renaming the arrays, but does not prove the original OVAL
Variable-instance machinery was broken. Parent-key preservation, source universe
and query failures are provider obligations. No arbitrary Cartesian join/default
positional zip is introduced. Distinct record keys may repeat the same record
type; duplicate Item identity is a protocol error.

## Application to all twelve original cases

The linked dossiers preserve original Check Text, source pin, complete dependency
graph and before content. This table separates implemented methods from sketches.

| Rule/dossier | New author-facing method | Same-check boundary and current evidence |
| --- | --- | --- |
| [SV-257889](../dossiers/SV-257889.md) home files | Each file's rights fit a named allowance | Permission predicate implemented/exhaustively equal. Account/File selection, Sets/Filters/traversal not implemented. |
| [SV-258179](../dossiers/SV-258179.md) audit | Configured rules cover every required event class | Ordered interval model implemented; policy-intent method, not source-regex equivalence or kernel proof. |
| [SV-258236](../dossiers/SV-258236.md) crypto | Each named backend has its required kind/canonical destination | Matching expected configuration map is a typed agreement operation, not a runtime loop over publisher templates. Specified only; all twelve expected resources and per-path absence must remain. Manual utility/content checks need distinct method identity. |
| [SV-278028](../dossiers/SV-278028.md) FTP | Each FTP site's resolved root is outside prohibited system areas | Native path containment proposal; root/case/separator/junction facts required. Configured-string and resolved-target contracts differ. Not implemented. |
| [SV-278138](../dossiers/SV-278138.md) AD rights | Every selected file grants required effective rights and grants no rights outside the permitted principal set | Effective-access matrix proposal; requires complete identities, rights and per-directory existence. No ACE shortcut or Windows engine implemented. |
| [SV-278001](../dossiers/SV-278001.md) registry | Compare observed ACE facts to role-specific allowed/required entries | Decision table proposal; whitelist/source display filtering is not complete ACL equality. Preserve numeric rights, inheritance and empty/null DACL distinctions. Not implemented. |
| [SV-259350](../dossiers/SV-259350.md) DNS RRs | Each zone contains required record types | Requirement/presence model implemented; 256 cases and scope/status counterexamples. Original Variable-instance/target behavior unexecuted. |
| [SV-259345](../dossiers/SV-259345.md) DNS duration | Each key's validity is within a typed duration range | Typed seconds proposal; source truncates hours and catches errors as zero, so exact boundaries/status are a changed method. Not implemented here. |
| [SV-259374](../dossiers/SV-259374.md) interfaces | Each selected interface/address satisfies addressing requirements | Scoped relationships generalize; source Up/SuffixOrigin signal must stay explicit. Multiple addresses require a key and gateway relation. Not implemented. |
| [SV-214228](../dossiers/SV-214228.md) KeepAlive | Explicit named settings satisfy presence/value requirements | Setting operation implemented; 36 cases. Source main/loaded groups preserved conceptually; acquisition and canonicalization unexecuted. |
| [SV-214268](../dossiers/SV-214268.md) cookies | Each applicable cookie has both required flags | Same-Item set inclusion is natural; source already correlates States. Parsing cookie grammar/enablement is provider work. Specified only. |
| [SV-214292](../dossiers/SV-214292.md) default documents | Each selected root contains its specified default document | Child Object existence; root-level source scope/case retained for faithful method. All-descendant/effective DirectoryIndex checks are distinct coverage methods. Native traversal stays native. Specified only. |

## Human benefit, costs and rejected shortcuts

| Method | Author/reviewer benefit | Implementation cost | Compatibility risk |
| --- | --- | --- | --- |
| Direct requirements | Read a population and its truth conditions in one place; avoid named scaffolding where not reused | Typed compiler, provider contracts, diagnostics and source plans | Different surface; independent capability typing must be established, not silently guessed |
| Permission allowance | Review owner/group/other/special access directly | Low comparison cost; native file acquisition unchanged | Low for this observed predicate; selection/status equivalence still separate |
| Named setting constraints | Know exactly whether absence and conflicting declarations fail | Moderate predicate cost; high parsing/scope/discovery cost | Explicit/effective/live distinctions and canonical values must be defined |
| Symbolic coverage | State required event population; see missing scope rather than regex mismatch | High: domain interpretation, rule ordering, partition budgets and acquisition | High; larger semantic change and target conformance required |
| Parent-owned relationships | Fields stay attached to their zone/site/installation | Medium provider/identity/status cost | Unknown source correlation and partial relation semantics need review |

These are reasoned readability hypotheses, not author-test results. Lower line
counts are not an acceptance criterion. Trial authors SHOULD write a new check,
explain its empty/error behavior and identify a deliberate bad case without
opening a graph or command script. Compare misunderstanding rates and maintenance
changes, not only preference ratings.

Reject free-form prose interpreted by an LLM, a universal `compliant` collector,
numeric permission ordering, sampled-user audit proof, blind effective-setting
defaults, probe sampling as universal proof, shell filesystem traversal and
Organizational Inputs supplying commands/Test structure. Advanced supported
Variables/Sets/Filters/functions/record behavior remain; this small prototype is
not a replacement conformance implementation or justification for their removal.
