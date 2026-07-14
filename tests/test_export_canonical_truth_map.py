from pathlib import Path

import pandas as pd
import pytest

from scripts.export_canonical_truth_map import export, infer_temperature_c

ROOT = Path(__file__).resolve().parents[1]


def test_temperature_can_be_inferred_from_reference_summary_name() -> None:
    assert infer_temperature_c(Path("400V_100C_fea_map.csv")) == pytest.approx(100.0)
    assert infer_temperature_c(Path("400V_60C_fea_map.csv")) == pytest.approx(60.0)


def test_reference_summary_exports_to_canonical_truth_map(tmp_path: Path) -> None:
    output = tmp_path / "truth_map_v1.csv"
    export(
        ROOT / "reference/summaries/400V_100C_fea_map.csv",
        output,
        "oneEighth_reference_v1",
    )

    frame = pd.read_csv(output)
    assert len(frame) > 100
    assert set(frame["source_solver"]) == {"FEMM"}
    assert set(frame["geometry_id"]) == {"oneEighth_reference_v1"}
    assert set(frame["temperature_C"]) == {100.0}
    assert frame.loc[0, "id_RMS_A"] == pytest.approx(-10.0)
    assert frame.loc[0, "iq_RMS_A"] == pytest.approx(10.0)
    assert frame.loc[0, "torque_Nm"] > 0.0
    assert frame.loc[0, "psiD_Wb"] != 0.0
    assert frame.loc[0, "psiQ_Wb"] != 0.0
