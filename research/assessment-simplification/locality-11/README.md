# Private Object/State locality research

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**
>
> Nothing in this directory changes schema/v0.3.0, schema/v0.2.0, the converter
> contract, result semantics, or the OVAL Board review baseline. This research
> tests a source-layout idea only.

## Research question

Can SCAP-NG keep the current Test/Object/State semantics while making ordinary
Assessments easier to read by using one simple rule?

> **Inline private components; hoist and name shared components.**

Under this hypothesis:

- an Object used only by one Test may be authored inside that Test;
- a State used only by one Test may be authored inside that Test;
- an Object or State that is reused, referenced by a Variable/Filter/Set, or
  otherwise independently addressable remains Assessment-scoped and named;
- Variables, Tests, evaluate logic, quantifiers, datatypes, collection
  behavior, reported elements, and six-state result semantics are unchanged.

This is deliberately much narrower than the Ansible-inspired research. It asks
whether most of the readability problem comes from graph layout/indirection
rather than from the underlying semantic model.

## Production source

Pinned NIWC Atlantic revision:

`8c8e5dff860af6b1290ee9273a282db24278f8d5`

Production packages:

- RHEL 9 V2R9 enhanced SCAP 1.4;
- Microsoft Windows Server 2025 V1R1 enhanced SCAP 1.4.

The experiment regenerates faithful current native content from the pinned
packages before applying the research-only layout transformation.

The converter-produced source used by this experiment currently declares the
0.2.0 Assessment specification. This research is intended to inform 0.3.0
authoring design; it does **not** claim that the inline form is valid 0.3.0
content today.

Successful workflow:

https://github.com/vanderpol/scap-ng/actions/runs/37544860242

## Safety invariant

The research renderer does not simplify semantic payloads.

For each transformed Assessment it:

1. counts all references to named Objects and States;
2. inlines a component only when its only reference is the consuming Test;
3. retains shared or otherwise referenced components at Assessment scope;
4. records the old identity -> lexical location mapping;
5. mechanically re-expands the inline representation; and
6. requires structural equality with the faithful source Assessment.

A mismatch fails the research run.

The first implementation did in fact fail this check because empty source
component sections were not restored during re-expansion. That defect was fixed
rather than weakening the equivalence guard.

## Twenty-Rule human-review sample

A deterministic complexity-spread sample of 10 RHEL 9 and 10 Windows Server
2025 Rule Assessments was rendered as full inline research YAML.

### RHEL 9

- SV-257779
- SV-258126
- SV-257785
- SV-257904
- SV-257999
- SV-258242
- SV-257794
- SV-257864
- SV-257983
- SV-258179

### Windows Server 2025

- SV-277989
- SV-278074
- SV-278111
- SV-278151
- SV-278200
- SV-278237
- SV-278061
- SV-278255
- SV-278253
- SV-278028

Across these 20 Assessments:

| Measure | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Test -> Object/State cross-references | 74 | 4 | **94.6%** |
| Assessment-scoped Objects | 52 | 5 | **90.4%** |
| Assessment-scoped States | 30 | 7 | **76.7%** |
| Normalized YAML lines | 2,294 | 2,165 | 5.6% |
| Normalized bytes | 81,090 | 77,259 | 4.7% |

The transformed sample inlined 47 Objects and 23 States.

The small line/byte reduction is important: the experiment is not winning by
deleting semantics. The large change is removal of cross-file/cross-section
mental dereferencing.

## Full two-platform census

The same transform/equivalence check was run in metrics-only mode against every
converted STIG Rule Assessment containing Tests: **676 Assessments** total.

| Measure | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Test -> Object/State cross-references | 1,758 | 152 | **91.4%** |
| Assessment-scoped Objects | 1,087 | 214 | **80.3%** |
| Assessment-scoped States | 858 | 125 | **85.4%** |
| Normalized YAML lines | 50,285 | 46,752 | 7.0% |
| Normalized bytes | 1,615,452 | 1,520,802 | 5.9% |

The full census inlined **873 Objects** and **733 States** while retaining every
component that the conservative reference analysis considered independently
addressable.

### RHEL 9

417 Rule Assessments containing Tests:

- Test component references: 1,049 -> 77 (**92.7% reduction**);
- Assessment-scoped Objects: 777 -> 147 (**81.1% reduction**);
- Assessment-scoped States: 423 -> 81 (**80.9% reduction**);
- normalized lines: 31,890 -> 29,860 (**6.4% reduction**).

### Windows Server 2025

259 Rule Assessments containing Tests:

- Test component references: 709 -> 75 (**89.4% reduction**);
- Assessment-scoped Objects: 310 -> 67 (**78.4% reduction**);
- Assessment-scoped States: 435 -> 44 (**89.9% reduction**);
- normalized lines: 18,395 -> 16,892 (**8.2% reduction**).

## Real sharing survived

The result is not "put everything inside Test."

Examples from the 20-Rule set demonstrate the intended boundary:

