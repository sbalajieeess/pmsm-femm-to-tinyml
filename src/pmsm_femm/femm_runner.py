from __future__ import annotations

import argparse
import importlib.util
import multiprocessing as mp
import shutil
import time
import traceback
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .config import PipelineConfig, load_config
from .femm_adapter import simulate_slice
from .io import OperatingPoint, read_operating_points, safe_token, sha256_file, write_json
from .model_validation import validate_fem_model
from .postprocess import summarize_raw_result
from .provenance import capture_environment


def _adapter_settings(config: PipelineConfig, raw_dir: Path) -> dict[str, Any]:
    raw = config.raw
    return {
        "hide_window": bool(raw["femm"]["hide_window"]),
        "smart_mesh": bool(raw["femm"]["smart_mesh"]),
        "save_flux_density_bitmap": bool(raw["run"]["save_flux_density_bitmap"]),
        "raw_dir": str(raw_dir),
        "rotor_angle_elec_deg": float(raw["coordinates"]["rotor_angle_elec_deg"]),
        "pole_pairs": int(raw["motor"]["pole_pairs"]),
        "d_axis_sliding_band_mech_deg": float(raw["coordinates"]["d_axis_sliding_band_mech_deg"]),
        "symmetry_factor": int(raw["motor"]["symmetry_factor"]),
        "circuit_names": [str(value) for value in raw["femm"]["circuit_names"]],
        "sliding_band_name": str(raw["femm"]["sliding_band_name"]),
    }


def _run_point(
    config: PipelineConfig,
    point: OperatingPoint,
    run_dir: Path,
    runtime_config_path: Path,
) -> dict[str, object]:
    raw_dir = run_dir / "raw"
    work_dir = run_dir / "work" / point.case_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    settings = _adapter_settings(config, raw_dir)
    arguments: list[tuple[str, int, dict[str, float | str], dict[str, Any]]] = []
    temporary_models: list[Path] = []

    for slice_index, skew_angle in enumerate(config.skew_angles):
        worker_model = work_dir / f"{config.model_path.stem}_slice{slice_index + 1}.fem"
        shutil.copy2(config.model_path, worker_model)
        temporary_models.append(worker_model)
        point_payload: dict[str, float | str] = {
            "case_id": point.case_id,
            "id_rms_a": point.id_rms_a,
            "iq_rms_a": point.iq_rms_a,
            "skew_angle_mech_deg": skew_angle,
        }
        arguments.append((str(worker_model), slice_index, point_payload, settings))

    start = time.perf_counter()
    try:
        processes = min(config.parallel_workers, len(arguments))
        with mp.Pool(processes=processes) as pool:
            output = pool.starmap(simulate_slice, arguments)
        elapsed = time.perf_counter() - start

        result = pd.concat([item[0] for item in output], ignore_index=True)
        airgap_frames = [item[1] for item in output if not item[1].empty]
        airgap = pd.concat(airgap_frames, ignore_index=True) if airgap_frames else pd.DataFrame()

        iq_token = safe_token(point.iq_rms_a)
        id_token = safe_token(point.id_rms_a)
        slice_count = len(config.skew_angles)
        raw_csv = raw_dir / f"FL_and_Torque_{iq_token}_{id_token}_{slice_count}skew.csv"
        airgap_csv = raw_dir / f"agReadings_{iq_token}_{id_token}_{slice_count}skew.csv"
        result.to_csv(raw_csv, index=False)
        airgap.to_csv(airgap_csv, index=False)

        summary = summarize_raw_result(raw_csv, runtime_config_path)
        summary.update(
            {
                "case_id": point.case_id,
                "description": point.description,
                "elapsed_seconds": elapsed,
                "status": "completed",
            }
        )
        return summary
    finally:
        for fem_file in temporary_models:
            with suppress(FileNotFoundError):
                fem_file.unlink()
            with suppress(FileNotFoundError):
                fem_file.with_suffix(".ans").unlink()
        with suppress(OSError):
            work_dir.rmdir()


def run(config_path: str | Path, points_path: str | Path, run_id: str | None = None) -> Path:
    config = load_config(config_path)
    model_errors = validate_fem_model(
        config.model_path,
        expected_depth_mm=float(config.raw["motor"]["stack_length_mm_per_slice"]),
        sliding_band_name=str(config.raw["femm"]["sliding_band_name"]),
        circuit_names=[str(value) for value in config.raw["femm"]["circuit_names"]],
    )
    if model_errors:
        raise ValueError("FEM model validation failed:\n- " + "\n- ".join(model_errors))
    if importlib.util.find_spec("femm") is None:
        raise RuntimeError(
            "The FEMM Python module is unavailable. Install FEMM/pyFEMM on Windows and rerun "
            "scripts/check_environment.py."
        )
    if bool(config.raw["run"]["save_mesh_text"]):
        raise NotImplementedError(
            "save_mesh_text is reserved for the future mesh-export adapter; "
            "keep it false for v0.1.0."
        )

    points = read_operating_points(points_path)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = config.output_root / (run_id or f"{config.run_name}_{timestamp}")
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "raw").mkdir()
    (run_dir / "work").mkdir()

    config_copy = run_dir / "config.toml"
    points_copy = run_dir / "operating_points.csv"
    shutil.copy2(config.source_path, config_copy)
    shutil.copy2(Path(points_path).resolve(), points_copy)

    manifest: dict[str, object] = {
        "pipeline_version": "0.1.0",
        "run_id": run_dir.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config_source": str(config.source_path),
        "operating_points_source": str(Path(points_path).resolve()),
        "model": str(config.model_path),
        "model_sha256": sha256_file(config.model_path),
        "point_count": len(points),
        "skew_angles_mech_deg": config.skew_angles,
        "parallel_workers": config.parallel_workers,
        "status": "running",
        "environment": capture_environment(config.repo_root),
    }
    write_json(run_dir / "manifest.json", manifest)

    rows: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []
    continue_on_error = bool(config.raw["run"]["continue_on_error"])

    for index, point in enumerate(points, start=1):
        print(
            f"[{index}/{len(points)}] {point.case_id}: "
            f"Id={point.id_rms_a:g} A RMS, Iq={point.iq_rms_a:g} A RMS"
        )
        try:
            row = _run_point(config, point, run_dir, config_copy)
            rows.append(row)
            pd.DataFrame(rows).to_csv(run_dir / "summary.csv", index=False)
            print(f"      completed in {float(row['elapsed_seconds']):.1f} s")
        except Exception as exc:
            failure = {
                "case_id": point.case_id,
                "error": str(exc),
                "traceback": traceback.format_exc(),
            }
            failures.append(failure)
            write_json(run_dir / "failures.json", failures)
            print(f"      FAILED: {exc}")
            if not continue_on_error:
                manifest["status"] = "failed"
                manifest["failed_case"] = point.case_id
                write_json(run_dir / "manifest.json", manifest)
                raise

    manifest["status"] = "completed_with_failures" if failures else "completed"
    manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["completed_points"] = len(rows)
    manifest["failed_points"] = len(failures)
    write_json(run_dir / "manifest.json", manifest)
    print(f"Run directory: {run_dir.resolve()}")
    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a config-driven FEMM skew-slice map.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--points", required=True)
    parser.add_argument("--run-id")
    args = parser.parse_args()
    mp.freeze_support()
    run(args.config, args.points, args.run_id)


if __name__ == "__main__":
    main()
