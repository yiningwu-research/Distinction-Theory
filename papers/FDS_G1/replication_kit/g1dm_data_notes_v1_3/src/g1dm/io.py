"""I/O helpers for G1DM data-note prototypes."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional
import re
import yaml
import numpy as np
import pandas as pd


def read_yaml(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def find_files(root: str | Path, patterns: Iterable[str]) -> list[Path]:
    root = Path(root)
    out: list[Path] = []
    if not root.exists():
        return out
    for pat in patterns:
        out.extend(root.rglob(pat))
    return sorted(set(out))


def read_cosmomc_paramnames(path: str | Path) -> list[str]:
    """Read a CosmoMC/GetDist .paramnames file.

    Returns raw parameter names, stripping LaTeX labels and comments.
    """
    names = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            names.append(line.split()[0].replace("*", ""))
    return names


def read_cosmomc_chains(
    chain_dir: str | Path,
    paramnames: Optional[str | Path] = None,
    include_weights: bool = True,
) -> pd.DataFrame:
    """Read CosmoMC-style chains from a folder.

    Expected format: text files with first column weight, second column -loglike,
    then parameter values. If a .paramnames file is found, it is used for names.

    This reader is intentionally permissive. It is meant for public Planck/DESI chains
    with slightly different naming conventions.
    """
    chain_dir = Path(chain_dir)
    if not chain_dir.exists():
        raise FileNotFoundError(f"Chain directory not found: {chain_dir}")

    if paramnames is None:
        candidates = list(chain_dir.glob("*.paramnames")) + list(chain_dir.rglob("*.paramnames"))
        paramnames = candidates[0] if candidates else None

    txts = []
    # common CosmoMC names: root_1.txt, root.1.txt, *.txt but avoid paramnames/readme
    for p in chain_dir.rglob("*.txt"):
        name = p.name.lower()
        if any(x in name for x in ["readme", "param", "log"]):
            continue
        txts.append(p)
    if not txts:
        raise FileNotFoundError(f"No chain .txt files found under {chain_dir}")

    arrays = []
    for p in sorted(txts):
        try:
            a = np.loadtxt(p)
        except Exception:
            continue
        if a.ndim == 1:
            a = a[None, :]
        if a.shape[1] >= 4:
            arrays.append(a)
    if not arrays:
        raise ValueError(f"No readable chain arrays found under {chain_dir}")
    arr = np.vstack(arrays)

    if paramnames is not None and Path(paramnames).exists():
        names = read_cosmomc_paramnames(paramnames)
    else:
        names = [f"p{i}" for i in range(arr.shape[1] - 2)]

    npars = arr.shape[1] - 2 if include_weights else arr.shape[1]
    names = names[:npars]
    if include_weights:
        df = pd.DataFrame(arr[:, 2:2 + len(names)], columns=names)
        df.insert(0, "minusloglike", arr[:, 1])
        df.insert(0, "weight", arr[:, 0])
    else:
        df = pd.DataFrame(arr[:, :len(names)], columns=names)
        df.insert(0, "weight", 1.0)
    return df


def load_chain_columns(
    chain_dir: str | Path,
    columns: list[str],
    paramnames: str | Path | None = None,
) -> pd.DataFrame:
    """Read CosmoMC-style chains and return only requested columns.

    Uses the existing read_cosmomc_chains backbone. If requested columns
    are not found by name, find_parameter is used with column-name candidates
    (case-insensitive, regex). Returns a DataFrame with a 'weight' column
    and the requested parameter columns.

    Raises
    ------
    FileNotFoundError
        If chain_dir does not exist or has no chain files.
    KeyError
        If a requested column cannot be found.
    """
    df = read_cosmomc_chains(chain_dir, paramnames=paramnames, include_weights=True)
    col_names = list(df.columns)
    result_cols = {}
    for col_req in columns:
        found = find_parameter(df, [col_req])
        result_cols[found] = col_req
    keep = ["weight"] + list(result_cols)
    out = df[keep].copy()
    rename_map = {k: v for k, v in result_cols.items() if k != v}
    if rename_map:
        out = out.rename(columns=rename_map)
    return out


def find_parameter(df: pd.DataFrame, candidates: Iterable[str]) -> str:
    """Find a parameter in a DataFrame using exact/case-insensitive/regex matching."""
    cols = list(df.columns)
    for c in candidates:
        if c in cols:
            return c
    lower = {c.lower(): c for c in cols}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    for pattern in candidates:
        regex = re.compile(pattern, re.IGNORECASE)
        for col in cols:
            if regex.fullmatch(col) or regex.search(col):
                return col
    raise KeyError(f"Could not find any of {list(candidates)} in columns: {cols[:20]}...")


def weighted_quantile(x: np.ndarray, q: float | list[float], w: Optional[np.ndarray] = None) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    qarr = np.atleast_1d(q)
    if w is None:
        return np.quantile(x, qarr)
    w = np.asarray(w, dtype=float)
    sorter = np.argsort(x)
    x = x[sorter]
    w = w[sorter]
    cdf = np.cumsum(w) / np.sum(w)
    return np.interp(qarr, cdf, x)
