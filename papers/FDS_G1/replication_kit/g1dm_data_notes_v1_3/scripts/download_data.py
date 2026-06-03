#!/usr/bin/env python3
"""Data download / acquisition planner for G1DM data notes.

This script deliberately avoids blind downloading of very large cosmology products.
It prints official landing pages and expected local paths, and can create local folders.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import textwrap
import requests
from tqdm import tqdm

from g1dm.io import read_yaml, ensure_dir


def download_url(url: str, dest: Path, chunk_size: int = 1024 * 1024):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))


def print_plan(registry: dict):
    print("\nG1DM public data acquisition plan\n" + "=" * 38)
    for key, meta in registry["datasets"].items():
        print(f"\n[{key}]")
        print(f"purpose: {meta.get('purpose','')}")
        for field in ["official_doc", "official_home", "archive", "data_url", "github", "paper"]:
            if field in meta:
                print(f"{field}: {meta[field]}")
        print(f"expected_local: {meta.get('expected_local','')}")
        notes = meta.get("notes", "")
        if notes:
            print("notes:")
            print(textwrap.indent(notes.strip(), "  "))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="config/data_registry.yml")
    ap.add_argument("--print-plan", action="store_true")
    ap.add_argument("--make-dirs", action="store_true")
    args = ap.parse_args()

    registry = read_yaml(args.registry)
    if args.print_plan:
        print_plan(registry)
    if args.make_dirs:
        for meta in registry["datasets"].values():
            loc = meta.get("expected_local")
            if loc:
                ensure_dir(loc)
                print(f"created: {loc}")


if __name__ == "__main__":
    main()
