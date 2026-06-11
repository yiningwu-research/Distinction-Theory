from __future__ import annotations

import argparse
import json

from .config import load_config
from .pipeline import run_precheck


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the FDS-G1 CMB-lensing pre-production stress test.")
    p.add_argument("config", help="YAML configuration file")
    return p


def main() -> None:
    args = build_parser().parse_args()
    cfg = load_config(args.config)
    summary = run_precheck(cfg)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
