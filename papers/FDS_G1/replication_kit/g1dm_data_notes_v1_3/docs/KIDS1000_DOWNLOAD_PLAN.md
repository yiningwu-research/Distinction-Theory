# KiDS-1000 Cosmic Shear — Data Download Plan for v0.4 Phase 4a

## Scientific goal

Reproduce the published KiDS-1000 $S_8$ constraint
($S_8 = 0.759^{+0.024}_{-0.021}$) from the public data vector and covariance,
using the fiducial COSEBIs analysis.

## Download instructions

### 1. Cosmic shear data release tarball

**URL:**
`https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS1000_cosmic_shear_data_release.tgz`

**Local path:** `data/raw/kids_1000/cosmic_shear/`

```bash
mkdir -p data/raw/kids_1000/cosmic_shear
cd data/raw/kids_1000/cosmic_shear
curl -LO https://kids.strw.leidenuniv.nl/DR4/data_files/KiDS1000_cosmic_shear_data_release.tgz
tar -xzf KiDS1000_cosmic_shear_data_release.tgz
```

### 2. Expected contents

| File / directory | Format | Purpose |
|-----------------|--------|---------|
| `*_COSEBIs_*.fits` | FITS | COSEBIs data vectors (5 tomographic bins, $E_n$ modes) |
| `*_covariance_*.fits` or `*_cov_*.fits` | FITS | Non-diagonal covariance matrices |
| `*_nz_*.fits` or `*_Nz_*.fits` | FITS | Redshift distributions $n_i(z)$ per tomographic bin |
| `*_Cov_Nz_*.fits` | FITS | Covariance of $n(z)$ uncertainty |
| `*chain*.txt` or `chains/*` | Text | Multinest posterior chains |
| `*.ini` | Text | CosmoSIS configuration files |
| `*.py` | Python | Plotting scripts (chainconsumer) |

### 3. Key references

- Asgari et al. (2021), "KiDS-1000 Cosmology: Cosmic shear constraints and
  comparison between two point statistics", A&A 645, A104
- Giblin et al. (2021), "KiDS-1000 catalogue: Weak gravitational lensing
  shear measurements"
- Hildebrandt et al. (2021), "KiDS-1000 catalogue: Redshift distributions
  and their calibration"
- Joachimi et al. (2021), "KiDS-1000 methodology: Modelling and inference
  for galaxy clustering and weak lensing"

### 4. Acknowledgment

Required acknowledgment text for any publication using KiDS-1000 data:

> Based on observations made with ESO Telescopes at the La Silla Paranal
> Observatory under programme IDs 177.A-3016, 177.A-3017, 177.A-3018 and
> 179.A-2004, and on data products produced by the KiDS consortium.

Required citations: Kuijken et al. (2019), Wright et al. (2020),
Hildebrandt et al. (2021), Giblin et al. (2021), Asgari et al. (2021),
Heymans et al. (2021), Tröster et al. (2021), Joachimi et al. (2021).

### 5. Relation to v0.3 compressed proxy

In v0.3, the KiDS $S_8$ constraint was represented by a single compressed
$z$-score:
$$ z_{S_8}^{\rm KiDS} = 2.77\sigma. $$

Phase 4a replaces this with the actual KiDS-1000 data vector and covariance.
The v0.3 compressed proxy serves as the cross-check target: Phase 4a
succeeds if the chain-derived $S_8$ posterior matches the published value.

### 6. File size estimate

The tarball is approximately 50–200 MB (data vectors, covariances, chains).
Exact size depends on the number of analysis configurations included.
