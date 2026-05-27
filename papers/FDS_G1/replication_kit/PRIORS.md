# Prior Specification
# FDS-G1 Complete Series v1.0-rc2

Machine-readable: spec/priors/medium.yaml, spec/priors/wide_topcontrol.yaml

## Medium prior (6 models)

Used for the six-model nested evidence comparison. All priors are uniform.

| Parameter | Range | Applies to |
|-----------|-------|------------|
| Omega_m   | [0.15, 0.45] | all models |
| s         | [1.5, 4.0]  | all G1DE |
| q_BAO     | [28.0, 33.0] | all models |
| sigma8_0  | [0.4, 1.2]   | all models |
| w0        | [-1.5, -0.3] | CPL |
| wa        | [-2.5, 2.5]  | CPL |
| mu0       | [-1.0, 1.0]  | G1DE-2 |
| Sigma0    | [-1.0, 1.0]  | G1DE-2 |
| kappa     | [0.0, 2.0]   | M_kappa |
| Sigma_c   | [-1.0, 1.0]  | const-Sigma |

## Wide top-control prior (3 models)

Used for sensitivity check on the three closest models. Wider bounds,
but only applied to the top control set.

| Parameter | Range | Note |
|-----------|-------|------|
| Omega_m   | [0.05, 0.60] | |
| s         | [1.0, 5.0]  | |
| q_BAO     | [24.0, 36.0] | |
| sigma8_0  | [0.2, 1.5]   | |
| kappa     | [0.0, 2.0]   | Corrected from [0,3] |
| Sigma_c   | [-0.95, 1.5] | Corrected from [-2,2] |

## Sampler settings

  Algorithm: dynesty NestedSampler
  bound: multi
  sample: rwalk
  nlive: 800
  dlogz: 0.5
  n_seeds: 3

Independent reimplementations may use different samplers
(e.g., PolyChord, MultiNest, ultranest) but should use the
same prior ranges and report 3+ seeds.
