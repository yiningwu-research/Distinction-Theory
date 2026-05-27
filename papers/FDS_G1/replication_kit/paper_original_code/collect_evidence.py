#!/usr/bin/env python3
from __future__ import annotations

import argparse, glob, json
from pathlib import Path
import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tables-dir", default="outputs/tables")
    ap.add_argument("--out", default="outputs/tables/evidence_comparison.csv")
    args = ap.parse_args()

    rows = []
    for path in glob.glob(str(Path(args.tables_dir) / "*_nested_evidence.json")):
        with open(path) as f:
            rows.append(json.load(f))
    if not rows:
        raise FileNotFoundError("No *_nested_evidence.json files found.")

    df = pd.DataFrame(rows).sort_values("logZ", ascending=False)
    df["Delta_logZ"] = df["logZ"] - df["logZ"].max()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
