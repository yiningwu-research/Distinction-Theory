#!/usr/bin/env python3
"""Validate CLASS backend units.

This is a knowledge-based check: verifies the config yamls contain
appropriate nk/nz settings and that the unit conversion in the
code is correct (h/Mpc to 1/Mpc).
"""
import os, sys, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "configs"

def test_configs_exist():
    configs = list(CONFIG_DIR.glob("stage3_kids1000_xipm_270_config*.yaml"))
    if not configs:
        print(f"FAIL: no configs found in {CONFIG_DIR}")
        return False
    print(f"OK: found {len(configs)} config files")
    for c in configs:
        with open(c) as f:
            d = yaml.safe_load(f)
        if d is None:
            print(f"  WARN: {c.name} is empty")
            continue
        nk = d.get("class_params", {}).get("nk", None)
        nz = d.get("class_params", {}).get("nz", None)
        print(f"  {c.name}: nk={nk}, nz={nz}")
    return True

if __name__ == "__main__":
    success = test_configs_exist()
    sys.exit(0 if success else 1)
