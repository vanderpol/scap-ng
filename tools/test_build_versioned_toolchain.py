"""Focused deterministic release-source snapshot and tamper checks."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED


spec = importlib.util.spec_from_file_location(
    "build_versioned_toolchain", Path(__file__).with_name("build_versioned_toolchain.py"))
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class ToolchainTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        git(self.repo, "config", "user.email", "test@example.invalid")
        git(self.repo, "config", "user.name", "Test")
        entries = list(tool.COMMON_REQUIRED) + list(tool.CURRENT_REQUIRED) + [
            "schema/v0.4.0/README.md", "tests/fixture.txt", "docs/guide.md"]
        for name in entries:
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name + "\n", encoding="utf-8")
        (self.repo / "tools/scap_ng_content_compiler.py").chmod(0o755)
        git(self.repo, "add", ".")
        git(self.repo, "commit", "-qm", "test fixture")

    def test_deterministic_and_complete(self):
        a, manifest = tool.build(self.repo, self.root / "out1", "0.4.0")
        b, _ = tool.build(self.repo, self.root / "out2", "0.4.0")
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual(tool.verify(a), manifest)
        self.assertEqual(len(manifest["files"]),
                         len(tool.COMMON_REQUIRED) + len(tool.CURRENT_REQUIRED) + 3)
        with ZipFile(a) as zf:
            mode = zf.getinfo("scap-ng-0.4.0-toolchain/tools/scap_ng_content_compiler.py").external_attr >> 16
            self.assertTrue(mode & 0o111)
        check = subprocess.run([sys.executable, str(Path(tool.__file__)), "--verify", str(a)],
                               check=True, capture_output=True, text=True)
        self.assertEqual(json.loads(check.stdout)["verification"], "pass")
        # Uncommitted changes must not contaminate a reproducible source archive.
        (self.repo / "tests/fixture.txt").write_text("uncommitted change")
        c, _ = tool.build(self.repo, self.root / "out3", "0.4.0")
        self.assertEqual(a.read_bytes(), c.read_bytes())

    def test_reject_missing_docs_and_wrong_version(self):
        with self.assertRaisesRegex(ValueError, "schema/v0.5.0"):
            tool.build(self.repo, self.root / "out", "0.5.0")
        with self.assertRaisesRegex(ValueError, "exact vX.Y.Z tag"):
            tool.build(self.repo, self.root / "out", "0.4.0", require_tag=True)

    def test_reject_archive_member_mutation(self):
        a, _ = tool.build(self.repo, self.root / "out", "0.4.0")
        bad = self.root / "tampered.zip"
        with ZipFile(a) as src, ZipFile(bad, "w", compression=ZIP_DEFLATED) as dest:
            for name in src.namelist():
                payload = src.read(name)
                if name.endswith("tests/fixture.txt"):
                    payload = b"tampered"
                dest.writestr(name, payload)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            tool.verify(bad)


if __name__ == "__main__":
    unittest.main()
