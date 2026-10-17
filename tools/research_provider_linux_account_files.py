#!/usr/bin/env python3
"""#235 read-only streamed home-directory evidence provider, research v0.1.

Accepts an already selected and complete list of account rows; does NOT
enumerate /etc/passwd or recursively search user directories. It does NOT
claim OVAL unix.file source parity, or the original recurse: symlinks meaning.
All filesystem observations are made read-only.
"""
from __future__ import annotations
import os
import re
import stat
from pathlib import Path

ID="linux.files_from_account_homes"
VERSION="0.1.0"

def collect(account_rows, *, filename_pattern, max_items=10000,
            follow_symlinks=False):
    if not isinstance(account_rows,list):
        raise ValueError("account_rows must be a selected, validated list")
    if not isinstance(max_items,int) or isinstance(max_items,bool) or max_items<1:
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
            # Stream directory entries; do NOT sort or materialize a giant
            # directory before enforcing max_items. Stable file identity
            # is guaranteed; sample ORDER is not.
            with os.scandir(home) as entries:
                for entry in entries:
                    if not pattern.search(entry.name):
                        continue
                    try:
                        data=entry.stat(follow_symlinks=follow_symlinks)
                    except OSError as exc:
                        diagnostics.append({"account_id":account["id"],
                                            "directory":str(home),
                                            "entry":entry.name,
                                            "reason":"stat failed",
                                            "detail":str(exc)})
                        continue
                    if stat.S_ISDIR(data.st_mode):
                        continue
                    if len(items)>=max_items:
                        truncated=True
                        diagnostics.append({"reason":"max_items reached",
                                            "max_items":max_items})
                        break
                    name=os.path.join(str(home),entry.name)
                    key=account["id"]+"::"+name
                    if key in seen_ids:
                        diagnostics.append({"account_id":account["id"],
                                            "entry":entry.name,
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
                        "path":name,
                        "is_symlink":entry.is_symlink(),
                        "follow_symlinks":follow_symlinks,
                    })
        except OSError as exc:
            diagnostics.append({"account_id":account["id"],
                                "directory":str(home),
                                "reason":"home enumeration failed",
                                "detail":str(exc)})
        if truncated:
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
