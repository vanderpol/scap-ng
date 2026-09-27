#!/usr/bin/env python3
"""Verify prototype .scapng member hashes and Ed25519 manifest signature."""
from __future__ import annotations
import argparse, base64, hashlib, json, zipfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("bundle",type=Path); args=ap.parse_args()
    with zipfile.ZipFile(args.bundle) as z:
        mb=z.read("META-INF/manifest.json"); manifest=json.loads(mb)
        sig=json.loads(z.read("META-INF/signature.prototype.json"))
        if hashlib.sha256(mb).hexdigest()!=sig["manifest_sha256"]: raise SystemExit("manifest digest mismatch")
        key=Ed25519PublicKey.from_public_bytes(base64.b64decode(sig["public_key_raw_base64"]))
        key.verify(base64.b64decode(sig["signature_base64"]),mb)
        expected={"META-INF/manifest.json","META-INF/signature.prototype.json"}|{x["path"] for x in manifest["files"]}
        if set(z.namelist())!=expected: raise SystemExit("unexpected or missing package members")
        for item in manifest["files"]:
            data=z.read(item["path"])
            if len(data)!=item["size"] or hashlib.sha256(data).hexdigest()!=item["sha256"]:
                raise SystemExit(f"member integrity failure: {item['path']}")
    print(f"OK: {args.bundle}")
    return 0
if __name__=="__main__": raise SystemExit(main())
