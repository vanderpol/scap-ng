# SCAP 1.4 → SCAP-NG 0.2.0: key changes

**Status:** concise OVAL Board briefing for the frozen 0.2.0 working design. Nothing here implies Board approval.

SCAP-NG is intended to preserve useful SCAP 1.4 and OVAL assessment semantics while replacing legacy serialization, packaging, result, and authoring constraints.

## Key changes

- **Assessments are small, standalone files instead of one monolithic checking document.** Each automated Assessment is independently valid and executable, which makes checks easier to author, review, test, reuse, and load only when needed. Reuse does **not** require rebuilding a giant shared OVAL document: common Assessments can be referenced as dependencies, and scanners may reuse compatible Collection Results/Items that were already collected rather than collect the same target data again. Reused collection data retains its original execution provenance, status, and completeness so efficiency does not change assessment truth.

- **Conditional assessment logic is now explicit.** Native `evaluate` expressions support `if / then / else`. Only the selected branch is evaluated, allowing authors to express cases such as “if this role or condition applies, perform check A; otherwise perform check B” without encoding the behavior as an opaque Boolean workaround. Conditional execution preserves the full result domain rather than treating errors, unknowns, or not-applicable states as simple false values. Existing OVAL `AND`/`OR` trees are **not** automatically converted to conditionals unless the source semantics actually require conditional execution.

- **Organizational Input replaces the practical need for unused interactive-variable behavior.** A publisher can deliberately leave a typed policy Parameter unresolved when the correct value must come from the deploying organization, site, mission owner, or system owner—for example an organization-approved timeout or required server list. The supplied value is validated, resolved before normal Assessment execution, and can carry authority/provenance information. Organizational Input is **not Tailoring**, does not make a Rule “tailored,” and cannot change which Tests run, inject commands, or alter executable control flow.

- **NG Benchmarks are not a one-for-one copy of XCCDF.** XCCDF concepts that are used by real content or are necessary to preserve policy semantics are carried forward in cleaner native forms. Features, wrappers, indirections, and serialization mechanics that were unused and provided no required semantic behavior were intentionally not reproduced merely for structural compatibility. Migration tooling records source provenance and reports unsupported or omitted semantics rather than forcing obsolete XCCDF structure into native NG Benchmarks.

- **The SCAP 1.4 source datastream is replaced by a simple native package.** Authors work with ordinary SCAP-NG source files—such as a Benchmark, Rules, applicability, Profiles, and standalone Assessments—rather than assembling XCCDF, OVAL, dictionaries, components, component references, and catalog indirection into a source datastream. For distribution, those native files are compiled into a deterministic `.scapng` ZIP with a manifest that identifies and integrity-binds the package contents. Logical IDs and references carry meaning; archive paths are only storage details. This keeps the useful idea of shipping a self-contained security-content package while removing the datastream's XML container and cross-component wiring complexity.

- **Profiles are subtractive and much smaller.** Every Rule that belongs to a Benchmark is enabled by default. A publisher Profile records only the Rules it disables, plus permitted publisher Parameter values, rather than repeating a large list of Rules that are already enabled. Profile inheritance remains monotonic: child Profiles can disable additional Rules but do not silently re-enable parent exclusions. Local Tailoring remains separate and can explicitly enable or disable existing Benchmark Rules when an organization intentionally departs from publisher policy.

- **Benchmark → Rule → Assessment.** A Rule owns the requirement, policy metadata, applicability references, and named Assessment choices/default. An Assessment owns how the requirement is evaluated. There is **no separate Policy object** in the current design.

- **No hidden semantic defaults.** SCAP-NG requires behavior that affects collection, evaluation, reporting, or results to be visible in authored content. Authors must explicitly state choices such as reporting selection rather than relying on omission to mean a default value, and schemas must reject content when a required semantic choice is absent. This is a deliberate change from SCAP 1.4/OVAL patterns where schema or specification defaults could make effective behavior less obvious from the content itself.

- **Preserve OVAL meaning, not OVAL XML structure.** Used, non-deprecated semantics are retained; XML type hierarchies, serialization workarounds, implicit/defaulted serialization behavior, and wrapper structure are not automatically carried forward.

- **Recognizable OVAL vocabulary remains.** Native automated content uses **Test, Object, State, Variable, and Item**. `evaluate` replaces OVAL `criteria/criterion`. Typed titles replace generic OVAL `comment` metadata.

