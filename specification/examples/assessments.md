# SCAP-NG 0.3 examples — Assessments

**Start with the two real RHEL 9 examples below:** a Rule selecting its Assessment and a readable Test with its own Object and State. Then see what the scanner reports. Modernization features and evidence come afterward.

A **Rule** says *what is required*; an **Assessment** says *how to check it*. For the Benchmark and full Rule fields, see [Benchmark and Rule examples](README.md).

**Status:** 0.3.0 is pre-alpha. **Converted** examples come from published STIG content; **synthetic results** are illustrations, not live scans. Agreed authoring syntax that the current converter/compiler cannot yet emit is clearly labeled.


## Start here: the Rule and its automated Assessment

**SCAP 1.4:** A Rule points to an OVAL Definition; following its Tests, Objects and States usually means jumping among separate IDs. **SCAP-NG:** The Rule still says *what is required*, but its Assessment shows *how to check it*, with private Objects and States directly beside their Test.

### 1. The Rule chooses how to check the requirement

The **real RHEL 9 STIG Rule SV-257851** requires the `/home` filesystem to use the `nosuid` mount option. In SCAP-NG, a Rule selects its automated or manual Assessment by **logical ID**, without embedding filesystem locations in the Rule:

```yaml
rule:
  id: SV-257851
  assessment_choices:
    default:
      assessment: home-is-mounted-with-the-nosuid-option
    automated:
      assessment: home-is-mounted-with-the-nosuid-option
    manual:
      assessment: SV-257851.manual
```

