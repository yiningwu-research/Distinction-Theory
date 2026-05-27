#!/usr/bin/env python3
"""
Quick environment check. This does not run a chain.
It verifies that required files exist and that the likelihood can be initialized.
"""

from stage2d_exact_likelihood import load_config, make_likelihood_from_config

config = load_config("configs/stage2d_exact_config.json")
like = make_likelihood_from_config(config)

print("Loaded likelihood successfully.")
print("SN points:", len(like.z_sn))
print("BAO points:", len(like.z_bao))
print("Growth points:", len(like.z_growth))
print("E_G points:", len(like.z_eg))
