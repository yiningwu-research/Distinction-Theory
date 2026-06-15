#!/usr/bin/env python3
"""Verify files listed in PHASE3_MANIFEST.json."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest",
        nargs="?",
        default="PHASE3_MANIFEST.json",
        help="Manifest path relative to the project root.",
    )
    args = parser.parse_args()

    manifest_path = ROOT / args.manifest
    manifest = json.loads(manifest_path.read_text())

    missing = []
    mismatched = []
    checked = 0

    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        if not path.exists():
            missing.append(entry["path"])
            continue
        checked += 1
        digest = sha256_file(path)
        size = path.stat().st_size
        if digest != entry["sha256"] or size != entry["bytes"]:
            mismatched.append(
                {
                    "path": entry["path"],
                    "expected_sha256": entry["sha256"],
                    "actual_sha256": digest,
                    "expected_bytes": entry["bytes"],
                    "actual_bytes": size,
                }
            )

    result = {
        "manifest": args.manifest,
        "checked": checked,
        "missing": missing,
        "mismatched": mismatched,
        "ok": not missing and not mismatched,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