- **RHEL SV-257794** has two Tests with private Objects but a genuinely shared
  State. Both Objects inline; the shared State remains Assessment-scoped and
  both Tests continue to reference it.
- **Windows Server 2025 SV-278028** contains significant Variable/dataflow
  structure. Four private Test Objects inline, but five Objects feeding
  Variables and five States participating in the richer graph remain named at
  Assessment scope.
- The renderer also refuses to inline an Object merely because one Test uses it
  if a Variable, Set, Filter, or another location also references that Object.

This behavior is the key point of the hypothesis: **a name is evidence that the
component needs independent addressability.**

## Candidate authoring rule — not adopted

If this direction survives human review, a possible 0.3 authoring contract would
be:

1. A Test's `object` MAY be either a reference to an Assessment-scoped Object
   or a complete inline Object.
2. A Test's `states` MAY contain references to Assessment-scoped States and/or
   complete inline States.
3. An inline Object/State is private to the enclosing Test and SHALL NOT be
   referenced from outside that Test.
4. Any component that needs reuse or external reference SHALL be hoisted to the
   Assessment's `objects` or `states` map and given a meaningful ID.
5. The compiler SHALL assign deterministic lexical semantic identities to
   inline components for results/evidence/provenance.
6. Inlining SHALL NOT create hidden semantic defaults or change Test/Object/
   State capability typing, quantifiers, existence behavior, datatype,
   reporting, or error/completeness semantics.

That is a review candidate only. It is not schema text.

## Why this looks more promising than a parallel simple DSL

The empirical result supports a narrower possibility:

```
current SCAP-NG semantic model
        +
inline private Object/State authoring
        +
named shared Object/State authoring
```

rather than:

```
new simple language
        ->
different compiler IR
        ->
SCAP-NG
```

More than 90% of Test-to-component indirection disappears in the two-platform
census without changing the semantic graph after re-expansion.

This does not prove human preference. It does show that most of the current
Object/State naming burden is not required by reuse in these production
Assessments.

## Recursive private Set-operand follow-up

A bounded second locality experiment tested whether the same locality principle
can apply one level deeper:

> A leaf Object used exactly once as an **unfiltered Set operand** may inline
> into that Set; if the Set Object is itself private to one Test, it may then
> inline into the Test.

The experiment deliberately refuses filtered operands, nested Set operands,
reused Objects, Variable-referenced Objects, and other graph shapes.

Successful workflow:

https://github.com/vanderpol/scap-ng/actions/runs/37551115801

Across the same **676** RHEL 9 + Windows Server 2025 Rule Assessments:

| Measure | Direct locality | Recursive Set locality |
| --- | ---: | ---: |
| Top-level Objects remaining | 214 | **107** |
| Object-scope reduction | 80.3% | **90.2%** |
| Named component refs remaining | 433 | **326** |
| Named-ref reduction | 78.8% | **84.0%** |
| Additional private Set-operand Objects inlined | 0 | **107** |

The gain is entirely RHEL in this proof class:

- RHEL top-level Objects: 777 -> **40** (**94.9% reduction**);
- RHEL named component refs: 1,250 -> **171** (**86.3% reduction**);
- **107** private unfiltered Set-operand Objects were inlined;
- all transformed Assessments mechanically re-expanded to structural equality
  with the faithful source.

Windows Server 2025 inlined **zero** additional Set operands because the
remaining Windows Set operands are filtered or otherwise outside the proof
class. They remain named.

