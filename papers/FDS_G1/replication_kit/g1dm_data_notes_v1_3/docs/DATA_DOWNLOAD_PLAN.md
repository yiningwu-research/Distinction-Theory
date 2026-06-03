# Data Download Plan for G1DM Data Notes

This document gives a reproducible public-data acquisition plan for the Companion G data notes.

## Note 1: Carrier floor / pure-Weyl exclusion

**Scientific question:** Can a pure Weyl/optical residual replace the full CDM sector?

**Primary data:**

1. Planck 2018 likelihood or CosmoMC chains.
   - Official home: <https://www.cosmos.esa.int/web/planck>
   - Archive: <https://pla.esac.esa.int/>
   - Place chains under `data/raw/planck_chains/`.

2. Optional ACT DR6 CMB lensing likelihood.
   - GitHub: <https://github.com/ACTCollaboration/act_dr6_lenslike>
   - Install with `pip install act_dr6_lenslike` or clone the repository.
   - Run the official `get-act-data.sh` script.

**First-pass computation:** read Planck chains and quantify the posterior exclusion of `omegach2 = 0`.
A full production run should compare actual CMB likelihoods using CAMB/CLASS + Cobaya.

## Note 2: DESI DR1 mu=1 growth-leakage consistency

**Scientific question:** Does public full-shape/RSD information require leading modified growth, or is `mu_grav = 1` compatible with a dark source inventory?

**Primary data:** DESI DR1 full-shape cosmology chains.

- Documentation: <https://data.desi.lbl.gov/doc/releases/dr1/vac/full-shape-cosmo-params/>
- Data URL: <https://data.desi.lbl.gov/public/dr1/vac/dr1/full-shape-cosmo-params>
- Expected local folder: `data/raw/desi_dr1/full-shape-cosmo-params/`
- Use `_mu_sigma` model folders for modified-gravity parameters.

**First-pass computation:** use Gaussian compressed constraints for `mu0` and `Sigma0`, or read chains if available.

## Note 3: Lensing-growth split / Weyl residual diagnostic

**Scientific question:** Is there an independent lensing/Weyl residual with near-GR growth?

**Primary public data options:**

- DESI DR1 full-shape/RSD for growth.
- KiDS-1000 weak-lensing data vectors/covariances/posteriors.
- DES Y3 3x2pt data products.
- ACT DR6 CMB lensing likelihood.

**First-pass computation:** compressed Gaussian test in the `(mu0, Sigma0)` plane.
A production run should use actual weak-lensing and RSD/full-shape likelihoods.

## Note 4: Source--Response--Optics sparse audit

**Scientific question:** Does dark-sector phenomenology require a sparse combination of source, response, and optics components, or arbitrary absorption?

**Data:** combine compressed observables from the above sources. Start with a hand-curated YAML table:

- `source` channels: CMB/equality/omega_cdm constraints;
- `growth` channels: DESI/eBOSS RSD/full-shape constraints;
- `optics` channels: KiDS/DES/ACT lensing constraints;
- `dynamics` channels: SPARC/cluster diagnostics.

**First-pass computation:** compare sparse model masks using Gaussian evidence approximations and BIC/AIC.

## Note 5: Optional acceleration-scale drift

**Scientific question:** Does a galaxy acceleration scale drift with a boundary-response proxy such as `c H(z) R_D(z)`?

**Primary data:**

- SPARC z~0 baseline: <https://astroweb.case.edu/SPARC/>
- High-z comparison: KURVS/KROSS/KMOS3D-like samples from paper tables/supplements.

**Warning:** high-z rotation curves have heavy systematics. Treat this as exploratory.
