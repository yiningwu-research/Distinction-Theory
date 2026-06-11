from copy import deepcopy
import numpy as np

from cmb_lensing_precheck.config import DEFAULTS
from cmb_lensing_precheck.background import make_background
from cmb_lensing_precheck.growth import solve_growth
from cmb_lensing_precheck.power import make_power
from cmb_lensing_precheck.lensing import compute_lensing


def small_cfg():
    cfg = deepcopy(DEFAULTS)
    cfg["model"].update({"name": "g1de_m34", "s": 2.55, "normalization": "code"})
    cfg["power"].update({"backend": "analytic", "n_k": 500})
    cfg["integration"].update({"n_z": 180, "ell_min": 10, "ell_max": 100, "ell_step": 10})
    return cfg


def test_lensing_outputs_are_finite():
    cfg = small_cfg()
    bg_m = make_background(cfg, "g1de")
    bg_l = make_background(cfg, "lcdm")
    gm = solve_growth(bg_m, cfg["integration"]["a_ini"], n_a=500)
    gl = solve_growth(bg_l, cfg["integration"]["a_ini"], n_a=500)
    p = make_power(cfg)
    result = compute_lensing(cfg, bg_m, bg_l, gm, gl, p)
    assert np.all(np.isfinite(result.ratio))
    assert np.all(result.clpp_lcdm > 0)
    assert np.all(result.clpp_model > 0)


def test_lcdm_model_ratio_is_one():
    cfg = small_cfg()
    cfg["model"]["name"] = "lcdm"
    bg_m = make_background(cfg, "lcdm")
    bg_l = make_background(cfg, "lcdm")
    gm = solve_growth(bg_m, cfg["integration"]["a_ini"], n_a=500)
    gl = solve_growth(bg_l, cfg["integration"]["a_ini"], n_a=500)
    p = make_power(cfg)
    result = compute_lensing(cfg, bg_m, bg_l, gm, gl, p)
    assert np.allclose(result.ratio, 1.0, rtol=2e-5)
