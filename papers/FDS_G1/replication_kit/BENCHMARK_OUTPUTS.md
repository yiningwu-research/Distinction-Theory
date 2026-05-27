# Benchmark Outputs
# FDS-G1 Complete Series v1.0-rc3
# Expected values for independent validation

## chi2_min (optimizer best-fit, exact pilot)

Model          chi2_min    chi2_SN     chi2_BAO   chi2_GROWTH  chi2_EG
------         --------    -------     --------   -----------  -------
LCDM           1785.0      -           -          -            -
CPL            1768.0      -           -          -            -
G1DE-1         1767.3      -           -          -            -
G1DE-2         1767.14     1749.61     9.63       6.88         1.01
M_{3/4}        1767.15     -           -          -            -
M_kappa        1767.21     -           -          -            -
const-Sigma    1767.26     -           -          -            -

All models converge to chi2_min in range [1767.1, 1767.3].
Independent reimplementation should match chi2_min within ~0.1.

## Medium-prior nested evidence (6 models, 3 seeds each)

Model          ndim  logZ_mean  Delta_logZ  Bayes_factor  chi2_best
-----          ----  ---------  ----------  ------------  ---------
M_{3/4}        4     -894.26    0.00        194.28        1767.15
M_kappa        5     -895.23    0.97        73.52         1767.21
const-Sigma    5     -896.18    1.92        28.19         1767.26
G1DE-2         6     -900.95    6.70        0.24          1767.30
CPL            5     -903.69    9.43        0.02          1768.0
LCDM           3     -906.22    11.96       0.001         1789.2

Evidence hierarchy: M_{3/4} > M_kappa > const-Sigma > G1DE-2 > CPL > LCDM.
Ranking should be stable within Delta_logZ ~0.5 across independent reimplementations.

## Wide-prior sensitivity (top 3 models, 3 seeds each)

Model          ndim  logZ_mean  Delta_logZ  Bayes_factor  chi2_best
-----          ----  ---------  ----------  ------------  ---------
M_{3/4}        4     -896.81    0.00        7.05          1767.17
M_kappa        5     -897.66    0.85        3.02          1767.19
const-Sigma    5     -898.76    1.95        1.00          1767.24

Ranking M_{3/4} > M_kappa > const-Sigma survives prior broadening.

## AIC / BIC

Model          n_params  AIC        Delta_AIC  BIC        Delta_BIC
-----          --------  ---        ---------  ---        ---------
M_{3/4}        4         1775.15    0.00       1797.35    0.00
M_kappa        5         1777.21    2.06       1804.96    7.61
const-Sigma    5         1777.26    2.11       1805.01    7.66

## Tolerance

  chi2_min       : +/- 0.2
  logZ           : +/- 0.5
  Delta_logZ     : +/- 0.5
  Bayes_factor   : factor of ~2
  Ranking        : M_{3/4} > M_kappa > const-Sigma (must hold)

Independent reimplementation should reproduce the evidence ranking
and approximate logZ differences within these tolerances.
Exact logZ values depend on sampler, seed, nlive, dlogz.
