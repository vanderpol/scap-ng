# Alignment Without Exact Automation Reuse

## Why this example matters

The four-anchor mapping found one cross-benchmark rule pair whose normalized
XCCDF Check Text is identical but whose complete OVAL assessment semantics are
not equivalent.

This is a useful control case for the reuse experiment: **rule alignment and
assessment reuse are deliberately different conclusions.**

## Aligned policy rules

**RHEL 9**

- Rule: `xccdf_mil.disa.stig_rule_SV-257920r1101926_rule`
- Title: "RHEL 9 library files must be owned by root."

**Oracle Linux 9**

- Rule: `xccdf_mil.disa.stig_rule_SV-271790r1134866_rule`
- Title: "OL 9 library files must be owned by root."

Their normalized Check Text is identical and instructs the reviewer to inspect
shared library files beneath `/lib`, `/lib64`, `/usr/lib`, and
`/usr/lib64` for files not owned by root.

Therefore the rules are mapped as corresponding policy requirements.

## Why the OVAL is not considered equivalent

Both implementations use a Unix `file_test` with
`check_existence="none_exist"`, but their collection/filter semantics differ.

### Oracle Linux 9

The Oracle implementation:

- uses a filename pattern equivalent to `\.so(\S+)*$`;
- includes objects with file type `regular`;
- excludes objects whose user ID is root;
- relies on the source/default filter semantics for that exclusion.

### RHEL 9

The RHEL implementation:

- uses a narrower filename pattern equivalent to `\.so(\.\d+)*$`;
- excludes objects owned by root;
- explicitly excludes symbolic links;
- explicitly excludes directories.

These differences are preserved in the canonical semantic graph and therefore
produce different exact semantic fingerprints.

## Required conclusion

The pair is:

- **policy aligned:** yes, by identical normalized Check Text;
- **exact automated assessment reuse:** no;
- **automatic parameterized reuse:** not established;
- **review candidate:** yes.

The converter/reuse tooling must not choose one implementation and silently use
it for both benchmarks.

This is exactly the kind of distinction a shared-assessment model must preserve:
discovering that policies correspond is useful, but reuse is permitted only
when the technical semantics have also been shown equivalent or a reviewed
parameterization explicitly accounts for the differences.
