"""Check complete known UNIX file metadata independently of a collector."""
from pathlib import PurePosixPath
import stat
import unittest

from conformance.tools.runner import CONFORMANCE, ROOT, load, schema_validator
from conformance.tools.semantic import validate

SUITE = CONFORMANCE / "file-metadata"

PERMISSIONS = {
    "setuid": stat.S_ISUID, "setgid": stat.S_ISGID, "sticky": stat.S_ISVTX,
    "owner_read": stat.S_IRUSR, "owner_write": stat.S_IWUSR, "owner_execute": stat.S_IXUSR,
    "group_read": stat.S_IRGRP, "group_write": stat.S_IWGRP, "group_execute": stat.S_IXGRP,
    "other_read": stat.S_IROTH, "other_write": stat.S_IWOTH, "other_execute": stat.S_IXOTH,
}


def fields(snapshot):
    path = PurePosixPath(snapshot["path"])
    mode = int(snapshot["mode_octal"], 8)
    metadata = {name: snapshot[name] for name in (
        "owner_uid", "owner_gid", "access_time", "change_time", "modify_time", "size", "has_extended_acl",
    )}
    return metadata | {
        "full_path": str(path), "directory": str(path.parent), "name": path.name,
        "type": snapshot["kind"],
    } | {name: bool(mode & mask) for name, mask in PERMISSIONS.items()}


def mismatches(observed, predicates):
    return {name for name, predicate in predicates.items()
            if type(observed[name]) is not type(predicate["equals"]) or observed[name] != predicate["equals"]}


class UnixFileMetadataCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load(SUITE / "expected.json")
        cls.source = load(SUITE / cls.manifest["source"])
        cls.snapshot = load(SUITE / cls.manifest["fixture"])
        assessment = cls.source["assessment"]
        test_ref = assessment["evaluate"]["test"]
        cls.test = assessment["tests"][test_ref]
        cls.selector = assessment["shared_objects"][cls.test["object"]]
        cls.predicates = cls.test["require"]["fields"]

    def test_all_canonical_file_fields_have_typed_supplied_expectations(self):
        schema_validator("assessment.schema.json").validate(self.source)
        self.assertEqual(validate(self.source), [])
        schema_commit = load(CONFORMANCE / "manifest.json")["schema_commit"]
        self.assertEqual(self.manifest["schema_commit"], schema_commit)
        mapping = load(ROOT / self.manifest["native_field_mapping"])
        self.assertEqual(self.test["capability"], "unix.file")
        self.assertEqual(self.selector["capability"], self.test["capability"])
        self.assertEqual(self.selector["full_path"]["equals"], self.snapshot["path"])
        self.assertEqual(set(mapping["native"]["state_field_map"].values()), self.predicates.keys())
        self.assertEqual(self.test["require"]["item_requirement"],
                         {"items_found": "exactly_one", "items_satisfying": "every"})
        self.assertEqual(self.test["require"]["field_requirement"],
                         {"values_found": "exactly_one", "values_matching": "every"})
        observed = fields(self.snapshot)
        datatype = {str: "string", int: "integer", bool: "boolean"}
        for name, value in observed.items():
            self.assertIn(datatype[type(value)], mapping["native"]["field_datatypes"][name])
            self.assertIs(type(value), type(self.manifest["fields"][name]))
        self.assertEqual(observed, self.manifest["fields"])
        self.assertIs(not mismatches(observed, self.predicates), self.manifest["positive_outcome"])

    def test_every_permission_bit_is_independently_decisive(self):
        controls = self.manifest["single_bit_controls"]
        self.assertEqual(controls.keys(), PERMISSIONS.keys())
        for name, mode in controls.items():
            with self.subTest(bit=name):
                observed = fields(self.snapshot | {"mode_octal": mode})
                changed = int(mode, 8) ^ int(self.snapshot["mode_octal"], 8)
                self.assertEqual(changed, PERMISSIONS[name])
                self.assertEqual(mismatches(observed, self.predicates), {name})
                self.assertIs(not mismatches(observed, self.predicates), self.manifest["negative_outcome"])

    def test_type_and_metadata_changes_do_not_disappear(self):
        integer = self.snapshot["owner_uid"]
        for value in (integer + 1, str(integer)):
            with self.subTest(value=value):
                observed = fields(self.snapshot | {"owner_uid": value})
                self.assertEqual(mismatches(observed, self.predicates), {"owner_uid"})
