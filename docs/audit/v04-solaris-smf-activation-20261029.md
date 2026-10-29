# Solaris SMF activation — existing 0.4 contract

Under [#251](https://github.com/vanderpol/scap-ng/issues/251), fourteen original
Solaris 11 Rules (seven SPARC, seven x86) are blocked by activation rather than
an undecided assessment contract. Their existing `solaris.smf` mapping already
defines the `fmri` selector and seven string fields. The generic converter,
compiler and independent scalar readers already implement those operations.

## Concrete source and change

SPARC `SV-216342r959010` and x86 `SV-216107r959010` reference original Test
`oval:mil.disa.stig.solaris11:tst:5400`. It selects the exact FMRI
`svc://localhost/network/ftp:default`, has no State, and requires `none_exist`.
Native output preserves `solaris.smf`, that exact FMRI and `items_found: none`.
The related terminal-service Tests retain State `service_state equals DISABLED`;
graphical-login predicates retain `ONLINE`. Extended Definitions, Variables,
shared Objects and other capabilities remain in their original closures.

This change activates only the existing SMF mapping, adds its frozen identity
crosswalk to the independent reader, and admits only `solaris.smf` through the
converter's platform guard. Other Solaris capabilities remain outside that guard.
No schema, mapping, compiler, population, acquisition or scanner meaning changes.
The source spelling `server_arguements` remains unchanged.

Rejected alternatives: treating an SMF service as a generic process changes
acquisition; removing referenced service preconditions changes the Definition;
admitting every Solaris capability would exceed the demonstrated increment.
No `all_exist`, function, import/export or unsupported acquisition contract is
resolved by enabling this identity mapping.

## Verification

- **37 focused/affected tests pass**, including seven new original-backed
  regressions. Two compact closures preserve all original node identities and
  pass original XSD, Schematron, reference and deprecation checks. Tests cover
  absence, independent item-count/match axes, exact original fields/spellings,
  scope restrictions and Filter preservation. Schema-valid selector, State,
  count and Filter mutants fail independent source/native and compiled-operand
  comparisons. Unknown fields/namespaces/attributes and nil selectors reject.
- Fresh selected acceptance on the actual production code proves all **14**
  Rules; their Rule/dependency hashes match the immutable DRAFT ledger. This
  includes native schemas, independent terms, compilation and package consumers.
  These are new programs: the DRAFT previously blocked them, so no previously
  compiled hash is invented for them.
- All **3,130** previously added cohort authoring/proof/source/native-term hashes
  retain parity. All **523** preceding conformance four-hash records are retained.
  Three original SMF conformance Tests additionally prove: **526/716 configured
  Tests**, out of 803 originals. Production Rules and conformance Tests remain
  separate denominators.
- Own exact-commit hosted maintained/six-source integration follows publication.
  The preceding 3,292-test green run is not claimed to verify this activation.
  Do not supersede the active gate, dispatch a duplicate maintained suite, or
  regenerate the frozen all-65 archive.

[Source-pinned fixtures](../../tests/fixtures/v04-solaris-smf/provenance.json) ·
[Machine-readable receipt and fourteen Rule records](v04-solaris-smf-activation-20261029.json) ·
[Release-readiness reconciliation](v04-release-readiness-20261029.md).

Local recovery: `/workspace/coverage-next-20261029/`; `smf-final/`,
`smf-proof-hashes.json`, `smf-retention.json`, `smf-conformance.json` and
`smf-affected.log`. This is static primary-source proof, not runtime parity,
complete policy/CPE/manual conversion, or final toolchain-release acceptance.