- **Objects and collection are distinct.** Objects describe resource selection/acquisition. Collection is the runtime act of evaluating an Object and producing Items plus status/completeness.

- **Native Tests can use the natural source directly.** NG does not require an Object wrapper when the semantic source is another first-class node, such as a Variable.

- **Shared primitives replace duplicated schema mechanics.** Comparison, quantifiers, existence/cardinality, datatypes, records, Sets, Filters, and traversal behavior are defined consistently across capabilities.

- **Capability names can be cleaner.** Source OVAL IDs remain in provenance, while reviewed NG names may remove obsolete historical suffixes when semantics justify it. Example: supported `wmi57_test` maps to `windows.wmi.query`.

- **Deprecated OVAL Tests are conversion blockers.** They are not copied into NG as runtime `deprecated` flags. Later authoritative reinstatements can be recorded explicitly.

- **OVAL 5.12.3 is the current semantic baseline.** Later corrections/reinstatements are reviewed explicitly. OVAL 6 is used mainly to identify genuinely new Test semantics rather than as an automatic wholesale replacement.

- **Source defects are not silently repaired.** Invalid or contradictory source content is quarantined/reported. Migration and semantic remediation are separate review actions.

- **Applicability is explicit content, not scanner magic.** CPE/platform names may describe targets, but executable applicability is represented by authored assessment logic. Hidden OS/domain-role inference is not assumed.

- **Manual assessment is first-class.** Human procedures, manual outcomes, comments/evidence, and workflow state are modeled intentionally alongside automation.

- **Profiles, Tailoring, Parameters, and Organizational Input have separate jobs.** Profiles express publisher-defined variations; Tailoring records deliberate local policy changes; Parameters carry typed policy data; Organizational Input resolves publisher-delegated values. These mechanisms are not interchangeable.

- **Rule policy truth and Assessment technical truth are separate.** Informational/reporting-only policy remains a Rule concern rather than being forced into Assessment outcome semantics.

- **Results are redesigned instead of reproducing ARF.** Benchmark Results provide compact Rule Results and precomputed summary counters; detailed Assessment Results retain the execution/evidence graph. See **Results: less volume, more useful information** below.

- **Evidence can be bounded without changing the verdict.** A scanner may retain only a configured maximum number of evidence samples while explicitly reporting observed failures, returned samples, truncation, stop reason, and whether the total population is known.

- **Migration provenance is outside executable native content.** Source IDs, conversion diagnostics, parity traces, skipped defects, and legacy graph evidence are separate artifacts; native content does not require them to execute.

- **Compiled distribution is manifest-based and self-contained.** The working direction is a deterministic `.scapng` ZIP whose manifest binds logical objects; archive paths are storage details, not semantic identity.

- **Stable logical identity is separate from filenames.** IDs and revisions are explicit, meaningful, and intended to survive packaging or directory changes.

- **Publisher extensions are isolated.** Vendor/publisher-specific content is not allowed to silently redefine core semantics.

- **Forward conversion is lossless in semantics, not literal serialization.** Supported SCAP 1.4 conversion must preserve effective policy, applicability, selectors, defaults, Variables, Sets, Filters, dependencies, datatypes, result behavior, evidence-relevant behavior, and source provenance. NG may normalize the representation—for example, multiple source Rules that resolve to the same exact Assessment semantics may reference one shared Assessment instead of carrying duplicate Assessment definitions. That deduplication is permitted only when semantic equivalence is proven; every original Rule/check binding remains represented. Unsupported or non-lossless paths must be explicit blockers rather than guessed conversions.

- **Conformance requires more than schema validation.** Structural validation, semantic validation, known-result evaluation, collection/acquisition conformance, live-target behavior, and migration equivalence are separate evidence layers.

## Results: less volume, more useful information

SCAP-NG does **not** carry forward ARF/OVAL Results as-is. The result redesign is a major part of the NG proposal, because SCAP 1.4 results can be simultaneously **very large** and **hard to consume**.

### What is difficult about SCAP 1.4 results

In SCAP 1.4, useful policy context, OVAL execution detail, system-characteristic data, result directives, and reporting wrappers are spread across several related structures. Large assessments can repeat substantial context and can emit very large collections of system-characteristic Items even when a small number of concrete examples are sufficient to explain the result.

