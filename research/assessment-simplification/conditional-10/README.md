# Conditional-shaped OVAL criteria research

> **RESEARCH ONLY — NOT AN ACCEPTED SCAP-NG DESIGN**
>
> This directory does not change the 0.2.0 or 0.3.0 schema, converter contract,
> or accepted conditional semantics. It exists to determine how much real
> production OVAL Boolean nesting is better understood by humans as
> applicability/branching rather than generic AND/OR trees.

## Why this matters

The RHEL/Windows authoring-language research showed that Boolean composition is
more common than Variable/dataflow complexity. A key question is whether some
nested criteria are only complicated because OVAL expresses an environmental
choice as:

```
OR
  AND guard-A, payload-A
  AND guard-B, payload-B
```

when the human requirement is closer to:

```
when environment A:
  check A
otherwise:
  check B
```

This matters to both:

1. 0.3.0 conditional/applicability design; and
2. the research-only Ansible-inspired authoring prototype.

## Representative production census

Pinned NIWC revision:

`8c8e5dff860af6b1290ee9273a282db24278f8d5`

Packages measured:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025
- Solaris 11 x86
- Windows Server DNS
- Apache 2.4 UNIX Server

Total automated OVAL-backed Rules: **1,537**.

Workflow:
https://github.com/vanderpol/scap-ng/actions/runs/37535531157

### Structural counts

| Shape | Rules | Percent |
| --- | ---: | ---: |
| Any OR criteria | 194 | 12.7% |
| Nested criteria | 114 | 7.4% |
| OR whose children are AND branches | 29 | 1.9% |
| Strict same-guard positive/negative binary branch | 9 | 0.6% |
| OVAL `applicability_check=true` observed | 0 | 0.0% |

The absence of `applicability_check` in this representative DISA/NIWC sample
is notable: production content is encoding many environment choices as ordinary
Boolean criteria rather than using OVAL's explicit applicability marker.

## Manual review of the 29 OR-of-AND branch Rules

### Clear environment/requirement conditionals — 19

These are naturally read as a branch selected by target state/configuration.

- RHEL 9: SV-258004 — whether `sshd_config.d` is included determines which
  effective KerberosAuthentication check applies.
- Oracle Linux 9: analogous KerberosAuthentication Rule.
- Windows 11: SV-253260 — BitLocker startup/PIN policy branch.
- Windows 11: SV-253340, SV-253341, SV-253342 — event-log path form determines
  which ACL/path check applies.
- Windows 11: SV-253491, SV-253494 — domain member versus standalone user-right
  requirements.
- Windows Server 2025: SV-278001 — Domain Controller versus non-DC registry
  permission expectation.
- Windows Server 2025: SV-278004, SV-278005 — server role determines local
  versus domain-account requirement.
- Windows Server 2025: SV-278043, SV-278044, SV-278045 — event-log path form.
- Windows Server 2025: SV-278184, SV-278185, SV-278187, SV-278188 — domain
  member versus standalone user-right requirements.
- Windows Server DNS: SV-259341 — forwarder presence determines the allowed
  recursion state.

### Windows Server role/domain proof update

The current generic enum-guard recognizer now covers all six Server 2025
role/domain user-right fixtures in the focused production matrix:

- SV-278004
- SV-278005
- SV-278184
- SV-278185
- SV-278187
- SV-278188

SV-278184 and SV-278185 exposed a stale workflow expectation rather than a
recognizer gap. Their source guards compare the same WMI `domainrole` field
against disjoint values. Because the value sets are not exhaustive, the
rewritten else branch retains the second guard instead of treating "not the
first role" as automatically meaning "the second role".

The existing overlap/existence refusal tests remain the boundary: overlapping
enum sets or non-positive guard existence are not rewritten.

### Alternative compliance paths — 8

These should remain ordinary `any` / alternatives rather than being forced
into if/else.

