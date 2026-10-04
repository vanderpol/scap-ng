# Family: a small system-source Assessment

Compare [source](../sources/family.xml), [Assessment](../content/family.assessment.yaml),
[provenance](../provenance/family.json), and [expectations](../expected/family.json).
Human status: **pending-review**. Provenance: Inherited source / Common explanation.

The complete Self-Assertion Definition `oval:org.mitre.oval.test:def:95` asks whether
the reported system family matches its supplied regex. This is a conformance
assertion, not a security-hardening Rule or a claim that every matching family
is supported by every scanner. Its source regex does not include every family
allowed by the broader capability vocabulary.

Before: `tst:906 → obj:427` (empty singleton Object), `ste:429 → var:403`.
After: `test-system-family` uses `independent.family` directly; `family-matches-pattern` still references
the named `family-pattern` Variable. The reviewed mapping removes only the meaningless
singleton Object, not the comparison or its Variable dependency.

`unix` matches; the valid vocabulary value `undefined` does not. An acquisition
error is `error`; an unavailable/not-collected source is `unknown`. These statuses
are not ordinary unmatched strings. State `variable_match: all` and `match: all`
retain the source scopes, even though this particular Variable has one value.

The supplied Item is synthetic. The helper compares the observed family and
the source's simple alternative regex; it does not implement family acquisition
or prove general OVAL regex equivalence.

Mechanical comparison: [converter output](../mechanical/family.assessment.yaml)
now comes from the maintained lower/align/mapping API path, with a source-ID-keyed
local naming plan. The readable native file only shortens titles and, where
applicable, uses Constant `value` syntax. Executable selectors, State predicates,
quantifiers and criteria are identical between forms. No manual semantic fix is
applied. File/registry mapping calls are explicitly case-scoped; their general
automatic converter readiness remains unchanged.
