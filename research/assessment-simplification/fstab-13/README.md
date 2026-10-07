# Typed `/etc/fstab` assessment research

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**
>
> This study does not change schema/v0.3.0, the converter contract, capability
> semantics, or the frozen 0.2.0 baseline. It evaluates whether recurring
> `independent.textfilecontent54` + Variable plumbing around `/etc/fstab`
> should become a typed native capability.

## Question

Can SCAP-NG represent persistent Linux mount configuration as typed records
without changing the semantics of existing published OVAL checks?

The key distinction is:

- `linux.partition` describes the **currently mounted** filesystem; and
- `/etc/fstab` describes **persistent configuration text**.

Those are different evidence sources and must not be silently merged.

## Source evidence

Production source is the pinned NIWC RHEL 9 V2R9 enhanced package at revision:

`8c8e5dff860af6b1290ee9273a282db24278f8d5`

The maintained converted RHEL 9 source contains **23 automated Assessments that
read `/etc/fstab`**.

Observed families include:

| Family | Representative Rules | Shape |
| --- | --- | --- |
| Live + persistent mount option | SV-257863, SV-257864, SV-257865, SV-257868, SV-257869, SV-257874, SV-257875, SV-257876, SV-257878 | `linux.partition` plus direct `textfilecontent54` option test |
| Split Variable persistent option | SV-257866, SV-257870, SV-257871, SV-257872, SV-257873 | live partition + text row presence + projected/split option Variable |
| Separate filesystem | SV-257844, SV-257845 and related cases | live partition existence + persistent row existence |
| NFS-wide option policy | SV-257854, SV-257855, SV-257856 | select all NFS rows and test option text |
| Non-root local partition policy | SV-257881 | live partition filter + persistent device/mount row policy |
| Derived mount target | SV-257847 | target path derived from another configuration source before fstab lookup |

The five split-Variable Rules are the most obvious readability problem, but they
are not the whole `fstab` use case.

## OVAL baseline

OVAL 5.12.3 has no `fstab_test`.

The OVAL Community `v5.12.3` Linux schema defines `partition_test` for
partitions on the local system. Its `mount_options` documentation explicitly
warns that `/etc/fstab` may contain additional options and MUST NOT be relied
upon as the mounted-filesystem source.

Therefore a native persistent-configuration feature should **not** redefine
`linux.partition`. If pursued, a separate typed capability such as
`linux.fstab` is the cleaner model.

## Representative real case: SV-257866

Requirement:

> RHEL 9 must mount `/tmp` with the `nodev` option.

The published manual procedure checks the live mount. The automated OVAL-backed
Assessment is stricter: it also requires a matching `/etc/fstab` row and
requires the persisted options to contain `nodev`.

### Faithful converted shape

Condensed from the maintained conversion:

```yaml
evaluate:
  all:
    - check: tmp-mounted-nodev-option
    - check: tmp-configured-nodev-option-in-etc-fstab
    - check: tmp-configured-in-etc-fstab

checks:
  tmp-mounted-nodev-option:
    capability: linux.partition
    collect:
      select:
        mount_point: /tmp
    assert:
      state:
        field: mount_options
        value: nodev
        entity_check: at least one

  tmp-configured-nodev-option-in-etc-fstab:
    capability: independent.variable
    collect:
      select:
        var_ref:
          variable: mount-options-tmp-in-etc-fstab
    assert:
      state:
        field: value
        value: nodev
        entity_check: at least one

  tmp-configured-in-etc-fstab:
    capability: independent.textfilecontent54
    collect:
      select:
        filepath: /etc/fstab
        pattern:
          value: '^\\s*[^#\\s]+\\s+/tmp\\s+\\S+\\s+(\\S+)\\s+\\S+\\s+\\S+\\s*$'
        instance:
          datatype: int
          value: '1'

variables:
  mount-options-tmp-in-etc-fstab:
    expression:
      split:
        value:
          object_values:
            collect:
              capability: independent.textfilecontent54
              select:
                filepath: /etc/fstab
                pattern:
                  value: '^\\s*[^#\\s]+\\s+/tmp\\s+\\S+\\s+(\\S+)\\s+\\S+\\s+\\S+\\s*$'
                instance:
                  datatype: int
                  value: '1'
            field: subexpression
        delimiter: ','
```

The indirection is real: authors are using a generic text regex to recover a
typed mount record and then a Variable merely to split its option field.

### Research-only typed sketch

A clearer native authoring surface could be approximately:

