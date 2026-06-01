
# Phase 4D: EE+nE Nuisance Robustness Stress Tests
## Status: COMPLETE / PASS

## Core Boundary Text
Phase 4D is a set of diagnostic nuisance robustness stress tests on the validated EE+nE BandPower bridge. It is not full 3×2pt, not production evidence, not nested evidence, and not a final cosmological constraint. The nn/clustering channel remains unavailable locally.

## Phase4D Subphase Recap
| Subphase | Status | Purpose |
|----------|--------|---------|
| 4D-1 Bias Prior Stress | PASS | Test robustness to b_lens prior changes |
| 4D-2 Shear m Prior Stress | PASS | Test robustness to shear calibration prior changes |
| 4D-3 IA Prior Stress | PASS | Test robustness to intrinsic alignment prior changes |

## Tested Nuisance-Prior Variations
- b_lens: [0.5,3.0], [0.2,5.0], [0.05,10.0]
- m_i: [-0.05,0.05], [-0.10,0.10], [-0.20,0.20]
- A_IA: fixed at 0, [-2,2], [-5,5], [-10,10]

## Key Results
- All fits finite for all test runs!
- No catastrophic boundary absorption!
- ia_fixed0 control works without failure!
- The diagnostic χ² hierarchy is stable across the tested nuisance-prior variations, but is not interpreted as model evidence.

## Phase4D Safe Main Line
EE+nE BandPower diagnostic bridge validated for local refit, mock recovery, noisy mock screening, and nuisance-prior robustness.

## Reminder Boundary
not full 3×2pt, not production evidence, not final cosmological constraints.

## Next Optional Step
Photo-z nuisance stress can be done as Phase4E in the future, but is not required for v1.2-dev.
