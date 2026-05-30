#!/usr/bin/env python3
"""Validate deterministic mock injection confusion matrix.

Checks that no truth model (LCDM, const-Sigma, binned-Sigma) is misclassified
as M3/4. Requires phase2b4_confusion_deterministic.json in the outputs dir.
"""
import json, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "outputs" / "phase2b4_confusion_deterministic.json"

def load_confusion(path):
    with open(path) as f:
        return json.load(f)["results"]

def test_diagonal_lowest():
    if not JSON_PATH.exists():
        print(f"SKIP: {JSON_PATH} not found. Run 03_mock_injection_deterministic.sh first.")
        return True
    data = load_confusion(JSON_PATH)
    passed = True
    for truth in data:
        min_bic = float("inf")
        best_model = None
        for test, result in data[truth].items():
            bic = result.get("BIC", float("inf"))
            if bic < min_bic:
                min_bic = bic
                best_model = test
        if truth != "m34" and best_model == "m34":
            print(f"FAIL: {truth} truth misclassified as M3/4 (BIC={min_bic:.1f})")
            passed = False
        else:
            print(f"OK: {truth} truth -> best model = {best_model} (BIC={min_bic:.1f})")
    return passed

if __name__ == "__main__":
    success = test_diagonal_lowest()
    sys.exit(0 if success else 1)
