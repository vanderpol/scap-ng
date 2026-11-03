# Coordinated binary32 comparison contract — 2026-11-03

Owner direction: **“Yes I approve”**, in the Issue14 task session on 2026-11-03,
approving the coordinated binary32 work recommended in the
[ten-source decision packet](https://github.com/vanderpol/scap-ng-tools/blob/688a71896cac03dad3a5664d1e8d500866ac1fa2/docs/ISSUE14-FLOAT-DECISION.md).
Tracking: [canonical #12](https://github.com/vanderpol/scap-ng/issues/12) and
[tools #14](https://github.com/vanderpol/scap-ng-tools/issues/14).
Implementation is under coordinated draft review; this approval does not assert
subsequent human acceptance, Board ratification or scanner conformance.

## Contract and bounded representation

[Versioned contract](metadata/binary32-comparison-contract.json) binds the six
existing self-describing `float_*` operators to IEEE754 binary32 comparisons.
All **143 schema JSON files and their aggregate hash remain unchanged**; this
adds no grammar, datatype tag, nonfinite JSON number or Result field. The generic
untyped comparison path does not activate this explicit profile.

Observed text is cast directly from the OVAL/W3C decimal lexical form to
binary32 using nearest-even rounding, gradual subnormal underflow, signed zero
and signed infinity on overflow. XML whitespace at the edges is allowed; empty,
multi-dot, hex, Unicode-digit and other malformed numerals raise a cast error.
Existing collection/error/unknown/incomplete and six-state propagation rules
remain required. A cast error never becomes zero, absence or a Boolean result.

Expected operands initially require **finite canonical binary32 JSON numbers**.
For original source decimals the converter rounds the exact lexical value once,
then emits a numeric value whose binary64 JSON round-trip recovers that exact
binary32 number. It never performs a decimal→binary64→binary32 cast. Thus source
`1.2` can be preserved as numeric `1.2000000476837158`; an unqualified native
binary64 `1.2` is rejected by this profile, rather than silently reinterpreted.
Source `0` remains a float predicate with numeric `0.0`, never integer semantics.
Finite values overflowing binary32 and explicit `INF`, `-INF`, `NaN` remain
blocked as expected operands. Arrays retain their independent `value_match`;
typed references remain subject to the same runtime finite/canonical invariant
and existing type/provision checks. The source converter does not gain float
Variables, arithmetic, record-field or selector conversion in this amendment.

Against finite expected values, NaN observations produce true for `not_equal`
and false for the other five operations; infinities order below/above every
finite number; signed zeros compare equal. These observations are internal
comparison states. Retain original observed lexical text/provenance; do not
write nonfinite numbers into JSON or invent a new Result representation.
The broader nonfinite expected/Result design stays deferred under research #218.

## Real source and independent numerical boundaries

Nine signed NIWC Rules compare float subexpressions with `>=10.0`; SLES12
SV-237605 compares float timeout with `>=0`. Exact ZIP/Rule/entity/closure pins
remain in tools PR18 and the successor recovery packet. The comparison meaning,
two audit regex captures, Set references, Boolean graph and all source controls
are retained. Activation uses explicit converter opt-in plus the exact contract
sidecar; ordinary and frozen strict conversion retain their previous behavior.

`9.9999999` rounds to binary32 `10` and satisfies `>=10`; a binary64 comparison
does not. A source-shaped negative decimal `-1e-46` underflows to signed zero and
satisfies `>=0`; binary64 remains negative. A second trap is
`1.0000000596046447753906250000000001`: direct binary32 conversion rounds up,
while a binary64 intermediate loses the tiny excess above the midpoint and
incorrectly rounds down. These are numerical/lexical witnesses, not complete
Rule outcomes or actual scanner/provider observations.

[Nineteen fixed vectors](../tests/fixtures/binary32-vectors.json) include ties to
even in both directions, the minimum subnormal, half-minimum underflow, maximum
finite value, overflow and observed nonfinite values. Canonical tests justify
their finite expectations with exact rational nearest-neighbor intervals,
without the converter or a host float cast. Converter tests check exact vector
bits, all comparison operations, invalid input and independent native `strtof`
experiments where available. This is not an OVAL evaluator-conformance claim.

## Program compatibility and review

Affected native programs use `native-assessment-program/0.4`, binding the exact
contract ID/hash and a sorted predicate source-path/operator/hash inventory.
The independent package reader reconstructs that inventory and rejects missing,
forged, downgraded or stale profile metadata, including rehashed package mutants.
Input-presence and approved Variable-function metadata coexist with the profile.
Programs without self-describing float comparisons retain their earlier format
and exact bytes. Historical float programs are not silently reinterpreted:
reproduce them with their pinned pre-contract toolchain, or recompile under the
explicit new contract. Frozen artifacts, original source pins, legacy0.3, old
proofs and manual Assessments remain unchanged.

Rejected alternatives: binary64 by default, float-to-integer coercion, strings
standing in for expected numbers, finite-literal-only activation without observed
rounding, arbitrary precision lost through host parsing, and new nonfinite
JSON/Result shapes. These would either alter the original comparisons or exceed
the approved scope. Editor PR36, release preparation, mandatory six-Benchmark
transfers and full65 generation are excluded. CI/local receipts belong on the
coordinated PRs; passing structural/program checks do not prove scanner behavior.
