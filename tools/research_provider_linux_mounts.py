#!/usr/bin/env python3
"""Research #235: real, READ-ONLY Linux mounts collection via /proc/self/mountinfo.

Version v0.1. Returns actual kernel mount IDs, options and mount namespace.
Not a production scanner, not OVAL linux.partition parity, not a standard
SCAP-NG provider. Only the caller's mount namespace is visible.
"""
from __future__ import annotations
from pathlib import Path
import os
import re

PROVIDER="linux.mounts"
VERSION="0.1.0"
OCTAL_ESCAPES={"040":" ","011":"\t","012":"\n","134":"\\"}
ESCAPE=re.compile(r"\\([0-7]{3})")

def decode_mountinfo_path(text):
    if not isinstance(text,str) or not text:raise ValueError("invalid empty mountinfo path")
    def replace(m):
        sequence=m.group(1)
        if sequence not in OCTAL_ESCAPES:
            raise ValueError("unrecognized mountinfo escape: "+sequence)
        return OCTAL_ESCAPES[sequence]
    value=ESCAPE.sub(replace,text)
    if "\\" in value and "\\" not in text.replace(r"\134",""):
        # Kernel strings should use only documented octal sequences.
        raise ValueError("unrecognized mountinfo path escape")
    if not value.startswith("/"):
        raise ValueError("mountinfo path must be absolute")
    return value

def parse_mountinfo_line(line, namespace):
    """A single Linux mountinfo record; source and VFS options stay separate."""
    if not isinstance(namespace,str) or not namespace:
        raise ValueError("must specify source mount namespace")
    if " - " not in line:
        raise ValueError("missing mountinfo separator")
    before,after=line.rstrip("\n").split(" - ",1)
    b=before.split()
    a=after.split()
    if len(b)<6 or len(a)<3:
        raise ValueError("truncated mountinfo record")
    try:
        mount_id=int(b[0]);parent_id=int(b[1])
        if mount_id<1 or parent_id<0:raise ValueError("invalid IDs")
    except ValueError as exc:
        raise ValueError("invalid mountinfo IDs") from exc
    if ":" not in b[2]:
        raise ValueError("missing major:minor device")
    source=a[1]
    vfs_options=b[5].split(",")
    if not all(vfs_options):
        raise ValueError("blank VFS mount option")
    item={
        "id":namespace+":"+str(mount_id),
        "fields":{
            "mount_id":mount_id,
            "parent_id":parent_id,
            "namespace":namespace,
            "major_minor":b[2],
            "root":decode_mountinfo_path(b[3]),
            "mount_point":decode_mountinfo_path(b[4]),
            "mount_options":vfs_options,
            "optional_fields":b[6:],
            "filesystem":a[0],
            "source":source,
            "super_options":a[2].split(",")
        }
    }
    return item

def parse_mountinfo_text(text, namespace):
    """Malformed lines degrade completeness, never silently disappear."""
    if not isinstance(text,str):
        raise ValueError("mountinfo must be text")
    items=[];diagnostics=[];ids=set()
    for n,line in enumerate(text.splitlines(),1):
        if not line.strip():continue
        try:
            item=parse_mountinfo_line(line,namespace)
            if item["id"] in ids:
                raise ValueError("duplicate mount identity "+item["id"])
            ids.add(item["id"])
            items.append(item)
        except ValueError as err:
            diagnostics.append({"line":n,"reason":str(err)})
    return {
        "provider":PROVIDER,
        "provider_version":VERSION,
        "status":"incomplete" if diagnostics else "complete",
        "namespace":namespace,
        "items":items,
        "diagnostics":diagnostics
    }

def collect_current_linux_mounts(path="/proc/self/mountinfo",ns_path="/proc/self/ns/mnt"):
    """Read ONLY current process mount namespace; no user-host remote access."""
    try:
        namespace=os.readlink(ns_path)
        source=Path(path).read_text(encoding="utf-8")
    except OSError as err:
        return {"provider":PROVIDER,"provider_version":VERSION,"status":"error",
                "namespace":None,"items":[],"diagnostics":[{"reason":str(err)}]}
    return parse_mountinfo_text(source,namespace)

if __name__=="__main__":
    import json
    info=collect_current_linux_mounts()
    print(json.dumps({"provider":info["provider"],"version":info["provider_version"],
         "collection_status":info["status"],"namespace":info["namespace"],
         "total_items":len(info["items"]),"diagnostics":info["diagnostics"],
         "home_mounts":[{"mount_id":x["fields"]["mount_id"],
                         "mount_options":x["fields"]["mount_options"]}
                        for x in info["items"] if x["fields"]["mount_point"]=="/home"]},indent=2))
