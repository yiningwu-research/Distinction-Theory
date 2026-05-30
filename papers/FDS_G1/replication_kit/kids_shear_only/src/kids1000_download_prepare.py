#!/usr/bin/env python3
"""
KiDS-1000 Stage-3 downloader / preparer for FDS-G1 lensing tests.

This script intentionally does two separate things:
  1. download/extract the public KiDS-1000 3x2pt data repository;
  2. build a file manifest and candidate map for Stage-3 FDS-G1 adapters.

The KiDS repository contains multiple products: CosmoSIS FITS cubes, ascii
xi_pm measurements, n(z), covariance matrices, BOSS clustering products, and
plotting data.  Survey products are not all in the simple CSV format expected
by stage3_lensing_3x2pt.py, so this script first creates an auditable manifest.
If simple ascii xipm/nofz/covariance candidates are recognized, it also writes a
starter config that the user can edit.

For production 3x2pt evidence, prefer a survey-specific likelihood or a SACC /
CosmoSIS adapter.  This preparer is meant to make the data ingest auditable and
repeatable.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List

DEFAULT_REPO_ZIP = "https://github.com/KiDS-WL/Cat_to_Obs_K1000_P1/archive/refs/heads/master.zip"

CATEGORIES = {
    "xipm_ascii": ["xipm", "xi_pm", "xiplus", "ximinus"],
    "gammat_ascii": ["gammat", "gamma_t", "gt"],
    "wtheta_ascii": ["wtheta", "w_theta", "clustering"],
    "covariance": ["cov", "covariance"],
    "nofz": ["nofz", "nz", "redshift"],
    "fits_cube": [".fits", ".fit"],
    "data_plot": ["data_plot", "dataplot", "data_plots"],
}

TEXT_EXT = {".txt", ".dat", ".asc", ".ascii", ".csv", ".tsv", ".list"}


def download(url: str, dest: Path, overwrite: bool = False) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not overwrite:
        print(f"[download] exists: {dest}")
        return
    print(f"[download] {url}")
    with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    print(f"[download] wrote {dest} ({dest.stat().st_size/1e6:.2f} MB)")


def extract_zip(zip_path: Path, out_dir: Path, overwrite: bool = False) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    marker = out_dir / ".extracted"
    if marker.exists() and not overwrite:
        roots = [p for p in out_dir.iterdir() if p.is_dir()]
        if roots:
            print(f"[extract] using existing {roots[0]}")
            return roots[0]
    if overwrite and out_dir.exists():
        for p in out_dir.iterdir():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
    print(f"[extract] {zip_path} -> {out_dir}")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(out_dir)
    marker.write_text("ok\n")
    roots = [p for p in out_dir.iterdir() if p.is_dir()]
    if not roots:
        raise RuntimeError("No extracted directory found")
    return roots[0]


def classify(path: Path) -> List[str]:
    s = str(path).lower()
    cats = []
    for cat, keys in CATEGORIES.items():
        for k in keys:
            if k in s:
                if cat == "fits_cube" and path.suffix.lower() not in {".fits", ".fit"}:
                    continue
                cats.append(cat)
                break
    return sorted(set(cats))


def inspect_text_file(path: Path, max_lines: int = 5) -> Dict[str, object]:
    info: Dict[str, object] = {"n_header_lines": 0, "n_columns_guess": None, "first_data_line": None}
    if path.suffix.lower() not in TEXT_EXT:
        return info
    try:
        with open(path, "r", errors="ignore") as f:
            lines = []
            for _ in range(max_lines + 20):
                line = f.readline()
                if not line:
                    break
                lines.append(line.strip())
        data_line = None
        header_count = 0
        for line in lines:
            if not line or line.startswith("#"):
                header_count += 1
                continue
            toks = re.split(r"[\s,]+", line.strip())
            numeric = 0
            for t in toks:
                try:
                    float(t)
                    numeric += 1
                except ValueError:
                    pass
            if numeric >= 2:
                data_line = line
                info["n_columns_guess"] = len(toks)
                break
            else:
                header_count += 1
        info["n_header_lines"] = header_count
        info["first_data_line"] = data_line
    except Exception as e:
        info["error"] = str(e)
    return info


def build_manifest(root: Path, out_dir: Path) -> Dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    candidates: Dict[str, List[str]] = {k: [] for k in CATEGORIES}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        cats = classify(rel)
        try:
            size = p.stat().st_size
        except OSError:
            size = -1
        tinfo = inspect_text_file(p)
        row = {
            "path": str(rel),
            "suffix": p.suffix.lower(),
            "size_bytes": size,
            "categories": ";".join(cats),
            "n_columns_guess": tinfo.get("n_columns_guess"),
            "first_data_line": tinfo.get("first_data_line"),
        }
        rows.append(row)
        for c in cats:
            candidates[c].append(str(rel))
    with open(out_dir / "manifest.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["path"])
        w.writeheader()
        w.writerows(rows)
    summary = {
        "root": str(root),
        "n_files": len(rows),
        "candidates": candidates,
    }
    (out_dir / "manifest.json").write_text(json.dumps(summary, indent=2))
    print(f"[manifest] {len(rows)} files -> {out_dir/'manifest.csv'}")
    for k, v in candidates.items():
        print(f"  {k:14s}: {len(v)} candidates")
    return summary


def write_config_template(out_dir: Path) -> None:
    txt = """# Starter template for stage3_lensing_3x2pt.py.
