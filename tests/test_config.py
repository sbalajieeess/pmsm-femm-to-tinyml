from pathlib import Path

import pytest

from pmsm_femm.config import load_config, validate_config_dict
from pmsm_femm.io import read_operating_points, safe_token
from pmsm_femm.model_validation import inspect_fem_model, validate_fem_model

ROOT = Path(__file__).resolve().parents[1]


def test_supplied_configs_and_models_match() -> None:
    for temperature in (20, 60, 100):
        config = load_config(ROOT / f"configs/one_eighth_{temperature}C.toml")
        assert config.model_path.is_file()
        errors = validate_fem_model(
            config.model_path,
            expected_depth_mm=float(config.raw["motor"]["stack_length_mm_per_slice"]),
            sliding_band_name=str(config.raw["femm"]["sliding_band_name"]),
            circuit_names=list(config.raw["femm"]["circuit_names"]),
        )
        assert errors == []
        info = inspect_fem_model(config.model_path)
        assert info["depth_mm"] == pytest.approx(38.0)
        assert set(info["circuits"]) >= {"U", "V", "W"}


def test_smoke_operating_points_are_valid() -> None:
    points = read_operating_points(ROOT / "examples/smoke_points.csv")
    assert [point.case_id for point in points] == ["P001", "P002"]
    assert points[1].id_rms_a == pytest.approx(-30.0)
    assert points[1].iq_rms_a == pytest.approx(100.0)


def test_invalid_config_is_rejected() -> None:
    with pytest.raises(ValueError, match="Missing configuration sections"):
        validate_config_dict({"run": {}})


def test_filename_tokens_are_windows_safe() -> None:
    assert safe_token(-30.0) == "m30"
    assert safe_token(12.5) == "12p5"
