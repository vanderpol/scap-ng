#!/usr/bin/env python3
"""#235 read-only experimental account-home file evidence provider.

Accepts a PRESELECTED and complete list of accounts. Does not enumerate the
system's passwd DB; does not recursively follow subdirectories. Explicit
source-parity limits: cannot claim to implement original unix.file OVAL object
with max_depth 1, recurse symlinks or filesystem all.
"""
from __future__ import annotations
import os
import stat
from pathlib import Path

ID="linux.files_from_account_homes"
VERSION="0.1.0"

def collect(account_rows, *, filename_pattern, max_items=10000,
            follow_symlinks=False):
    import re
    if not isinstance(account_rows,list):
        raise ValueError("account_rows must be a selected, validated list")
    if not isinstance(max_items,int) or max_items<1:
        raise ValueError("max_items must be a positive integer")
    if not isinstance(follow_symlinks,bool):
        raise ValueError("follow_symlinks must be Boolean")
    if not isinstance(filename_pattern,str):
        raise ValueError("filename_pattern must be a string")
    pattern=re.compile(filename_pattern)
    items=[]
    diagnostics=[]
    seen_ids=set()
    truncated=False
    for account in account_rows:
        if not isinstance(account,dict) or not all(
           isinstance(account.get(k),str) and account.get(k)
           for k in ("id","username","home_dir")):
            raise ValueError("account requires stable string id/username/home_dir")
        home=Path(account["home_dir"])
        if not home.is_absolute():
            raise ValueError("account home_dir must be absolute")
        try:
            with os.scandir(home) as iterator:
                entries=sorted(iterator,key=lambda row: row.name)
        except OSError as exc:
            diagnostics.append({"account_id":account["id"],"directory":str(home),
                                "reason":"home enumeration failed","detail":str(exc)})
            continue
        for entry in entries:
            if not pattern.search(entry.name):
                continue
            try:
                data=entry.stat(follow_symlinks=follow_symlinks)
            except OSError as exc:
                diagnostics.append({"account_id":account["id"],"directory":str(home),
                                    "entry":entry.name,"reason":"stat failed","detail":str(exc)})
                continue
            if stat.S_ISDIR(data.st_mode):
                continue
            if len(items)>=max_items:
                truncated=True
                break
            key=account["id"]+"::"+os.path.join(str(home),entry.name)
            if key in seen_ids:
                diagnostics.append({"account_id":account["id"],"entry":entry.name,
                                    "reason":"duplicate per-account file identity"})
                continue
            seen_ids.add(key)
            items.append({
                "id":key,
                "account_id":account["id"],
                "directory":str(home),
                "name":entry.name,
                "kind":"file" if stat.S_ISREG(data.st_mode) else "other",
                "mode":stat.S_IMODE(data.st_mode),
                "path":os.path.join(str(home),entry.name),
                "is_symlink":entry.is_symlink(),
                "follow_symlinks":follow_symlinks,
            })
        if truncated:
            diagnostics.append({"reason":"max_items reached","max_items":max_items})
            break
    return {
        "provider":ID,
        "version":VERSION,
        "status":"incomplete" if diagnostics or truncated else "complete",
        "items":items,
        "accounts_requested":len(account_rows),
        "diagnostics":diagnostics,
        "max_depth":1,
        "symlink_files_followed":follow_symlinks,
    }
