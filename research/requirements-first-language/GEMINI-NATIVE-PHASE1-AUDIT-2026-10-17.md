# Gemini first-read Phase 1 audit — authoring NO-GO, architectural pilot still open

17 October 2026 · Issues #235 / #229. Written AFTER the [frozen original response](GEMINI-NATIVE-PHASE1-RESPONSE-2026-10-17.md). Keep this audit OUT of Gemini's context until Phase 2 is complete. The prepared [Phase 2 request](GEMINI-NATIVE-AUTHORING-PHASE2.md) remains unchanged.

## Separate verdicts

**Current first-time, unaided auditor authoring: NO-GO.** This is a fair judgment of the unlabeled examples, missing provider dictionary, missing collection/error semantics, and the unsuccessful independent new-authoring attempt.

**Research feasibility for native requirements-first AST: conditional GO for continued pilot only.** Eight typed research examples, one AST, source-conscious examples, actual Linux mountinfo and fixture tests support feasibility. These do NOT prove user authorability.

**Mandatory SCAP 1.4 conversion / normative v0.4: NO-GO.** Verified source-to-native parity remains 0/5 pinned cases. The generic Test-level compatibility dispatch is NOT an OVAL Object/State/Variable converter or a full six-state scanner. Keep earlier compatibility work.

## What Gemini understood and where it struggled

- A: Correctly understood required selected /home mount and all matching mounts having nosuid.
- B: Correctly understood guest-account filtering and all matching accounts disabled. Marking complete-empty undefined is reasonable in an intentionally blind sample packet. The current prototype interprets a COMPLETE zero selected optional population as True, and an INCOMPLETE zero as Unknown. This must be explicit to auditors.
- C: **Critical internal contradiction.** The first-read prose says at least one compliant KeepAlive and at least one acceptable MaxKeepAliveRequests directive, but the authored check means ALL selected directives must match, with at least one selected per type. Later, Gemini correctly predicts failure for one violation. Our [fixture test](../../tools/test_research_gemini_phase1_counterexamples.py) proves that KeepAlive On + KeepAlive Off + MaxKeepAliveRequests 150 must fail; the weaker prose would pass.
- D: Correctly identified minimum one forward zone plus minimum one zone-signing and key-signing key per zone. Did not establish the exact per-parent association or per-key ALL semantics; cannot be expected to infer a versioned provider contract from an isolated example.
- Incomplete acquisition, missing property, wrong-parent DNS keys: Gemini's CANNOT DETERMINE is an honest result of a packet lacking a contract, not evidence the prototype has no answer. Current research implementation distinguishes known field absence from unreadable/unknown field, incomplete vs complete collection and mismatched parent identity, but those rules are not an approved public standard.

## The attempted new Linux file rule changed policy

**Correct aspect:** minimum_resources: 1 was placed on the combined selected file population rather than separately requiring a file per root user.

**Incorrect/unsupported aspects:**

1. Wrote acquisition_options instead of using — rejected by grammar.
2. Used home_directory (not a known provider field) and changed the filter from home_dir not equal to the filesystem root path / into home_directory not equal to /root. That includes UID0 accounts homed at / and excludes valid UID0 accounts homed at /root — an objective semantic inversion. A compiler can catch a field typo but cannot know a valid wrong string constant was not intended.
3. Limited filenames to .bashrc and .profile, omitting other initialization dotfiles. The provider currently requires a filename regex, not a map/list.
4. Used max_depth 2. The available fixture collector only implements 1. **The Phase 1 task itself did NOT specify a required depth, so this is an unsupported assumption, not a mistake against the supplied security sentence.**
5. Used follow_symlinks false. The Phase 1 sentence did not fix symlink behavior, so this is an explicit research question rather than a provable mistake against the new native policy. Original source migration requires a separately tested setting.
6. Wrote permissions / octal_equals 0740. The valid typed operator is mode / only_these_bits '0740': a subset-mask check rather than exact equality. Mode 0600 is compliant even though not equal to 0740. **The Phase 1 samples did not show that operator**, so missing documentation was a fair reviewer complaint, even though the prototype actually implemented the operator.

These cases now have [typed grammar regression tests](../../tools/test_research_native_contract_candidate.py) and [semantic mismatch tests](../../tools/test_research_gemini_phase1_counterexamples.py). Strengthening typed nested account filter validation uncovered a genuine prototype bug: previously the compiler validated only acquisition parameter names at the top level, not the account_filter fields inside. That has been corrected. The stricter tests also revealed that not_equals was used by an existing native example but absent from the registered operators; it was added.

## Gemini's proposed flat relationship model is NOT equivalent yet

The suggested target/filter/constraints/sub_resources syntax removes a lexical $zone reference but (1) omits the required key-signing key branch entirely, (2) introduces relationship: parent_zone_id without an identity/cardinality contract, (3) uses a special-purpose must_be_signed field, and (4) has no evidence/field missing behavior. It may be aesthetically better; **it is not a fair A/B comparison until it expresses BOTH key types, their individual minima, all-key validity ranges and wrong-parent/incomplete behavior**. An editor may display an explicit relation while the compiler uses a typed lexical association. Neither approach merits automatic acceptance or rejection yet.

## Go/no-go gates sharpened

1. Provider catalog with typed input fields, operator lists, identity, parent-child/cardinality relations, completeness and evidence statuses, surfaced in an editing assistant — not assumed from YAML examples.
2. Auditor-facing preview must clearly distinguish required vs optional selected populations and show the exact account/root path filters before saving.
3. The next independent test must be a new-policy AUTHORING exercise, not just first-read interpretation, using actual provider reference/autocomplete and validator error messages.
4. A/B test an equivalent full DNS rule using lexical typed relations and explicit relationship syntax — not the incomplete one-key suggestion.
5. Preserve source conversion compatibility and require source-specific six-state parity before promoting any new standard.

**External review next:** send only the already prepared Phase 2 prompt after preserving the initial response; do not feed this correction ledger to Gemini until Phase 2 is finished.