# Fill these paths after inspecting manifest.csv / manifest.json.
# The current Stage-3 prototype expects real-space xip/xim/gammat/wtheta CSVs.
# KiDS-1000 official products may be bandpowers or CosmoSIS FITS cubes, so a
# survey-specific adapter may be required before production evidence runs.

data_vector_csv: REPLACE_WITH_CONVERTED_DATA_VECTOR.csv
covariance_txt: REPLACE_WITH_MATCHING_COVARIANCE.txt
rbh_table: REPLACE_WITH_G1_RBH_TABLE.csv

z_min: 0.001
z_max: 2.0
nz_grid: 160
ell_min: 5.0
ell_max: 3000.0
nell: 180

vary_lens_bias: true
lens_bias_bounds: [0.5, 3.0]
vary_shear_m: true
shear_m_bounds: [-0.08, 0.08]

sources:
  - {name: src0, nz_file: REPLACE_WITH_SOURCE_NZ_0.csv, m: 0.0}
  - {name: src1, nz_file: REPLACE_WITH_SOURCE_NZ_1.csv, m: 0.0}

lenses:
  - {name: lens0, nz_file: REPLACE_WITH_LENS_NZ_0.csv, bias: 1.5}
  - {name: lens1, nz_file: REPLACE_WITH_LENS_NZ_1.csv, bias: 1.7}
"""
    (out_dir / "stage3_config_template.yaml").write_text(txt)
    print(f"[config] wrote {out_dir/'stage3_config_template.yaml'}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="stage3_kids1000", help="Output directory")
    ap.add_argument("--url", default=DEFAULT_REPO_ZIP, help="Repo zip URL")
    ap.add_argument("--from-existing", default=None, help="Scan an existing extracted repo instead of downloading")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--no-download", action="store_true", help="Only write template files")
    args = ap.parse_args()

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    data_root = None
    if args.from_existing:
        data_root = Path(args.from_existing).resolve()
        if not data_root.exists():
            raise SystemExit(f"Missing --from-existing path: {data_root}")
    elif not args.no_download:
        zip_path = out / "raw" / "kids1000_repo.zip"
        download(args.url, zip_path, overwrite=args.overwrite)
        data_root = extract_zip(zip_path, out / "raw" / "extracted", overwrite=args.overwrite)
    else:
        print("[no-download] writing template only")

    write_config_template(out)
    if data_root:
        build_manifest(data_root, out)
        print("\nNext steps:")
        print(f"  1. Inspect {out/'manifest.csv'}")
        print("  2. Convert chosen survey product into the generic Stage-3 CSV format")
        print(f"  3. Edit {out/'stage3_config_template.yaml'}")
        print("  4. Run stage3_lensing_3x2pt.py --config <edited.yaml> --model m34")


if __name__ == "__main__":
    main()
