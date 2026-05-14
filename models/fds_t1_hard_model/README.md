# FDS-T1 Minimal Finite-Observer Maintenance Model

This repository contains a minimal numerical model for the FDS-T1 paper
"Finite Distinguishability Budgets and Maintenance Bounds for Physical Observers."

The model is intentionally conservative. It does not simulate quantum gravity or a real black hole.
It tests the finite-observer maintenance logic:

```tex
C_{acc}(t)=min{C_{mem}+C_{ext}^{eff}, C_{chan}(t), C_{hor}(t), C_{therm}(t)}
```

```tex
Delta_{FDS}(t,tau,epsilon)=R_min^{(tau)}(epsilon,t)-C_acc(t,tau)
```

and, in the minimal no-rescue case,

```tex
Qdot_maint(t) >= k_B T(t) ln 2 * tau^{-1} [Delta_FDS(t,tau,epsilon)]_+.
```

## Generated figures

- `fig1_capacity_bottleneck_switching`: active bottleneck switches among channel, causal-boundary, and thermodynamic limits.
- `fig2_gaussian_error_floor_kinks`: Gaussian rate-distortion error floor under capacity collapse.
- `fig3_deficit_and_heat_spike`: fixed-distortion capacity deficit and Landauer maintenance heat lower bound.
- `fig4_observer_entropy_divergence`: entropy divergence between two finite observers with unequal causal access.
- `fig5_binary_error_floor`: binary-source Hamming distortion floor.
- `fig6_minimal_deficit_map`: minimal no-rescue deficit map.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/generate_figures.py
```

The default model is deterministic and uses fixed parameters; no random seeds are required.
