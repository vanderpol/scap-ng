# Approved exact selector alternatives: all-100 contract review

Owner approval: 2026-10-27, continuation of
[#251](https://github.com/vanderpol/scap-ng/issues/251). Base implementation:
`615cd6e49`. The [original counterexample and decision](v04-process-selector-schema-conflict.md)
explain why a two-selector process Object matched three `oneOf` branches.

`flat_object` now prohibits selectors absent from each declared direct
alternative. It retains `oneOf`, required acquisition parameters and the existing
Set/direct/for_each exclusions. An alternative containing every selector keeps
its old serialized Set prohibition, avoiding irrelevant parity changes.

All 100 full generated dictionaries were captured before correction and verified
against the existing parity lock. Each regenerated dictionary was then compared
recursively with an independently constructed expected change: only direct
Object variant `not` clauses may prohibit additional selectors. Any other
difference aborts review. **Ten expected changes, 90 byte-identical contracts,
zero unexpected differences; every existing Set branch is unchanged.**
The [machine audit](v04-exact-selector-contracts.json) records before/after hashes
and each variant's required/newly prohibited selector fields for all 100 entries.
Only the ten explained parity hashes changed.

| Contract | Individually reviewed direct alternatives; each prohibits the other selectors |
| --- | --- |
| `file.hash` | full_path; directory + name |
| `independent.textfilecontent54` | full_path + pattern + instance; directory + name + pattern + instance |
| `independent.xmlfilecontent` | full_path + xpath; directory + name + xpath |
| `independent.yamlfilecontent` | full_path + yamlpath; directory + name + yamlpath; content + yamlpath |
| `linux.selinuxsecuritycontext` | full_path; directory + name; pid |
| `macos.plist511` | app_id + xpath; filepath + xpath; no macOS converter admission added |
| `unix.file` | full_path; directory + name |
| `unix.process58` | command_line; pid; command_line + pid; combined pair now matches exactly one branch |
| `windows.file` | full_path; directory + name |
| `windows.fileeffectiverights53` | full_path + trustee_sid; directory + name + trustee_sid |

Normative SCAP-NG schemas, original OVAL files, capability mappings, compiler
semantics and scanner behavior are unchanged. Generated contracts remain derived
validation output. No source selector is dropped or approximated.

All eight original process Tests pass original XSD/Schematron, current authoring
validation, native compilation, exact compiled operands and independent source
terms. Ordinary activation and frozen identity data reuse the existing visitor;
there is no new capability-specific conversion algorithm. Negative tests retain
the old overlapping-contract failure, extra/mixed selectors, Set/direct mixtures,
for_each conflicts and explicit incompatible datatype. File/Set/projection and
Variable regressions are included in **21 passing focused tests**.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python -m unittest \
  test_v04_process_selector_conflict test_v04_native_schema_generation \
  test_v04_direct_file_traversal test_v04_direct_variables -v
```

Mandatory regressions pass **3,155 tests, zero failures/errors, one existing
skip**. Three subsequently added snapshot-retention guards pass separately;
selection reconciliation accounts for all **3,158 current test identities** with
none lost. The 803-Test audit reports 629 configured attempts / 339 compiled /
318 independently proved. The six-source gate proves and compiles **1,001 primary
closures** (269 RHEL, 264 Oracle, 219 Windows 11, 249 Server), independently consumes
all four packages and retains every original 816 program hash. The proof floor
now protects all 1,001. Applicability and 395 primary gaps remain explicit.
The [verification receipt](v04-recovery-resumption.json) records exact evidence.

The prior UNIX-password CI failure was an exact directory comparison rejecting
four newly proved mixed file/password closures. All six old original snapshots
remain byte-identical. Its guard now requires each old file unchanged, allows
additional proved files, rejects an empty baseline and refuses fixture overwrite.
The complete local source run passes **six retained / four additional**; no
source fixture was rewritten or test weakened to accept changed old evidence.

The earlier pre-correction full run completed 3,154 tests with one unchanged skip
and one parity-lock failure after the baseline changed while that process retained
the old generator; it is not claimed as passing final-tree verification. Fresh
results, implementation SHA and hosted CI belong in the engineering ledger.
No scanner-runtime equivalence or release readiness follows from these checks.
