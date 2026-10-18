#!/usr/bin/env python3
"""#235: frozen research JSON boundary for the single B fixture evaluator.

NOT a normative SCAP-NG bundle, scanner, signature, source converter or
production validation API. Compatibility Test nodes consume ALREADY evaluated
item_results supplied by a trusted fixture; source Objects/States/Variables
are NOT executable through this payload. Scanner implementation feasibility
is the research question, not a claim of end-to-end SCAP 1.4 parity.
"""
from __future__ import annotations

import hashlib
import json

from oval_result_truth_tables import RESULTS
from research_native_contract_candidate import OPS, PROVIDERS
from research_native_provider_catalog import CATALOG

FORMAT = "scap-ng-b-fixture-ir/0.1"
SCOPE = "research-fixture-evaluator-only"
SOURCE_KINDS = {"native", "compiler-compatibility", "mixed", "manual"}
COMPAT_INPUTS = {"flag", "existence", "check", "item_results", "has_state",
                 "exists", "does_not_exist", "error", "not_collected"}
COLLECTION_KEYS = {"kind", "provider", "mode", "exists_only", "min_count",
                   "singleton", "using", "where", "predicates", "as",
                   "nested", "parent_ref", "owner_field"}


def _canonical(value):
    """Stable JSON bytes; rejects NaN and other non-JSON Python values."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _ensure(condition, reason):
    if not condition:
        raise ValueError("B compiled fixture IR: " + reason)


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        _ensure(key not in result, "duplicate JSON property " + key)
        result[key] = value
    return result


def _predicates(values):
    _ensure(isinstance(values, list), "predicates must be array")
    for entry in values:
        _ensure(isinstance(entry, dict) and set(entry) == {"field", "operator", "value"},
                "predicate must have field/operator/value only")
        _ensure(isinstance(entry["field"], str) and bool(entry["field"]),
                "predicate field must be named")
        _ensure(isinstance(entry["operator"], str) and entry["operator"] in OPS,
                "unknown predicate operation")
        # Authoring compilation validates typed fields. This research decode
        # only validates JSON/tree shape, NOT a production provider contract.


def _node(node, source_kind, depth=0):
    _ensure(depth <= 64, "excessive requirement depth")
    _ensure(isinstance(node, dict) and isinstance(node.get("kind"), str),
            "every node needs a kind")
    kind = node["kind"]

    if kind == "manual_procedure":
        _ensure(source_kind=="manual" and depth==0,
                "manual procedures cannot be embedded in automated tests")
        keys={"kind","source_assessment_id","version","title",
              "class","purpose","procedure","response","evidence_guidance"}
        _ensure(set(node)==keys,"unexpected manual procedure fields")
        _ensure(isinstance(node["source_assessment_id"],str) and
                bool(node["source_assessment_id"]) and
                isinstance(node["procedure"],str) and bool(node["procedure"]),
                "manual Assessment requires immutable id/procedure")
        _ensure((type(node["version"]) in {int,str}) and
                bool(str(node["version"])), "manual version invalid")
        _ensure(node["title"] is None or isinstance(node["title"],str),
                "manual title invalid")
        _ensure(node["purpose"] in {"assessment","applicability"} and
                node["class"] in {"compliance","vulnerability","patch",
                                   "inventory","miscellaneous"}, "manual purpose/class invalid")
        _ensure(node["evidence_guidance"] is None or
                isinstance(node["evidence_guidance"],str), "manual evidence guidance invalid")
        from research_b_manual_lowering import lower_manual_assessment
        raw={"id":node["source_assessment_id"],
             "version":node["version"],"assessment_title":node["title"],
             "mode":"manual","class":node["class"],"purpose":node["purpose"],
             "procedure":node["procedure"],"response":node["response"],
             "evidence_guidance":node["evidence_guidance"]}
        _ensure(lower_manual_assessment({"assessment":raw})==node,
                "manual procedure is not semantically canonical")
        return

    if kind == "compat_oval_test":
        _ensure(source_kind != "native",
                "compiler-only OVAL compatibility node cannot be native authored")
        _ensure(set(node) == {"kind", "source_test_id", "test"},
                "invalid compatibility Test node keys")
        _ensure(isinstance(node["source_test_id"], str) and bool(node["source_test_id"]),
                "compatibility source Test requires identity")
        t = node["test"]
        _ensure(isinstance(t, dict) and {"flag", "existence", "check", "exists"} <= set(t)
                and not (set(t) - COMPAT_INPUTS), "invalid source Test inputs")
        _ensure(isinstance(t["flag"], str) and
                t["flag"] in {"complete", "incomplete", "error", "not collected",
                              "not applicable", "does not exist"}, "invalid source collection flag")
        _ensure(isinstance(t["existence"], str) and
                t["existence"] in {"all_exist", "any_exist", "at_least_one_exists",
                                   "none_exist", "only_one_exists"}, "invalid existence operation")
        _ensure(isinstance(t["check"], str) and
                t["check"] in {"all", "at least one", "only one", "none satisfy"},
                "invalid OVAL Item check")
        for key in ("exists", "does_not_exist", "error", "not_collected"):
            if key in t:
                _ensure(type(t[key]) is int and t[key] >= 0,
                        "invalid OVAL Item-status count")
        if "has_state" in t:
            _ensure(type(t["has_state"]) is bool, "has_state requires Boolean")
        if "item_results" in t:
            _ensure(isinstance(t["item_results"], list) and
                    all(isinstance(v, str) and v in RESULTS for v in t["item_results"]),
                    "invalid pre-evaluated OVAL Item results")
        return

    if kind == "compat_oval_provider_state":
        _ensure(source_kind != "native",
                "source State operations may only be compiler generated")
        keys={"kind","source_assessment_id","source_test_id","provider",
              "using","existence","check","state"}
        _ensure(set(node)==keys, "unexpected State compatibility IR keys")
        _ensure(node["provider"]=="linux.textfile_matches",
                "State evaluation supported only for bounded textfile pilot")
        _ensure(all(isinstance(node[k],str) and bool(node[k])
                    for k in ("source_assessment_id","source_test_id")),
                "source State provenance identity required")
        _ensure(node["existence"] in {"at_least_one_exists","none_exist","only_one_exists"},
                "unsupported source Test existence")
        _ensure(node["check"] in {"all","at least one","only one","none satisfy"},
                "unsupported source Item matching")
        using=node["using"]
        required={"path","pattern","ignore_case","multiline","singleline"}
        _ensure(isinstance(using,dict) and set(using)==required,
                "source State acquisition parameters invalid")
        _ensure(isinstance(using["path"],str) and using["path"].startswith("/")
                and isinstance(using["pattern"],str) and bool(using["pattern"]),
                "source State path/regex must be explicit")
        _ensure(all(type(using[k]) is bool
                    for k in ("ignore_case","multiline","singleline")),
                "source State regex flags must be Boolean")
        import re
        try:
            expression=re.compile(using["pattern"],
                    (re.IGNORECASE if using["ignore_case"] else 0) |
                    (re.MULTILINE if using["multiline"] else 0) |
                    (re.DOTALL if using["singleline"] else 0))
        except re.error as exc:
            raise ValueError("source State regex must compile for research provider") from exc
        _ensure(expression.groups==1 and not expression.groupindex,
                "source State comparison requires exactly one unnamed group")
        state=node["state"]
        _ensure(isinstance(state,dict) and set(state)=={
            "field","operation","expected","entity_existence","entity_check"},
            "invalid State entity IR")
        numeric={"greater_than_or_equal","greater_than","less_than","less_than_or_equal"}
        _ensure(state["field"]=="subexpression" and
                state["operation"] in {"equals","not_equals","pattern_match"}|numeric and
                state["entity_existence"]=="at_least_one_exists" and
                state["entity_check"]=="all",
                "unsupported source State entity operation/cardinality")
        if state["operation"] in numeric:
            _ensure(type(state["expected"]) is int and
                    -(2**63)<=state["expected"]<2**63,
                    "numeric source State requires signed int64 literal")
        else:
            _ensure(isinstance(state["expected"],str),
                    "text source State requires string literal")
        if state["operation"]=="pattern_match":
            _ensure(len(state["expected"])<=2048,
                    "source State regex exceeds bounded research length")
            try:
                re.compile(state["expected"])
            except re.error as exc:
                raise ValueError("invalid source State regex for research provider") from exc
        return

    if kind == "compat_oval_registry_view_invariant":
        _ensure(source_kind != "native",
                "source registry compatibility IR cannot be native authored")
        keys={"kind","source_assessment_id","source_test_id","provider",
              "using","source_view","existence","check","state"}
        _ensure(set(node)==keys,"invalid source registry Test IR fields")
        _ensure(node["provider"]=="windows.registry_source_views" and
                node["source_view"]=="unspecified_requires_xml_parity",
                "source registry view must not be invented")
        _ensure(all(isinstance(node[k],str) and bool(node[k])
                    for k in ("source_assessment_id","source_test_id")),
                "source registry provenance is required")
        _ensure(node["existence"]=="at_least_one_exists" and
                node["check"] in {"all","only one","at least one"},
                "source registry Test cardinality unsupported")
        using=node["using"]
        _ensure(isinstance(using,dict) and set(using)=={"hive","key","name"} and
                using["hive"]=="HKLM" and
                all(isinstance(using[k],str) and bool(using[k]) for k in ("key","name")),
                "source registry using identity invalid")
        state=node["state"]
        def valid_registry_field(field):
            _ensure(isinstance(field,dict) and set(field)=={
                "field","operation","expected","entity_existence","entity_check"},
                "source registry State child fields invalid")
            _ensure(field["field"] in {"value","type"} and
                    field["operation"]=="equals" and
                    field["entity_existence"]=="at_least_one_exists" and
                    field["entity_check"]=="all",
                    "unsupported source registry State child operation/cardinality")
            v=field["expected"]
            if field["field"]=="type":
                _ensure(type(v) is str and v in {"string","dword","qword"},
                        "source registry type must be recognized literal")
            else:
                _ensure(type(v) in (str,int) and
                        (type(v) is str or -(2**63)<=v<2**63),
                        "source registry value must be bounded typed literal")
        _ensure(isinstance(state,dict),"source registry State must be a mapping")
        if set(state)=={"all"}:
            fields=state["all"]
            _ensure(isinstance(fields,list) and len(fields)==2,
                    "source registry AND must have exactly two field children")
            for field in fields:
                valid_registry_field(field)
            _ensure({f["field"] for f in fields}=={"type","value"},
                    "type/value required on the same source registry Item")
        else:
            valid_registry_field(state)
            _ensure(state["field"]=="value",
                    "unpaired source registry type comparison unsupported")
        return

    if kind == "compat_oval_provider_existence":
        _ensure(source_kind != "native",
                "source provider compatibility operation cannot be native authored")
        provider=node.get("provider")
        base={"kind","source_assessment_id","source_test_id",
              "provider","using","existence"}
        expected=base|({"where"} if provider=="linux.mounts" else set())
        _ensure(set(node)==expected,"source provider compatibility node has unexpected keys")
        _ensure((provider in {"linux.textfile_matches","linux.mounts"} and
                 node["existence"]=="at_least_one_exists") or
                (provider=="windows.wmi.query" and
                 node["existence"] in {"none_exist","at_least_one_exists"}),
                "unsupported source provider existence contract")
        _ensure(all(isinstance(node[k],str) and bool(node[k])
                    for k in ("source_assessment_id","source_test_id")),
                "missing source provenance identity")
        using=node["using"]
        if provider=="windows.wmi.query":
            _ensure(isinstance(using,dict) and set(using)=={"namespace","query"},
                    "WMI fixture acquisition must name namespace and query")
            from research_b_source_wmi_lowering import validate_wmi_query
            validate_wmi_query(using["namespace"],using["query"])
            return
        if provider=="linux.mounts":
            _ensure(using=={}, "mount provider uses no acquisition inputs")
            where=node["where"]
            _ensure(isinstance(where,dict) and set(where)=={"field","equals"} and
                    where["field"]=="mount_point" and
                    isinstance(where["equals"],str) and where["equals"].startswith("/"),
                    "mount point requires an explicit absolute path")
            return
        required={"path","pattern","ignore_case","multiline","singleline"}
        _ensure(isinstance(using,dict) and set(using)==required,
                "source acquisition parameter contract mismatch")
        _ensure(isinstance(using["path"],str) and using["path"].startswith("/")
                and isinstance(using["pattern"],str) and bool(using["pattern"]),
                "source path and regex must be specified")
        _ensure(all(type(using[k]) is bool
                    for k in ("ignore_case","multiline","singleline")),
                "source regex flags must be typed booleans")
        return

    if kind == "logic":
        _ensure(set(node) == {"kind", "operator", "children"},
                "logic node has unexpected keys")
        _ensure(isinstance(node["operator"], str) and
                node["operator"] in {"all", "any"},
                "only current B AND/OR logic is supported")
        _ensure(isinstance(node["children"], list) and len(node["children"]) >= 2,
                "logic node needs two or more children")
        for child in node["children"]:
            _node(child, source_kind, depth + 1)
        return

    if kind == "fields":
        _ensure(set(node) == {"kind", "predicates"}, "field node shape invalid")
        _predicates(node["predicates"])
        _ensure(bool(node["predicates"]), "empty scoped field checks")
        return

    _ensure(kind == "collection", "unknown executable node kind")
    _ensure(not (set(node) - COLLECTION_KEYS), "unknown collection keys")
    required = {"provider", "mode", "min_count", "singleton", "using", "where", "predicates"}
    _ensure(required <= set(node), "collection missing required contract keys")
    p = node["provider"]
    _ensure(isinstance(p, str) and bool(p) and
            (p in PROVIDERS or p.startswith("$")),
            "unknown typed resource")
    _ensure(isinstance(node["mode"], str) and
            node["mode"] in {"each", "some", "none", "exactly_one"},
            "unknown collection quantifier")
    _ensure(type(node["min_count"]) is int and node["min_count"] >= 0,
            "invalid minimum-resource cardinality")
    _ensure(type(node["singleton"]) is bool and isinstance(node["using"], dict),
            "invalid resource identity or acquisition parameters")
    _predicates(node["where"])
    _predicates(node["predicates"])
    if "exists_only" in node:
        _ensure(type(node["exists_only"]) is bool, "exists_only must be Boolean")
    if "nested" in node and node["nested"] is not None:
        _node(node["nested"], source_kind, depth + 1)
    if "parent_ref" in node and node["parent_ref"] is not None:
        ref = node["parent_ref"]
        _ensure(isinstance(ref, dict) and set(ref) == {"alias", "relation"} and
                all(isinstance(v, str) and bool(v) for v in ref.values()),
                "invalid nested parent identity")


def _classify(node, depth=0):
    """Make compiler-owned source compatibility impossible to conceal."""
    _ensure(depth <= 64 and isinstance(node, dict) and
            isinstance(node.get("kind"), str), "invalid or excessive requirement tree")
    kind = node["kind"]
    if kind == "manual_procedure":
        return {"manual"}
    if kind in {"compat_oval_test","compat_oval_provider_existence",
                "compat_oval_provider_state","compat_oval_registry_view_invariant"}:
        return {"compiler-compatibility"}
    if kind == "logic":
        result = set()
        for child in node["children"]:
            result.update(_classify(child, depth + 1))
        return result
    if kind == "collection" and isinstance(node.get("nested"), dict):
        return {"native"} | _classify(node["nested"], depth + 1)
    return {"native"}


def _semantic_payload(assessment_id, root):
    _ensure(isinstance(assessment_id, str) and bool(assessment_id),
            "assessment identity is required")
    kinds = _classify(root)
    if kinds == {"manual"}:
        source_kind = "manual"
    elif kinds == {"native"}:
        source_kind = "native"
    elif kinds == {"compiler-compatibility"}:
        source_kind = "compiler-compatibility"
    else:
        source_kind = "mixed"
    _node(root, source_kind)
    return {
        "format": FORMAT,
        "scope": SCOPE,
        "assessment_id": assessment_id,
        "source_kind": source_kind,
        "catalog_version": CATALOG["catalog_version"],
        "evidence_contract": CATALOG["evidence_contract"],
        "root": root,
    }


def encode(assessment_id, root):
    """Compile-side deterministic bytes for one fixture-only Assessment.

    An actual scanner must independently verify an outer signed bundle
    and must implement the full source lowering/evidence provenance model.
    This digest is a corruption check, NOT an authenticity signature.
    """
    obj = _semantic_payload(assessment_id, root)
    obj["payload_sha256"] = hashlib.sha256(_canonical(obj)).hexdigest()
    return _canonical(obj) + b"\n"


def decode(raw):
    """Scanner-side strict version/shape/corruption gate for this experiment."""
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    _ensure(isinstance(raw, bytes) and len(raw) <= 2_000_000,
            "missing or oversized JSON")
    try:
        obj = json.loads(raw, object_pairs_hook=_unique_pairs,
                         parse_constant=lambda value:
                         (_ for _ in ()).throw(ValueError("non-finite number: " + value)))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("B compiled fixture IR: invalid JSON") from exc
    _ensure(isinstance(obj, dict), "envelope must be a JSON object")
    expected = {"format", "scope", "assessment_id", "source_kind",
                "catalog_version", "evidence_contract", "root", "payload_sha256"}
    _ensure(set(obj) == expected, "invalid envelope properties")
    _ensure(obj["format"] == FORMAT and obj["scope"] == SCOPE,
            "unsupported compiled IR version or scope")
    _ensure(obj["catalog_version"] == CATALOG["catalog_version"] and
            obj["evidence_contract"] == CATALOG["evidence_contract"],
            "wrong typed provider or fixture evidence contract")
    proof = obj.pop("payload_sha256")
    _ensure(isinstance(proof, str) and len(proof) == 64 and
            hashlib.sha256(_canonical(obj)).hexdigest() == proof,
            "content digest mismatch")
    reconstructed = _semantic_payload(obj["assessment_id"], obj["root"])
    _ensure(obj == reconstructed, "declared provenance and actual IR differ")
    return reconstructed


def evaluate_json(raw, fixtures):
    from research_native_contract_evaluator import evaluate
    return evaluate(decode(raw)["root"], fixtures)
