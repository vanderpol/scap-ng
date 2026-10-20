#!/usr/bin/env python3
"""Exact full-document source-backed RHEL9 must/may vocabulary projection.
Research only; no normative schema changes or scanner-result equivalence.
Pinned original source content is embedded verbatim with its repository blob SHA.
Refs #227 #246.
"""
from copy import deepcopy
import json
import yaml

PINNED_SOURCE_REPO = "vanderpol/scap-ng-editor-sample-data"
PINNED_BLOBS = {"home-mounted-nosuid-option.assessment.yaml":"a74cefc9b51e1f7a4bde0d94aa0b0250f52f6792","initialization-files-0740-less-permissive.assessment.yaml":"68b3dbd4ef6afa123188786cb515b49644737e0f"}
SOURCES_JSON = "{\"home-mounted-nosuid-option.assessment.yaml\":\"assessment:\\n  id: ng.shared.home-is-mounted-with-the-nosuid-option\\n  version: 1\\n  assessment_title: Linux must prevent files with the setuid and setgid bit set from being executed on file systems\\n    that contain user home directories.\\n  mode: automated\\n  class: compliance\\n  purpose: assessment\\n  specification:\\n    id: scap-ng.pre-alpha.assessment\\n    version: 0.4.0\\n  tests:\\n    home-mounted-nosuid-option-test:\\n      test_title: /home is mounted with the nosuid option.\\n      capability: linux.partition\\n      object:\\n        capability: linux.partition\\n        select:\\n          mount_point:\\n            matches_regex: .*\\\\/home\\n        object_title: null\\n      states:\\n      - mount_options:\\n          require: at_least_one_exists_and_some_match\\n          equals: nosuid\\n      reported_elements: all\\n      collected_items_require: at_least_one_exists_and_all_match\\n  evaluate:\\n    test: home-mounted-nosuid-option-test\\n\",\"initialization-files-0740-less-permissive.assessment.yaml\":\"assessment:\\n  id: ng.shared.linux-local-initialization-files-must-have-mode-0740-or-less-permissive\\n  version: 1\\n  assessment_title: Linux local initialization files must have mode 0740 or less permissive.\\n  mode: automated\\n  class: compliance\\n  purpose: assessment\\n  specification:\\n    id: scap-ng.pre-alpha.assessment\\n    version: 0.4.0\\n  tests:\\n    local-initialization-files-non-system-users-have-mode-0740-or-test:\\n      test_title: Local initialization files for non-system users have mode 0740 or less permissive.\\n      capability: unix.file\\n      object:\\n        capability: unix.file\\n        object_title: local initialization files of non-system users.\\n        set:\\n          operator: union\\n          operands:\\n          - object:\\n              capability: unix.file\\n              for_each:\\n                item: user\\n                in: only-non-system-users-uid-999-home-dirs-excluding-root-object\\n              select:\\n                directory:\\n                  from: user.home_dir\\n                name:\\n                  matches_regex: ^\\\\.[^\\\\s\\\\.]+\\n              object_title: local initialization files of non-system users.\\n              filesystem: all\\n              traversal:\\n                max_depth: 1\\n                recurse: symlinks\\n            filters:\\n            - exclude:\\n                type:\\n                  require: at_least_one_exists_and_all_match\\n                  equals: directory\\n      states:\\n      - and:\\n        - setuid:\\n            equals: false\\n        - setgid:\\n            equals: false\\n        - sticky:\\n            equals: false\\n        - group_write:\\n            equals: false\\n        - group_execute:\\n            equals: false\\n        - other_read:\\n            equals: false\\n        - other_write:\\n            equals: false\\n        - other_execute:\\n            equals: false\\n        state_fields_require: at_least_one_exists_and_all_match\\n      reported_elements: all\\n      collected_items_require: may_be_absent_and_all_match\\n    local-initialization-files-root-have-mode-0740-or-less-permissive-test:\\n      test_title: Local initialization files for root have mode 0740 or less permissive.\\n      capability: unix.file\\n      object:\\n        capability: unix.file\\n        object_title: local initialization files of root user.\\n        set:\\n          operator: union\\n          operands:\\n          - object:\\n              capability: unix.file\\n              for_each:\\n                item: user\\n                in: only-root-users-uid-0-home-dirs-excluding-root-directory-object\\n              select:\\n                directory:\\n                  from: user.home_dir\\n                name:\\n                  matches_regex: ^\\\\.[^\\\\s\\\\.]+\\n              object_title: local initialization files of root user.\\n              filesystem: all\\n              traversal:\\n                max_depth: 1\\n                recurse: symlinks\\n            filters:\\n            - exclude:\\n                type:\\n                  require: at_least_one_exists_and_all_match\\n                  equals: directory\\n      states:\\n      - and:\\n        - setuid:\\n            equals: false\\n        - setgid:\\n            equals: false\\n        - sticky:\\n            equals: false\\n        - group_write:\\n            equals: false\\n        - group_execute:\\n            equals: false\\n        - other_read:\\n            equals: false\\n        - other_write:\\n            equals: false\\n        - other_execute:\\n            equals: false\\n        state_fields_require: at_least_one_exists_and_all_match\\n      reported_elements: all\\n      collected_items_require: at_least_one_exists_and_all_match\\n  evaluate:\\n    all:\\n    - test: local-initialization-files-non-system-users-have-mode-0740-or-test\\n    - test: local-initialization-files-root-have-mode-0740-or-less-permissive-test\\n  shared_objects:\\n    users-username-object:\\n      capability: unix.password\\n      select:\\n        username:\\n          matches_regex: '[\\\\w]+'\\n      object_title: Users with an username\\n    only-non-system-users-uid-999-home-dirs-excluding-root-object:\\n      capability: unix.password\\n      set:\\n        operator: difference\\n        operands:\\n        - object: users-username-object\\n          filters:\\n          - exclude:\\n              user_id:\\n                require: at_least_one_exists_and_all_match\\n                less_than: 1000\\n          - exclude:\\n              home_dir:\\n                require: at_least_one_exists_and_all_match\\n                equals: /\\n      object_title: only non-system users (uid>999) home-dirs excluding root directory\\n    only-root-users-uid-0-home-dirs-excluding-root-directory-object:\\n      capability: unix.password\\n      set:\\n        operator: difference\\n        operands:\\n        - object: users-username-object\\n          filters:\\n          - exclude:\\n              user_id:\\n                require: at_least_one_exists_and_all_match\\n                greater_than: 0\\n          - exclude:\\n              home_dir:\\n                require: at_least_one_exists_and_all_match\\n                equals: /\\n      object_title: only root users (uid=0) home-dirs excluding root directory\\n\"}"
SOURCES = json.loads(SOURCES_JSON)
TO_ITEMS = {
    "at_least_one_exists_and_all_match": "one_or_more",
    "may_be_absent_and_all_match": "may_be_absent",
}
TO_NATIVE = {value: key for key, value in TO_ITEMS.items()}

