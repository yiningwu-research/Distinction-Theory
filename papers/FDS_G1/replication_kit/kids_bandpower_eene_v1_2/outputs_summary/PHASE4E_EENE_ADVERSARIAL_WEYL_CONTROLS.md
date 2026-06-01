# Phase 4E: EE+nE BandPower Adversarial Weyl-Control Stress

## Status: COMPLETE
\[
\boxed{
\text{Phase 4E: EE+nE adversarial Weyl-control stress — PASS}
}
\]

---
## Boundary Enforcement
> Phase 4E is a diagnostic adversarial-control stress test on the validated EE+nE BandPower bridge. It is not full \(3\times2\)pt, not production evidence, not nested evidence, and not a final cosmological constraint. The nn/clustering channel remains unavailable locally.
---
## Results
| Model               | EE+nE (\(\chi^2\)) | Notes                                                                 |
| ------------------- | ------------------: | --------------------------------------------------------------------- |
| M3/4 (baseline)     |             1187.16 | Base EE+nE BandPower local refit result                               |
| const-\(\Sigma\)    |             1043.89 | Cannot reproduce M3/4 fit; \(\Sigma_0\) at upper bound (\(=1.0\))     |
| binned-\(\Sigma_2\) |             1043.89 | 2-bin redshift freedom does not help; both \(\Sigma\) bins at upper bound |

---
## Interpretation
The constant-\(\Sigma\) and two-bin \(\Sigma(z)\) adversarial controls do not reproduce the M3/4 EE+nE diagnostic performance. Both adversarial controls remain at \(\chi^2\simeq1043.89\), substantially above the M3/4 diagnostic fit at \(\chi^2=1187.16\). The two-bin control collapses to the same solution as constant-\(\Sigma\), with both \(\Sigma\) bins at the upper bound. 

The binned-\(\Sigma_2\) control is prior-bound limited in this diagnostic run; this is interpreted as a failure of the tested adversarial control to absorb the M3/4 improvement, not as a production model-comparison result.

This indicates that, within the tested EE+nE BandPower diagnostic bridge, the M3/4 improvement is not reproduced by simple redshift-independent or two-bin Weyl-amplitude freedom. These results are diagnostic only and are not interpreted as production evidence.

---
## Caveats
1. This is local diagnostic refit, not nested evidence. No statistical proof claims are made.
2. Only 2-bin redshift-binned \(\Sigma(z)\) tested, broader basis sets not explored.
3. nn/clustering channel unavailable locally; full 3×2pt analysis pending.

---
## Conclusions
\[
\boxed{
\text{Within the tested EE+nE diagnostic setup, constant-}\Sigma\text{ and 2-bin }\Sigma(z)\text{ controls do not absorb the M3/4 improvement.}
}
\]
\[
\boxed{
\text{supports shape-specificity of the M3/4 Weyl response in this diagnostic bridge.}
}
\]
