# SCAP 1.4 → SCAP-NG 0.2.0: key changes

**Status:** concise OVAL Board briefing for the frozen 0.2.0 working design. Nothing here implies Board approval.

SCAP-NG is intended to preserve useful SCAP 1.4 and OVAL assessment semantics while replacing legacy serialization, packaging, result, and authoring constraints.

## Key changes

- **Benchmark → Rule → Assessment.** A Rule owns the requirement, policy metadata, applicability references, and named Assessment choices/default. An Assessment owns how the requirement is evaluated. There is **no separate Policy object** in the current design.

- **Preserve OVAL meaning, not OVAL XML structure.** Used, non-deprecated semantics are retained; XML type hierarchies, serialization workarounds, hidden defaults, and wrapper structure are not automatically carried forward.

- **Recognizable OVAL vocabulary remains.** Native automated content uses **Test, Object, State, Variable, and Item**. `evaluate` replaces OVAL `criteria/criterion`. Typed titles replace generic OVAL `comment` metadata.

- **Objects and collection are distinct.** Objects describe resource selection/acquisition. Collection is the runtime act of evaluating an Object and producing Items plus status/completeness.

- **Native Tests can use the natural source directly.** NG does not require an Object wrapper when the semantic source is another first-class node, such as a Variable.

- **Shared primitives replace duplicated schema mechanics.** Comparison, quantifiers, existence/cardinality, datatypes, records, Sets, Filters, and traversal behavior are defined consistently across capabilities.

- **Capability names can be cleaner.** Source OVAL IDs remain in provenance, while reviewed NG names may remove obsolete historical suffixes when semantics justify it. Example: supported `wmi57_test` maps to `windows.wmi.query`.

- **Deprecated OVAL Tests are conversion blockers.** They are not copied into NG as runtime `deprecated` flags. Later authoritative reinstatements can be recorded explicitly.

- **OVAL 5.12.3 is the current semantic baseline.** Later corrections/reinstatements are reviewed explicitly. OVAL 6 is used mainly to identify genuinely new Test semantics rather than as an automatic wholesale replacement.

- **Source defects are not silently repaired.** Invalid or contradictory source content is quarantined/reported. Migration and semantic remediation are separate review actions.

- **Applicability is explicit content, not scanner magic.** CPE/platform names may describe targets, but executable applicability is represented by authored assessment logic. Hidden OS/domain-role inference is not assumed.

- **Conditional execution preserves the full result domain.** Source-authored conditional behavior may schedule Assessments lazily, but existing Boolean OVAL structures are not automatically rewritten into conditionals because that can change error/unknown/not-applicable and evidence behavior.

- **Manual assessment is first-class.** Human procedures, manual outcomes, comments/evidence, and workflow state are modeled intentionally alongside automation.

- **Profiles, Tailoring, and Organizational Input are separated.** Publisher Profiles are subtractive. Tailoring can enable/disable existing Rules and choose published Assessment choices; it does not silently replace implementations or publisher Parameter values. Delegated values use typed Organizational Input.

- **Rule policy truth and Assessment technical truth are separate.** Informational/reporting-only policy remains a Rule concern rather than being forced into Assessment outcome semantics.

- **Results are redesigned instead of reproducing ARF.** Results link Rule context to distinct Assessment executions and local Test/Object/Variable/Item evidence. They retain execution identity, provenance, completeness, and reasons for outcomes.

- **Evidence can be bounded without changing the verdict.** Evidence caps/early termination may limit output volume, but completeness/truncation must be explicit and must not imply every matching/failing Item was enumerated.

- **Migration provenance is outside executable native content.** Source IDs, conversion diagnostics, parity traces, skipped defects, and legacy graph evidence are separate artifacts; native content does not require them to execute.

- **Compiled distribution is manifest-based and self-contained.** The working direction is a deterministic `.scapng` ZIP whose manifest binds logical objects; archive paths are storage details, not semantic identity.

- **Stable logical identity is separate from filenames.** IDs and revisions are explicit, meaningful, and intended to survive packaging or directory changes.

- **Publisher extensions are isolated.** Vendor/publisher-specific content is not allowed to silently redefine core semantics.

- **Forward conversion from SCAP 1.4 is a core requirement.** Supported conversion must account for policy, applicability, selectors, defaults, Variables, Sets, Filters, dependencies, datatypes, and evidence-relevant behavior. Unsupported paths must be explicit.

- **Conformance requires more than schema validation.** Structural validation, semantic validation, known-result evaluation, collection/acquisition conformance, live-target behavior, and migration equivalence are separate evidence layers.

## What is ready for Board review

The frozen 0.2.0 schema baseline is accompanied by six small converter-produced review cases under [review-content/0.2.0](review-content/0.2.0/): family, UNIX file, Windows registry, directory filter, Windows WMI process query, and symlink resolution. Four earlier native/manual examples remain supporting examples rather than being claimed as converter successes.

These samples preserve source provenance, independently stated expected outcomes, meaningful IDs, and strict 0.2.0 validation. They are **pending human review**, not Board-approved conformance content.

## What we need from the OVAL Board

- Review the six small source-to-NG examples for semantic fidelity and readability.
- Confirm whether OVAL 5.12.3 plus explicitly reviewed later fixes/reinstatements is a reasonable baseline.
- Identify any non-deprecated Test/Object/State/Variable semantics that NG has unintentionally omitted or changed.
- Confirm or challenge the proposed handling of deprecated Tests and later reinstatements.
- Review native capability naming where historical numeric/version suffixes are removed but source identity remains in provenance.
- Advise on genuinely new OVAL 6 Test semantics, especially deferred ESX/VMware work and any known 5.12.3 errata.
- Review applicability, record/entity, existence/cardinality, Variable/Set/Filter, and six-state result behavior for interoperability concerns.
- Review the separation of policy, Assessment execution, collected evidence, and Results.
- Ratify, reject, or revise the narrow proposals that affect OVAL semantics; published proposal text should not be silently rewritten after voting begins.
- Tell us where OVAL governance should own a rule versus where SCAP-NG should define a migration/native-language rule.

## What happens next

After the six-case human review gate:

1. **Fix only demonstrated defects first.** Any issue becomes a small permanent reproducer and regression before broader changes.
2. **Expand the conformance corpus.** Add more Self-Assertion coverage and representative RHEL, Windows, DNS, Apache, and other content only after the small examples are accepted.
3. **Close known converter gaps.** Direct Variable Tests, more complex Object-component/function chains, Sets/Filters, and other valid OVAL patterns are next priorities.
4. **Increase independent runtime evidence.** Add collector/live-target and differential/reference-scanner testing so conversion and schema checks are not the only evidence.
5. **Build the editor from accepted native content.** The editor should follow the stabilized language rather than drive its semantics.
6. **Harden packaging/results.** Continue manifest, signing/trust, privacy, evidence-volume, and enterprise-scale work without changing assessment truth semantics.
7. **Prepare the standards path.** Once semantics and conformance evidence are stable, consolidate normative language, terminology, crosswalks, and Board decisions into a specification suitable for broader SCAP/NIST discussion.

Until that review occurs, 0.2.0 remains a tested working draft, not a finished standard.
