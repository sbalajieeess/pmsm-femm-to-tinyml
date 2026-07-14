from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export(input_csv: Path, output_csv: Path, geometry_id: str) -> Path:
    source = pd.read_csv(input_csv)
    required = {
        "temperature_c",
        "id_rms_a",
        "iq_rms_a",
        "torque_positive_motoring_nm",
        "psi_d_rms_wb",
        "psi_q_rms_wb",
        "ld_h",
        "lq_h",
    }
    missing = required.difference(source.columns)
    if missing:
        raise ValueError(f"Summary is missing columns: {sorted(missing)}")
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
    args = parser.parse_args()
    output = export(Path(args.input), Path(args.output), args.geometry_id)
    print(f"Wrote {output.resolve()}")


if __name__ == "__main__":
    main()
