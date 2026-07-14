from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd

from .config import load_config
from .transforms import abc_to_dq


def summarize_raw_result(
    raw_csv: str | Path,
    config_path: str | Path,
) -> dict[str, float | int | str]:
    config = load_config(config_path)
    data = pd.read_csv(raw_csv)
    data = data.loc[:, ~data.columns.str.startswith("Unnamed:")]
    required = {
        "sliceNo",
        "IdRMS",
        "IqRMS",
        "wa",
        "wb",
        "wc",
        "torque",
        "wa_q",
        "wb_q",
        "wc_q",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Raw result is missing columns: {sorted(missing)}")

    rotor_angle = float(config.raw["coordinates"]["rotor_angle_elec_deg"])
    id_rms = float(data["IdRMS"].iloc[0])
    iq_rms = float(data["IqRMS"].iloc[0])
    if data["IdRMS"].nunique() != 1 or data["IqRMS"].nunique() != 1:
        raise ValueError("A raw result file must contain exactly one operating point.")

    wa = float(data["wa"].sum())
    wb = float(data["wb"].sum())
    wc = float(data["wc"].sum())
    psi_d_peak, psi_q_peak = abc_to_dq(wa, wb, wc, rotor_angle)

    wa_q = float(data["wa_q"].sum())
    wb_q = float(data["wb_q"].sum())
    wc_q = float(data["wc_q"].sum())
    psi_pm_peak, _ = abc_to_dq(wa_q, wb_q, wc_q, rotor_angle)

    root2 = math.sqrt(2.0)
    psi_d_rms = psi_d_peak / root2
    psi_q_rms = psi_q_peak / root2
    psi_pm_rms = psi_pm_peak / root2
    ld_h = (psi_d_rms - psi_pm_rms) / id_rms if not math.isclose(id_rms, 0.0) else 0.0
    lq_h = psi_q_rms / iq_rms if not math.isclose(iq_rms, 0.0) else 0.0

    pole_pairs = int(config.raw["motor"]["pole_pairs"])
    magnetic_torque = 3.0 * pole_pairs * psi_pm_rms * iq_rms
    reluctance_torque = 3.0 * pole_pairs * id_rms * iq_rms * (ld_h - lq_h)
    analytical_torque = magnetic_torque + reluctance_torque

    dc_voltage = float(config.raw["inverter"]["dc_voltage_v"])
    v_phase_max_rms = dc_voltage / math.sqrt(3.0) / math.sqrt(2.0)
    voltage_factor = math.hypot(lq_h * iq_rms, psi_pm_rms + ld_h * id_rms)
    max_speed_rpm = (
        v_phase_max_rms * 60.0 / (2.0 * math.pi * pole_pairs * voltage_factor)
        if voltage_factor > 0.0
        else math.inf
    )

    raw_torque = float(data["torque"].sum())
    torque_sign = float(config.raw["coordinates"]["torque_sign_to_positive_motoring"])
    return {
        "source_file": Path(raw_csv).name,
        "temperature_c": float(config.raw["motor"]["temperature_c"]),
        "dc_voltage_v": dc_voltage,
        "slice_count": int(len(data)),
        "id_rms_a": id_rms,
        "iq_rms_a": iq_rms,
        "is_rms_a": math.hypot(id_rms, iq_rms),
        "phase_advance_deg": math.degrees(math.atan2(id_rms, iq_rms)),
        "torque_raw_sum_nm": raw_torque,
        "torque_positive_motoring_nm": raw_torque * torque_sign,
        "torque_slice_std_nm": float(data["torque"].std(ddof=0)),
        "psi_pm_rms_wb": psi_pm_rms,
        "psi_d_rms_wb": psi_d_rms,
        "psi_q_rms_wb": psi_q_rms,
        "ld_h": ld_h,
        "lq_h": lq_h,
        "magnetic_torque_nm": magnetic_torque,
        "reluctance_torque_nm": reluctance_torque,
        "analytical_torque_nm": analytical_torque,
        "v_phase_max_rms_v": v_phase_max_rms,
        "max_speed_rpm_no_resistance": max_speed_rpm,
    }


def summarize_folder(
    raw_dir: str | Path,
    config_path: str | Path,
    output_csv: str | Path,
) -> Path:
    raw_path = Path(raw_dir)
    files = sorted(raw_path.glob("FL_and_Torque_*.csv"))
    if not files:
        raise FileNotFoundError(f"No FL_and_Torque_*.csv files found in {raw_path}")
    rows = [summarize_raw_result(path, config_path) for path in files]
    output = Path(output_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize raw four-slice FEMM output files.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = summarize_folder(args.raw_dir, args.config, args.output)
    print(f"Wrote {output.resolve()}")


if __name__ == "__main__":
    main()
