from pathlib import Path

import numpy as np
import pytest

from cmb_lensing_precheck.mcmc.structured_emu import StructuredRatioEmulator
from cmb_lensing_precheck.mcmc.likelihood import LensingLikelihood


ROOT = Path(__file__).resolve().parents[1]
V4_ARTIFACT = ROOT / "artifacts" / "ratio_v4_candidate_001"


@pytest.fixture(scope="module")
def v4_emulator():
    return StructuredRatioEmulator.load(V4_ARTIFACT)


def test_v4_artifact_loads_packaged_format(v4_emulator):
    assert v4_emulator.ell is not None
    assert len(v4_emulator.ell) > 0
    assert v4_emulator._weyl_target == "G_L"


def test_v4_null_branches_are_enforced(v4_emulator):
    r_q0 = v4_emulator.predict_R(0.30, 0.67, 0.0, 0.75)
    r_k0 = v4_emulator.predict_R(0.30, 0.67, 0.4, 0.0)
    r_bg = v4_emulator.predict_R(0.30, 0.67, 0.4, 0.0)
    r_m34 = v4_emulator.predict_R(0.30, 0.67, 0.4, 0.75)
    r_mkappa_locked = v4_emulator.predict_R(0.30, 0.67, 0.4, 0.75)

    assert np.allclose(r_q0, 1.0)
    assert np.allclose(r_k0, r_bg)
    assert np.allclose(r_mkappa_locked, r_m34)


def test_v4_emulator_fails_outside_training_domain(v4_emulator):
    with pytest.raises(ValueError, match="outside training domain"):
        v4_emulator.predict_R(0.10, 0.67, 0.4, 0.75)


def test_likelihood_loader_uses_frozen_v4_emulator():
    like = object.__new__(LensingLikelihood)
    emu = like._load_emulator()
    assert isinstance(emu, StructuredRatioEmulator)
    assert emu._weyl_target == "G_L"
