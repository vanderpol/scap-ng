# Native capability identity migration (#255/#268)

Decision 5 removes eleven OVAL revision suffixes from native authoring. The
[complete old/new/source identity ledger](v04-native-identity-migration-20261031.json)
records exact source QNames and mapping hashes. The supported catalog remains
100 distinct contracts; the direct activation registry and result extensions
use the new names. Current compiler entry points reject old native aliases.
Original source Test/Object/State names, identifiers, XML and source archives
retain their suffixes and original bytes.

## Collision and preservation

Blind digit stripping would merge `solaris.package511` into the existing
`solaris.package`. Original Solaris XSD lines 452 and 577 distinguish SVR4
pkginfo from Image Packaging System metadata. The revised native identity is
`solaris.package.ips`; existing SVR4 `solaris.package` remains distinct. No
selector, datatype, collection or matching semantics were merged.

Each of the eleven original mapping files is preserved byte-for-byte under
`tests/fixtures/v04-owner-original-mappings-20261031/`. New mapping JSON must
equal the approved native-name projection of that original; generated schemas
must satisfy the same identity-only projection. Scalar proof admission still
checks the original frozen mapping SHA, then checks that the current map differs
only by the approved names. A deliberate selector-map mutation is rejected.
The frozen scalar-proof and generator fingerprint files are untouched; new
native content needs fresh proof and new compiled hashes. No existing proof
floor or library has been rebaselined.

The independent archival witness reader maps only capability identity values.
Expected comparison text containing an old capability name remains literal.
This explicit decoder is not an authoring/compiler alias. The independent
file-rights reader now uses an explicit original QName, rather than deriving
it from the native capability name (which selected a different old source
family after the rename).

## Bounded observations

37 tests PASS (20.114s): all eleven generated contract identity comparisons,
old-alias rejection including the direct compiler, preservation/mutant checks,
real text-file and Windows rights conversions, source-pinned traversal, original
process selector cases, producer contracts and the mechanical audit. An
additional 23 focused compiler/conditional/producer tests PASS (0.957s).
A further 33 original-source integration tests PASS (11.083s), covering
Windows cmdlet/remaining primitives and scalar batches/behaviors, including
46 scalar source Tests. Frozen fixture capability labels are projected explicitly
in test expectations; their files/hashes remain unchanged.

Original Windows rights source comparisons retain typed fields and SID
acquisition behavior. No live scanner execution or all_exist/error-oracle
change is claimed.

Local Rule/Assessment names retain a readable source control discriminator
when available, preventing truncation from merging different long STIG titles.
These local names are not promoted global/shared Assessment names; Decision
11/12 promotion remains a separate, proof-backed reuse gate. Residual collisions
still fail closed with no silent overwrite.

Generator baseline parity remains a separately tracked migration gate: the
historic fingerprints use old identities (and the input PR already had one
other mismatch). This checkpoint preserves them and does not turn a changed
hash into proof. Current gallery/default catalog and broader compiler identity
migration remain in progress on the draft PR.
