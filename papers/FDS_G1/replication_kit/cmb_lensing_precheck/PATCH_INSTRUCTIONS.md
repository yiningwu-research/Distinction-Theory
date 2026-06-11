# Patch instructions

Copy this directory into the existing replication kit as:

```text
papers/FDS_G1/replication_kit/cmb_lensing_precheck/
```

No existing files need to be overwritten. A later integration commit may add the following
lines to the parent `README.md` quick-start section:

```bash
cd cmb_lensing_precheck
pip install -e .
fds-g1-cmb-precheck configs/g1_m34_fiducial.yaml
```

Recommended parent `.gitignore` additions:

```text
cmb_lensing_precheck/outputs/
cmb_lensing_precheck/.venv/
cmb_lensing_precheck/data/*.npz
```

Do not commit official ACT/Planck likelihood data unless their upstream redistribution terms
explicitly permit it. The package downloads them through `act_dr6_lenslike`.
