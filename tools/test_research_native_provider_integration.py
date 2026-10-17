#!/usr/bin/env python3
"""#235 research-only integration between small typed providers and native AST.

Fixture/CI mounted data only. Actual Linux /proc is read-only if present.
No Apache runtime, Windows runtime, SCAP 1.4 conversion or OVAL parity.
"""
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from research_native_contract_candidate import EXAMPLES,read
from research_native_contract_evaluator import evaluate
from research_provider_linux_mounts import parse_mountinfo_text,collect_current_linux_mounts
from research_provider_apache_directives import collect as apache_collect
from research_dns_zone_key_evidence import normalize
from oval_result_truth_tables import TRUE,FALSE,UNKNOWN

def compiled(name):
    return read(EXAMPLES/name)["ast"]

def zone(name,*,ad=True,signed=True,reverse=False):
    return {"ZoneName":name,"ZoneType":"Primary","IsAutoCreated":False,
            "IsReverseLookupZone":reverse,"IsDsIntegrated":ad,"IsSigned":signed}
def key(name,ident,kind="ZoneSigningKey",days=3,hours=0):
    return {"KeyId":ident,"ZoneName":name,"KeyType":kind,"Days":days,"Hours":hours}

def dns_adapter(observation):
    """Translate fixture-normalized provider relations without guessing completeness.

    This explicit adapter is *necessary*: a Python list itself does NOT
    guarantee its provider finished enumerating all signing keys.
    """
    status=observation["status"]
    nested_status=observation["key_source_status"]
    if status!="complete":
        nested_status="error" if status=="error" else "incomplete"
    items=[]
    for zone_data in observation["zones"]:
        typed={"direction":zone_data["direction"],
               "directory_integration":zone_data["directory_integration"],
               "signed":zone_data["signed"]}
        for field in ("zone_signing_keys","key_signing_keys"):
            typed[field]={"status":nested_status,
                          "items":[{
                            "id":entry["id"],
                            "fields":{"zone_id":entry["zone_id"],
                                      "kind":entry["kind"],
                                      "validity_hours":entry["validity_hours"]}
                          } for entry in zone_data[field]]}
        items.append({"id":zone_data["id"],"fields":typed})
    return {"status":status,"items":items}

class RealProviderToASTTests(unittest.TestCase):
    def test_parsed_linux_mountinfo_selected_complete(self):
        raw=("31 21 8:1 / /home rw,nosuid - ext4 /dev/sda1 rw\n"
             "32 21 8:2 / /var rw - ext4 /dev/sda2 rw\n")
        observed=parse_mountinfo_text(raw,"mnt:[fixture]")
        x=evaluate(compiled("01-required-home.yaml"),{"linux.mounts":observed})
        self.assertEqual(x.result,TRUE)
        observed=parse_mountinfo_text(raw.replace("rw,nosuid","rw",1),"mnt:[fixture]")
        x=evaluate(compiled("01-required-home.yaml"),{"linux.mounts":observed})
        self.assertEqual(x.result,FALSE)

    def test_linux_runner_mount_collection_end_to_end(self):
        if not Path("/proc/self/mountinfo").exists():
            self.skipTest("not a Linux mountinfo host")
        observed=collect_current_linux_mounts()
        self.assertEqual(observed["status"],"complete",observed["diagnostics"])
        x=evaluate(compiled("01-required-home.yaml"),{"linux.mounts":observed})
        self.assertIn(x.result,{TRUE,FALSE})
        # May Fail because the CI host has no separate /home mount.
        if not any(i["fields"]["mount_point"]=="/home" for i in observed["items"]):
            self.assertEqual(x.result,FALSE)

    def test_apache_config_files_directly_fed_to_native_ast(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"httpd.conf").write_text(
                "KeepAlive On\nInclude conf.d/site.conf\n")
            (root/"conf.d").mkdir()
            site=root/"conf.d"/"site.conf"
            site.write_text("MaxKeepAliveRequests 150\n")
            observed=apache_collect(root/"httpd.conf",server_root=root)
            x=evaluate(compiled("04-apache-two-settings.yaml"),
                       {"apache.config_directives":observed})
            self.assertEqual(x.result,TRUE)
            site.write_text("MaxKeepAliveRequests 99\n")
            observed=apache_collect(root/"httpd.conf",server_root=root)
            self.assertEqual(evaluate(compiled("04-apache-two-settings.yaml"),
                                      {"apache.config_directives":observed}).result,FALSE)
            # This checks canonical integer values in the native provider;
            # the four original shellcommand Tests are still not replaced.

    def test_apache_partial_source_does_not_pass_even_with_good_lines(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"httpd.conf").write_text(
                "KeepAlive On\nMaxKeepAliveRequests 150\nInclude missing.conf\n")
            observed=apache_collect(root/"httpd.conf",server_root=root)
            self.assertEqual(observed["status"],"incomplete")
            self.assertEqual(evaluate(compiled("04-apache-two-settings.yaml"),
                                      {"apache.config_directives":observed}).result,UNKNOWN)

    def test_dns_structured_zone_and_two_key_groups_feed_native_ast(self):
        observed=normalize([zone("corp.test")],
                   [key("corp.test","z"),key("corp.test","k",kind="KeySigningKey",days=7)])
        self.assertEqual(observed["status"],"complete")
        self.assertEqual(evaluate(compiled("08-dns-signing-nested.yaml"),
                                   {"windows.dns.zones":dns_adapter(observed)}).result,TRUE)
        observed=normalize([zone("corp.test")],
                   [key("corp.test","z",days=7,hours=1),
                    key("corp.test","k",kind="KeySigningKey",days=7)])
        self.assertEqual(evaluate(compiled("08-dns-signing-nested.yaml"),
                                   {"windows.dns.zones":dns_adapter(observed)}).result,FALSE)

    def test_dns_zone_ad_optional_population_after_typed_adapter(self):
        observed=normalize([zone("reverse.in-addr.arpa",reverse=True)],[])
        self.assertEqual(evaluate(compiled("05-dns-if-any.yaml"),
                                   {"windows.dns.zones":dns_adapter(observed)}).result,TRUE)
        observed=normalize([zone("forward.test",ad=False)],[])
        self.assertEqual(evaluate(compiled("05-dns-if-any.yaml"),
                                   {"windows.dns.zones":dns_adapter(observed)}).result,FALSE)

    def test_dns_unknown_key_source_never_passes_signed_requirement(self):
        observed=normalize([zone("corp.test")],
                           [key("corp.test","z")],keys_status="incomplete")
        self.assertEqual(evaluate(compiled("08-dns-signing-nested.yaml"),
                                   {"windows.dns.zones":dns_adapter(observed)}).result,UNKNOWN)

    def test_dns_malformed_zone_source_does_not_disappear_for_optional_rule(self):
        bad=zone("corp.test")
        del bad["IsDsIntegrated"]
        observed=normalize([bad],[])
        self.assertEqual(observed["status"],"incomplete")
        self.assertEqual(evaluate(compiled("05-dns-if-any.yaml"),
                                   {"windows.dns.zones":dns_adapter(observed)}).result,UNKNOWN)

if __name__=="__main__":unittest.main()
