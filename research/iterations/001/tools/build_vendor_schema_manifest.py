#!/usr/bin/env python3
"""Create a deterministic manifest for a vendored schema directory."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import sys

root=Path(sys.argv[1])
files=[]
for p in sorted(root.rglob("*")):
    if not p.is_file() or p.name=="VENDOR-MANIFEST.json":
        continue
    data=p.read_bytes()
    files.append({
        "path": p.relative_to(root).as_posix(),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    })
out={
    "source_repository":"vanderpol/scap-content",
    "source_revision":"32ab7642b4d9e9eb02476d59698dd3f83ae0e282",
    "source_path":"schemas/scap-1.4-oval-5.12.3",
    "files":files,
}
(root/"VENDOR-MANIFEST.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print(f"Manifested {len(files)} vendored schema files")
