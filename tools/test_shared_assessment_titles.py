"""Cross-benchmark display titles must not carry a donor STIG product label."""
import unittest
from scap_ng_repo_normalizer import neutralize_shared_title


class SharedAssessmentTitleTests(unittest.TestCase):
    def test_windows11_server2025_reuse_has_neutral_title(self):
        title="WN11-AC-000005 - Windows 11 account lockout duration must be configured."
        actual=neutralize_shared_title(
            title, {"ms_windows_11","ms_windows_server_2025"})
        self.assertEqual("Windows account lockout duration must be configured.",actual)

    def test_server2025_shared_with_win11(self):
        title="WN25-00-000110 - Windows Server 2025 Telnet Client must not be installed."
        actual=neutralize_shared_title(
            title, {"ms_windows_11","ms_windows_server_2025"})
        self.assertEqual("Windows Telnet Client must not be installed.",actual)

    def test_rhel9_oraclelinux9_reuse_is_generic(self):
        title="OL09-00-002071 - OL 9 must prevent setuid on the home filesystem."
        actual=neutralize_shared_title(
            title, {"rhel_9","oracle_linux_9"})
        self.assertEqual("Linux must prevent setuid on the home filesystem.",actual)

    def test_single_benchmark_keeps_author_title(self):
        title="WN11-AC-000005 - Windows 11 account lockout duration must be configured."
        self.assertEqual(title,neutralize_shared_title(title,{"ms_windows_11"}))


if __name__=="__main__":
    unittest.main()