```yaml
evaluate:
  all:
    - check: tmp-mounted-nodev
    - check: tmp-persisted-nodev

checks:
  tmp-mounted-nodev:
    capability: linux.partition
    collect:
      select:
        mount_point: /tmp
    assert:
      existence: at_least_one_exists
      check: all
      state:
        field: mount_options
        operation: equals
        value: nodev
        entity_check: at least one

  tmp-persisted-nodev:
    capability: linux.fstab
    collect:
      select:
        mount_point: /tmp
        occurrence: first
    assert:
      existence: at_least_one_exists
      check: all
      state:
        field: options
        operation: contains
        value: nodev
```

This is a readability sketch, **not a proven migration rewrite**.

A typed Item would likely need at least:

- source/device;
- mount point;
- filesystem type;
- ordered option values;
- dump value;
- fsck/pass value;
- source line number / occurrence;
- raw source text or equivalent provenance;
- collection status/completeness.

## Why automatic conversion is not proven yet

### 1. Occurrence/order is semantic

The five split-Variable Rules use `instance: 1`. Other fstab Rules use
`instance >= 1` or `instance != 0`.

A parser that simply returns every matching mount record changes behavior when
duplicate rows exist. A typed representation must retain source order and
support the same occurrence/cardinality selection before automatic migration
can be lossless.

### 2. Missing-row behavior is intentionally composed

In the five split-Variable Rules, the projected Variable depends on a matching
text Item. OVAL ObjectComponent-style value production can become an error when
the source Object has no Items, while the separate row-existence Test is false.

The surrounding OVAL `AND` can therefore yield ordinary noncompliance rather
than exposing the Variable error as the Rule result. The apparently redundant
third Test is part of the result behavior.

A one-Test typed rewrite must prove the same six-state result behavior, not just
the same true/false intent.

### 3. Parser semantics can expand the accepted language

The source regexes implement specific lexical subsets of `fstab`. A standards-
aware parser may correctly understand escaped whitespace, unusual device
specifiers, comments, or other legal syntax that the original regex does not.

That may be a better native Assessment, but it is a semantic improvement rather
than a lossless rewrite unless equivalence is proven for the matched source
pattern.

### 4. Different Rules intentionally use different existence semantics

The corpus uses `all_exist`, `any_exist`, and `at_least_one_exists` in
different fstab checks. Those choices must remain explicit. A typed capability
must not hide them behind a convenience default.

### 5. Live and persistent state remain separate evidence

A mounted filesystem can differ from `/etc/fstab`, and `/etc/fstab` can
contain entries that are not mounted. Combining both into a single
"mount compliant" collector would erase useful evidence and change acquisition
semantics.

### 6. Multi-row policies are broader than mount-point lookup

The NFS and non-root-partition Rules select records by filesystem type or device
patterns across many rows. A useful typed capability must support record
selection generally; it cannot be only a `mount_point -> option` helper.

## Candidate capability boundary

If pursued, `linux.fstab` should be a typed **record collector**, not a policy
collector.

It SHOULD expose fstab facts and ordinary Object/State/Test mechanics should
still express:

- which records are selected;
- existence/cardinality;
- whether all/any records must satisfy a condition;
- option membership;
- Variables or derived selectors when needed.

It SHALL NOT decide whether a mount is compliant.

This keeps the capability aligned with SCAP-NG's existing rule that collectors
provide typed facts while Assessments own policy truth.

## Automatic modernization proof class

A future fail-closed rewrite could be considered only when all of these are
proven:

1. the source is the canonical `/etc/fstab` textfile pattern family;
2. every source regex field maps unambiguously to the typed record fields;
3. source occurrence/instance behavior maps exactly;
4. source existence/check/entity quantifiers are preserved;
5. option tokenization is identical, including empty/malformed values;
6. source and typed collection error/incomplete behavior is equivalent;
7. duplicate rows retain the same order and multiplicity;
8. the rewrite preserves the separate live-partition boundary;
9. the Rule's complete six-state result is equivalent for boundary cases; and
10. decisive evidence can be mapped back to the source row and option.

Outside that class, conversion must retain the faithful
`textfilecontent54`/Variable graph.

## First executable proof

Focused fixtures now model the five split-Variable Rules for the bounded case
where the underlying text collection is **complete** and the source
`instance=1` selection is preserved.

Files:

- `tools/research_fstab_semantics.py`
- `tools/test_research_fstab_semantics.py`
- `.github/workflows/fstab-modernization-research.yml`

The complete-source matrix proves:

