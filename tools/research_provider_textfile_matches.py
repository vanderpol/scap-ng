#!/usr/bin/env python3
"""#235: bounded read-only, fixture-tested text file regex evidence collector.

Implements a narrow NATIVE Python-regex model with explicit acquisition
identity, diagnostic statuses and match-instance items. Does not replicate
full OVAL 5.12.3 independent.textfilecontent54 object/item/variable semantics,
filesystem all, collation, regex engine, encoding or scanner execution.
"""
from __future__ import annotations
from pathlib import Path
import re

PROVIDER="linux.textfile_matches"
VERSION="0.1.0"

def collect(*,path,pattern,ignore_case=False,multiline=True,singleline=False,
            max_bytes=1024*1024,max_matches=10000):
    using={"path":path,"pattern":pattern,"ignore_case":ignore_case,
           "multiline":multiline,"singleline":singleline}
    if any(type(x)!=bool for x in (ignore_case,multiline,singleline)):
        raise ValueError("regex mode settings must be Boolean")
    if not isinstance(path,str) or not path.startswith("/"):
        raise ValueError("text file path must be absolute")
    if not isinstance(pattern,str) or not pattern or len(pattern)>4096:
        raise ValueError("regex must be a nonempty bounded string")
    if any(type(x)!=int or x<1 for x in (max_bytes,max_matches)):
        raise ValueError("read limits must be positive integers")
    flags=(re.IGNORECASE if ignore_case else 0)
    flags|=re.MULTILINE if multiline else 0
    flags|=re.DOTALL if singleline else 0
    try:
        expression=re.compile(pattern,flags=flags)
    except re.error as exc:
        raise ValueError("invalid acquisition regex: "+str(exc)) from exc
    diagnostics=[]
    items=[]
    status="complete"
    target=Path(path)
    if target.is_symlink():
        # Source's 'filesystem: all' and symlink handling aren't proved:
        # refuse to silently consider the path scanned.
        diagnostics.append({"reason":"symlink_semantics_unimplemented","path":path})
        status="incomplete"
    else:
        try:
            with target.open("rb") as stream:
                data=stream.read(max_bytes+1)
            if len(data)>max_bytes:
                status="incomplete"
                diagnostics.append({"reason":"file_byte_limit","limit":max_bytes})
            else:
                try:
                    text=data.decode("utf-8")
                except UnicodeDecodeError:
                    status="incomplete"
                    diagnostics.append({"reason":"file_encoding_unsupported"})
                else:
                    for match in expression.finditer(text):
                        if len(items)>=max_matches:
                            status="incomplete"
                            diagnostics.append({"reason":"match_limit","limit":max_matches})
                            break
                        index=len(items)+1
                        items.append({
                            "id":path+"#"+str(index),
                            "fields":{
                                "full_path":path,
                                "instance":index,
                                "match_text":match.group(0),
                                "start_offset":match.start(),
                                "end_offset":match.end(),
                            },
                        })
        except FileNotFoundError:
            # A successfully determined absent file produces an empty
            # population; it is NOT equivalent to a failed enumeration.
            pass
        except (OSError,PermissionError) as exc:
            status="error"
            diagnostics.append({"reason":"file_read_error","detail":str(exc)})
    return {
        "provider":PROVIDER,
        "version":VERSION,
        "using":using,
        "status":status,
        "items":items,
        "diagnostics":diagnostics,
    }
