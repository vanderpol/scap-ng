# Research: test / check and collection / object terminology

**Status:** Candidate design, NON-NORMATIVE, not approved by the OVAL Board.  
**Trigger:** Reviewer found a v003 assessment with `checks:`, `test_title`, `capability`, `collect:`, `object_title`, `assert:`, with no clear distinction between inherited SCAP 1.4 words and native NG semantics.

## Observed implementation (do not overwrite existing source until approved)

- The current RHEL9 upconverter emits `assessment.checks[ID]` with `test_title` and a test-level `capability`, `collect` with `object_title` and a separate collection-level `capability`, and `assert` with Test existence, cardinality, states and their capabilities.
- The round-trip OVAL emitter uses the check-level `capability` to choose the original Test XML QName, and the collection-level capability to choose the Object QName. Test and Object can require different families. Silently eliminating either value is **not lossless**.
- Policy already has *named check selectors*; using `checks` to mean an OVAL-like Test graph inside an Assessment makes `check` ambiguous.
- This is a source-naming concern with possible scanner schema and compatibility implications, NOT an authorization to change normative vocabulary.

## Candidate separation

| Role | Candidate native word | Historical SCAP analogue |
| --- | --- | --- |
| Policy's named implementation choice | **check selection** | XCCDF check selector |
| Automated executable/evaluation node | **test** | OVAL Test |
| Evidence acquisition/selection | **collection** | OVAL Object |
| Evaluation of observations | **assertion** | OVAL State plus Test item/existence semantics |
| Typed supplied/derived value | **variable** | OVAL Variable |
| Reusable inspection/evaluation interface | **capability** | OVAL Test, Object or State family/interface depending on context |

Candidate source model:
```yaml
assessment:
  tests:
    gpgcheck-enabled:
      test_title: Check gpgcheck is enabled
      capability: independent.textfilecontent54 # TEST / result semantics
      collection:
        collection_title: Read dnf.conf
        capability: independent.textfilecontent54 # EVIDENCE collection semantics
        select:
          filepath: /etc/dnf/dnf.conf
      assertion:
        existence: at_least_one_exists # collection-to-test cardinality
        check: all                    # OVAL item/result quantifier; consider clearer key later
        state:
          field: subexpression
          operation: equals
          datatype: string
          value: "1"
```
This is illustrative and not yet schema-valid. `assertion.check` is a third use of the English word `check`, but is a distinct **quantifier**; a separate sub-question should consider the key `item_quantifier` or `item_check` without silently changing its values.

## Evaluation capability: keep or infer?

**Candidate starting rule:** retain explicit Test-level capability and collection-level capability; validate the pairing against a declared compatibility matrix. A Test capability is not necessarily an additional collector: it can identify which item/result evaluation interface and OVAL Test family applies, even when the collection is a different source Object type. State capability may also differ and must be retained when relevant.

An authoring editor MAY offer a presentation that *looks* less repetitive, but a compiler must fill an unambiguous canonical representation, produce diagnostics, and not rely on scanner magic/defaults. Do not eliminate Test capability until a pinned full-corpus scan verifies it can always be reconstructed without extra semantics; OVAL tests with no object (e.g., `unknown_test`) provide a counterexample to naive derivation.

## Preconditions for a decision and migration

1. Inventory actual RHEL9, Win11 and Self-Assertion Test/Object/State capability triples and count equality vs mismatch, including tests without objects and cross-family references.
2. Produce examples showing identical source meaning before/after field changes, with **independently validated** expected results, OVAL reverse reconstruction and parser/assessment schema validity.
3. Cover named policy check selectors, manual alternatives, applicability, recursive sets, variables and multi-State evaluation.
4. Define an exact versioned schema migration or authoring alias mechanism (old `checks/collect/assert/object_title` versus new `tests/collection/assertion/collection_title`) with diagnostic rejection of ambiguous mixed formats; don't accept both silently.
5. Keep source readability and reviewer-first title/capability ordering. Explicit semantic defaults stay explicit.
6. Do not regenerate all native benchmarks until a decision is approved and the tests pass. Treat this file as Board discussion material, not as a vote.

## Preliminary distinction

