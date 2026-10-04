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
After: `test-family` uses `independent.family` directly; `supported` still references
the named `families` Variable. The reviewed mapping removes only the meaningless
singleton Object, not the comparison or its Variable dependency.

`unix` matches; the valid vocabulary value `undefined` does not. An acquisition
error is `error`; an unavailable/not-collected source is `unknown`. These statuses
are not ordinary unmatched strings. State `variable_match: all` and `match: all`
retain the source scopes, even though this particular Variable has one value.

The supplied Item is synthetic. The helper compares the observed family and
the source's simple alternative regex; it does not implement family acquisition
or prove general OVAL regex equivalence.