For common consumers—dashboards, APIs, SIEMs, compliance summaries, and human reviewers—SCAP 1.4 also does not provide the compact policy-facing summary that is usually wanted first. Consumers often have to walk the result hierarchy and reconstruct basic information such as pass/fail counts, the effective check, which concrete value caused a failure, and whether the scanner stopped collecting after the answer was already known.

The result can therefore be **high-volume but low-convenience**: a great deal of serialized execution data, while ordinary questions still require significant post-processing.

### What NG changes

NG separates **policy-facing results** from **detailed Assessment execution evidence**.

A Benchmark Result contains compact Rule Results plus a required precomputed `summary`. Detailed Test/Object/State/Variable/Item evidence lives in referenced Assessment Results instead of being duplicated into every policy-facing Rule Result.

A current 0.2.0 Benchmark summary looks like:

```json
"summary": {
  "total": 253,
  "pass": 219,
  "fail": 21,
  "not_applicable": 8,
  "not_evaluated": 2,
  "error": 1,
  "unknown": 2
}
```

This lets a scanner, API, dashboard, or SIEM consumer answer the first operational question—**“what happened?”**—without rereading every Rule Result just to compute totals.

Each Rule Result then carries a compact, self-describing policy-facing record such as:

```json
{
  "rule_id": "SV-257777r1045123_rule",
  "outcome": "fail",
  "message": "Observed mode 0666; expected 0644.",
  "reason": {
    "code": "value_mismatch"
  },
  "instances": [
    {
      "id": "instance-1",
      "outcome": "fail",
      "assessment_result_ref": "assessment-execution-42"
    }
  ]
}
```

The detailed Assessment Result retains the execution graph and concrete evidence needed to explain **why** the Rule failed.

### Bounded evidence instead of unlimited result growth

NG also makes evidence retention an explicit first-class concept.

A check may encounter thousands or millions of failing Items. Returning every one can make result packages enormous without improving the verdict. NG allows the scanner to retain a bounded number of representative evidence records while preserving the technical result and explicitly stating what was and was not fully evaluated.

The current 0.2.0 `evidence_summary` shape is:

```json
"evidence_summary": {
  "observed_failures": 10000,
  "actual_failures": "unknown",
  "maximum": 50,
  "returned": 50,
  "truncated_population": true,
  "stop_reason": "evidence_maximum_reached"
}
```

The important distinction is:

- `maximum` — the configured maximum number of evidence samples retained;
- `returned` — how many evidence records are actually present;
- `observed_failures` — failures actually seen before evaluation stopped;
- `actual_failures` — the true total when known, otherwise explicitly `"unknown"`;
- `truncated_population` — whether the scanner stopped before exhausting the population;
- `stop_reason` — why collection/evidence generation stopped.

The Assessment Result separately records:

- `logical_complete` — enough evaluation occurred to determine the technical truth;
- `population_complete` — the full target population was examined;
- `evidence_complete` — all evidence that would otherwise have been retained is present.

This means a scanner can truthfully say:

> **The requirement failed. We observed at least 10,000 failures, retained the first 50 examples, and stopped because the evidence cap was reached. The final population size is unknown.**

That is substantially more useful than either dumping millions of records or silently truncating output.

### More value in a smaller result

The NG result model is intended to reduce volume **without throwing away explanation**:

- Benchmark-level counters are precomputed.
- Rule Results carry deterministic human-readable messages and machine-readable reason codes.
- Detailed Assessment Results retain the technical evidence needed to reconstruct the decision.
- Repeated run/target/Benchmark context is normalized rather than copied into every low-level record.
- Evidence can be capped independently from assessment truth.
- Redaction can suppress sensitive values without changing the comparison result.
- Reporting projection can retain only fields useful to the consumer while canonical evidence remains authoritative.
- Completeness flags make early termination and truncation explicit.
- Result-instance identity preserves multiple Assessment invocations without relying on array position or legacy `variable_instance` numbering.

The goal is therefore not merely **smaller results**. It is **smaller, more directly useful, more explainable results**.

For the current normative draft, see [Results and Evidence](../specification/results/results.md), [Benchmark Result schema](../schema/v0.2.0/benchmark-result.schema.json), [Assessment Result schema](../schema/v0.2.0/assessment-result.schema.json), and [shared bounded-evidence type](../schema/v0.2.0/result-types.schema.json).

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