The Rule and requirement are real. The **compiler now resolves these logical IDs** to Assessment source files and packages them automatically. Existing SCAP 1.4 converter output still uses transitional relative paths; migrating generated content and verifying all cross-file reference types remains tracked in [#199](https://github.com/vanderpol/scap-ng/issues/199).

### 2. The automated check keeps its Object and State nearby

This is a **real converted RHEL 9 Assessment** (only surrounding metadata is omitted).

```yaml
tests:
  home-mounted-nosuid-option-test:
    capability: linux.partition
    object:
      capability: linux.partition
      select:
        mount_point:
          value: .*\\/home
          operation: pattern_match
          datatype: string
    states:
      - capability: linux.partition
        state:
          field: mount_options
          value: nosuid
          operation: equals
          datatype: string
          match: one_or_more
          existence: one_or_more
    reported_elements: all
    existence: one_or_more
    match: all
evaluate:
  test: home-mounted-nosuid-option-test
```

Read the check from top to bottom: the **Test** checks the mount options; its local **Object** selects the `/home` filesystem; its local **State** expects `nosuid`; and **`evaluate`** identifies the Test that supplies the Assessment's technical outcome.

Unlike SCAP 1.4's separately referenced Test/Object/State records, this check can be understood in one place. The Rule's title, severity and fix remain in the [policy example](README.md#rhel-9-rule--the-requirement).

## The alternative: a manual Assessment

**SCAP 1.4:** Manual STIG Check Text generally lives in XCCDF. **SCAP-NG:** The real procedure becomes a first-class Assessment with explicit recorded responses.

**Real converted RHEL 9 SV-257851:** the manual procedure explains how to verify `/home` has `nosuid`. Its response choices include:

```yaml
assessment:
  id: SV-257851.manual
  mode: manual
  response:
    type: compliance
    choices:
      - value: pass
        label: Pass
        outcome: 'true'
      - value: fail
        label: Fail
        outcome: 'false'
    allow_comment: true
    allow_evidence: true
```

A completed manual result can record **who checked it, when, the answer, and supporting evidence**. See the [synthetic Manual Assessment Result](0.3.0/results/manual-assessment-result.json).

## After scanning: Assessment Results that explain why

**OVAL / SCAP 1.4:** A Definition's outcome, the Test verdicts, and collected System Characteristics live in separate structures. Understanding a failure requires joining Tests, Objects, States and Items.

**SCAP-NG:** One Assessment execution produces a self-contained Assessment Result. Each Test has its **technical outcome**, reported system Items and expected-versus-observed comparisons **together**. This works for standalone Assessment scans as well as for Benchmark-linked results.

### One failed file ownership Test

The [single-file synthetic Assessment Result](0.3.0/results/assessment-result.json) includes this Test-local observation (other fields and comparisons omitted here):

```json
{
  "id": "file-owner-is-root",
  "outcome": "false",
  "per_item_results": [{
    "item_ref": "config-file-1",
    "item": {
      "id": "config-file-1",
      "capability": "unix.file",
      "status": "exists",
      "fields": {
        "full_path": {"datatype": "string", "value": "/etc/example.conf", "status": "exists"},
        "owner_uid": {"datatype": "integer", "value": 1001, "status": "exists"}
      }
    },
    "outcome": "false"
  }]
}
```

The complete result also shows the decisive comparison: **UID 1001 found; UID 0 required**, along with the owner's name, collection provenance and other authorized attributes.

### Several files, including two different checks

Our [three-Item synthetic Assessment Result](0.3.0/results/assessment-result-multi-file.json) retains each Item's path, type, owner, group, mode, size and provenance directly beside the per-Item Test verdict:

| File or directory | UID found | UID required | Technical outcome |
| --- | ---: | ---: | --- |
| `/etc/example.d` | 0 | 0 | `true` |
| `/etc/example.d/agent.conf` | **1001** | 0 | **`false`** |
| `/etc/example.d/network.conf` | 0 | 0 | `true` |

This fixture also checks the **same `agent.conf` file a second time**, against a *different* requirement:

- **Owner Test:** UID **1001** was found; UID **0** was required.
- **Permissions Test:** mode **`0644`** was found; mode **`0600`** was required.

Both Tests can display the same collected Item next to *their own* comparisons. Repeating the data in the report need not mean recollecting it.

### Normal versus diagnostic evidence: same Assessment

The **scanner application**, not a separate Benchmark or Assessment file, selects the evidence-retention limit. A diagnostic run may override it, without modifying the authored checks or verdict.

| | Normal scan | Diagnostic run |
| --- | --- | --- |
| Per-Test maximum reported Items | 2 | 50 |
| Failing Items observed | 20 | 20 |
| Detailed Items retained | 2 | 20 |
| Assessment outcome | `false` | `false` |
| Entire population evaluated? | No | No |

Compare the [normal bounded-evidence fixture](0.3.0/results/assessment-result-bounded-evidence.json) with the [diagnostic override fixture](0.3.0/results/assessment-result-diagnostic-override.json). These are **synthetic examples**, not real scanner runs. Their `evidence_retention` object records the effective per-Test maximum and whether it came from scanner configuration or an operator override, including the override reason. **50 is an example setting, not a hidden default.**

An evidence cap limits retained examples, **not what the Test evaluates**. If actual collection stops early, the result separately reports incomplete population and an unknown final mismatch total. Raising the reporting limit does not bypass scanner resource safeguards or author-controlled `reported_elements` and redaction. The [Benchmark Result](README.md#readable-benchmark-and-rule-results) needs only the concise decisive finding; the Assessment Result preserves the detailed technical evidence.

## Applicability: first check whether a rule applies

**SCAP 1.4:** Applicability can be scattered among CPE, XCCDF, and OVAL. **SCAP-NG:** Applicability refers to explicit technical Assessments.

The converted RHEL 9 Benchmark has an applicability check for the `gnome-shell` package. Here is the **current logical-ID authoring form**, which the compiler resolves; legacy converter output may still contain transitional paths ([#199](https://github.com/vanderpol/scap-ng/issues/199)):

```yaml
applicability:
  id: benchmark.rhel_9.applicability
  conditions:
    benchmark.rhel_9.condition.gnome-shell-package:
      assessment: condition.gnome-shell-package
```

The Assessment checks whether `gnome-shell` is installed using `linux.rpminfo` or `linux.dpkginfo`. Applicability is an explicit Test, **not an assumption inferred from CPE text**.

## Practical authoring improvements

SCAP-NG keeps familiar OVAL concepts (Test, Object, State, Variable, Item) but puts them where readers need them. Each short example is source-derived; see the [modernization review guide](../../review/current/REVIEW-GUIDE.md) for full before/after files.

### Consumer-local components and shared Objects

**SCAP 1.4:** Even private Objects/States live in separate registries. **SCAP-NG 0.3:** Keep the private parts with the Test, while preserving named acquisitions when they are genuinely referenced.

**Real converted RHEL 9 SV-258029:** a shared dconf directory acquisition feeds a private text-file Object (excerpt; full Set/Filter/select fields are in the [review guide](../../review/current/REVIEW-GUIDE.md#1-consumer-local-components-plus-a-genuinely-shared-object)):

```yaml
shared_objects:
  dconf-database-directories-object:
    capability: unix.file
    set:
      operator: union
      # Operands and Filter remain in the full file
tests:
  dconf-disable-restart-buttons-true-test:
    capability: independent.textfilecontent54
    object:
      capability: independent.textfilecontent54
      for_each:
        item: item
        in: dconf-database-directories-object
```

The [review guide](../../review/current/REVIEW-GUIDE.md) links the complete faithful and modernized files.

### Static values without Variable plumbing

**SCAP 1.4:** Static multi-value constants often require separate Variables. **SCAP-NG 0.3:** Inline exact compile-time literals while retaining datatype and source quantifiers.

**Real converted RHEL 9 SV-257923:** library directories are listed directly in a `unix.file` selector:

```yaml
select:
  directory:
    value:
      - /lib
      - /lib64
      - /usr/lib
      - /usr/lib64
    operation: equals
    datatype: string
    value_match: one
```

This changes **authoring**, not the required behavior. `value_match` controls comparisons against expected values (including literal arrays, Inputs and Variables); it is distinct from observed-entity `match` and existence. This is the finalized 0.3 vocabulary; conversion and six-state regression are tracked in [#194](https://github.com/vanderpol/scap-ng/issues/194).

### Runtime collection `for_each`

**SCAP 1.4:** Object → ObjectComponent → Variable → Object chains may exist simply to feed each collected Item into another collection.

**SCAP-NG 0.3:** **RHEL 9 SV-258029** is a *mechanically converted* use of collection iteration. This actual excerpt belongs to its text-file Test Object:

```yaml
for_each:
  item: item
  in: dconf-database-directories-object
select:
  directory:
    from: item.directory
```

This expands a collection, not one Test per Item, and does not change Test aggregation.

**Nested production case — Windows Server DNS SV-259388:** The original PowerShell code iterates zones and A/AAAA hosts and checks RRSIG responses. Native correlated nested iteration is illustrated in the [0.3 review guide](../../review/current/REVIEW-GUIDE.md), but it is **production-derived native authoring, not an automatic rewrite**: the converter cannot prove arbitrary PowerShell semantics, so the real generated candidate retains the command.

### Direct Variable evaluation

**SCAP 1.4:** Comparing computed values can require an artificial Variable Object. **SCAP-NG 0.3:** The real **RHEL 9 SV-258045** UID-uniqueness check uses `variable.value` directly, retaining both runtime Variables.

```yaml
tests:
  uids-unique-test:
    capability: variable.value
    variable: count-passwd-entries-variable
    states:
      - capability: variable.value
        state:
          field: value
          value:
            variable: count-unique-uids-variable
          operation: equals
          datatype: integer
```

This is an excerpt; the full converted example also includes explicit quantifiers and reporting fields.

### Predictable named component IDs

**SCAP 1.4:** Internal OVAL identifiers are often difficult to interpret by inspection. **SCAP-NG 0.3:** Descriptive kebab-case names carry the component-type suffix.

**Real RHEL 9 SV-258045** uses `interactive-users-object`, `count-passwd-entries-variable`, `count-unique-uids-variable`, and `uids-unique-test`. Private inline components need no artificial IDs.

### Localized Set and Filter semantics

**SCAP 1.4:** Separate Objects may be necessary even for one check's local Set. **SCAP-NG 0.3:** **Oracle Linux 9 SV-271608**, verifying MFA certificate status checking, puts the two SSSD configuration-file acquisitions inside the Test's Object while **retaining their `union` operator**. The underlying files are `/etc/sssd/sssd.conf` and `/etc/sssd/conf.d/*.conf`. See its [source-linked review](../../review/current/REVIEW-GUIDE.md#6-set-and-filter-semantics-remain-explicit).

The same principle applies to Filters: locality is a presentation improvement, not a reason to alter set membership or filter action.

### Explicit evaluation logic

**SCAP 1.4:** `criteria` composes Boolean Tests, sometimes with many references. **SCAP-NG:** `evaluate` preserves genuine multi-Test logic instead of burying it in execution code.

**Real converted Windows Server DNS SV-259388** retains three ways to satisfy the Rule: caching-only, AD-integrated zones, or both IPv4 and IPv6 RRSIG checks:

```yaml
evaluate:
  any:
    - test: dns-server-caching-only-there-no-forward-or-reverse-lookup-test
    - test: all-forward-lookup-zones-if-any-integrated-active-directory-test
    - all:
        - test: there-at-least-one-rrsig-resource-record-signature-associated-each-test
        - test: there-at-least-one-rrsig-resource-record-signature-associated-each-2-test
```

This is the actual converted tree, not a fabricated `evaluate` example.

## Advanced or not-yet-automated features

These examples involve semantics that must **not** be silently rewritten during lossless SCAP 1.4 conversion. A conceptual example is not proof that a converter emits it.

### Conditional evaluation

**SCAP 1.4:** Platform-dependent requirements often hide behind nested Boolean
criteria and guard Tests. **SCAP-NG:** `evaluate: if/then/else` is available
for explicitly authored branch semantics (inherited from 0.2), **but a converter
must not silently rewrite a source Boolean graph**.

**Real Windows Server 2025 SV-278001:** Domain controllers and other servers
have different Registry-permission requirements. The converted 0.3 Assessment
preserves the source `evaluate: all/any/not` expression; see
[SV-278001 in the actual review bundle](../../review/current/REVIEW-GUIDE.md#7-explicit-evaluate-where-composition-is-real).

Conceptually a publisher might author:

```yaml
evaluate:
  if:
    test: system-windows-domain-controller-test
  then:
    test: default-domain-controller-permissions-hkey-local-machine-system-registry-key-test
  else:
    test: default-non-domain-controller-permissions-hkey-local-machine-system-registry-test
```

**This excerpt is not the converted result or a complete equivalent Assessment.**
If the role Test is `unknown` and *both* permission Tests are `false`, the
source Boolean graph can resolve `false`, while the conditional cannot select a
branch and yields `unknown`. An author may intentionally choose conditional
behavior; a lossless converter cannot guess that choice. See the
[existing conformance fixtures](../../tests/conditional-0.2.0/README.md)
and [source-pattern research](../../research/assessment-simplification/conditional-10/README.md).

### Organizational Input

**SCAP 1.4:** Site-specific expected values often require a chain of XCCDF
Value → Tailoring → external OVAL Variable. **SCAP-NG:** The publisher declares
a typed Benchmark Parameter, the Rule binds it to an Assessment Input, and an
approved Organizational Input Set supplies the value **without changing the
published Test logic**.

**Integration research fixture, not a DISA STIG Rule:** The publisher delegates
the allowed filesystem types for `/home` to the organization. The site supplies
`[ext4, xfs]`, and a `linux.partition` Assessment evaluates the collected
`fs_type` against that input:

```yaml
states:
  - capability: linux.partition
    state:
      field: fs_type
      value:
        input: approved-filesystem-types-input
      operation: equals
      datatype: string
      value_match: one_or_more
      match: one_or_more
      existence: one_or_more
```

The Benchmark parameter, Rule binding, Assessment input contract, completed
Input Set, request and resolution context are shown together in the
[worked source files](../../research/iterations/003/examples/organizational-input/README.md).
**Status:** research illustration—not a complete verified 0.3 package. The direct input-resolution contract
still requires end-to-end proof; these are *fictional site values*, not a DISA-approved STIG modification.

**Template ownership:** The publisher/build should provide a typed Input Set
template for declared organization-resolved Parameters; the scanner may help
populate and validate it. Arbitrary scanner-created Tailoring of fixed policy
values is a different, deferred capability ([#196](https://github.com/vanderpol/scap-ng/issues/196)).
Missing required input must not produce a fabricated pass.

### Referencing another Assessment (advanced)

An Assessment can depend on another Assessment's result and combine it in its own `evaluate` expression. That is **result reuse**, distinct from sharing collected Objects or Items across Assessments.

**Agreed logical-ID authoring target (illustrative; not yet compiler-supported):**

```yaml
assessment:
  id: example.composed-assessment
  dependencies:
    platform-applicable:
      assessment: example.platform-applicable
      expected_version: 1
      purpose: applicability
  evaluate:
    all:
      - assessment: platform-applicable
      - test: local-setting-correct
```

The publisher refers to the stable Assessment ID; the build resolves it within a declared source/import scope, checks the type and version, rejects cycles, and packages the dependency. The alias `platform-applicable` remains local to the requesting Assessment.

**Status:** logical-ID dependency compilation is implemented and regression-tested, including version/purpose checks and cycle rejection ([#199](https://github.com/vanderpol/scap-ng/issues/199)). Full migration of generated source is ongoing; broader cross-Assessment runtime collection sharing is deferred ([#44](https://github.com/vanderpol/scap-ng/issues/44)).

### Two research-only design studies

**Flagship integration example: [Windows Server 2025 SV-278029 — time synchronization](../../research/iterations/003/examples/stig-derived/SV-278029/README.md).** Combines reusable domain/PDC applicability, conditional evaluation, existing Registry collection, approved organizational time sources, and explainable results. [Readable proposed authoring](../../research/iterations/003/examples/stig-derived/SV-278029/readable-authoring.proposal.yaml) is **research-only, not schema-valid or executable**; PDC resolution, NTP token parsing and missing-input semantics remain open. This example supports side-by-side comparison of original requirements and proposed authoring.

**Focused companion: [Windows Server 2025 SV-278217 — DWORD Registry type/value](../../research/iterations/003/examples/stig-derived/SV-278217/README.md).** Tests whether streamlined authoring preserves `REG_DWORD` versus `REG_SZ` versus `REG_MULTI_SZ`, numeric type and explicit existence. This is **also proposed research syntax** and does **not** replace the NTP case.

## Evidence and further reading (optional)

The examples above show how to read and write an Assessment; you don't need the following engineering details to start.

### Where to find real source files

The [0.3 six-benchmark review package](https://github.com/vanderpol/scap-ng/actions/runs/37813594321) contains real converted Linux, Windows, DNS and Apache authoring sources. The [review guide](../../review/current/REVIEW-GUIDE.md) identifies each before/after Rule and Assessment. Search the downloadable `authoring/` tree for **`for_each:`** (not `foreach`), `shared_objects:`, `evaluate:`, or `assessment_choices:`.

In this pinned six-benchmark artifact there are **8 `for_each:` occurrences across 7 Assessments** and **79 `shared_objects:` occurrences**; these numbers describe a single build, not an entire standard or runtime scan. The checked `reported_elements:` entries in that bundle are all `all`—the bundle does **not** demonstrate selective redaction, native conditionals, Organizational Input binding, cross-Assessment result reuse, or *live* scanner output. See the [fixture catalog](0.3.0/results/README.md) for expressly synthetic results.

### What the production conversion measurements actually mean

**Where the 65 benchmarks came from.** NIWC Atlantic publishes a public
[SCAP 1.4 content library](https://github.com/niwc-atlantic/scap-content-library).
For a reproducible baseline, this project pinned its `Current/` directory to
[revision `8c8e5dff`](https://github.com/niwc-atlantic/scap-content-library/tree/8c8e5dff860af6b1290ee9273a282db24278f8d5/Current).
That snapshot contains **65 individual signed benchmark ZIPs** for operating
systems and applications, plus **one consolidated bundle**. The bundle is not a
66th distinct benchmark. These are existing production SCAP 1.4 artifacts,
not 65 examples written specifically for SCAP-NG. We used them to see whether
the new design works beyond hand-picked demonstrations.

**What we did.** We ran conversion and modernization across that frozen
source set, compared fidelity-first generated Assessments with the same
Assessments after supported, semantics-preserving 0.3 authoring simplifications,
and separately validated six representative benchmark trees for human review.
The figures below describe **conversion and authoring structure**, not scans
of live machines or a claim that all SCAP 1.4 constructs are supported.

| Measure | Observed result |
| --- | --- |
| Individual SCAP 1.4 benchmark packages examined | **65** |
| Packages converted | **61** |
| Known blockers | **4**, all from the unsupported SQL extension; **0 unexpected** |
| Representative benchmark trees passing schema and semantic validation | **6 of 6** |
| Rule Assessments in the measured modernization set | **6,916** |
| Confirmed automatic `for_each` rewrites | **55** |
| Compile-time constant Variables folded | **509** |
| Fewer top-level named Objects / States | **95.68% / 100%** |
| Fewer top-level Variables / named component references | **59.69% / 94.42%** |
| Reduction in normalized serialized bytes / lines | **3.13% / 5.20%** |

**How to read the reductions.** The dramatic percentages refer to the
*top-level named component graph* that an author must navigate: many Objects
and States moved next to their consuming Test rather than disappearing as
actual collection or comparison behavior. They are **not** a 95% reduction
in file size, scanner work, or runtime, and do not mean all real-world
assessment complexity disappeared. The much smaller byte/line changes
provide an important cross-check on that distinction. The converter deliberately
retains complex structures when simpler syntax would alter OVAL results.

For the actual before/after STIG cases, see the
[modernization review guide](../../review/current/REVIEW-GUIDE.md).
The [current review page](../../review/current/README.md) maintains the
validated build, detailed census evidence, and links to the downloadable
artifact. The [corpus manifest](../../tests/corpus-manifest.yaml) records
the exact source snapshot and separates real production migration evidence
from synthetic conformance fixtures.

### Review and future work

- [Current 0.3 review and evidence](../../review/current/README.md) — source-specific samples and the latest verified review artifacts.
- [Historical 0.2 Board samples](../../board/review-content/0.2.0/README.md) — earlier checkpoint, not current 0.3 examples.
- [Deferred 0.3 decisions](../deferred-after-0.3.md) — Shared Observation and a redesign of `evaluate` are deferred, not silently added. 0.3 also does not introduce a separate shared-applicability artifact.

The six-benchmark validation is **static source/schema/compile evidence**, not proof of scanner-runtime equivalence. The 65-source release gate and known extension blockers are tracked in [#202](https://github.com/vanderpol/scap-ng/issues/202).

