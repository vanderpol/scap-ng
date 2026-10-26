# Direct OpenSSH text-file proof — 2026-10-26

Continued under [#251](https://github.com/vanderpol/scap-ng/issues/251#issuecomment-6401652271)
after the [service checkpoint](v04-direct-service.md). No approved schema,
production converter/compiler, source fixture or release gate changed.

| Field | Verified result |
| --- | --- |
| BASE_SHA | `ca1ee36f36e858cb384a1edf92fea179af179438` |
| RESULT_SHA | `4adfdbad939c63b7dab74b59788bf09f29dc3655` |
| IMPLEMENTED | Generic text-file acquisition, exact regex/capture operands and bounded behavior parameters |
| SOURCE_PROVED / COMPILED_UNPROVED / BLOCKED | **220 / 0 / 71** of 291 original Rules |
| CANDIDATES | All **seven** original OpenSSH closures independently prove and compile |
| AUTHORING | 220 Assessments / 295 Tests; 174 inline Test Objects, 36 references to 12 genuinely shared Objects, 85 no-Object Tests, 120 compact Registry Objects; deprecated grammar zero |
| TESTS / CI | **3,052** maintained tests, zero failures/errors, one existing skip; **57** related tests pass; all five implementation-head hosted workflows PASS |
| NEXT | Eight-candidate Windows file-effective-rights source/dependency investigation |

**Acquisition fidelity.** The small `v04_direct_file_behaviors` helper keeps
collection behavior separate from matching. It materializes original optional
defaults (`ignore_case: false`, `multiline: true`, `singleline: false`,
`item_creation: all_object_elements_fullfilled`, filesystem `all`) and preserves
explicit overrides. Original `defined` filesystem scope maps to approved native
`same`. Patterns, paths, instances, capture datatypes and State Boolean structure
remain exact. No regex rewriting or collected-Item fabrication is performed.
Explicit Windows-view/traversal attributes, unknown or duplicate/nonempty
behaviors, invalid Boolean tokens and invalid creation/scope values fail closed.

Five focused tests cover all seven actual closures and YAML/JSON equality;
original XSD optional/default declarations; all eight flag combinations; both
item-creation modes and three filesystem scopes; changed flags, patterns,
instances and capture types; and invalid-source mutants. Controlled derivatives
add no original Rule coverage. The independent reader checks original acquisition
parameters and terms without importing the new helper. It also rejects duplicate
empty behavior elements and correctly retains native field-name correspondence.

Public gates validate **442 JSON / 442 YAML documents**, compile 220 programs and
pass the separate package consumer. All **213** previous compiled program hashes
are unchanged. The [machine packet](v04-direct-textfile.json) records individual
original Rule/Definition/dependency hashes, proofs, compiled hashes, exact commands,
remaining blockers and CI. Source ZIP/XML SHA-256 remain
`2f46264b5fa21c8a033236121794ebe372314bf7458dac0aca4f81179fe7ece0` /
`52b7918ea577095cb1c130589e5061c52ef4b12370ebb4ce84d2dfba68757440`.

[Actual pinned OpenSSH YAML/JSON](../examples/direct-textfile/README.md) is generated
by the converter, with source identities, validation, compilation and proof in its
manifest. Regenerate from that manifest's converter SHA with
`PYTHONPATH=tools python tools/v04_direct_authoring_examples.py --capability independent.textfilecontent54 --output /tmp/direct-textfile-examples`.
Run `PYTHONPATH=tools python tools/test_v04_direct_textfile.py -v`; the
[developer guide](../developer/DIRECT-V04-CONVERTER.md) covers extension contracts.
No scanner execution, regex-engine conformance, signing/trust, full six-STIG
coverage or production-release readiness is claimed. No new `all_exist`
normalization is introduced.

Issue commenting remains blocked by the previous exact error
`Post "https://api.github.com/graphql": Forbidden`; no repeated retry was made.
This committed report and the engineering ledger are the handoff.

Exact implementation CI: [Markdown navigation and duplication audit](https://github.com/vanderpol/scap-ng/actions/runs/40308503456), [Rebaseline smoke regression](https://github.com/vanderpol/scap-ng/actions/runs/40308503241), [Commit issue reference](https://github.com/vanderpol/scap-ng/actions/runs/40308503324), [0.4.0 canonical authoring fast checks](https://github.com/vanderpol/scap-ng/actions/runs/40308503114), [Current-design regression contracts](https://github.com/vanderpol/scap-ng/actions/runs/40308503122).
