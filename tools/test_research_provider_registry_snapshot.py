#!/usr/bin/env python3
"""#235 native B registry snapshot bounds, not Windows scanning or SCAP parity."""
import unittest
from research_provider_registry_snapshot import normalize, PROVIDER, VERSION

QUERY={"hive":"HKLM",
       "key":r"SOFTWARE\Microsoft\PolicyManager\current\device\Connectivity",
       "name":"AllowBluetooth", "view":"64bit"}


def snapshot(status="complete", records=None, query=None):
    return {"status":status,"query":QUERY if query is None else query,
            "records":[] if records is None else records}


class SnapshotTests(unittest.TestCase):
    def scan(self, snap):
        return normalize(snap, **QUERY)

    def test_pinned_query_identity_and_numerical_value(self):
        result=self.scan(snapshot(records=[{"value_kind":"REG_DWORD","raw_value":0}]))
        self.assertEqual((result["provider"],result["version"]),(PROVIDER,VERSION))
        self.assertEqual((result["status"],result["using"]),("complete",QUERY))
        self.assertEqual(result["items"][0]["fields"]["value"],0)
        self.assertEqual(result["items"][0]["fields"]["value_kind"],"REG_DWORD")

    def test_complete_absence_is_distinct_from_incomplete_zero(self):
        self.assertEqual(self.scan(snapshot())["status"],"complete")
        self.assertEqual(self.scan(snapshot(status="incomplete"))["status"],"incomplete")
        for state in ("error","not collected","not applicable"):
            self.assertEqual(self.scan(snapshot(status=state))["status"],state)

    def test_wrong_registry_view_must_not_reuse_evidence(self):
        other=dict(QUERY,view="32bit")
        result=self.scan(snapshot(query=other, records=[{"value_kind":"REG_DWORD","raw_value":0}]))
        self.assertEqual(result["status"],"error")
        self.assertEqual(result["items"],[])

    def test_string_zero_must_not_masquerade_as_integer_zero(self):
        got=self.scan(snapshot(records=[{"value_kind":"REG_SZ","raw_value":"0"}]))
        self.assertEqual(got["items"][0]["fields"]["value"],{"field_status":"error"})
        self.assertEqual(got["diagnostics"][0]["reason"],"unsupported_or_invalid_registry_value_type")

    def test_invalid_numeric_flags_do_not_coerce(self):
        for kind,raw in (("REG_DWORD","0"),("REG_DWORD",False),
                         ("REG_DWORD",-1),("REG_DWORD",2**32),
                         ("REG_QWORD",2**64), ("REG_MULTI_SZ",["0"])):
            with self.subTest(kind=kind,raw=raw):
                got=self.scan(snapshot(records=[{"value_kind":kind,"raw_value":raw}]))
                self.assertEqual(got["items"][0]["fields"]["value"],{"field_status":"error"})
        got=self.scan(snapshot(records=[{"value_kind":"REG_QWORD","raw_value":2**64-1}]))
        self.assertEqual(got["items"][0]["fields"]["value"],2**64-1)

    def test_duplicate_records_are_not_silently_collapsed(self):
        a={"value_kind":"REG_DWORD","raw_value":0}
        got=self.scan(snapshot(records=[a,a]))
        self.assertEqual(len(got["items"]),2)
        self.assertEqual(len(set(x["id"] for x in got["items"])),2)
        # Native named-resource evaluation must reject this as a singleton violation.

    def test_bad_snapshot_does_not_look_like_verified_absence(self):
        for bad in (None,{}, {"status":"complete","query":QUERY},
                    snapshot(records=[{"value_kind":"REG_DWORD"}]),
                    snapshot(status="error", records=[{"value_kind":"REG_DWORD","raw_value":0}]),
                    snapshot(status=[],records=[])):
            with self.subTest(bad=bad):
                self.assertEqual(self.scan(bad)["status"],"error")

    def test_invalid_query_contract_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize(snapshot(), **dict(QUERY,view="native"))


class SourceBoundaryTests(unittest.TestCase):
    def test_source_w11_registry_shape_and_unverified_parity(self):
        import yaml
        from research_native_contract_candidate import EXAMPLES, read
        from research_native_contract_evaluator import evaluate
        from oval_result_truth_tables import TRUE, FALSE, UNKNOWN, ERROR

        source=(EXAMPLES.parent / "corpus/source-specimens" /
                "windows-registry-0-de183f784659.source.yaml")
        old=yaml.safe_load(source.read_text())["assessment"]
        original=next(iter(old["tests"].values()))
        self.assertEqual(original["capability"],"windows.registry")
        self.assertEqual(original["existence"],"one_or_more")
        self.assertEqual(original["match"],"one")
        self.assertEqual(original["object"]["select"]["name"]["value"],"AllowBluetooth")
        # Source state uses TEXT '0'. Native B's numeric registry provider
        # requires INTEGER 0; those cannot be presumed source-equivalent.
        self.assertEqual(original["states"][0]["value"],"0")
        self.assertIs(type(original["states"][0]["value"]),str)
        self.assertNotIn("view",original["object"]["select"])

        ast=read(EXAMPLES / "03-named-registry.yaml")["ast"]
        self.assertEqual(ast["mode"],"exactly_one")
        ast=dict(ast,using=QUERY)
        def verdict(status="complete", records=None, query=None):
            evidence=normalize(snapshot(status,records,query),**QUERY)
            return evaluate(ast,{PROVIDER:evidence}).result
        dword={"value_kind":"REG_DWORD","raw_value":0}
        self.assertEqual(verdict(records=[dword]),TRUE)
        self.assertEqual(verdict(),FALSE)
        self.assertEqual(verdict(status="incomplete"),UNKNOWN)
        self.assertEqual(verdict(query=dict(QUERY,view="32bit")),ERROR)
        self.assertEqual(verdict(records=[{"value_kind":"REG_SZ","raw_value":"0"}]),ERROR)
        self.assertEqual(verdict(records=[dword,dword]),ERROR)
        # No source conversion/parity claim: source Test match 'one' need not
        # equal named-singleton cardinality. Registry type/view also unresolved.


if __name__=="__main__": unittest.main()
