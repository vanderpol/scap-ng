#!/usr/bin/env python3
"""Print every selected check text, with stable source-order ordinals for reading."""
import argparse
import json
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("family", choices=("rhel_9", "ms_windows_server_2025"))
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--count", type=int, default=40)
    args = parser.parse_args()
    payload = json.loads((Path(__file__).parent / "evidence" / f"{args.family}.json").read_text())
    for rule in payload["rules"][args.start - 1:args.start - 1 + args.count]:
        print(f"\n[{rule['ordinal']}] {rule['id']} {rule['version']}: {rule['title']}")
        texts = list(dict.fromkeys(t for check in rule["checks"] for t in check["content"] if t.strip()))
        for text in texts:
            print(text.strip())