def present(doc):
    output = deepcopy(doc)
    tests = output["assessment"]["tests"]
    for test in tests.values():
        native = test.pop("collected_items_require")
        if native not in TO_ITEMS or not test.get("states"):
            raise ValueError("Unsupported source shape")
        test["require"] = {"items": TO_ITEMS[native], "all_items_must": True}
    return output

def lower(doc):
    output = deepcopy(doc)
    tests = output["assessment"]["tests"]
    for test in tests.values():
        if "collected_items_require" in test:
            raise ValueError("Ambiguous old/new requirement")
        requirement = test.pop("require", None)
        if not isinstance(requirement, dict) or set(requirement) != {"items", "all_items_must"}:
            raise ValueError("Unsupported requirement syntax")
        if requirement["all_items_must"] is not True or not test.get("states"):
            raise ValueError("Matching requirement needs local State")
        existence = requirement["items"]
        if not isinstance(existence, str) or existence not in TO_NATIVE:
            raise ValueError("Unproven existence semantics")
        test["collected_items_require"] = TO_NATIVE[existence]
    return output

def main():
    docs = [yaml.safe_load(content) for content in SOURCES.values()]
    count = 0
    for source in docs:
        candidate = present(source)
        restored = lower(candidate)
        assert restored == source, "whole-document original differs"
        count += len(source["assessment"]["tests"])
        for test in candidate["assessment"]["tests"].values():
            assert "require" in test and "collected_items_require" not in test
    original = present(docs[0])
    first_id = next(iter(original["assessment"]["tests"]))
    cases = [
        {"items": "none", "all_items_must": True},
        {"items": "exactly_one", "all_items_must": True},
        {"items": "one_or_more", "all_items_must": False},
        {"items": "one_or_more", "no_items_may": True},
        {"items": "one_or_more"},
        {"items": "one_or_more", "all_items_must": True, "hidden_default": True},
    ]
    for bad in cases:
        changed = deepcopy(original)
        changed["assessment"]["tests"][first_id]["require"] = bad
        try:
            lower(changed)
        except ValueError:
            continue
        raise AssertionError("accepted unsupported vocabulary: " + repr(bad))
    print(f"PASS: {len(docs)} full source documents, {count} Test mappings, {len(cases)} negative cases")
    print("No six-state parity or compiler semantics established.")

if __name__ == "__main__":
    main()
