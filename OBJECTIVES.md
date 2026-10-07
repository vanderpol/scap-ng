# Objective-to-issue traceability

The normative project objectives are defined once in
[specification/objectives.md](specification/objectives.md).

This page maps active work to those objectives. It exists to detect two defects:

- a major release issue that advances no stated SCAP-NG objective; or
- a core objective with unfinished work but no issue tracking that work.

## 0.3.0 issue traceability

The GitHub issue is the detailed source for the problem, evidence, alternatives,
and disposition. This table only records which project objective(s) justify the
work. Every open 0.3.0 issue is listed so both directions can be audited.

| Issue | Objective(s) |
| --- | --- |
| [#6 Extract authoritative OVAL assessor semantics](https://github.com/vanderpol/scap-ng/issues/6) | O1, O3, O7 |
| [#7 Full round-trip census](https://github.com/vanderpol/scap-ng/issues/7) | O1, O7 |
| [#9 Preserve effective defaults and explicitness](https://github.com/vanderpol/scap-ng/issues/9) | O1, O3 |
| [#10 OVAL Variable graph / input / function equivalence](https://github.com/vanderpol/scap-ng/issues/10) | O1, O3 |
| [#12 Native Rule/Assessment/applicability contracts](https://github.com/vanderpol/scap-ng/issues/12) | O2, O3, O7 |
| [#20 Manual questions, Organizational Input, Tailoring, provenance](https://github.com/vanderpol/scap-ng/issues/20) | O1, O3, O6 |
| [#22 XCCDF policy/profile/group/selector conversion audit](https://github.com/vanderpol/scap-ng/issues/22) | O1, O6 |
| [#24 Split-source authoring workflow](https://github.com/vanderpol/scap-ng/issues/24) | O2, O8 |
| [#26 Reference evaluator and differential execution](https://github.com/vanderpol/scap-ng/issues/26) | O1, O3, O7, O8 |
| [#27 Reproducible packaging/signature/compatibility](https://github.com/vanderpol/scap-ng/issues/27) | O7, O8 |
| [#28 Governance and open-source readiness](https://github.com/vanderpol/scap-ng/issues/28) | O7 |
| [#29 Enterprise scale/performance/offline gates](https://github.com/vanderpol/scap-ng/issues/29) | O4, O8 |
| [#30 Profile selection vs inherited XCCDF defaults](https://github.com/vanderpol/scap-ng/issues/30) | O1, O3, O6 |
| [#37 Nested-Set validation coverage](https://github.com/vanderpol/scap-ng/issues/37) | O1, O3, O7 |
| [#38 Converter computation budgets/resource diagnostics](https://github.com/vanderpol/scap-ng/issues/38) | O7, O8 |
| [#41 Shared Assessment repository normalization](https://github.com/vanderpol/scap-ng/issues/41) | O2, O4, O8 |
| [#42 Content compiler, bundle builder, signer](https://github.com/vanderpol/scap-ng/issues/42) | O4, O7, O8 |
| [#44 Assessment composition/shared collection reuse](https://github.com/vanderpol/scap-ng/issues/44) | O1, O4, O8 |
| [#47 XCCDF Value / native Parameter decision](https://github.com/vanderpol/scap-ng/issues/47) | O1, O3, O6 |
| [#48 Result ownership/organization/POC metadata](https://github.com/vanderpol/scap-ng/issues/48) | O5, O6 |
| [#49 Implementation guide/worked examples](https://github.com/vanderpol/scap-ng/issues/49) | O2, O7 |
| [#50 Canonical feature corpus with known-good results](https://github.com/vanderpol/scap-ng/issues/50) | O1, O3, O7 |
| [#53 Post-assessment deviations without erasing truth](https://github.com/vanderpol/scap-ng/issues/53) | O3, O5, O6 |
| [#54 Manual Assessment semantics](https://github.com/vanderpol/scap-ng/issues/54) | O5, O6 |
| [#55 Deprecation/removal lifecycle](https://github.com/vanderpol/scap-ng/issues/55) | O7 |
| [#56 Benchmark Result signing](https://github.com/vanderpol/scap-ng/issues/56) | O5, O7, O8 |
| [#116 Upstream OVAL schema/content defects](https://github.com/vanderpol/scap-ng/issues/116) | O1, O7 |
| [#117 Invalid source textfilecontent54 operations](https://github.com/vanderpol/scap-ng/issues/117) | O1, O7 |
| [#118 Redacted Result input bindings](https://github.com/vanderpol/scap-ng/issues/118) | O3, O5 |
| [#119 Manual mode independent of filename](https://github.com/vanderpol/scap-ng/issues/119) | O3, O6, O7 |
| [#120 Subtractive publisher Profile structure](https://github.com/vanderpol/scap-ng/issues/120) | O3, O6 |
| [#121 Ambiguous duplicate manual response values](https://github.com/vanderpol/scap-ng/issues/121) | O3, O6 |
| [#122 Typed DNS acquisition validation](https://github.com/vanderpol/scap-ng/issues/122) | O1, O3, O7 |
| [#123 RHEL 9 xattr audit source coverage](https://github.com/vanderpol/scap-ng/issues/123) | O1, O7 |
| [#125 Content-authored reported_elements](https://github.com/vanderpol/scap-ng/issues/125) | O3, O5 |
| [#128 Complete feature corpus/vendor expected results](https://github.com/vanderpol/scap-ng/issues/128) | O1, O3, O7 |
| [#131 Current coverage/new OVAL 6 tests audit](https://github.com/vanderpol/scap-ng/issues/131) | O1, O7 |
| [#133 Repository cleanup / stale branches](https://github.com/vanderpol/scap-ng/issues/133) | O7 |
| [#137 Upstream Kubernetes Test binding defect](https://github.com/vanderpol/scap-ng/issues/137) | O1, O7 |
| [#151 Assessment IDs and filenames](https://github.com/vanderpol/scap-ng/issues/151) | O2, O7, O8 |
| [#152 Existence vocabulary](https://github.com/vanderpol/scap-ng/issues/152) | O1, O2, O7 |
| [#153 Check/match quantifier vocabulary](https://github.com/vanderpol/scap-ng/issues/153) | O1, O2, O7 |
| [#154 Comparison-operation vocabulary](https://github.com/vanderpol/scap-ng/issues/154) | O1, O2, O7 |
| [#155 Filesystem-scope vocabulary](https://github.com/vanderpol/scap-ng/issues/155) | O1, O2, O7 |
| [#156 Variable-function enumerations](https://github.com/vanderpol/scap-ng/issues/156) | O1, O3, O7 |
| [#157 Prose-only STIG manual conversion](https://github.com/vanderpol/scap-ng/issues/157) | O1, O2, O6 |
| [#158 Human-readable STIG HTML](https://github.com/vanderpol/scap-ng/issues/158) | O2, O6 |
| [#159 Optional HTML/Excel manual-audit outputs](https://github.com/vanderpol/scap-ng/issues/159) | O2, O6 |
| [#164 Bounded foreach modernization](https://github.com/vanderpol/scap-ng/issues/164) | O1, O2 |
| [#165 Consumer-local Object/State scope](https://github.com/vanderpol/scap-ng/issues/165) | O1, O2, O3 |
| [#166 Shared Observation artifacts/typed exports](https://github.com/vanderpol/scap-ng/issues/166) | O1, O2, O4, O8 |
| [#167 Evaluate/criteria composition](https://github.com/vanderpol/scap-ng/issues/167) | O1, O2, O3 |
| [#168 Typed persistent Linux fstab observations](https://github.com/vanderpol/scap-ng/issues/168) | O1, O2, O3, O4 |
| [#169 Named Variable scope](https://github.com/vanderpol/scap-ng/issues/169) | O1, O2, O3 |
| [#170 reported_elements defaults/sensitive fields](https://github.com/vanderpol/scap-ng/issues/170) | O3, O5 |
| [#171 Author/publisher provenance](https://github.com/vanderpol/scap-ng/issues/171) | O3, O7 |
| [#172 Full 65-benchmark modernization census](https://github.com/vanderpol/scap-ng/issues/172) | O1, O2, O4 |
| [#173 Native conditional/case authoring](https://github.com/vanderpol/scap-ng/issues/173) | O1, O2, O3 |
| [#174 0.3 agenda/promotion tracker](https://github.com/vanderpol/scap-ng/issues/174) | O1–O8 |
| [#175 Organizational Input target/instance scoping](https://github.com/vanderpol/scap-ng/issues/175) | O1, O3, O6 |
| [#176 Manual Assessment result attribution](https://github.com/vanderpol/scap-ng/issues/176) | O5, O6 |
| [#177 Thin/full Result profiles](https://github.com/vanderpol/scap-ng/issues/177) | O5, O7 |
| [#178 Shared applicability authoring](https://github.com/vanderpol/scap-ng/issues/178) | O1, O2, O4, O6 |
| [#179 Residual Set/Filter classification](https://github.com/vanderpol/scap-ng/issues/179) | O1, O2, O3 |
| [#180 0.3 prerelease specification normalization](https://github.com/vanderpol/scap-ng/issues/180) | O2, O7 |
| [#181 Require issue references in every commit](https://github.com/vanderpol/scap-ng/issues/181) | O7 |
| [#182 0.3 documentation cleanup and navigation normalization](https://github.com/vanderpol/scap-ng/issues/182) | O2, O7 |
| [#183 Maintain release changelog from issue-linked work](https://github.com/vanderpol/scap-ng/issues/183) | O7 |
| [#184 Define and maintain release objectives and issue traceability](https://github.com/vanderpol/scap-ng/issues/184) | O7 |
| [#185 Audit 0.3 changes for complexity versus objective value](https://github.com/vanderpol/scap-ng/issues/185) | O2, O3, O7, O8 |

## Coverage audit

Every core objective has active tracked work:

| Objective | Representative active issues |
| --- | --- |
| O1 | #7, #10, #164–#169, #172 |
| O2 | #24, #151–#159, #164–#169 |
| O3 | #9, #10, #37, #118–#122, #165–#175 |
| O4 | #29, #41, #42, #44, #166, #168, #178 |
| O5 | #48, #53, #54, #56, #118, #170, #176, #177 |
| O6 | #20, #22, #30, #47, #48, #53, #54, #120, #121, #157–#159, #175, #176, #178 |
| O7 | #6, #26–#28, #37, #38, #42, #49, #50, #55, #56, #116–#119, #122, #123, #128, #131, #133, #137, #151–#156, #171, #177 |
| O8 | #24, #26, #27, #29, #38, #41, #42, #44, #56, #151, #166 |

If a future audit finds an open 0.3 issue with no objective, either map it
honestly or question whether it belongs in the release. If an objective has no
remaining tracked work while it is not demonstrably satisfied, create or
identify the missing issue rather than treating the objective as aspirational
prose.

## Change rule

For each new major design issue or review packet:

1. identify the applicable objective IDs;
2. state the concrete problem being solved;
3. explain how the proposal advances those objectives;
4. identify any objective it may trade off against;
5. provide evidence and counterexamples;
6. do not accept the change solely because CI is green or the representation is shorter.

