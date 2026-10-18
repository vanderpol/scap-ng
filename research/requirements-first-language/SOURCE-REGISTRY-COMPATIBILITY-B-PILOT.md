# Source-registry compatibility pilot — 0.4-B research

**Issue #237 · October 2026 · research-only. Not an original SCAP 1.4 parity claim, Windows collector, or scanner bundle.**

The published [six-STIG source registry specimen](contract-candidate/corpus/source-specimens/windows-registry-0-de183f784659.source.yaml), Windows 11 **SV-253291** (Bluetooth), has three source semantics that must not be erased: `existence: one_or_more`, Test `match: one` (exactly **one matching Item**, not exactly one Item), and a State expected value `'0'` (source *text*). Its converted 0.3 source omits `windows_view`; whether that omission preserves the original OVAL default is **not yet established**.

The [strict source lowerer](../../tools/research_b_source_registry_lowering.py) maps only one direct, literal HKLM registry Test with one exact-key/name source Object and one simple typed `value equals` State into **compiler-owned** `compat_oval_registry_view_invariant` IR. More complex Checks, Set/State cardinality, Variables, nonliteral selectors and explicit view metadata are rejected. The main B auditor-authored language is unchanged.

The [offline per-view adapter](../../tools/research_b_source_registry_snapshot.py) retains exact HKLM/key/name/view query identity, status, stable Item ID, original REG_SZ strings, and REG_DWORD/REG_QWORD integers separately. Wrong acquisition identity and unsupported value types fail as errors rather than disappearing as zero Items. It does **not** read Windows hosts or certify collection completeness.

The [fixture evaluator](../../tools/research_b_source_registry_evaluator.py) applies the pinned OVAL Test Item matching/existence result tables **separately** to independently supplied 32-bit and 64-bit snapshots. Because original view semantics remain unresolved, **both** are required for this provisional experiment. Equal results produce a *view-invariant fixture verdict*; conflicting views produce **unknown** (or error if the conflict includes an unsupported/failed collection). This is a conservative research condition, **not a substitute for the original SCAP 1.4 registry_view behavior**.

| Fixture observation | Research outcome for Bluetooth source Test |
| --- | --- |
| Both views contain REG_SZ "0", and no other matching Item | true |
| Each view has two records, one matching "0" and one not | true — one **matching** Item |
| Each view has two matching "0" Items | false — more than one matching Item |
| View 32 matches but view 64 does not | unknown |
| Only one view supplied | unknown |
| Incomplete, only one matching Item observed | unknown |
| Source State expected text "0", but collected Item is numeric REG_DWORD 0 | error — no coercion |
| Source State explicitly integer 0, collected REG_DWORD 0 | true in typed fixture |
| Wrong acquisition identity or duplicate evidence IDs | error |

The [regression tests](../../tools/test_research_b_source_registry.py) pin the above results; [GitHub CI results](contract-candidate/corpus/source-runtime-ci.md) include a source registry test gate. The [six-STIG conversion ledger](contract-candidate/corpus/conversion-progress.md) records *fixture IR lowering* separately from *fully executable scanner-equivalent conversion*. As of the first registry CI pass, 48 distinct automated research lowerings are classified, **zero** original source-equivalent scanner conversions are proven. The latest live ledger takes precedence.

## Work still required

Original immutable SCAP 1.4 source XML needs to be linked to each converted 0.3 Test and evaluated against actual OVAL 5.12.3 source definitions. In particular, determine what `windows_view` and registry Item type/datatype semantics mean on real Windows systems, plus default and redirected view treatment, key access errors, per-Item statuses, multi-string registry values, record fields, case matching, and version operator behavior.

This limited dual-view research proves only that the IR can **represent ambiguity without pretending it does not exist**. A real scanner must implement a validated Windows acquisition adapter and signed compiled-content execution, without introducing two alternative authored languages.

The source patterns to prioritize next are inventoried in the [registry shape census](contract-candidate/corpus/registry-shapes.md) when the six-STIG CI run publishes it. Candidate A remains unchanged; any cross-pollination belongs in [issue #236](https://github.com/vanderpol/scap-ng/issues/236).
