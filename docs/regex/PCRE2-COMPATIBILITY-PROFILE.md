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

## Proposed baseline

These are proposals for review, not hidden runtime defaults:

1. **Engine/version:** PCRE2, with an exact minimum library version and Unicode
   data version selected by the owner before implementation. Every binary and
   editor package records the engine/profile versions it embeds. The current
   VS Code `pcre2-wasm` 10.49.2 package is a test/oracle input, not a decision
   that RI must use that build.
2. **Encoding:** patterns and subjects are UTF-8. Invalid UTF-8 is a diagnostic
   (`invalid_utf8`), never a nonmatch. No locale-dependent matching is used.
   Unicode normalization is not performed; canonically equivalent sequences
   remain distinct unless a pattern explicitly handles them.
3. **Feature boundary:** the OVAL common subset is the default compatibility
   target. Positive and negative lookahead are included because they occur in
   existing OVAL-derived content and are represented in the vector pack.
   Lookbehind, backreferences, recursion/subroutines, conditionals, callouts,
   verbs, and other PCRE2-only constructs are rejected or held unless a later
   owner-approved profile admits them. `\p{...}`/UCP behavior is an owner hold,
   not an implicit extension of OVAL compatibility.
4. **Matching:** `matches_regex` is an unanchored search over the declared
   subject framing. It is not an implicit full match. `^`/`$` remain distinct
   from `\A`/`\z`; anchors must not be added or removed during conversion.
5. **Newlines:** preserve subject bytes and make newline handling explicit.
   The proposal uses PCRE2 `ANYCRLF` for multiline text framing so LF, CRLF,
   and CR are tested as newline forms without silently rewriting the subject.
   Whether text collectors strip line terminators before matching is a
   capability/framing rule and remains an owner decision. Generic scalar
   matching must not inherit text-file line behavior.
6. **Flag allow-list:** the existing VS Code preview accepts `i`, `m`, `s`, `x`, `u`, `U`, `A`, `D`, and `g` as preview controls. That UI allow-list is not the native profile. The proposed OVAL-compatible profile maps only source `ignore_case`, `multiline`, and `singleline` to `i`, `m`, and `s`; `x`, `u`, `U`, `A`, and `D` require explicit owner approval, and `g` has no native single-subject meaning and must remain editor-only or be rejected.
7. **Case and dot/newline flags:** an OVAL text-content behavior of
   `ignore_case`, `multiline`, or `singleline` maps to effective `i`, `m`, or
   `s` respectively. The OVAL 5.12.3 source defaults (`false`, `true`,
   `false`) are materialized by conversion where the existing native Object
   contract already carries them; this profile does not create a schema default.
   Inline modifiers remain in the pattern and are scoped by PCRE2. Precedence
   for a source behavior flag that conflicts with an inline modifier is an
   owner decision; the proposed default is explicit source options establish
   the outer mode and inline modifiers can narrow/override within their scope.
8. **Captures:** native `regex_capture` returns the first numbered capturing
   group for each input as described by the current 0.4 schema documentation.
   Repeated-group behavior follows the qualified PCRE2 capture result. A
   missing group, an empty group, and no match must be represented distinctly
   internally; the conversion/result normalization (including the historical
   empty-string behavior) is an owner decision and is covered by hold vectors.
   Named captures are preview/conformance data only until a native wire contract
   exists.
9. **Errors:** invalid syntax, disallowed features, invalid encoding, engine
   unavailability, cancellation, and resource exhaustion are diagnostics. They
   must not be converted to a genuine nonmatch or a technical Pass/Fail. The
   final mapping to `unknown`, `error`, or another technical status requires
   owner approval and must be consistent with collection/evidence completeness.
10. **Limits:** every implementation supplies independent limits for pattern
   bytes, subject bytes, compile work, match steps, depth, heap/JIT stack,
   capture count, compiled-pattern cache size, concurrent operations, and
   wall-clock cancellation. Limits are execution controls, not authoring
   semantics, and a pattern cannot relax them. The vector budgets are minimum
   adversarial cases, not final product defaults.

## Compatibility matrix

| Construct | Proposed Phase 1 disposition | Reason/evidence |
| --- | --- | --- |
| Literals, classes, quantifiers, groups, alternation | OVAL-compatible candidate | Basic operation vectors; source examples use these forms. |
| `matches_regex` search versus explicit anchors | OVAL-compatible candidate | Linux `/home` example is intentionally unanchored; anchor vectors distinguish `^/$` and `\A/\z`. |
| Positive/negative lookahead | OVAL-compatible candidate, qualify | Existing corpus witnesses include `^(?!#)...`; both directions are in the vector pack. |
| Inline `(?i)`, `(?m)`, `(?s)` | OVAL-compatible candidate, qualify | Windows SYSVOL example uses `(?i)`; OVAL behaviors map separately to effective flags. |
| OVAL `ignore_case`, `multiline`, `singleline` | Preserve as explicit source/capability behavior | XSD documents the `i/m/s` intent and defaults; no new schema field is proposed. |
| Named captures | Editor/engine capability; native semantic hold | Existing VS Code test displays named captures, but native 0.4 only specifies first numbered capture. |
| Unicode literal and no-normalization behavior | Proposed; qualify | Exact UTF-8 literal vectors are unambiguous. Case folding/UCP has owner holds. |
| `\p{...}`, UCP, Unicode version | Owner decision | PCRE2/Unicode behavior is broader than the OVAL statement and can change `\w`, `\d`, `\s`, and case results. |
| Lookbehind, backreferences, recursion, conditionals, verbs/callouts | Reject/hold in this profile | PCRE2-only or security-sensitive features; none may become valid by compilation alone. |
| YAML/XML escaping | Preserve decoded pattern text; qualify round trips | Single-quoted Windows backslashes and source XML escaping require byte-level vectors. |
| Missing/empty/optional/repeated capture | Owner decision hold | Current schema prose and OVAL-derived vectors do not settle every wire normalization. |

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

## Owner decisions required before Phase 2

1. Exact PCRE2 minimum/version and Unicode data policy.
2. Whether the 0.4 compatibility profile is OVAL-subset-only, and if/when
   PCRE2 extensions can be authored.
3. UCP/property behavior, Unicode case folding, and normalization policy.
4. CRLF/newline convention and whether each text capability strips line endings.
5. Precedence of capability behavior flags versus inline modifiers.
6. Missing group, empty group, no-match, repeated-group, and named-capture
   normalization for native Variables/Results.
7. Error/resource-limit mapping to collection/evaluation statuses and evidence
   completeness.
8. RI distribution choice (cgo/native library, helper process, or portable
   implementation), supported Windows architectures, and packaging/signing.
9. Whether a profile identifier is introduced only in a later language version
   or can be associated externally with frozen 0.4.0 content.

Until these decisions are approved, this PR is documentation and vector
provenance only. It does not authorize schema changes, converter changes, RI
runtime implementation, editor behavior changes, archive regeneration, or
repinning.
