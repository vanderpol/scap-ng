# Review of the three pilot capabilities

This is a documentation review, not collection qualification. The generated
platform pages contain the frozen contracts and three structural examples.
Examples pass local Draft 2020-12 validation with pinned local references; they
have not been executed on target systems. Schema probes test acceptance only.

## Source provenance

Reviewed OVAL Community **5.12.3**, tag `v5.12.3`, commit
[`2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`](https://github.com/OVAL-Community/OVAL/tree/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas).
The [machine inventory](../metadata/developer-guide-oval-audit.json) now pins eight
XSD files and 39 annotation inventories. The original three-pilot subset below
retains its six-file / 15-node identities; Phase 2 adds five capability reviews.
It includes exact namespace-qualified XPath locators; `xsd` denotes
`http://www.w3.org/2001/XMLSchema`. Descriptions here are paraphrases; original
XSD licensing remains with upstream. No complete XSD or verbatim documentation
is redistributed. Original source declarations and examples are unchanged.

Reproduce offline from that checkout:

```sh
python tools/harvest_oval_developer.py /path/to/OVAL/oval-schemas --check
```

## windows.registry

**Documented native facts:** canonical hive enum; key/value-name identity is
case-insensitive, without changing the authored comparison operator. Null key
requires null name and selects the hive; null name selects a key, while empty
name selects its default value. The generated page preserves the explicit
selectors, collected fields, type enums and value datatypes. Removed
`windows_view` is not a native selector.

**Legacy research candidates:** `registry_object` distinguishes nil from a
wildcard. `registry_state` and `registry_item` describe FILETIME units and the
containing key's last-write time, unsigned DWORD/QWORD values, hexadecimal binary,
pre-expanded versus expanded strings, and multi-string handling. The item notes
special handling of an empty multi-string. `RegistryBehaviors` describes depth,
recursion direction and 32/64-bit views. None of these details is newly adopted
merely because a native field has a matching name or integer datatype.

**Open contracts:** access-denied versus missing keys/values; registry view
selection after removal of the OVAL view property; binary/multi-string encoding
and cardinality; timestamp units and range. Frozen metadata names hierarchy
traversal, but the closed native registry Object overlay rejects `traversal`.
The schema probe preserves that rejection. Document the discrepancy for 0.4;
review any future traversal syntax separately. Do not add a parameter in prose.

**Required runtime evidence:** named/default/key/hive collection; case variants;
missing and inaccessible parents; each value type including empty/multiple
strings; expansion failures; view differences; timestamp boundary fixtures.
Owner review must select encoding/cardinality and status contracts before
scanner conformance vectors can be authoritative.

## unix.file

**Correction:** Object selectors are `filepath`, `path`, `filename`. Collected
fields are `full_path`, `directory`, `name`. The pilot previously called the
collected names native selectors. The resolved selector contract documents
null `filename` as the directory-object form. Use native `matches_regex` rather
than the migration label `pattern_match`.

**Documented native facts:** mapping alternatives are `filepath` or
`path` + `filename`; filesystem scope has `all`, `local`, `same`; file traversal
has explicit `max_depth` (nonnegative integer or `"unlimited"`) and `recurse`
(`directories`, `symlinks`, `symlinks_and_directories`). An editor default is not
a scanner fallback. Mapping alternatives and semantic checks are distinct from
JSON Schema required properties. The no-traversal semantic rule still uses
`full_path`; record its naming mismatch rather than rewriting the frozen rule.

**Legacy research candidates:** `file_object`/`FileBehaviors` describe directory
selection, symbolic links, starting-directory inclusion, recursion restrictions
and filesystem boundaries. OVAL uses `-1` for unlimited depth, `defined` for a
filesystem boundary, and an omitted filesystem behavior of `all`. These are
source forms; do not import them as native tokens or omitted-value behavior.
`file_state`/`file_item` specify epoch seconds, byte size, numeric ownership,
permission bits and unsupported-versus-absent ACL handling. Native datatype
names alone do not approve those units or failure mappings.

**Open contracts:** symlink following versus link evidence, mount classification
and changes during collection, time units/resolution, ACL status, transient
removal and permission failures. Recommend preserving authored selector names
and correcting the result/selector crosswalk in a future reviewed metadata
revision. Adding result-name aliases would create unnecessary compatibility
questions; do not do so in 0.4.

**Required runtime evidence:** file and directory forms; missing, denied and
removed objects; symlink cycles; depth zero/unlimited; local/remote/bind mounts;
UID/GID and permission extremes; timestamp and ACL availability fixtures.

## independent.shellcommand

**Documented native facts:** shell and command are explicit; both error flags
are required by the mapping. `pattern` retains matching stdout lines and exposes
captures separately. Collected `stdout_line` is string; comparison overrides
permit other explicit datatypes. Keep original string evidence. Trust policy
is enforced outside command text; shellcommand must not discard meaningful
structured native collection semantics.

**Legacy research candidates:** `shellcommand_test` favors bounded one-line
commands from trusted sources. `shellcommand_object` and `shellcommand_item`
describe one item per execution, echoed command identity, stdout filtering,
captures and stderr lines. `ShellCommandBehaviors` provides false defaults for
the two error flags; native metadata instead requires explicit booleans.
Do not adopt the source prose's default shell. Shell enums do not guarantee
that an interpreter is installed or suitable on a target.

**Observed validation gap:** the generic Object baseline accepts an omitted
error flag, a string in place of a boolean, an unknown shell and an omitted
command. Regression probes preserve these existing outcomes. Mapping
requirements above are not claims of schema rejection. Fixing that gap requires
a separately approved validation-contract change; this PR only documents it.

**Conflicting source prose:** for no stdout, the object describes an item
containing an absent stdout entity, while the item description says an item
with a `does not exist` status. The item also loosely equates item status with
process exit status. These cannot serve as an unambiguous native status contract.
Source regex/capture wording also needs comparison with the native regex
contract, rather than wholesale inheritance.

**Open contracts:** empty output and unmatched output, item versus field status,
multiple captures and ordering, newline/encoding rules, malformed typed
comparisons, missing interpreter, launch/permission failure, timeout,
cancellation, output truncation, working directory/environment and privileges.
Recommend a native decision table preserving process status and raw output
independently of collection success; exact mappings require owner review.

**Required runtime evidence:** exit zero/nonzero with each flag combination;
stdout/stderr absent, empty, multiline and unterminated; matching/nonmatching
patterns and multiple captures; encoding failures; unavailable interpreter;
permission failure; cancellation and limits. Neither compilation nor schema
validation supplies this proof.