A clean semantic model need not expose OVAL XML's **Object** type as a top-level native file. The term **collection** describes the acquisition operation more plainly. The native **Test** remains the smallest evaluation node, distinct from a Rule selecting a **check** through Policy.

**Decision required later:** Confirm native words and whether the Test capability is mandatory in authored source, mandatory only in canonical compiled JSON, or safely derived through a proven capability contract. No normative change authorized here.


## Pinned Test/Object/State evidence (2026-09-30)

[Successful audit run](https://github.com/vanderpol/scap-ng/actions/runs/36747126738), using OVAL 5.12.3 upstream schemas and NIWC source pin `8c8e5dff860af6b1290ee9273a282db24278f8d5`, found across RHEL 9 and Windows 11:
- 1,026 Tests; 1,026 direct Object references; 797 direct State references.
- **Zero** mismatched Test/Object/State qualified types, missing direct reference targets or duplicate component IDs.
- 251 of the inventory's 258 Test declarations have recognized explicit type-reference Schematron checks. Seven do not: `independent.unknown_test`, `junos.show_test`, `junos.version_test`, `junos.xml_show_test`, `windows.license_test`, `windows.peheader_test`, `windows.systemmetric_test`.
- Upstream Junos `show_test`, `version_test`, and `xml_show_test` have required `object` and optional `state` references of generic reference types. Lack of typed-reference assertions is a candidate *validator coverage gap*, not a demonstrated permission to mix families.

**Provisional inference:** user proposal to declare capability just once at Test level, with Collection and State inheriting their types, is consistent with every tested direct reference and with the typical upstream typed Schematron pattern. The independent unknown Test has no Object and requires a special native result capability, not a duplicate collection capability. This does not yet prove coverage for all 258 Test types, all 65 published source packages or nested set/filter paths.

**Conformance tests needed before adopting as normative:** (1) capability mismatch must fail even if bare XML XSD accepts the references; (2) nested filters and sets must enforce compatible type constraints, potentially with typed collection ancestry beyond a single Test; (3) special no-Object Tests get explicit contracts; (4) reject legacy mismatched source graphs or report them as source defects instead of retagging. Until the tests pass, keep independent Test/Object/State types in Stage-1 conversion data and source provenance to avoid obscuring failures.

The type-count inventory is empirical and *not* an OVAL Board vote. A clearly labeled non-voting Discussion can summarize it after the gap audit closes.


## Candidate replacement for OVAL Test `check`: `state_match`

OVAL 5.12.3 defines Test `check` as the quantifier over collected items
(excluding items whose status is Does Not Exist) that determines how many
items must satisfy the referenced State requirements. It is evaluated only
after the Test `check_existence` requirement is satisfied. When a Test has no
State references, OVAL says `check` has no evaluation meaning.

That exact distinction should be visible in native NG rather than preserved
under the vague word `check`.

Candidate native form:

```yaml
assertion:
  existence: at_least_one_exists
  state_match: all
  state:
    ...
```

Candidate semantics:

- `existence` answers **whether the Collection produced the required set of
  existing observations**. It is evaluated before State matching for the
  purpose of Test truth.
- `state_match` answers **how many existing collected observations must
  satisfy the Test's State requirement(s)**.
- An observation representing a source item with status `does_not_exist`
  SHALL NOT participate in `state_match`; it participates in the existence
  semantics instead.
- If a Test has multiple States, each existing collected observation is
  compared against those States and their per-observation results are first
  combined by `state_operator`. The resulting per-observation result is then
  aggregated by `state_match`.
- If no State is present, `state_match` has no semantic effect. Native NG
  SHOULD avoid requiring a meaningless value in that shape rather than
  copying OVAL's required-but-ignored `check` attribute.
- `state_match` SHALL NOT be confused with State-entity
  `entity_check`, variable `variable_check`, or Policy check selection.
  Those are different quantification scopes.

The exact value vocabulary must preserve OVAL `CheckEnumeration` behavior in
lossless Stage-1 conversion. Friendly value names may be considered separately
only if they map bijectively and retain error/unknown behavior.

This candidate name is intentionally descriptive rather than a one-word
replacement. It remains non-normative until negative/edge-case regressions are
added and the Board accepts the native terminology.
