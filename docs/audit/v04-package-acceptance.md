# 0.4.0 independent package acceptance — #251, 2026-10-25

Reviewed source checkpoint: `4e1ec2737c7b43002282a1d6762896b25b162060`.
Started from clean synchronized `main`; [#251 coordination](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6391177767)
distinguishes archive migration, original-source conversion, publisher trust and
scanner execution. This audit preserves that distinction. No schema, conversion
semantics, RHEL admission, Oracle exception, editor or scanner changed. No tag or
release asset was created. Production signing/trust and scanner acceptance remain
separate gates.

## Independent six-package acceptance

The reviewed generated bundles were unavailable in this workspace. Reconstructed
them once using the **unchanged reviewed archive adapter and paired compiler**,
not a fresh original-source six-STIG rebaseline. Inputs were the immutable
`v0.4.0-six-stig-canonical-flat-authoring-20261022-restored` assets:

- JSON `f481ff109b1f6abfda2d7f115e3140f4e82429517e4adc8cf9de00733180d8f5`;
- YAML `d7a989c66f32c8ea7af4c6e3355847da2d39d23b82366ce3f323cd71d4a6c5c1`.

Original six NIWC ZIPs were retrieved at immutable source revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5`; every original ZIP/XML SHA and source
member is preserved in the [source ledger](v04-package-acceptance/source-ledger.json).
The Windows 11 ZIP also matches previously recorded Git blob
`712cc3176b1e44616aaf2f3ba5e62b299ad0643c`. Original files remain unchanged in the
external evidence inputs; no bulk source payload is committed or deleted.

All **six reconstructed bundle SHA-256 values exactly match the reviewed
checkpoint**, including its independent second-compilation evidence. Exact full
hashes and all rejection diagnostics are in [consumer results](v04-package-acceptance/consumer-results.json).

| Bundle | Documents | Programs | Test references |
| --- | ---: | ---: | ---: |
| Apache 2.4 UNIX | 665 | 561 | 852 |
| Windows 11 | 1151 | 631 | 949 |
| Windows Server 2025 | 1236 | 648 | 970 |
| Windows DNS | 724 | 559 | 848 |
| Oracle Linux 9 | 1488 | 579 | 852 |
| RHEL 9 | 1498 | 595 | 894 |
| Total | 6762 | **3573** | **5365** |

Package totals include the full shared library in each package; they are not
unique source/Assessment coverage counts. The global authoring has 4,012 documents,
2,433 Assessments (883 automated, 1,550 manual), 1,567 Rules and 1,390 Tests.

`verify_v04_package_consumer.py` runs in a separate process and imports **no compiler,
compiler verifier, graph index or result-plan builder**. It independently checks
ZIP paths/CRC/member inventory; canonical JSON and hashes/sizes; manifest/schema
versions; Benchmark/Rule/Assessment/catalog and local Test/Object/Variable/foreach
references; Object/Variable cycles; whole source documents; exact Test operands;
and its own postorder reconstruction of result-program instructions/requirements.
Both independently parsed external YAML and JSON authoring graphs must equal
the packaged graph. Paired compilation proves native byte equality; the consumer
independently checks source/program equality and the previously recorded native
byte hashes, without calling the compiler to reconstruct expected instructions.

**24 real-package corruptions rejected:** for each of six bundles, stale member
hash, unsupported package version, unresolved Rule/Assessment reference after
rehashing, and altered compiled requirement after rehashing. Eight focused
consumer tests additionally cover CRC damage, unsafe/unlisted members, unsupported
Assessment versions, result-program forgery, unresolved Object/catalog/policy
references and a consistently altered package that only external source comparison
can distinguish. Hash agreement is not publisher authentication.

## Original-source ledger and denominators

The [complete original declaration CSV](v04-package-acceptance/source-ledger-original-records.csv)
contains **2,695 Definitions and 2,140 Tests**, scoped by source benchmark, XML
member and OVAL component. Denominators include all original declarations,
including inventory/CPE and unreferenced declarations; cross-benchmark shared
IDs are not silently collapsed. Original XCCDF Rule count is **1,567**. Types,
versions, hashes, quantifiers, State/Object/Definition references and unverified
dispositions are retained, with additional Set/Filter/Variable construct counts.

| Original source | Definitions | Tests | Standalone root proofs | Covered Tests |
| --- | ---: | ---: | ---: | ---: |
| RHEL 9 | 846 | 673 | 2 | 26 |
| Oracle Linux 9 | 827 | 621 | 0 | 0 |
| Windows 11 | 474 | 353 | 1 | 1 |
| Windows Server 2025 | 501 | 372 | 1 | 5 |
| Windows DNS | 24 | 64 | 1 | 5 |
| Apache 2.4 UNIX | 23 | 57 | 0 | 0 |

Only five previously proved fixtures were converted for this ledger. Each fixture
was matched to its original published SCAP semantic root before the maintained
converter admitted it. Bounded standalone evidence is **5/2695 roots (0.185529%)**
and **37/2140 Tests (1.728972%)**, including one root/16 Tests requiring the approved
RHEL normalization. Those conditional results are not unrestricted OVAL equivalence
or complete feature coverage. The other source records remain **unverified**, not
automatically classified unsupported merely because no broad conversion was run.

All 2,433 packaged-source Assessments retain their **historical review-archive
migration** classification in the [Assessment inventory](v04-package-acceptance/source-ledger-migrated-assessments.csv).
The five standalone proofs are not tied to proof of those exact migrated
Assessment graphs: **0/883 automated packaged Assessments have independently
established original-OVAL graph equivalence in this audit**. Schema validity,
native compilation and the consumer pass must not inflate that numerator.

Normalizations remain explicit and separate:

- RHEL SV-258179: exact pinned source SHA `463b539c469c3302aa52c23fdca35814f40fd5fd7de31346964e1b4a97b5d8a9`,
  16 Test-level all_exist cases, original identities/versions retained. No admission
  expansion; original mixed nonexistent-Item OVAL counterexample and error/unknown
  guards remain. The 207 **review-token diagnostics** in the migration report do
  not establish 207 source-attested conversions or authorize new source admission.
- Oracle SV-271844: source ZIP SHA `6733abd693380b43b2350c2692775e4ff902f895f16899db97b34fecf7fba74d`,
  Test `oval:navy.navwar.niwcatlantic.scc.rhel8:tst:27184401`, exact original
  Object/State attributes and `stderr_line none_exist` plus `.*` retained in
  provenance. The approved operand removal is a review-archive exception, not
  fresh original-source conversion or unrestricted equivalence.

## Clean environment and validator finding

Built a source toolchain snapshot at the exact reviewed SHA and extracted it
outside the checkout with no `.git`. A fresh Python 3.12.14 venv used only the
eleven hash-pinned wheels in [dependency inventory](v04-package-acceptance/dependency-wheels.json)
and [Linux/Python 3.12 lock](v04-package-acceptance/requirements-linux-py312.lock).
No inherited PYTHONPATH/user-site modules are used. Original family XML is an
explicit checksum-pinned input; mature 0.3 mapping resources must remain in the
toolchain because the approved converter reuses that infrastructure.

The baseline public converter, compiler and existing verifier API worked from
outside the checkout. The public validator **failed** on valid 0.4 content:
`referencing.exceptions.PointerToNowhere: '/$defs/field_predicate_body'` resolved
against the wrong Assessment resource. The legacy `RefResolver` mixed with Draft
2020-12 unevaluatedProperties caused the scope error. The scoped fix uses a local
resource Registry for **0.4 only**, with positive and fail-closed absence/comparator
regressions; schemas and archived-version resolver behavior are unchanged.

Other reproducibility limits: the older miniature smoke wrapper names an absent
unused applicability catalog; it is not independent closure evidence. The clean
acceptance wrapper explicitly includes that catalog. The public directory
validator classifies by filenames, so the harness uses `benchmark.yaml` and checks
**four checked/four valid/zero unclassified**, avoiding a zero-document success.
Existing compiler/API verification is not substituted for the independent consumer.
Source snapshot/specification prose still requires release-version reconciliation;
an executable source snapshot is not a finalized interoperable specification.

Candidate snapshot `90a1a90c9ef1a71f576cdee1916a6ed5e2f39013` passed **all 11
steps**, including execution of the extracted snapshot's converter, validator,
paired compiler, verifier API and independent consumer. The exact commands,
working directory, Python/dependency versions and return codes are committed in
[clean-environment evidence](v04-package-acceptance/clean-environment.json).
The two independently built toolchain archives were byte-identical:
`24c9b87558085b8bc8988ff39d938f148c45e018cd9b09120828f2ecdf9b9d90`
(6,270 verified files). The family source SHA-256 is
`6966982d66e004f77ceb9e5ccceb5161275a79729d4178f290f99efd3b8b84a7`;
paired compiled bundle SHA-256 is
`9d600e4753f85723109f4f43291c8bc81b9869e548107a2753a4aac81276cf80`.
This is reproducibility at the recorded Git ref and Linux/Python wheel profile,
not a cross-platform reproducibility claim. The original harness accidentally
resolved the venv Python symlink to base Python; preserving the executable path
fixed that harness failure. No final-release tag/assets or production signing
identity were created.

## Commands and validation

Use the documented existing migration CLI with the two source hashes above and
the exact original Oracle ZIP; its output is artifact reconstruction only. Then:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=.:tools:tools/scap_upconvert_v003:tools/scap_ng_roundtrip_v003
python tools/v04_native_bundle_compiler.py --json-archive current.json.zip \
  --yaml-archive current.yaml.zip --output-dir compiled --report compiler.json
python tools/audit_v04_package_acceptance.py --bundles-dir compiled \
  --source-json current.json.zip --source-yaml current.yaml.zip --report consumer.json
python tools/audit_v04_original_source_ledger.py --inputs-dir pinned-original-six \
  --authoring-json current.json.zip --migration-report migration.json --report ledger.json
python -m venv /tmp/v04-acceptance-venv
/tmp/v04-acceptance-venv/bin/python -m pip download --dest wheelhouse \
  -r docs/audit/v04-package-acceptance/requirements-linux-py312.lock --require-hashes
/tmp/v04-acceptance-venv/bin/python -m pip install --no-index --find-links wheelhouse \
  --require-hashes -r docs/audit/v04-package-acceptance/requirements-linux-py312.lock
python tools/audit_v04_clean_environment.py --repo . --ref AUDIT_COMMIT_SHA \
  --python /tmp/v04-acceptance-venv/bin/python --source /path/to/ind-def_family_test.xml \
  --evidence-dir /tmp/unique-clean-acceptance
python tools/run_current_tool_regressions.py --report /tmp/mandatory.json
```

Supply the pinned source bindings from rebaseline CI for mandatory execution.
Local full mandatory: **2,923 tests, zero failures/errors, one unchanged optional
research-corpus skip**, repeated at candidate `90a1a90c9` in **133.558 s**. Exact reviewed-snapshot selection: 2,911 methods; candidate:
2,923; **zero removed, twelve added**. Focused package/compiler/toolchain/bridge
tests: **34 passed**; final consumer/validator/ledger subset: **12 passed**.
Repository layout audit passed (34,242 baseline paths preserved). Markdown
sample regressions: **4 passed**. The navigation audit still reports the same
three pre-existing Board links to a removed heading; no new broken link was
introduced. Historical research failures remain in their previously approved
visible non-release partition; they were not removed, skipped or revived here.

Remaining true release blockers: original-source/package semantic coverage,
unverified constructs, intended whole-package coverage acceptance, release-grade
dependency/platform/document correspondence, production signing/trust and actual
scanner/collector acceptance. No source or package pass in this report establishes
those separate gates. Issue writes remain blocked by
`Post "https://api.github.com/graphql": Forbidden`; the committed report is the
handoff without repeated permission attempts.


## Published commits and hosted checks

Normal, non-forced pushes to `main`:

- [c5be32236ef25c9c0215815c11b70e5043967137](https://github.com/vanderpol/scap-ng/commit/c5be32236ef25c9c0215815c11b70e5043967137): independent consumer,
  adversarial tests, ledger/audits, 0.4-only public-validator fix and fast-CI test
  registration. Production converter/compiler and approved schemas unchanged.
- [1567ba4ccba59f3bd1bd510996e976078091c1cc](https://github.com/vanderpol/scap-ng/commit/1567ba4ccba59f3bd1bd510996e976078091c1cc): LF CSV output and refreshed
  ledger hashes; parsed rows unchanged.
- [90a1a90c9ef1a71f576cdee1916a6ed5e2f39013](https://github.com/vanderpol/scap-ng/commit/90a1a90c9ef1a71f576cdee1916a6ed5e2f39013): preserve clean-venv executable
  path; this is the tested candidate toolchain pin.

Hosted implementation checks at `c5be32236`: [current contracts](https://github.com/vanderpol/scap-ng/actions/runs/40149007808),
[canonical fast](https://github.com/vanderpol/scap-ng/actions/runs/40149007813),
[Markdown](https://github.com/vanderpol/scap-ng/actions/runs/40149007855),
[issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40149007823) and
[repository preservation](https://github.com/vanderpol/scap-ng/actions/runs/40149007824)
all **SUCCESS**. Its [rebaseline run](https://github.com/vanderpol/scap-ng/actions/runs/40149007804)
was **CANCELLED** by the subsequent normal push under existing concurrency policy.
At `90a1a90c9`, [canonical fast](https://github.com/vanderpol/scap-ng/actions/runs/40149220787)
and [issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40149220791)
are **SUCCESS**. The [replacement maintained regression run](https://github.com/vanderpol/scap-ng/actions/runs/40149220815)
completed **SUCCESS** before handoff (checked 2026-10-25 01:10 UTC). No untriggered/manual historical workflow is claimed as a fresh
passing check. The evidence/report publication commit
[84f0c8fbe4a0f139246f58e34b2dcab5339a26e4](https://github.com/vanderpol/scap-ng/commit/84f0c8fbe4a0f139246f58e34b2dcab5339a26e4)
also passed [Markdown](https://github.com/vanderpol/scap-ng/actions/runs/40149438084)
and [issue-reference](https://github.com/vanderpol/scap-ng/actions/runs/40149438098)
checks. The final follow-up only records these terminal outcomes.

No new semantic decision was made. Recommended owner follow-up: decide the
required original-source-to-exact-package proof coverage before release; retain
unverified entries until source-backed proofs exist. Signing/trust policy and
scanner acceptance still require their separate work and decisions.