RHEL 9 and Oracle Linux 9 each contain four module-disable Rules where either
the `/etc/modprobe.d` pair or the legacy `/etc/modprobe.conf` pair satisfies
the requirement:

- ATM
- FireWire
- SCTP
- cramfs

The branches represent alternative evidence/configuration locations, not a
single guard choosing exactly one applicable expectation.

### Requires deeper review — 2

RHEL 9 and Oracle Linux 9 sudo invoking-user-password Rules combine direct
`/etc/sudoers` settings with an included `/etc/sudoers.d` path. The source
tree is branch-shaped but the effective sudoers precedence/include semantics
make a simple procedural if/else interpretation unsafe without a dedicated
semantic review.

## Six-state warning

A strict Boolean source shape:

```
OR(
  AND(G, P),
  AND(NOT G, Q)
)
```

is **not generally equivalent** to a procedural conditional whose semantics are:

```
if G == true:  result = P
if G == false: result = Q
otherwise:     propagate G
```

Using the project's pinned OVAL truth-table implementation, the generic
three-input space contains **216** combinations:

- 135 produce the same outcome;
- **81 differ**.

Therefore the structural candidates above are **human-authoring candidates, not
automatic converter rewrites**.

The mismatch is especially important around `not_applicable`,
`not_evaluated`, `unknown`, and `error`, where OVAL AND/OR aggregation can
mask or transform a branch outcome differently from procedural branch
selection.

## Applicability-scoped branch experiment

A second natural rendering is to make each simple Test/check applicable only
under its branch condition and combine the branch checks with `any`:

```yaml
check:
  any:
    - when: domain_controller
      registry: ...
      expect: ...

    - when:
        not: domain_controller
      registry: ...
      expect: ...
```

Conceptually this is very attractive for the Ansible-inspired authoring layer,
and may be preferable to a visibly procedural `if/then/else`.

However, with the current intrinsic-applicability rule that a false guard yields
`not_applicable`, this form has the **same 135/216 generic equivalence result**
as procedural if/else when compared with the source OVAL formula
`OR(AND(G,P),AND(NOT G,Q))`. It therefore is not a generally lossless
mechanical rewrite either.

If guard and branch outcomes are restricted to ordinary Boolean
`true/false`, all 8 possible combinations are equivalent. The problem begins
when real scanner outcomes include `error`, `unknown`, `not_evaluated`, or
`not_applicable`.

This suggests a useful separation:

- **native authoring:** applicability-scoped checks may be an excellent simple
  surface if their six-state behavior is explicitly defined;
- **legacy conversion:** preserve the OVAL Boolean graph unless a specific
  equivalence condition is proven, or define the research `case/when` syntax
  as exact desugaring to that graph rather than procedural branch selection.

## Design implication

There may be two different concepts hiding under the word "conditional":

1. **Procedural/selective conditional** — evaluate a guard, select one branch,
   propagate non-Boolean guard outcomes. This is the existing experimental
   `if/then/else` direction.
2. **Declarative case/variant shorthand** — a human-readable syntax that
   desugars to the original Boolean expression and therefore retains its
   six-state aggregation semantics.

Those should not be conflated.

For new native content, a procedural conditional may be exactly what authors
want. For lossless migration of an existing OVAL branch tree, a declarative
`case/when` form defined by explicit desugaring may be safer if we decide the
readability improvement is worth adding another surface form.

## Next research

1. Render the 19 clear conditional Rules side-by-side as OVAL criteria, current
   NG evaluate, and research-only case/when syntax.
2. Determine whether each guard is best understood as:
   - intrinsic Assessment applicability;
   - local branch selection;
   - target-role/inventory selection; or
   - organizational-input-dependent selection.
3. Prove six-state semantics for any proposed desugaring before converter use.
4. Keep the eight alternative-compliance Rules as `any` examples to prevent
   overuse of conditional syntax.
5. Revisit the two sudo Rules only after modeling sudo include/precedence
   semantics.
