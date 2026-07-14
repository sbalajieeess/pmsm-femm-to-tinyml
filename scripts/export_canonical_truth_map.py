from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd

SUMMARY_REQUIRED = {
    "temperature_c",
    "id_rms_a",
    "iq_rms_a",
    "torque_positive_motoring_nm",
    "psi_d_rms_wb",
    "psi_q_rms_wb",
    "ld_h",
    "lq_h",
}

LEGACY_REFERENCE_REQUIRED = {
    "Id_RMS",
    "Iq_RMS",
    "Torque(Nm)",
    "psiD_RMS",
    "psiQ_RMS",
    "Ld",
    "Lq",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def infer_temperature_c(path: Path) -> float | None:
    match = re.search(r"(?:^|[_-])([-+]?\d+(?:\.\d+)?)C(?:[_-]|$)", path.stem, re.IGNORECASE)
    return float(match.group(1)) if match else None


def normalize_source(
    source: pd.DataFrame,
    input_csv: Path,
    temperature_c: float | None,
    legacy_torque_sign_to_positive_motoring: float,
) -> pd.DataFrame:
    source = source.loc[:, ~source.columns.str.startswith("Unnamed:")].copy()
    if SUMMARY_REQUIRED <= set(source.columns):
        return source

    if LEGACY_REFERENCE_REQUIRED <= set(source.columns):
        resolved_temperature = temperature_c
        if resolved_temperature is None and "temperature_c" in source:
            resolved_temperature = float(source["temperature_c"].iloc[0])
        if resolved_temperature is None:
            resolved_temperature = infer_temperature_c(input_csv)
        if resolved_temperature is None:
            raise ValueError(
                "Legacy reference map is missing temperature metadata. "
                "Pass --temperature-c or use a filename containing '<temperature>C'."
            )
        return pd.DataFrame(
            {
                "source_file": [
                    f"{input_csv.stem}_row_{index + 1:05d}" for index in range(len(source))
                ],
                "temperature_c": resolved_temperature,
                "id_rms_a": source["Id_RMS"],
                "iq_rms_a": source["Iq_RMS"],
                "torque_positive_motoring_nm": (
                    source["Torque(Nm)"] * legacy_torque_sign_to_positive_motoring
                ),
                "psi_d_rms_wb": source["psiD_RMS"],
                "psi_q_rms_wb": source["psiQ_RMS"],
                "ld_h": source["Ld"],
                "lq_h": source["Lq"],
            }
        )

    summary_missing = sorted(SUMMARY_REQUIRED.difference(source.columns))
    legacy_missing = sorted(LEGACY_REFERENCE_REQUIRED.difference(source.columns))
    raise ValueError(
        "Summary is missing required columns. "
        f"Canonical summary missing: {summary_missing}. "
        f"Legacy reference missing: {legacy_missing}."
    )


def export(
    input_csv: Path,
    output_csv: Path,
    geometry_id: str,
    temperature_c: float | None = None,
    legacy_torque_sign_to_positive_motoring: float = -1.0,
) -> Path:
    source = normalize_source(
        pd.read_csv(input_csv),
        input_csv,
        temperature_c,
        legacy_torque_sign_to_positive_motoring,
    )
    result = pd.DataFrame(
        {
            "case_id": source.get(
                "source_file", pd.Series([f"P{i + 1:05d}" for i in range(len(source))])
            ),
            "source_solver": "FEMM",
            "geometry_id": geometry_id,
            "temperature_C": source["temperature_c"],
            "slice_id": "4slice_average",
            "id_RMS_A": source["id_rms_a"],
            "iq_RMS_A": source["iq_rms_a"],
            "current_magnitude_RMS_A": np.hypot(source["id_rms_a"], source["iq_rms_a"]),
            "current_angle_deg": np.degrees(np.arctan2(source["id_rms_a"], source["iq_rms_a"])),
            "torque_Nm": source["torque_positive_motoring_nm"],
            "psiD_Wb": source["psi_d_rms_wb"],
            "psiQ_Wb": source["psi_q_rms_wb"],
            "Ld_H": source["ld_h"],
            "Lq_H": source["lq_h"],
            "Bmax_T": np.nan,
            "converged": True,
            "solver_iterations": np.nan,
            "runtime_s": np.nan,
            "model_hash": sha256(input_csv),
            "config_hash": "captured_in_run_manifest",
        }
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_csv, index=False)
    return output_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a FEMM summary to truth_map_v1.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--geometry-id", required=True)
    parser.add_argument(
        "--temperature-c",
        type=float,
        help="Temperature to use when exporting legacy reference maps without metadata.",
    )
    parser.add_argument(
        "--legacy-torque-sign-to-positive-motoring",
        type=float,
        default=-1.0,
        help="Sign multiplier for legacy reference-map Torque(Nm) values.",
    )
    args = parser.parse_args()
    output = export(
        Path(args.input),
        Path(args.output),
        args.geometry_id,
        temperature_c=args.temperature_c,
        legacy_torque_sign_to_positive_motoring=args.legacy_torque_sign_to_positive_motoring,
    )
    print(f"Wrote {output.resolve()}")


if __name__ == "__main__":
    main()
