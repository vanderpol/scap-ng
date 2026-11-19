# Proposed PCRE2 compatibility profile (Issue #62, Phase 1)

**Status: owner-review proposal; not normative and not implemented.**

This document proposes the cross-repository contract needed before SCAP-NG can
use PCRE2 for native `matches_regex`, regex-bearing acquisition selectors,
text-content matching, or Variable `regex_capture`. It does not modify the
frozen 0.4.0 schemas, converter, RI runtime, published archives, or pins.
The companion [`conformance-vectors.v1.json`](conformance-vectors.v1.json) is a
versioned, engine-neutral vector pack. A vector expectation is either a
proposed semantic expectation or an explicit owner decision hold; it is not
scanner evidence.

## Scope and terminology

| Term | Proposed meaning |
| --- | --- |
| **OVAL-compatible** | The common Perl-style subset named by OVAL 5.12.3, with the source operation's search, framing, flags, and capture rules preserved. PCRE2 compilation alone does not establish this class. |
| **PCRE2 profile** | A versioned PCRE2 configuration, feature allow-list, encoding policy, option mapping, error mapping, and resource envelope. “PCRE2” without a profile is not a contract. |
| **effective flags** | The options actually applied by an evaluator after source behavior flags and inline modifiers are resolved. They are not new 0.4 YAML fields in this proposal. |
| **subject framing** | The boundary being searched: one scalar, one output line, a text block, or a complete multiline subject. The same pattern can have different meaning under different framing. |
| **qualified** | Demonstrated by the shared vectors on every supported implementation and platform. Schema validity, compilation, or editor preview is not qualification. |

The proposed profile identifier is `scap-ng-pcre2-oval-compatible/0.1`. The
identifier is deliberately not inserted into 0.4 documents. A later approved
profile/version must be selected before runtime implementation or archive
regeneration.

## Evidence register

The following evidence resolves several discussions that were previously only
holds. It is pinned as review evidence, not as a new runtime dependency:

