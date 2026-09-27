#!/usr/bin/env python3
"""Render one normalized SCAP-NG semantic assessment into candidate YAML styles."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import yaml


class Quoted(str):
    pass


def quoted_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


yaml.SafeDumper.add_representer(Quoted, quoted_presenter)


def matrix_from_semantic(s):
    cov=s["required_coverage"]
    return {
        "syscall":cov["syscalls"],
        "architecture":cov["architectures"],
        "subject":cov["subjects"],
    }


def original(doc):
    s=doc["semantic"]
    src=doc["source"]
    return {
      "scap_ng":"0.1-prototype",
      "prototype":True,
      "assessment":{
        "id":f"NG-{src['rule_id']}",
        "description":src.get("title"),
        "collect":{
          "configured_audit_rules":{
            "capability":s["capability"],
            "source":s["source"],
          }
        },
        "derive":{"required_coverage":{"matrix":matrix_from_semantic(s)}},
        "assert":{
          "every":{
            "item":"$derived.required_coverage",
            "satisfies":{
              "covered_by_audit_rule":{
                "rules":"$configured_audit_rules",
                "required":"$item",
                "action":{"equivalent_to":s["required_coverage"]["action_equivalent_to"]},
              }
            },
          }
        },
        "migration":{
          "source_rule":src["rule_id"],
          "source_definition":src["definition_id"],
          "status":doc["migration_status"],
          "semantic_fingerprint_sha256":doc["semantic_fingerprint_sha256"],
        },
      },
    }


def ansible(doc):
    s=doc["semantic"]
    src=doc["source"]
    return {
      "scap_ng":"0.1-prototype",
      "prototype":True,
      "authoring_style":"ansible-inspired",
      "runtime_dependency":"none",
      "assessment":{
        "id":f"NG-{src['rule_id']}",
        "name":src.get("title"),
        "steps":[
          {
            "name":"Read configured audit rules",
            "collect":{
              "capability":"scapng."+s["capability"],
              "source":s["source"],
            },
            "register":"configured_audit_rules",
          },
          {
            "name":"Build required syscall audit coverage",
            "derive":{"matrix":matrix_from_semantic(s)},
            "register":"required_coverage",
          },
        ],
        "assert":{
          "that":{
            "every":{
              "item":"required_coverage",
              "satisfies":{
                "covered_by_audit_rule":{
                  "rules":"configured_audit_rules",
                  "required":"item",
                  "action":{"equivalent_to":s["required_coverage"]["action_equivalent_to"]},
                }
              },
            }
          }
        },
        "migration":{
          "source_rule":src["rule_id"],
          "source_definition":src["definition_id"],
          "status":doc["migration_status"],
          "semantic_fingerprint_sha256":doc["semantic_fingerprint_sha256"],
        },
      },
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("--style",choices=["original","ansible-inspired"],required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    doc=json.loads(args.input.read_text())
    out=original(doc) if args.style=="original" else ansible(doc)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(yaml.safe_dump(out,sort_keys=False,width=100,allow_unicode=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
