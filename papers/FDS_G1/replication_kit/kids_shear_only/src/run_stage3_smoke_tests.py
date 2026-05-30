#!/usr/bin/env python3
"""End-to-end smoke tests for the FDS-G1 Stage-3 likelihood prototype.

This test uses the included mock generator because online survey downloads are
not available in all environments.  It checks that the likelihood loads, model
vectors are finite, and the M_kappa branch reproduces M3/4 at kappa=0.75.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd):
    print("$", " ".join(map(str, cmd)))
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if p.stdout:
        print(p.stdout)
    if p.stderr:
        print(p.stderr, file=sys.stderr)
    if p.returncode != 0:
        raise SystemExit(p.returncode)
    return p.stdout


def parse_last_json(stdout: str):
    # The CLI prints a single JSON object for theta-json runs.
    start = stdout.rfind("{")
    if start < 0:
        raise ValueError("No JSON object in stdout")
    return json.loads(stdout[start:])


def main():
    run([sys.executable, "-m", "py_compile", "stage3_lensing_3x2pt.py", "kids1000_download_prepare.py"])
    run([sys.executable, "make_stage3_mock.py"])
    cfg = ROOT / "stage3_mock" / "config.yaml"
    theta_m34 = json.dumps({"Omega_m":0.30,"h":0.68,"Omega_b":0.049,"sigma8":0.80,"n_s":0.965,"s":2.55,"b_lens0":1.4,"b_lens1":1.7})
    out = run([sys.executable, "stage3_lensing_3x2pt.py", "--config", str(cfg), "--model", "m34", "--theta-json", theta_m34])
    res_m34 = parse_last_json(out)
    theta_mk = json.dumps({"Omega_m":0.30,"h":0.68,"Omega_b":0.049,"sigma8":0.80,"n_s":0.965,"s":2.55,"kappa":0.75,"b_lens0":1.4,"b_lens1":1.7})
    out = run([sys.executable, "stage3_lensing_3x2pt.py", "--config", str(cfg), "--model", "mkappa", "--theta-json", theta_mk])
    res_mk = parse_last_json(out)
    theta_lcdm = json.dumps({"Omega_m":0.30,"h":0.68,"Omega_b":0.049,"sigma8":0.80,"n_s":0.965,"b_lens0":1.4,"b_lens1":1.7})
    out = run([sys.executable, "stage3_lensing_3x2pt.py", "--config", str(cfg), "--model", "lcdm", "--theta-json", theta_lcdm])
    res_lcdm = parse_last_json(out)
    assert res_m34["chi2"] < 1e-8, res_m34
    assert abs(res_m34["chi2"] - res_mk["chi2"]) < 1e-8, (res_m34, res_mk)
    assert res_lcdm["chi2"] >= -1e-12, res_lcdm
    report = {"m34": res_m34, "mkappa_kappa075": res_mk, "lcdm": res_lcdm, "status": "PASS"}
    outpath = ROOT / "stage3_smoke_test_report.json"
    outpath.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    print(f"Wrote {outpath}")


if __name__ == "__main__":
    main()