| Evidence | Relevant finding |
| --- | --- |
| [OVAL Regular Expression Support](https://ovalproject.github.io/documentation/policy/regex/) (retrieved body SHA-256 `8607d1cd11c44bc82f42a38d05405cc3e33f2e42f87b305551bb874c5b57b683`) | OVAL's common subset explicitly lists `(?=...)` and `(?!...)` lookahead, single-digit `\n` backreferences, and Unicode character matching; it explicitly says Perl `m/i/s/x` modifiers are off unless an OVAL construct documents them. |
| OVAL 5.12.3 checkout `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `oval-definitions-schema.xsd` SHA-256 `06b79e8683d6b9dcaad3ab074a456588ed82c4edd2e8fff209def10aa0a366cc`, lines 910–915 | `regex_capture` applies per input, uses the first match and first capture, returns empty string for no capture/no match, and uses the last participation of a quantified capture. |
| The same OVAL checkout, `independent-definitions-schema.xsd` lines 1940–1952 | `ignore_case`, `multiline`, and `singleline` explicitly document their `i/m/s` intent and defaults (`false/true/false`) for text content. |
| [PCRE2 pattern documentation](https://www.pcre.org/current/doc/html/pcre2pattern.html), retrieved body SHA-256 `e1ae7a7a415031293d774f2b9ee94075f258c2eba1695b40d412dbff957e6681` | PCRE2 defaults `\d/\s/\w` to ASCII even in UTF mode unless UCP is enabled; newline convention affects anchors and dot; JIT ignores depth and heap limits, so limit claims must name the execution mode. |
| [PCRE2 10.49 release](https://github.com/PCRE2Project/pcre2/releases/tag/pcre2-10.49), tag commit `6f9d7c1373262c541324a16a358785b33ef116cf`, source tarball SHA-256 `53c156e1ba416a20da8e65395daa132da0d80e76910424caca3fcdae7831d384`; `src/pcre2_ucd.c` SHA-256 `cfa8bcb3ad316e09ebfdf3e4b07d708a9d4e53795cc7c0bf04ce5156d7695adc` | The current PCRE2 release is a concrete candidate baseline, and its checked-in Unicode table reports Unicode `17.0.0`. This is a recommendation for owner approval, not a runtime pin in Phase 1. |
| VS Code commit `6f5a2bc38261586ea3e7badb95592a039b72e5da`, `test/source.test.mjs` and `src/playground.ts` | The existing preview proves only bounded PCRE2-WASM UX cases: inline modifiers, named captures, invalid input, input limits, pathological patterns, and cancellation. |
| VS Code dependency `pcre2-wasm` 10.49.2 (package-lock integrity `sha512-KT/xILUIPAgxAFA9ZbwMUBrRbt06B31DlS88dt7DsaHbLTfvfx+thRtnhLyZ9kX+JvzOqwStHDzzg9szDjQLWg==`; package README SHA-256 `2d01a6401390401cca6403471cb0cb19a08e7591471b33bf7f59eac725a8bf0d`) | The wrapper documents byte mode by default, requires `UTF` or `UCP` for non-ASCII, maps match-limit exhaustion to PCRE2 error `-47`, and treats `g` as a no-op. A local non-qualification smoke check produced `aa`/`ab` results for `^(a|b)\1$`, `ipp` for `(i..)+` over `mississippi`, and Unicode `\w+` matching `café` only with `FLAGS.UTF|FLAGS.UCP`. This supports vector expectations while leaving cross-platform/runtime qualification open. |

The OVAL policy evidence changes the classification of inline `(?i)` in the
existing Windows converted example: PCRE2 can evaluate it, but it is not an
OVAL-compatible modifier under the general OVAL policy. The converter must
preserve it and classify it as a source-preserved compatibility hold until an
owner-approved native extension profile exists.

## Proposed baseline

These are proposals for review, not hidden runtime defaults:

1. **Engine/version:** PCRE2, with an exact minimum library version and Unicode
   data version selected by the owner before implementation. Every binary and
   editor package records the engine/profile versions it embeds. The current
   VS Code `pcre2-wasm` 10.49.2 package is a test/oracle input, not a decision
   that RI must use that build.
2. **Encoding:** patterns and subjects are UTF-8. Invalid UTF-8 is a diagnostic
   (`invalid_utf8`), never a nonmatch. The proposed OVAL-compatible character
   policy enables PCRE2 UCP with a pinned Unicode data version because OVAL
   states that character matching assumes Unicode. Locale-dependent matching is
   disabled, and compile options must prevent pattern-controlled `(*UTF)` or
   `(*UCP)` changes. Unicode normalization is not performed; canonically
   equivalent sequences remain distinct unless a pattern explicitly handles
   them.
3. **Feature boundary:** the OVAL common subset is the default compatibility
   target. Positive and negative lookahead, plus single-digit numbered
   backreferences, are OVAL-listed candidates and are represented in the
   vector pack. Lookbehind, named backreferences, recursion/subroutines,
   conditionals, callouts, verbs, and other PCRE2-only constructs are rejected
   or held unless a later owner-approved profile admits them. `\p{...}` remains
   outside this OVAL profile. PCRE2 UCP is an execution option for the Unicode
   character-class policy below, not permission to admit arbitrary PCRE2 syntax.
4. **Matching:** `matches_regex` is an unanchored search over the declared
   subject framing. It is not an implicit full match. OVAL-listed `^`/`$`
   semantics remain distinct from the PCRE2-only `\A`/`\z`; the latter are
   held outside this compatibility profile and must not be introduced by
   conversion.
5. **Newlines:** preserve subject bytes and make newline handling explicit.
   The proposal uses PCRE2 `ANYCRLF` for multiline text framing so LF, CRLF,
   and CR are tested as newline forms without silently rewriting the subject.
   Whether text collectors strip line terminators before matching is a
   capability/framing rule and remains an owner decision. Generic scalar
   matching must not inherit text-file line behavior.
6. **Flag allow-list:** the OVAL policy says Perl `m`, `i`, `s`, and `x`
   modifiers are off unless a construct permits them. The existing VS Code
   preview accepts `i`, `m`, `s`, `x`, `u`, `U`, `A`, `D`, and `g` as preview
   controls, but that UI list is not the native profile. Only the explicit OVAL
   text-content behavior mapping below is admitted in the proposed profile;
   inline `(?i)`/`(?m)`/`(?s)` in existing converted content are preserved but
   remain a source-compatibility hold, not proof of OVAL compatibility. `x`,
   `u`, `U`, `A`, `D`, and `g` require a later owner-approved profile; `g` has
   no native single-subject meaning.
7. **Case and dot/newline flags:** an OVAL text-content behavior of
   `ignore_case`, `multiline`, or `singleline` maps to effective `i`, `m`, or
   `s` respectively. The OVAL 5.12.3 source defaults (`false`, `true`,
   `false`) are materialized by conversion where the existing native Object
   contract already carries them; this profile does not create a schema default.
   A source behavior flag is therefore not the same thing as an inline modifier.
   The precedence question is resolved for this proposal by rejecting a claim
   of OVAL compatibility when inline and explicit modes conflict; a later
   extension profile may define scoped PCRE2 precedence.
8. **Captures:** the OVAL 5.12.3 XSD resolves the source rule: process each
   input independently; use the first match and first numbered capture; return
   an empty string for no capture or no match; and return the last participation
   of a quantified capture. The native `regex_capture` proposal adopts those
   value semantics. Internal diagnostics may still distinguish missing group,
   empty group, and no match, but a later native wire contract must not silently
   change the source value result. Named captures remain preview/conformance
   data only because neither OVAL's function contract nor frozen native 0.4
   syntax gives them a named-result wire shape.
9. **Errors:** invalid syntax, disallowed features, invalid encoding, engine
   unavailability, cancellation, and resource exhaustion are diagnostics. They
   must not be converted to a genuine nonmatch or a technical Pass/Fail. The
   final mapping to `unknown`, `error`, or another technical status requires
   owner approval and must be consistent with collection/evidence completeness.
10. **Limits:** every implementation supplies independent limits for pattern
   bytes, subject bytes, compile work, match steps, depth, heap/JIT stack,
   capture count, compiled-pattern cache size, concurrent operations, and
   wall-clock cancellation. Phase 1 proposes JIT disabled for the initial
   compatibility adapter: PCRE2 documents that heap and depth limits do not
   apply to JIT in the same way. A later JIT-enabled profile must prove its
   separate match/JIT-stack behavior and cannot claim the interpreter's heap or
   depth limit semantics by analogy. Limits are execution controls, not
   authoring semantics, and a pattern cannot relax them. The vector budgets are
   minimum adversarial cases, not final product defaults.

## Compatibility matrix

| Construct | Proposed Phase 1 disposition | Reason/evidence |
| --- | --- | --- |
| Literals, classes, quantifiers, groups, alternation | OVAL-compatible candidate | Basic operation vectors; source examples use these forms. |
| `matches_regex` search versus explicit anchors | OVAL-compatible candidate | Linux `/home` example is intentionally unanchored; anchor vectors distinguish `^/$` and `\A/\z`. |
| `\A`/`\z` absolute anchors | PCRE2 extension hold | OVAL lists `^`/`$` line anchors but not these PCRE2 anchors; retain only as a later-profile vector. |
| Positive/negative lookahead | OVAL-compatible candidate, evidence-backed | OVAL policy explicitly lists `(?=...)` and `(?!...)`; both directions are in the vector pack. |
| Inline `(?i)`, `(?m)`, `(?s)` | Source-preserved PCRE2 hold, not OVAL-compatible | OVAL policy says Perl modifiers are off unless an OVAL construct permits them; the Windows sample is preserved evidence, not a compatibility claim. |
| OVAL `ignore_case`, `multiline`, `singleline` | Preserve as explicit source/capability behavior | XSD documents the `i/m/s` intent and defaults; no new schema field is proposed. |
| Named captures | Editor/engine capability; native semantic hold | Existing VS Code test displays named captures, but native 0.4 only specifies first numbered capture. |
| Unicode literal and no-normalization behavior | Proposed; qualify | Exact UTF-8 literal vectors are unambiguous. Case folding/UCP has owner holds. |
| UCP character classes / Unicode version | Proposed UCP-on policy; version owner hold | OVAL assumes Unicode character matching; PCRE2 documents UCP changes to `\w`, `\d`, `\s`, and case behavior. Pin the Unicode data version. |
| Single-digit numbered backreferences | OVAL-compatible candidate, qualify | OVAL policy lists `\n` as a backreference; include bounded vectors. Named/multi-digit/recursive forms remain held. |
| Lookbehind, named backreferences, recursion, conditionals, verbs/callouts | Reject/hold in this profile | PCRE2-only or security-sensitive features; none may become valid by compilation alone. |
| YAML/XML escaping | Preserve decoded pattern text; qualify round trips | Single-quoted Windows backslashes and source XML escaping require byte-level vectors. |
| Missing/empty/optional capture | Native wire-status hold; source value rule resolved | OVAL resolves no-capture/no-match to empty string; internal diagnostics may retain the distinction. |
| Repeated capture / first-match precedence | OVAL-compatible candidate, evidence-backed | OVAL 5.12.3 XSD specifies first match/first capture and last quantified participation. |

## Subject framing and source mapping

The evaluator must receive framing metadata from the caller; it must not infer
it from the pattern:

* a native Object selector generally searches one collected scalar;
* an OVAL `textfilecontent54` pattern produces text blocks and may select an
  `instance`; its `multiline` and `singleline` behaviors are acquisition/content
  semantics;
* an OVAL `shellcommand` pattern selects stdout lines before state matching;
* `regex_capture` applies independently to each input value and returns a
  capture result, not an Assessment outcome.

The converter currently emits patterns without executing them. It must preserve
source pattern text, effective source behavior, source identity, and any
unsupported/held classification. It must never turn a line pattern into a
whole-file pattern, or a full-text pattern into a line pattern, merely to make
PCRE2 compilation succeed.

The canonical converted examples used by the vector pack are:

* [`examples/linux-home-nosuid.assessment.yaml`](../../examples/linux-home-nosuid.assessment.yaml),
  `mount_point: {matches_regex: '.*\\/home'}`;
* [`examples/windows-server-2025-sysvol-permissions.assessment.yaml`](../../examples/windows-server-2025-sysvol-permissions.assessment.yaml),
  the `regex_capture` path pattern and nine inline `(?i)` stdout patterns.

The pack also records provenance for OVAL-derived lookahead witnesses and the
existing VS Code PCRE2 preview tests; those references are not claims that the
other repositories already implement the proposed profile.

## RI implementation alternatives (design only)

RI currently has no authored-regex evaluator. The following alternatives must
be compared before runtime work begins:

| Alternative | Advantages | Costs/risks | Windows implication |
| --- | --- | --- | --- |
| **Native `libpcre2-8` via cgo** | Exact PCRE2 API/options, match/depth/heap/JIT controls, closest to the proposed profile | cgo toolchain, ABI and cancellation boundary; native dependency/SBOM; static linking and license review; cross-build complexity | Current RI validation uses `CGO_ENABLED=0`; Windows needs a reproducible MSVC/MinGW static or trusted DLL package, safe DLL loading, and amd64/arm64 qualification. |
| **Native PCRE2 helper process** | Hard process boundary for time/memory/cancellation; can package a platform-native helper | IPC/serialization overhead, deployment/signing, lifecycle and evidence-status complexity; still needs native builds | Ship and verify a signed helper per Windows architecture; never search an untrusted DLL/helper path. |
| **Portable Go/WASM implementation** | Easier cross compilation and distribution; avoids cgo | No assumption of PCRE2 equivalence; `regexp2` is a .NET dialect, not PCRE2; a WASM runtime adds overhead and its own limits | A single artifact is attractive, but Windows runtime and Unicode/limit parity still require qualification. |
| **Host/platform regex APIs** | No added dependency | JavaScript, Go RE2, .NET, PowerShell, and Windows path APIs have different syntax and semantics; unacceptable as silent fallback | Must not be used for native semantics. |

The Phase 1 recommendation is to design the adapter boundary and packaging
matrix first, then select native PCRE2 or another implementation only after it
passes the shared vectors. No RI dependency, cgo setting, collector, or runtime
entry point is changed by this proposal.

## Existing VS Code evidence

The vector pack is derived from, and links back to, the existing preview tests:

* `test/source.test.mjs` covers inline modifiers, invalid patterns, the
  100,001-character input limit, pathological patterns, worker cancellation,
  and named captures;
* `src/playground.ts` and `src/playground-worker.ts` define the current preview
  bounds: 10,000 pattern characters, 100,000 input characters, one million
  match steps, depth 1,000, up to 100 patterns, worker initialization timeout,
  and normal worker timeout;
* the preview remains explicitly labelled `PCRE2-safe-preview`, not a scanner
  or RI result. Its numeric bounds are test inputs for Phase 1, not normative
  runtime limits.

## Proposed decision record for owner approval

The evidence supports the following narrow choices. They are recorded here to
turn the remaining discussions into explicit approval items rather than leaving
runtime implementers to infer behavior:

| Decision | Evidence-backed recommendation | Why this is the safe Phase 1 choice |
| --- | --- | --- |
| PCRE2/Unicode baseline | PCRE2 10.49 with Unicode 17.0.0, built with the 8-bit UTF and UCP support; the editor oracle remains the separately pinned `pcre2-wasm` 10.49.2 package. | The official release and checked-in UCD are content-addressed above; version drift otherwise changes character classes and case folding. |
| UCP and normalization | UCP on whenever UTF-8 mode is on; reject invalid UTF-8; perform no normalization. | OVAL requires Unicode character matching, while PCRE2 documents that UCP changes `\w/\d/\s`; byte mode and normalization would silently change existing text. |
| Newline and framing | Preserve bytes; use `ANYCRLF` only for multiline text-block matching. A line-framed caller supplies a terminator-free line; a scalar caller supplies exactly its scalar. No global CRLF rewrite. | PCRE2 newline mode affects `^/$` and dot, but OVAL acquisition determines whether a subject is a line or block. A single global rewrite would conflate shell-command and text-file semantics. |
| Failure mapping | Only a completed engine operation may produce `match` or `nonmatch`. Compile, unsupported-feature, invalid-UTF-8, unavailable-engine, cancellation, and resource-limit outcomes remain diagnostics/indeterminate and never become nonmatch. | The editor wrapper exposes compile/match errors and PCRE2 documents match-limit errors; treating them as false would create false compliance results. |
| RI distribution | Preserve the current `CGO_ENABLED=0` Go build as the release baseline. Prefer a separately versioned, signed native helper for the first cross-platform proof-of-concept; compare cgo/static-linking in the same matrix before selecting in-tree linkage. | A helper preserves the existing Go cross-build and gives an OS-level cancellation/memory boundary. It costs packaging/IPC complexity, which must be measured rather than hidden in a collector. |
| Frozen 0.4 association | Do not add a profile field or rewrite 0.4 YAML. If association is needed, publish an external profile manifest keyed by the frozen schema/content pins. | Frozen 0.4 has no engine contract; external metadata avoids changing schema meaning or released bytes. |

These are recommended dispositions, not owner approval and not runtime
implementation. The owner must explicitly accept or reject each row before the
profile can become normative.

## Owner decisions required before Phase 2

The following contract points are now evidence-resolved for this proposal:

* positive/negative lookahead is in the OVAL listed subset;
* single-digit numbered backreferences are OVAL-listed, subject to bounded
  execution qualification;
* OVAL general `m/i/s/x` modifiers are off; text-content behavior flags are
  the documented exception and map to explicit `i/m/s` execution options;
* OVAL `regex_capture` uses first match/first capture, empty output for no
  capture/no match, and last participation for quantified captures;
* PCRE2-only `\A/\z`, inline modifier compatibility, named captures, and
  other extensions are not silently admitted; source-preserved cases remain
  classified holds;
* the initial adapter should disable JIT until separate JIT resource semantics
  are qualified.

Remaining owner approvals (the recommended disposition is in the table above):

1. Accept or revise the PCRE2 10.49 / Unicode 17.0.0 baseline and UCP-on policy.
2. Accept or revise `ANYCRLF`, terminator-free line framing, and no global
   line-ending rewrite.
3. Accept the no-false-nonmatch failure rule and choose the concrete native
   wire/status names for indeterminate diagnostics.
4. Choose the RI helper versus cgo/static-link implementation, supported
   Windows architectures, and signing/reproducible packaging requirements.
5. Confirm that any 0.4 association is external metadata only, not a frozen
   schema/profile field.

Until these decisions are approved, this PR is documentation and vector
provenance only. It does not authorize schema changes, converter changes, RI
runtime implementation, editor behavior changes, archive regeneration, or
repinning.
