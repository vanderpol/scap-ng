# Research experiment: affirmative existence instead of if_empty

**17 October 2026; not adopted and not valid under the existing prototype validator.** Tests a narrower claim raised by Gemini and ChatGPT first reads: an auditor should express whether a resource must exist, not hand-program what happens if an iterator is empty.

## Pair 1: required resource population

~~~yaml
id: home-mount-native
require:
  each: linux.mounts
  where:
    mount_point: {equals: /home}
  minimum_resources: 1
  must:
    mount_options: {contains: nosuid}
~~~

**Intended semantics:** the scanner must establish at least one **selected** mount after where, and **every** selected mount must contain nosuid. This intentionally counts selected mounts rather than only compliant mounts. Does not silently enforce exactly one.

## Pair 2: population is optional, property is not

~~~yaml
id: guest-accounts-native
require:
  each: windows.accounts
  where:
    category: {equals: guest}
  must:
    enabled: {equals: false}
~~~

**Intended semantics:** all existing selected guest accounts must be disabled. A **verified complete** selection with zero guests passes. This is a deliberately different policy from requiring at least one guest account. The word each means existing members only; it is not a guarantee of resource existence.

## Is this actually better?

- It removes if_empty: fail/pass boilerplate, while allowing a positive declaration of required resources when applicable.
- The separation between **which resources must exist** and **which existing resources must comply** remains explicit for the author and compiler.
- It still requires formal semantics for collection incompleteness and unreadable selectors; minimum_resources is not computed by counting only known matches when other records could match.
- It may read worse than a typed named **singleton** such as a required mount-at-/home resource. There is no winner yet.
- A new auditor may not guess the verified-empty behavior from each alone. This needs cold reading without result-laden headings.
- It still reveals logical quantification and selection. If a user cannot reliably predict it, prefer a more sentence-shaped resource DSL or editor-authored structured AST, not another word swap.

## Counterexample matrix: desired new-policy outcomes only (not original OVAL parity)

| Evidence state | Required mount policy | Optional guest policy |
| --- | --- | --- |
| Complete with zero selected resources | Fail | Pass |
| Complete, one compliant selected resource | Pass | Pass |
| Complete, two selected and one violates must | Fail | Fail |
| Incomplete and zero observed selected | Not established; must not conclude from zero | Not established; cannot safely declare Pass |
| Complete plus unreadable selector on possible candidate | Requires error/unknown provider state | Requires error/unknown provider state |
| Complete with a known-absent requirement field | Needs typed-field absence policy | Needs typed-field absence policy |
| Incomplete with one observed violation | Need documented decisive-outcome algorithm | Need documented decisive-outcome algorithm |

These are **intended native policy statements**, not actual scanner results. Full original SCAP 1.4/OVAL compatibility remains to be tested independently.

## Explicit alternative: resource-level existence verb

For a well-identified singleton source, another candidate is:

~~~yaml
id: home-mount-singleton
require:
  mount:
    at: /home
    must:
      options: {contains: nosuid}
~~~

The strong advantage is authorability; the serious risk is hiding resource identity/cardinality and inability to express multiple mount namespaces. The editor could show these decisions explicitly while a typed provider contract remains inspectable.

## Next trial

Show Pair 1, Pair 2 and the singleton to a genuinely unfamiliar auditor **without** headings saying required/optional or outcome answers. Ask for exact complete-zero, two Items/one violates, unreadable selector and incomplete outcomes. Require authors to write one adjacent rule. Prefer the representation with fewer **wrong confident answers**, not fewest YAML lines.
