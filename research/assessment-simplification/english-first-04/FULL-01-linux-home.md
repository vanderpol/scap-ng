# 01 · RHEL 9 /home mount option (simple) — complete before and after

**Review-only comparison. Neither version represents independently validated SCAP 1.4 scanner execution/evidence parity.**

[Back to all five complete examples](BEFORE-AFTER-REVIEW.md) · [Original pinned source](https://github.com/vanderpol/scap-ng-editor-sample-data/blob/99cbceae8d594c44cb509df95975ac1676a2b44a/focused-fixtures/source-backed/authoring/shared/assessments/linux/other/home-mounted-nosuid-option.assessment.yaml)

## What changed (without changing the underlying check)

- `capability: linux.partition` becomes `inspect: linux.partition`.
- `object.select.mount_point` becomes `where.mount_point`; the original regular expression is unchanged.
- The required *at least one selected Item; all selected Items match* and *some mount option equals nosuid* remain separate requirements.

**What to assess:** Can you identify the collected system data, source definitions, value/Item requirements and final evaluation without referring to another file?

## Complete assessments — side by side

Both columns contain **every line** of their respective full YAML checks. Use a wide desktop browser for the two-column view. If the rendered table overflows, scroll it horizontally; the original files remain available from the links above.

<table>
<thead><tr><th align="left" width="50%">BEFORE — Current 0.4</th><th align="left" width="50%">AFTER — English-first research</th></tr></thead>
<tbody><tr>
<td valign="top" width="50%"><pre><code>assessment:
  id: ng.shared.home-is-mounted-with-the-nosuid-option
  version: 1
  assessment_title: Linux must prevent files with the setuid and setgid bit set from being executed on file systems
    that contain user home directories.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
  tests:
    home-mounted-nosuid-option-test:
      test_title: /home is mounted with the nosuid option.
      capability: linux.partition
      object:
        capability: linux.partition
        select:
          mount_point:
            matches_regex: .*\/home
        object_title: null
      states:
      - mount_options:
          require: at_least_one_exists_and_some_match
          equals: nosuid
      reported_elements: all
      collected_items_require: at_least_one_exists_and_all_match
  evaluate:
    test: home-mounted-nosuid-option-test</code></pre></td>
<td valign="top" width="50%"><pre><code># RESEARCH ONLY — full English-first candidate for this exact pinned 0.4 Assessment.
# Consistent with the experimental compact-layout mapping; not normative 0.4 or scanner proof.
metadata:
  id: ng.shared.home-is-mounted-with-the-nosuid-option
  version: 1
  assessment_title: Linux must prevent files with the setuid and setgid bit set from being executed on file systems
    that contain user home directories.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
sources: {}
checks:
  home-mounted-nosuid-option-test:
    check: /home is mounted with the nosuid option.
    inspect: linux.partition
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        mount_options:
          some_values_is: nosuid
    report_elements: all
    where:
      mount_point:
        matches_regex: .*\/home
    description: null
evaluate:
  test: home-mounted-nosuid-option-test</code></pre></td>
</tr></tbody>
</table>


## Your review

- Which syntax would you prefer when writing this exact check from scratch?
- Are any named sources, collection operations or cardinality requirements still hard to understand?
- Does the new grammar look consistent with the other examples?

**Evidence boundary:** The simple case follows the established research mapping but this inline after file has not independently passed a complete converter round trip.
