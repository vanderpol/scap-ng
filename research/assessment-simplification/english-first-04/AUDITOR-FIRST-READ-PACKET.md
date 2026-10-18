# 0.4 Assessment authoring — unprimed first-read review

**Blind review packet · 18 October 2026 · experimental/pre-alpha**. Three *complete* renderings of the **same pinned Linux /home policy Assessment** appear below in different authoring styles. This document deliberately does **not** identify the existing design, reveal a preferred design, supply an answer key, or assert that the three forms are executable. They are **not three accepted 0.4 dialects**.

**Reviewer instructions:** You are a security compliance auditor unfamiliar with this YAML authoring language. Do not assume OVAL, Ansible, Python, or another language's semantics. The only information you get is the samples. For every question, distinguish **confident from visible YAML**, **plausible but ambiguous**, and **not knowable without documentation**. Do not use outside SCAP-NG docs until you have frozen the first response.

## Questions — answer independently for each sample

1. What real-world source of data is examined? Exactly what Item is selected? Could a mount path other than `/home` be selected by the literal selector?
2. Does the source require any selected mount Item to exist? What if the collection is complete but zero Items match the selector?
3. Suppose there are two selected mount Items, one with `nosuid`, one without. What result do you expect, and what line led you there?
4. Is `mount_options` a single text value or potentially a collection of values? How many values must satisfy `nosuid`?
5. What do you infer about **incomplete collection**, missing `mount_options`, collector error and not-applicable? Which outcomes are unknowable from the snippet alone?
6. Explain the entire check to a fellow security auditor in **two ordinary sentences**. Quote any YAML key that forced you to guess.
7. Could you write a new Assessment for a different mount option, retaining the same Item/field multiplicity, without copying an unknown default?
8. Identify keys that are confusing, redundant, ambiguously scoped or far from what they govern.

**After all three:** Rank A/B/C separately for (a) *understanding the check* and (b) *writing a new check*, 1 = easiest; give at most three precise reasons. Please do not praise readability without naming a specific semantic improvement.

## Sample A — complete YAML

```yaml
assessment:
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
    test: home-mounted-nosuid-option-test
```

## Sample B — complete YAML

```yaml
assessment:
  id: ng.shared.home-is-mounted-with-the-nosuid-option
  version: 1
  assessment_title: >-
    Linux must prevent files with the setuid and setgid bit set from being
    executed on file systems that contain user home directories.
  mode: automated
  class: compliance
  purpose: assessment
  specification:
    id: scap-ng.pre-alpha.assessment
    version: 0.4.0
  checks:
    home-mounted-nosuid-option-test:
      check: /home is mounted with the nosuid option.
      inspect: linux.partition
      where:
        mount_point:
          matches_regex: .*\/home
      collected_items_require: at_least_one_exists_and_all_match
      states:
        - mount_options:
            require: at_least_one_exists_and_some_match
            equals: nosuid
      reported_elements: all
  evaluate:
    test: home-mounted-nosuid-option-test
```

## Sample C — complete YAML

```yaml
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
    description: null
    where:
      mount_point:
        matches_regex: .*\/home
    require:
      at_least_one_item_exists: true
      every_item_must_match:
        mount_options:
          some_values_is: nosuid
    report_elements: all
evaluate:
  test: home-mounted-nosuid-option-test
```

---

**Freeze point:** Stop here before reading other files. This is a design-comprehension exercise, not a validator or schema-conformance test. A real auditor's feedback must be independent of the authors of these proposals.
