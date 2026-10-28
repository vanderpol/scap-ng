# Shellcommand regex recovery checkpoint

Issue: [#251](https://github.com/vanderpol/scap-ng/issues/251).
Base: `4f1400471d54a2b1b2fa8e2fd6f7233a03118f8f`.
[Machine-readable receipt](v04-shellcommand-regex-recovery-20261028.json).

The failed session's 4,301-file DRAFT was already published. Recovery fetched
its immutable tag, verified all ZIP CRCs, 12,276,247 bytes and SHA-256
`07f7b24f4d0522630159fbddf9f6d643ffcac3d49d3c482dc7fb263de9793317`,
and reconciled the ledger digest, all primary messages and capability counts
against the [341-blocker analysis](v04-six-draft-blockers-20261028.md).
No archive was regenerated or duplicated. The previous uncommitted batch and
its recorded stash object are absent from this recovered workspace.

## Bounded implementation

The shellcommand Object's `pattern` is already an intrinsic regex acquisition
input in the committed mapping and original OVAL contract. The converter
previously rejected explicit `operation="pattern match"` through a generic
equality-only invocation-input guard. It now consults the existing mapping for
this field only and preserves the regex bytes as the same native input. Shell,
command and unrelated parameters retain their previous operation guards.
No predicate is invented over acquired Items, and no command is executed.

Datatype, unexpected-attribute, multivalue, complement and dynamic quantifier
guards remain enforced. Tests cover equivalent implicit/explicit regex forms,
unchanged compiled operands, independently read source terms, unsupported
command/shell operations and removal of mapping authorization. Schemas,
mappings, compiler, independent semantic readers and workflows are unchanged.
Invalid original banner closures remain rejected; their raw compilation does
not admit them into accepted packages.

## Verification

44 focused/affected tests passed, zero failures/errors/skips, using:

```sh
PYTHONPATH=tools python -m unittest test_v04_acquisition_source_proof \
  test_v04_direct_shared_controls test_v04_direct_scalar_behaviors \
  test_v04_six_source_requirements test_v04_direct_scalar_batch \
  test_v04_direct_scalar_expansion test_v04_direct_scope \
  test_v04_converter_contracts -v
PYTHONPATH=tools python tools/verify_v04_direct_scope.py \
  --inputs ORIGINAL_SIX_ZIP_DIRECTORY --output NEW_EVIDENCE_DIRECTORY
```

The maintained six-source gate verifies ZIP hashes from the unchanged source
lock, original XSD/Schematron and nondeprecation, native schemas, independent
typed terms, compiled operands, package integrity/consumer and every previous
proof-floor program hash. Results:

| Benchmark | Proved primary Rules | Newly proved | Blocked automated |
| --- | ---: | ---: | ---: |
| RHEL 9 | 304 | 12 | 114 |
| Oracle Linux 9 | 291 | 5 | 117 |
| Windows 11 | 228 | 0 | 18 |
| Server 2025 | 249 | 0 | 12 |
| Windows DNS | 0 | 0 | 41 |
| Apache UNIX | 0 | 0 | 22 |
| Total | 1,072 | 17 | 324 |

All 1,055 previous program hashes match; all 17 primary acquisition-blocked
Rules from the published ledger now prove. The receipt identifies each new
original Rule, Assessment and program hash. There are still 171 manual/OCIL
Rules: 1,072 + 324 + 171 = 1,567. Applicability, complete policy conversion and
scanner-runtime equivalence remain separate obligations. This local gate is
not yet an exact-commit hosted maintained-suite verification or release.

The remaining major dependencies retain their existing dispositions under
[#255](https://github.com/vanderpol/scap-ng/issues/255): production `all_exist`,
canonical function integration and the comparator-bearing absence boundary.
Catalog defects and invalid original closures require source remediation,
not relaxed validation or guessed bindings. The original DRAFT is immutable.

Documentation checks: four current-entry-point tests pass; all 13 sampled
entry points pass. Strict link audit reports three pre-existing Board-discussion
anchor references, identical to the untouched base; no new broken current links.
Published discussion text was preserved.