This is especially relevant to the 30-rule RHEL layered-configuration family
identified in ../residual-patterns-12/: all 30 use exactly one \`union\` Set
with two unfiltered Object-reference operands. The result suggests that much of
their remaining authoring indirection may be removable through **recursive
locality alone**, without inventing a new Set/effective-configuration syntax.

This still does not prove that unioning source locations models configuration
precedence or effective-value semantics. It only proves that the existing Set
graph can be presented more locally without structural loss.

## Retained-component reason census

A follow-up census classified why components still remained Assessment-scoped
after direct locality and the bounded private Set-operand rule.

Across the same 676 RHEL 9 + Windows Server 2025 Assessments, the original
1,087 Objects fell to **107**. Those 107 break down as:

| Reason the Object remained named | Count |
| --- | ---: |
| Referenced only by graph/dataflow, not directly by a Test | 73 |
| Directly shared by multiple Tests | 19 |
| Referenced by one Test plus other graph/dataflow | 15 |

Only **34 / 1,087 original Objects (3.1%)** therefore have any direct
same-Assessment sharing pressure after the bounded locality transforms. The 73
graph-only survivors are candidates for further consumer-local placement
(Variable, Set, Filter, or another explicit dataflow construct), not evidence
that an Assessment-wide Object registry is normally useful.

The 858 original States fell to **125**:

| Reason the State remained named | Count |
| --- | ---: |
| Graph/filter-side reference | 57 |
| Shared by multiple Tests | 40 |
| Unreferenced or otherwise outside the direct-reference classifier | 28 |

This motivates a stronger research hypothesis:

> **Local to the semantic consumer; explicit shared acquisition only when
> collection identity is genuinely shared.**

For States, the consumer may be a Test or Filter. A shared State is a predicate,
so future research can test whether repeated consumers may carry local copies
while provenance retains the source identity.

Objects require a stricter boundary. Copying one shared Object into two Tests
can change acquisition identity, collection timing/caching, completeness, and
evidence. The stronger Object-local model therefore SHALL NOT be justified by
textual duplication. Genuine shared acquisition should instead be evaluated
against the project's explicit shared collection-execution / Item-materialization
model.

This census is evidence for further research only. It does not change the
0.3.0 schema.

## Consumer-local State and filtered-Set follow-up

The next experiment strengthened the locality rule from "private to one Test" to
"local to the semantic consumer."

A State used by a Test may be rendered beside that Test. A State used by a Set
Filter may be rendered beside that Filter. When the same source State is reused
by multiple consumers, each consumer receives the same predicate payload plus
an identity record; mechanical re-expansion restores the one original named
State before structural comparison.

The first implementation exposed a re-expansion ordering defect for Filter
States. The research workflow failed until the restored State references were
written back before the top-level Object map was copied. The guard was not
weakened.

Across all 676 RHEL 9 + Windows Server 2025 Assessments:

| Measure | Faithful source | Consumer-local presentation | Reduction |
| --- | ---: | ---: | ---: |
| Top-level States | 858 | **28** | **96.7%** |
| Test/Object/State cross-references | 1,758 | **65** | **96.3%** |
| Named component references | 2,039 | **162** | **92.1%** |

The transform localized **164 additional State consumer occurrences** beyond
the original single-use-State pass. The 28 States left top-level have no
remaining classified Test/Filter reference in this experiment and need a
separate dead/residual-state audit before any removal claim. They are not
positive evidence that ordinary authors need a global State registry.

A further bounded Object experiment allowed a single-use leaf Object to inline
into its Set operand even when that operand carries Filters. The Filter list,
actions, referenced/localized State predicates, Set operator, and enclosing
Object/Test boundaries remain unchanged.

That reduces top-level Objects from 107 after unfiltered recursive locality to
**98**:

- RHEL 9: 777 -> **38** (**95.1%** reduction);
- Windows Server 2025: 310 -> **60** (**80.6%** reduction);
- combined: 1,087 -> **98** (**91.0%** reduction).

The 98 survivors are:

- 64 graph/dataflow-only Objects;
- 19 Objects shared directly by multiple Tests;
- 15 Objects used by one Test plus graph/dataflow.

This strengthens, but does not yet prove, the authoring hypothesis:

> **State belongs with its consumer. Object belongs with its consumer unless
> acquisition identity/reuse is semantically meaningful.**

Object duplication across Tests remains intentionally unproven because repeated
acquisition can differ from one shared collection in timing, completeness,
evidence, and caching.

Latest successful workflow for the combined consumer-local experiment:
https://github.com/vanderpol/scap-ng/actions/runs/37613657218

## Residual State audit

The 28 States left after consumer-localization are not shared predicates.

Reference analysis finds **zero consumers** for all 28: no Test, Filter,
Variable, Object graph, or evaluate expression references them.

They occur in only 12 production Rules:

- RHEL 9: SV-257881, SV-257890, SV-258042, SV-258045, SV-258105;
- Windows Server 2025: SV-278028, SV-278030, SV-278138, SV-278240,
  SV-285320, SV-285321, SV-285322.

Counts:

- RHEL: 10 unreachable States;
- Windows Server 2025: 18 unreachable States.

This closes an important scoping question: the production census currently
provides **no positive example requiring an Assessment-wide State registry**
after State predicates are allowed to live with their semantic consumers.

Whether faithful conversion should retain unreachable legacy States as
migration evidence is separate from native authoring. They SHALL NOT be used
as evidence for a global native State scope.

## Open questions before any 0.3.0 change

- Are deterministic lexical IDs sufficient for result/evidence references to
  inline Objects and States?
- Should mixed inline/referenced entries be allowed in one `states` list, or
  should a more explicit `ref` form be used?
- Should inline components retain titles, or can some presentation-only titles
  be omitted by separate shorthand rules?
- Should an editor automatically offer "extract/hoist to shared component" and
  "inline private component" refactors?
- Does cross-Assessment collection/item reuse require an otherwise private
  Object to remain named?
- How should source migration provenance refer to an inline component without
  leaking source OVAL IDs into executable native content?
- Should Variables be allowed to contain private embedded Objects under the same
  locality rule? Current design already permits private embedded resource
  selection in Variables; this experiment intentionally did not alter Variable
  layout.

## Human status

**pending-review**

This is evidence for a possible 0.3.0 authoring-layout change, not an accepted
decision.
