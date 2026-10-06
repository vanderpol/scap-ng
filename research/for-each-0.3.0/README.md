# SCAP-NG 0.3.0 scoped-iteration research

**Status:** research branch; not normative and not part of the 0.2.0 contract.

## Working question

Can SCAP-NG make correlated/nested assessment logic materially easier to author,
review, debug, and render than OVAL while retaining a deterministic lossless
migration path from valid OVAL 5.12.3?

The current hypothesis is that NG should separate two concerns that OVAL often
mixes through multi-valued Variables:

1. **Item identity / evaluation scope** — expressed by an explicit scoped
   iteration construct such as a future for_each.
2. **Value transport and transformation** — expressed by Variables or direct
   typed value references.

A concise working rule is:

> Bindings identify Items. Variables derive or transport values.

This is a research hypothesis, not a specification decision.

## Why this matters

OVAL local Variables can project fields from collected Items, produce
zero/one/many values, run functions over value collections, feed those values
back into Object selectors, feed State comparisons, and participate in filters
and Sets. This is expressive but makes relationships between source Items and
downstream evaluation difficult to see and, in some cases, impossible to retain
after values have been flattened.

The production corpus shows three materially different situations that must not
be conflated:

### A. Value-set dataflow

A Variable projects values from one Object and supplies them to another Object
or State. The downstream semantics operate on the **set of values**, not on the
identity of the originating Items.

This should remain legal value dataflow. It is not automatically a for_each
rewrite.

### B. Nested/dependent collection expansion

A value derived from one collected population selects another population,
possibly through several levels. OVAL can represent this as a dependency graph,
but provenance/identity normally becomes flattened into value sets.

This may benefit from explicit native iteration or comprehension syntax, but a
rewrite is lossless only if the new construct reproduces the same flattened
collection and status/error semantics.

### C. Correlated evaluation

A requirement means, for each parent Item, evaluate a child Item or collection
against data from **that same parent**.

This is the strongest case for lexical scoped iteration. A converter SHALL NOT
infer this relationship merely because two Variables originated from the same
Object; doing so can add semantics that OVAL did not encode.

## Concrete production evidence

### RHEL 9 SV-258053 — manual-only correlation

Policy: each local interactive user's home directory must be group-owned by
that home-directory owner's primary group.

The published automated benchmark has no OVAL Assessment for this rule; the
manual procedure first obtains (username, primary_gid, home_dir) and then
compares the directory's actual GID with the primary GID belonging to that same
user.

This is a direct native scoped-iteration use case:

- bind one password/account Item;
- collect/stat that bound Item's home directory;
- compare the directory GID to the bound account's primary GID.

This is evidence for new NG expressiveness. It is **not** evidence that a
lossless OVAL converter can synthesize the automation, because no source OVAL
automation exists to preserve.

### RHEL 9 SV-258155 — same-Item field correlation risk

The production automated rule derives block_size and total_space from the same
linux.partition Object and multiplies them in a local Variable.

OVAL function operands are value collections. If the source Object returns more
than one partition Item, field projections can participate in collection-valued
function semantics rather than an element-wise same-Item calculation. The
published rule therefore provides a valuable proof case for distinguishing:

- collection-valued arithmetic inherited from OVAL; from
- an NG expression evaluated against one bound partition Item.

Whether target data guarantees singleton cardinality is a separate question and
must not be assumed by conversion.

### Solaris 11 — multi-level dependent collections

Multiple production Solaris rules contain dependency chains of the form:

    account population
      -> username values
      -> second account lookup
      -> home_dir values
      -> file/directory collection

These graphs are useful conformance cases for nested dataflow and for testing
whether an NG scoped form can remain lossless when OVAL has already flattened
parent identity.

## Current corpus audit direction

The research branch scans production SCAP 1.4 benchmarks for:

- Object field -> Variable -> dependent Object edges;
- nested dependent Object chains;
- multiple projections from one source Object;
- multiple same-source fields consumed by one function;
- Object-selector and State references that appear to reuse the same source
  population;
- manual-only policy/check text that appears to require parent-child
  correlation.

Current platforms include RHEL 7/8/9, Oracle Linux 7/8/9, Ubuntu 18/20/22/24,
SLES 12/15, Solaris 11 x86/SPARC, macOS variants, Windows 11, and Apache UNIX
benchmarks.

## Conversion safety principle

The migration pipeline should have at least two distinct products:

### Compatibility representation

Preserve the OVAL dependency graph and its value-set semantics exactly enough
for semantic comparison and, eventually, differential execution.

### Native normalization

Apply only transformations with a machine-checkable equivalence proof.

A native for_each rewrite is therefore not one generic transformation.
Candidates need to be classified first.

## Candidate transformation classes

1. **value_set_preserve**
   - keep Variable/value-reference semantics;
   - no parent identity introduced.

2. **flattened_collection_rewrite**
   - possible explicit iteration/comprehension syntax;
   - output must be flattened to exactly the source collection semantics;
   - incomplete/error/zero-value behavior must be proven equivalent.

3. **scoped_iteration_proven**
   - parent Item identity is already semantically fixed or singleton in a way
     that can be proven;
   - lexical binding is equivalent, not an inferred correction.

4. **correlation_recommendation**
   - source appears to be approximating or missing a parent-child relationship;
   - preserve source semantics and emit a recommendation only.

5. **manual_native_automation_candidate**
   - source policy/manual procedure expresses correlation but no OVAL
     automation exists;
   - propose native automation for human review, never label it a lossless
     conversion.

## Variable-scope hypothesis for 0.3.0

Native NG should investigate narrowing Variables to typed value transport and
transformation. Multi-valued Variables remain necessary for real value-set
operations such as constants, external inputs, split/unique/count, regex
capture, membership-style selectors, and many-to-many State comparison.

Native authors should not need Variables merely to emulate loop control.

Candidate future requirement:

> Native SCAP-NG authors SHOULD use explicit scoped iteration when evaluation
> depends on the identity of an originating Item. A multi-valued Variable SHOULD
> NOT be used to emulate per-Item control flow.

A stronger SHALL/SHALL NOT rule is deferred until corpus classification proves
that valid non-correlated OVAL semantics retain a clear native representation.

## Next proof work

1. Complete corpus classification including manual-only correlation candidates.
2. Define a typed semantic IR node for scoped iteration before defining final
   YAML.
3. Specify zero-item, error, incomplete, truncation, and aggregation behavior.
4. Build known-result fixtures for same-Item arithmetic, parent-child
   filesystem ownership, nested dependent collections, and unequal
   cardinalities.
5. Implement a research lowering that emits a transition plan:
   proven, preserve, or review; it SHALL NOT silently rewrite review cases.
6. Only after those proofs, prototype native syntax/schema and round-trip or
   differential execution.
