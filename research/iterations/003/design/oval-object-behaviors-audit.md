# OVAL Object behaviors: required semantic audit before SCAP-NG assessor freeze

**Status:** OPEN, blocking full behavioral-compatibility claims (2026-09-30).  
**Authority:** pinned *upstream* OVAL 5.12.3 XSD, embedded Schematron and normative Object/collector documentation. The SCC/NIWC augmented schemas are not authoritative for standard vocabulary.  
**Scope:** *all non-deprecated, supported* standard OVAL Object families, including behavior types inherited through XSD extensions and Object elements that define inline behavior types. SCC-specific `sqlext` remains out of scope.

## What was actually implemented

At the time this audit began, the Stage-1 lowerer in
`tools/scap_upconvert_v003/build_rhel9_review_slice.py` populated NG
`collect.behaviors` from `dict(child.attrib)`, **only if a source
`behaviors` element was present with explicit attributes**.
`native_assessment_to_oval.py` regenerated those attributes. The independent
`compare_oval_semantics.py` canonicalized the same explicit attribute map.

This proves fidelity for *explicit lexical attributes* encountered in passing
corpora. It does **not** independently test default expansion, collector
meaning, schema conditionals, behavior side effects, or runtime semantics when
a `behaviors` element/attribute is absent. A round trip can therefore pass
while the effective behavior remains hidden to NG content authors.

## Representative defaults verified against upstream OVAL v5.12.3

| Upstream family/type | Attribute | Declared XSD default | Important interpretation |
| --- | --- | --- | --- |
| unix:FileBehaviors | `max_depth` | `-1` | Unlimited maximum depth **if** recursion is active. |
| unix:FileBehaviors | `recurse` | `symlinks and directories` | What to recurse through when recursion is active. |
| unix:FileBehaviors | `recurse_direction` | `none` | Recursion disabled by default regardless of `max_depth=-1`. |
| unix:FileBehaviors | `recurse_file_system` | `all` | Filesystem scope of traversal when applicable. |
| independent:FileBehaviors | `max_depth`, `recurse`, `recurse_direction`, `recurse_file_system` | same core defaults | Also inherited by multiple independent content selectors. |
| independent:Textfilecontent54Behaviors | `ignore_case` | `false` | Case-sensitive regex matching. |
| independent:Textfilecontent54Behaviors | `multiline` | `true` | Anchors apply at line boundaries. |
| independent:Textfilecontent54Behaviors | `singleline` | `false` | Dot does not match a newline by default. |
| independent:ShellCommandBehaviors | `error_if_exit_status_not_0` | `false` | Nonzero exit status does not by itself flag collection error. |
| independent:ShellCommandBehaviors | `error_if_stderr_exists` | `false` | Stderr output does not by itself flag collection error. |
| independent:XMLFileContentBehaviors | `item_creation` | `all_object_elements_fullfilled` | Different from `filepath_exists`: can change item presence/existence results. |
| linux:RpmVerifyBehaviors and related types | `nodeps`, `nodigest`, etc. | `false` for documented flags | Every flag may change the work performed, collected facts and performance. |

**Caution:** A default on an XSD attribute does not establish that a scanner
must automatically materialize it when the entire optional parent
`behaviors` element is absent. For each Object family, inspect the Object's
schema/content model and prose to determine whether *absent behaviors
element*, *present empty behaviors element*, and *present partially populated
behaviors element* are semantically identical. If this is ambiguous, record
`requires_review` rather than guessing.

The `max_depth`/`recurse_direction` example also illustrates that
attributes may be **conditionally applicable**; mere equality of enumerated
defaults is not enough to prove collection equivalence. Unix and Linux file
behavior documentation also distinguishes `filepath` from `path` +
`filename` (recursion flags do not apply to `filepath`).

## Normative model requirements proposed for SCAP-NG

1. Each Capability SHALL define a versioned **behavior contract** listing
   attributes, types, allowed values, effective defaults, applicability
   conditions, and effects on collection/results/errors.
2. A native Assessment SHOULD serialize all **effective** behavior settings
   relevant to the collection, including those inherited from supported source
   defaults; values must not depend on private collector tribal knowledge.
3. A Stage-1 converter SHALL compute behaviors against the *correct upstream
   behavior type*, including XSD inheritance and the semantics of an omitted
   parent element; it SHALL NOT normalize unknown defaults speculatively.
4. The representation SHALL distinguish **source-specified**, **inherited
   default**, and **not applicable** in conversion provenance. Native authored
   values MAY be fully explicit without retaining legacy origin markers.
5. When a behavior changes item creation/existence, filtering, recursion,
   status/error flags, collector privileges, scope, or performance, its
   semantics SHALL be reflected by the evaluator and results/evidence.
6. The semantic comparator SHALL compare resolved *effective* behavior
   signatures independently of raw XML attribute spelling. A separate
   structural diff MAY preserve source lexical provenance.
7. Unknown or unimplemented non-default behaviors SHALL block conversion of
   the affected Definition with an exact diagnostic; support for some
   capabilities SHALL NOT imply support for all their behaviors.
8. A native assessor conformance profile SHALL identify the capabilities
   and **behavior variants** actually executed and validated; schema-only
   support is not execution support.

## Required work sequence

- [ ] Extract behavior types for every upstream OVAL 5.12.3 Definition XSD:
  Object→behaviors element mapping, type inheritance, local attributes, defaults,
  ranges/enums, deprecation and Schematron rules, prose/doc anchor.
- [ ] Produce per-Capability inventory and coverage matrix, explicitly listing
  Objects without a behavior element, missing defaults, family overrides, and
  ambiguous omission/conditional behavior.
- [ ] Define a vetted behavior-default resolver and canonical signature,
  independent of both the NG lowerer and reverse OVAL generator.
- [ ] Normalize each supported behavior into explicit human-readable native
  Collection fields; preserve source-explicit versus default provenance
  separately.
- [ ] Add synthetic negative tests proving missing or incorrect default
  expansion is detected (e.g. `multiline`, recursion direction, command error
  flags, XML item_creation).
- [ ] Add positive tests for explicit default equal to omitted default **only
  where source semantics establish equivalence**.
- [ ] Add behavioral-compatibility tests for each capability and variant:
  recursion with/without symlinks, path vs filepath, regex flags, item
  creation, RPM verify flags, nonzero shell exit status/stderr. Use SCC/source
  evaluation or a reference scanner against controlled fixtures.
- [ ] Require behavior coverage summary in full-corpus census and complete
  Benchmark review artifacts; do not claim the RHEL9 assessment set is fully
  executable based only on schema/semantic-graph gates.

## Review distinction

- **Proven currently:** explicit attribute copying and regeneration, for
  behavior variants exercised by successful round-trip tests.
- **Not yet proven:** all schema-declared behavior variants, implicit defaults,
  absence semantics, conditional applicability, and runtime effects.
- **Priority:** blocking before a declaration that native SCAP-NG *fully
  supports OVAL behaviors* or that reference scanner assessment semantics are
  frozen. It need not delay an earlier **format/layout-only** review of the
  complete RHEL9 benchmark, if that review is clearly labeled as such.

Reference: `specification/migration/oval-5.12.3-to-ng.md`,
`specification/assessment/assessment-method.md`,
`research/iterations/003/design/oval-derived-specification-lessons.md`.