| Source situation | Faithful graph | Compact typed candidate |
| --- | --- | --- |
| no matching row | false | false |
| first row contains required option | true | true |
| first row lacks required option | false | false |
| first duplicate lacks option, later duplicate has it | false | false |
| first duplicate has option, later duplicate lacks it | true | true |

The duplicate cases are important: source `instance=1` is semantic, so a later
matching row cannot rescue or invalidate the first matching row.

The fixture deliberately rejects empty option captures and parser/regex lexical
differences rather than silently broadening the proof class.

### Why this still does not permit an automatic converter rewrite

The proof depends on the source collection being `complete`. Collection status
is a **runtime result**, not a static property a converter can establish.

Therefore `source_collection_status == complete` cannot be a legitimate
compile-time precondition for rewriting published content. Non-complete source
status, ObjectComponent value status, and the surrounding OVAL six-state
aggregation remain part of the source semantics.

This changes the recommendation:

- the compact one-Test `linux.fstab` form is promising **native authoring**;
- it is **not** currently a safe automatic migration target;
- faithful migration must retain the source graph unless a typed shorthand is
  normatively defined to desugar to equivalent source-status/value-production
  behavior; and
- a typed collector alone must not be used as justification to collapse the
  separate presence/projection/evaluation boundaries.

The non-complete counterexample is now proven for the source processing model.
The compact form therefore remains an intentional native-authoring improvement,
not a lossless migration rewrite.

## Non-complete collection counterexample

The remaining status question is now sufficient to reject a compact one-Test
form as a lossless automatic migration.

The historical OVAL processing model defines the relevant chain as follows:

1. an ObjectComponent backed by an `incomplete` Object is itself
   `incomplete` when projected values exist;
2. zero source Items is an ObjectComponent `error`;
3. an OVAL Function evaluates only when its combined sub-component flag is
   `complete`; any other sub-component status makes the Function `error`;
4. the five real Rules put the ObjectComponent inside `split(',')`; and
5. the separate fstab-row Test over an incomplete collected Object is
   `unknown` for this existence/check shape.

OVAL 5.12.3 still explicitly states that zero source Items is an
ObjectComponent error. The OVAL Community issue discussing whether this should
ever change remains open (OVAL-Community/OVAL#59).

That produces these executable counterexamples:

| Incomplete source observation | Faithful split-Variable graph | Compact typed Test |
| --- | --- | --- |
| no matching row observed | **error** | unknown |
| first row observed and option present | **error** | unknown |
| first row observed and option absent | **error** | false |

For the faithful graph, the split/local-Variable path is `error` and the
separate row-presence Test is `unknown`; OVAL AND therefore remains
`error`.

For an ordinary typed Test, incomplete collection remains `unknown` unless a
seen item is already decisively false for `check: all`.

This is a genuine result-semantic difference. One counterexample is enough to
reject a general automatic collapse.

### Decision from this phase

**Do not automatically convert the five split-Variable Rules into one typed
`linux.fstab` Test.**

A native `linux.fstab` capability is still a strong authoring candidate, but
there are now two distinct products:

- **faithful migration:** retain the original result-producing graph unless a
  shorthand normatively desugars to all of its status/value-production
  boundaries; and
- **native reauthoring:** use the clearer typed record model and accept that it
  is a deliberate assessment modernization with its own semantics/provenance.

This is the same design discipline used elsewhere in the project: improve the
authoring surface without falsely claiming OVAL runtime equivalence.

## Before/after conclusion

The typed form is materially easier to read because it states the security
domain directly:

`persistent mount record for /tmp contains nodev`

instead of:

`regex fstab -> capture field 4 -> project subexpression -> split comma list -> test variable value`.

That is strong authoring evidence, but not yet migration-equivalence evidence.

## Recommendation

Proceed with a **research-only `linux.fstab` capability prototype** and focused
semantic fixtures.

Do **not** yet:

- extend `linux.partition` with persistent configuration;
- automatically rewrite the 23 production fstab Assessments;
- collapse live and persistent checks;
- claim six-state migration equivalence.

The complete-source zero/one/duplicate matrix is now covered by focused
fixtures. Remaining work is no longer required to decide automatic collapse: the
incomplete-source counterexample already rejects it. Follow-up research should
instead focus on the quality of a **native** typed collector:

- malformed option fields;
- comments/whitespace/escaped-field parser behavior;
- NFS/multi-row selection;
- duplicate-row evidence and source-order reporting; and
- how authoring provenance distinguishes native reauthoring from faithful
  conversion.

## Human status

**pending-review**

This research supports prototyping a typed persistent-configuration collector.
It does not yet support a schema or converter change.
