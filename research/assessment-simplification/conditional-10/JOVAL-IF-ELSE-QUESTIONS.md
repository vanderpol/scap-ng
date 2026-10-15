# Joval review — `if/then/else` and lossless OVAL conversion

**October 15, 2026 · SCAP-NG 0.4 pre-alpha · open decisions, not approved semantics.**

## Why we're asking

Two real DISA examples read naturally as conditionals: **Windows Server 2025 SV-278001** (domain-controller versus member-server registry permissions) and **RHEL 9 SV-258004** (effective SSH KerberosAuthentication check depends on the `sshd_config.d` include path). Their original OVAL criteria are Boolean expressions, not imperative control flow. The six-STIG 0.4 showcase retains the **source-faithful `evaluate` graph** for the real converted Assessment; any `if/else` rendering is a separately marked authoring illustration, not a validated automatic rewrite.

Consider the source pattern:

```text
OVAL: OR( AND(guard, expected_when_true),
          AND(NOT guard, expected_when_false) )
```

A procedural branch instead selects exactly one payload when the guard is `true` or `false`. **These are not generally equivalent across OVAL's six outcomes.** Our pinned generic model compared all `6 × 6 × 6 = 216` input combinations and found **135 equal, 81 different**; all eight Boolean-only combinations agree. See [source-shape audit and six-state proof](README.md).

The maintained *experimental* Assessment expression evaluator currently propagates a guard with `error`, `unknown`, `not_evaluated`, or `not_applicable` **without taking either branch**. That behavior is a clearly defined candidate, **not** evidence that the original OVAL Boolean expression may be rewritten as a native conditional.

## Questions for Joval (decisions we need, in order)

1. **One syntax or two meanings?** Should `if/then/else` mean *procedural selection* for new native authoring only, while an OVAL-source `OR(AND(G,P),AND(NOT G,Q))` stays explicit `any/all/not`? Or is a **declarative branch shorthand** valuable if it lowers *exactly* to the old six-state Boolean graph? If so, do not call both constructs `if`.
2. **Unresolved guard policy:** Is `else` selected **only for `false`**, with `error`, `unknown`, `not_evaluated`, and `not_applicable` propagated without selecting a branch? If a vendor prefers a different behavior, must it be explicit in authored content instead of an implicit default?
3. **Evaluation and evidence:** Must unselected branches be truly skipped, or merely ignored in the final result? What happens if they have collection side effects, expensive recursive discovery, an error, or evidence relevant to later audit? How do we record *why* a branch was selected or skipped?
4. **Nested conditions and dependency reuse:** Can `elseif` or dependent-applicability checks be expressed without duplicating a referenced Assessment? How are cycle detection, type compatibility, target binding, and caching handled?
5. **Applicability versus compliance:** Should an inapplicable branch produce `not_applicable` locally, or should it simply not be evaluated? When an entire Rule/Assessment is inapplicable, which level owns that outcome? The two are not interchangeable.
6. **Converter admissibility:** Should automatic OVAL→NG conditional rewriting remain **off** unless a narrowly defined source pattern has a proved six-state *and evidence/collection* equivalence? What minimal real-source counterexamples and differential regression tests would Joval require before enabling one?
7. **Boundary with legitimate alternatives:** How should authors distinguish branch selection from *two acceptable compliance methods*? The RHEL/Oracle module-disable rules are valid `any` alternatives, **not** if/else; don't force them into a conditional just for brevity.

## Recommendation for tomorrow's meeting

**Show the simple `if/else` candidate, then show the non-equivalence warning immediately.** Ask for the semantics and proof strategy first; do not ask Joval to approve syntax or runtime claims. Retain literal OVAL `all/any/not` in every conversion that cannot be proven equivalent. A readable native conditional and a faithful legacy converter may coexist without putting multiple ambiguous meanings into one key.

**Review sources:** [conditional production census and 216-case comparison](README.md) · [real but research-only before/after examples](EXAMPLES.md) · [maintained experimental evaluator](../../../tools/assessment_expression.py) · [Joval meeting packet](../compact-authoring-04/JOVAL-TECHNICAL-PREVIEW.md).

**Meeting output to capture:** guard-outcome truth table; skipped-branch/evidence policy; decision on source-preserving declarative shorthand; a short list of Joval-provided counterexamples; issue owner for each unresolved contract.
