from pathlib import Path

import pytest

from pmsm_femm.postprocess import summarize_raw_result

ROOT = Path(__file__).resolve().parents[1]


def test_reference_raw_sample_can_be_summarized() -> None:
    summary = summarize_raw_result(
        ROOT / "reference/raw_sample/FL_and_Torque_125_-30_4skew.csv",
        ROOT / "configs/one_eighth_100C.toml",
    )
    assert summary["slice_count"] == 4
    assert summary["id_rms_a"] == pytest.approx(-62.5)
    assert summary["iq_rms_a"] == pytest.approx(108.253175473)
    assert summary["torque_positive_motoring_nm"] > 0.0
    assert summary["psi_d_rms_wb"] != 0.0
    assert summary["max_speed_rpm_no_resistance"] > 0.0
