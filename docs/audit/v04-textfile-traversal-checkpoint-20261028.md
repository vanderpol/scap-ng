# Textfilecontent54 traversal: implementation of the existing contract

Tracking [#251](https://github.com/vanderpol/scap-ng/issues/251); schema-owner
integration blockers remain in [#255](https://github.com/vanderpol/scap-ng/issues/255).

## Problem, authority and change

The owner-authorized converter continuation on 2026-10-28 treats the committed
0.4 mappings as authoritative. The approved `independent.textfilecontent54`
mapping already declares `file_traversal` and its original behavior crosswalk;
this change implements that existing contract, with no new language decision.
The previous regex-behavior handler rejected inherited file traversal attributes,
blocking source-valid RHEL/Oracle Rules before acquisition could be represented.

The converter now validates and splits regex/Item-creation attributes from the
inherited FileBehaviors, then reuses the existing shared traversal translator.
The independent source reader separately reads original defaults and path rules;
its native reader checks the authored traversal, flags and their types. Neither
proof reader imports the renderer. Source nodes and provenance stay unchanged.

For example, pinned Oracle Rule `SV-271476r1091140_rule` reaches original Object
`oval:mil.disa.stig.ind:obj:25808701`:

```xml
<!-- Original acquisition excerpt; other selectors remain unchanged. -->
<behaviors ignore_case="true" recurse_direction="down"/>
<path>/etc/sudoers.d</path>
```

Previously conversion reported an unsupported `recurse_direction` attribute.
The native Object now contains this excerpt alongside the original name,
pattern and instance predicates:

```yaml
directory: {equals: /etc/sudoers.d}
ignore_case: true
multiline: true
singleline: false
item_creation: all_object_elements_fullfilled
filesystem: all
traversal: {max_depth: unlimited, recurse: symlinks_and_directories}
```

This is downward acquisition with original unbounded depth and original default
symlink/directory selection. Original direction none produces no traversal.
Dropping attributes, guessing paths, converting traversal into selector
predicates or introducing another traversal grammar were rejected alternatives.
Upward/deprecated traversal and unsupported view controls remain rejected.

## Source restrictions and compatibility

OVAL 5.12.3 `independent-definitions-schema.xsd` defines the inherited
`FileBehaviors` and `Textfilecontent54Behaviors` defaults. Its embedded
`ind-def_txt54objfilepath`, `ind-def_txt54objfilepath2` and
`ind-def_txt54objpath` rules prohibit filepath depth/direction, non-equality
path recursion controls, and defined-filesystem scope on non-equality selectors.
Those boundaries are enforced, not normalized away.

An old constructed filesystem-scope test used case-insensitive equality with
`defined`, which original Schematron forbids. Its positive derivative now uses
strict equality; new negatives execute the original scoped XPath assertions for
both pattern-match and case-insensitive-equality violations. A one-time full
original XSD/Schematron run also passed the corrected controlled derivatives.
The maintained test uses exact scoped assertions to avoid repeatedly validating
a large unchanged datastream. This correction changes no original source or
previously admitted original program; no validator or CI gate is weakened.

## Evidence and regression

[Individual Rule additions](v04-textfile-traversal-proofs-20261028.json) record
all 43 source Rule IDs/hashes, source Tests/Objects and behavior attributes,
previous diagnostics, new program hashes, pinned original archives and the
schema/mapping hashes. Each addition passes original closure validation, native
authoring/graph checks, independent source/native typed-term comparison,
compilation and compiled-package verification. The primary proof floor adds
these entries while retaining every existing entry unchanged.

- All six primary-source gates pass: **1,055/1,396** OVAL Rules proved/compiled,
  **+43**. RHEL is **292** (+22), Oracle **286** (+21), Windows 11 **228**, Server
  2025 **249**; existing DNS/Apache blockers are retained.
- All previous **1,012** primary program hashes and proof identities remain.
- **521/713** configured Self-Assertion Tests compile and term-prove;
  **519/803** additionally source-valid/nondeprecated. All 521 prior source/
  native terms and program hashes remain unchanged; zero mismatches.
- The combined text/file/expanded-proof/YAML/RPM regression invocation passes
  **55 tests**, zero failures/errors/skips. Targeted invalid-shape/type and
  source-scope checks pass after their final additions.
- All **100** capability contracts retain their reviewed parity hashes, with
  141 selectors and 694 State entries; no parity baseline is changed.
- [Original source Object regressions](../../tests/fixtures/v04-direct-textfile-traversal/README.md)
  preserve the complete original XML and its unrelated diagnostics. Two valid
  Object closures prove acquisition; their original `all_exist` Tests remain
  explicitly unsupported. Constructed compiler wrappers are not counted as
  original Test/Rule conversion or as successful `all_exist` modernization.

Capability activation stays **49/51** approved-platform mappings (**49/100**
globally). Additional public cohorts remain YAML **45/51**, RPM **1/1**.
The change does not implement a scanner, execute file acquisition, establish
runtime collection/error/incomplete equivalence, change function production
syntax, migrate repositories or declare a release.

## Mandatory gate dependency

The preceding exact-head maintained run at `b272f3629` ran **3,246 tests**, with
**one failure, zero errors, one skip**. The sole failure is the schema owner's
isolated `variable-function-expression.schema.json` missing required version/
date annotations. The required two-field correction is recorded in
[#255](https://github.com/vanderpol/scap-ng/issues/255#issuecomment-6472547036).
Converter code does not edit the protected schema or suppress the check.
This packet does not declare the overall integration all-green while that
schema-owned defect remains. Exact published-head CI is tracked in #251.
