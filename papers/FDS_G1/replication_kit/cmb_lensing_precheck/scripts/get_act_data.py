#!/usr/bin/env python3
"""Download the official ACT DR6 lensing likelihood data through its package API."""

try:
    import act_dr6_lenslike as alike
except ImportError as exc:
    raise SystemExit("Install first with: pip install act_dr6_lenslike>=1.2.1") from exc

alike.get_data()
print("ACT DR6 lensing likelihood data are installed.")
