#!/usr/bin/env python3
import unittest

from generate_niwc_current_review import native_artifact_base, native_benchmark_id


class NativeArtifactIdentityTests(unittest.TestCase):
    def test_stig_revision_and_build_suffix_do_not_change_identity(self):
        self.assertEqual(
            native_artifact_base(
                "U_MS_Defender_Antivirus_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV15-signed"
            ),
            "ms_defender_antivirus",
        )
        self.assertEqual(
            native_artifact_base(
                "U_MS_Defender_Antivirus_V2R10_STIG_SCAP_1-4_Benchmark-enhancedV16-signed"
            ),
            "ms_defender_antivirus",
        )

    def test_native_benchmark_namespace_is_publisher_neutral(self):
        self.assertEqual(
            native_benchmark_id(
                "U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed"
            ),
            "benchmark.rhel_9",
        )
        self.assertNotIn(
            "niwc",
            native_benchmark_id(
                "U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed"
            ),
        )

    def test_product_version_remains_part_of_product_identity(self):
        self.assertEqual(
            native_artifact_base(
                "U_MS_Windows_Server_2025_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV1-signed"
            ),
            "ms_windows_server_2025",
        )
        self.assertNotEqual(
            native_artifact_base(
                "U_MS_Windows_Server_2022_V2R10_STIG_SCAP_1-4_Benchmark-enhancedV19-signed"
            ),
            native_artifact_base(
                "U_MS_Windows_Server_2025_V1R1_STIG_SCAP_1-4_Benchmark-enhancedV1-signed"
            ),
        )


if __name__ == "__main__":
    unittest.main()
