# Ordinary scalar proof expansion after recovery

Base: `609da701fef2596409e3f6bfef18c9103b02eef4`. Continuation of
[#251](https://github.com/vanderpol/scap-ng/issues/251), following the
[read-only recovery assessment](v04-recovery-2026-10-27.md).

Ten capabilities are activated using the existing visitor and scalar proof
reader: `linux.inetlisteningservers`, `linux.selinuxboolean`, `linux.sestatus`,
`linux.systemdunitdependency`, `unix.interface`, `unix.shadow`, `unix.symlink`,
`unix.uname`, `windows.group_sid`, `windows.user_sid55`. No conversion or proof
algorithm changed. Independently frozen identities include the reviewed
`unix.symlink` filepath-to-full_path rename and system-source Object removal.
Original XSD field declarations, mapping hashes and XML operands are separate
checks; a live mapping cannot redefine its own proof.

| Gate | Local evidence |
| --- | --- |
| Human maintainability | PASS: activation/proof data only; no runtime module or capability dispatch growth |
| Pinned original files | 10 unchanged upstream files, 46 Tests; paths/hashes in fixture provenance |
| Original XSD/Schematron | All ten files VALID; historical metadata-note deprecation reports are retained, not assertion failures |
| Focused expansion tests | 6 passed, zero failures/errors/skips; includes all 46 original Test conversions |
| Related suites | 23 passed before adding the sixth expansion test; zero failures/errors/skips |
| Complete pinned corpus | 154 files, 145 OVAL documents, 803 Tests; inventory unchanged |
| Configured conversion corpus | 274 attempts, 227 compiled, 210 independently proved |
| Diagnostic mapping corpus | 298 compiled, 210 independently proved; unproved outputs are not admissions |
| Six-original proof/program floor | Required running gate; results recorded separately after completion |
| Mandatory/hosted CI | Pending implementation checkpoint verification |

Compared with the recovered configured baseline, 54 additional original Tests
compile and prove. The focused ten-file set covers 46; eight further UNIX
interface Tests are in the upstream macOS/Solaris directories. Their capability
is UNIX, not a new macOS collector. This is an OVAL term comparison, not execution
on those platforms. The isolated 53-Test probe from the old session was not used
as acceptance evidence.

Regressions independently reject unknown/foreign source fields, changed Item
quantifiers, invented system-source selectors and changed proof mapping hashes.
Tests compare native/source acquisition terms and verify exact compiled Test
operands. They do not calculate scanner outcomes. No schema, original source,
production converter/compiler, normalization scope or release state changed.

Reproduce from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python -m unittest \
  test_v04_direct_scalar_expansion test_v04_direct_scalar_batch test_v04_oval_test_corpus -v
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/audit_v04_oval_test_corpus.py \
  --source-root ORIGINAL_SELF_ASSERTION/SCAP_1.4/OVAL_Test_Content \
  --output /tmp/scalar-expansion-corpus.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=tools python tools/verify_v04_direct_scope.py \
  --inputs ORIGINAL_SIX_ZIPS --output /tmp/scalar-expansion-six
```

`ORIGINAL_SELF_ASSERTION` is pinned to `e3538595c5083b9c34d937a81d319234df9bbfaa`;
the corpus CLI verifies every file hash. `ORIGINAL_SIX_ZIPS` uses
`tests/fixtures/v04-direct-six-sources.json`. Choose new output paths. Do not
overwrite evidence or replace original Apache/DNS bindings. The six-source
workflow runs the expansion tests and retains the complete generated evidence.

Next: shared Variable sources and merge/unique, then shared traversal and scalar
behavior routing. The converter assignment remains incomplete. No release,
scanner parity, complete applicability or production replacement is claimed.
