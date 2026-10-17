#!/usr/bin/env python3
"""Research #235: read-only Apache configuration EVIDENCE discovery, not evaluator.

Loads a deliberately restricted static subset of Include/IncludeOptional into
source-positioned directive evidence. Fails closed as INCOMPLETE for unsupported
contexts/macros/path escapes, never invents the Apache effective configuration.
It does not invoke httpd, grep, shell, or read live hosts in CI. Rooted fixture
collections only; this is NOT parity with source OVAL shellcommand probes.
"""
from __future__ import annotations

from pathlib import Path
import glob
import itertools
import re
import shlex

PROVIDER="apache.config_directives"
VERSION="0.1.0"
DIRECTIVES={"keepalive":"KeepAlive","maxkeepaliverequests":"MaxKeepAliveRequests"}
MAX_INCLUDE_DEPTH=24
LINE=re.compile(r"^\s*([A-Za-z][A-Za-z0-9]*)\b(?:\s+(.*?))?\s*$")


def collect(root_config: str|Path, *, server_root: str|Path, max_files=500,
            max_directives=10000, max_depth=MAX_INCLUDE_DEPTH,
            max_bytes_per_file=2000000):
    """Return exact directive lines with file/line and explicit coverage status.

    File include order is retained (no sorting except deterministic glob
    expansion); all matching raw directive lines are collected. This does NOT
    decide inherited scopes, precedence, effective values or active contexts.
    """
    if any(not isinstance(x,int) or isinstance(x,bool) or x<1
           for x in (max_files,max_directives,max_depth,max_bytes_per_file)):
        raise ValueError("all collection limits must be positive integers")
    server_root=Path(server_root).resolve(strict=True)
    if not server_root.is_dir(): raise ValueError("server_root must be a directory")
    if not Path(root_config).is_absolute(): raise ValueError("root_config must be absolute")
    root=Path(root_config).resolve(strict=False)
    diagnostics=[]
    files=[]
    directives=[]
    traversing=set()
    seen=set()
    limits_hit=False

    def note(reason, **context):
        diagnostics.append({"reason":reason,**context})

    def inside(path:Path):
        candidate=path.resolve(strict=False)
        if not candidate.is_relative_to(server_root):
            note("path_outside_server_root",path=str(path))
            return None
        return candidate

    def visit(path:Path, depth:int):
        nonlocal limits_hit
        if limits_hit:return
        normalized=inside(path)
        if normalized is None:return
        if depth>max_depth:
            note("include_depth_limit",path=str(normalized))
            return
        if normalized in traversing:
            note("include_cycle",path=str(normalized))
            return
        if normalized in seen:
            # Different Include paths may reference one file. Keep one file
            # evidence observation and note repeated include context instead
            # of silently claiming Apache would ignore this inclusion.
            note("duplicate_include_ambiguous",path=str(normalized))
            return
        if len(seen)>=max_files:
            note("file_limit",limit=max_files)
            limits_hit=True
            return
        try:
            with normalized.open("rb") as reader:
                raw_file=reader.read(max_bytes_per_file+1)
            if len(raw_file)>max_bytes_per_file:
                note("file_byte_limit",path=str(normalized),limit=max_bytes_per_file)
                return
            text=raw_file.decode("utf-8")
        except (OSError,UnicodeError) as exc:
            note("file_unreadable",path=str(normalized),detail=str(exc))
            return
        traversing.add(normalized)
        seen.add(normalized)
        files.append(str(normalized))
        for line_number,raw in enumerate(text.splitlines(),1):
            if limits_hit:break
            stripped=raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.endswith(chr(92)):
                note("multiline_directive_unsupported",
                     path=str(normalized),line=line_number,text=stripped)
                continue
            if stripped.startswith("<"):
                note("conditional_or_container_context_unsupported",
                     path=str(normalized),line=line_number,text=stripped)
                continue
            match=LINE.match(raw)
            if not match:
                note("unparsed_config_line",path=str(normalized),line=line_number,text=raw)
                continue
            name,tail=match.group(1),match.group(2)
            value=(tail or "").strip()
            low=name.lower()
            if low in ("include","includeoptional"):
                try:
                    parsed=shlex.split(value, posix=True)
                except ValueError:
                    parsed=[]
                if len(parsed)!=1 or not parsed[0]:
                    note("unsupported_include_syntax",
                         path=str(normalized),line=line_number,text=raw)
                    continue
                pattern=parsed[0]
                if "$"+"{" in pattern or "%" in pattern:
                    note("dynamic_include_unresolved",
                         path=str(normalized),line=line_number,text=raw)
                    continue
                candidate=Path(pattern)
                if not candidate.is_absolute():candidate=server_root/candidate
                # Check literal path prefix BEFORE glob; symlinks are checked
                # again for each concrete match by inside().
                prefix=str(candidate).split("*")[0].split("?")[0].split("[")[0]
                if inside(Path(prefix)) is None:
                    note("unsafe_include_pattern",
                         path=str(normalized),line=line_number,text=raw)
                    continue
                # Cap the glob expansion itself before sorting; a huge
                # glob must not allocate an unbounded list then claim
                # collection was complete under max_files.
                expansion=list(itertools.islice(glob.iglob(str(candidate)),max_files+1))
                if len(expansion)>max_files:
                    note("glob_match_limit",limit=max_files,pattern=pattern)
                    expansion=expansion[:max_files]
                matches=sorted(Path(x) for x in expansion)
                if not matches and low=="include":
                    note("required_include_unmatched",
                         path=str(normalized),line=line_number,pattern=pattern)
                for next_path in matches:
                    if next_path.is_dir():
                        note("included_directory_unsupported",
                             path=str(normalized),line=line_number,target=str(next_path))
                        continue
                    visit(next_path,depth+1)
                continue
            if low not in DIRECTIVES:continue
            if not value:
                note("directive_without_value",path=str(normalized),
                     line=line_number, name=name)
                continue
            if "$"+"{" in value:
                note("dynamic_directive_value_unresolved",
                     path=str(normalized),line=line_number,text=raw)
                continue
            if len(directives)>=max_directives:
                note("directive_limit",limit=max_directives)
                limits_hit=True
                break
            integer_value={"field_status":"absent"}
            if low=="maxkeepaliverequests":
                if re.fullmatch(r"[0-9]+",value):
                    integer_value=int(value)
                else:
                    note("numeric_directive_not_canonical",
                         path=str(normalized),line=line_number,value=value)
                    integer_value={"field_status":"error"}
            directives.append({
                "id":str(normalized)+":"+str(line_number),
                "fields":{
                    "name":DIRECTIVES[low],
                    "raw_value":value,
                    "integer_value":integer_value,
                    "source_file":str(normalized),
                    "source_line":line_number,
                    "source_text":raw,
                }
            })
        traversing.remove(normalized)

    visit(root,0)
    return {
        "provider":PROVIDER,
        "version":VERSION,
        "status":"incomplete" if diagnostics else "complete",
        "root_file":str(root),
        "server_root":str(server_root),
        "files":files,
        "items":directives,
        "diagnostics":diagnostics,
        "effective_values_supported":False
    }
