# Optional automatic Benchmark grouping

**Change:** Conversion tools now leave inferred Benchmark grouping disabled by default and expose an explicit `--auto-map-groups` option. When enabled, only Rules matching a high-confidence functional topic are grouped; uncertain Rules remain ungrouped.

**Reason:** Faithful SCAP/XCCDF or STIG-manual migration should preserve source semantics without inventing editorial taxonomy. Grouping is useful for human navigation, but it is an optional normalization step rather than a prerequisite for valid native content.

**Before:** The current SCAP 1.4 full-review converter unconditionally generated heuristic Groups and forced unmatched Rules into a `needs-grouping` bucket. The standalone STIG-manual converter emitted no inferred Groups.

**After:** Both current SCAP 1.4 conversion and standalone STIG-manual conversion default to no inferred Group taxonomy. `--auto-map-groups` opts into the existing high-confidence functional heuristic. Unmatched Rules are left ungrouped. The NIWC current-review wrapper forwards the same option.

**Semantic effect:** Group membership remains navigation/editorial metadata. Grouped Rules SHALL resolve to Benchmark Rule identities and SHALL NOT appear in multiple Groups. A Benchmark Rule is not required to belong to a Group. Automatic grouping SHALL NOT change applicability, selection, Assessment behavior, Parameters, scoring, remediation, or results.

**Compatibility:** Existing native content with complete Group coverage remains valid. Conversion output changes only when rerun: default fresh conversion is now ungrouped unless the caller explicitly requests automatic grouping. Existing historical generated review artifacts are not rewritten.

**Source evidence:** Project-owner decision in the 2026-10-06 SCAP-NG design discussion: automatic grouping should be available as an optional conversion parameter and default off. Existing iteration-003 heuristic grouping code supplies the initial topic classifier.

**Alternatives considered:**
- Preserve unconditional heuristic grouping — rejected because it mixes editorial inference into faithful conversion.
- Force uncertain Rules into `needs-grouping` — rejected because absence of a confident taxonomy is better represented as ungrouped.
- Require all native Rules to be grouped — rejected because Group membership is organizational rather than execution-critical.

**Tests:** Focused STIG-manual conversion verifies default `groups: []` and opt-in mapping. Native package-graph tests verify partial/no Group coverage is valid, while duplicate and unknown Rule membership remain errors.

**Machine evidence:** Focused STIG-manual workflow passed on branch head lineage: https://github.com/vanderpol/scap-ng/actions/runs/37465029661 . The PR broad regression gates remain the pre-merge integration evidence.

**Human status:** accepted

**Reviewer/date:** Project owner / 2026-10-06
