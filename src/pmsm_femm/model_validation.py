from __future__ import annotations

import re
from pathlib import Path

_DEPTH_PATTERN = re.compile(r"\[Depth\]\s*=\s*([0-9.+\-Ee]+)")
_BOUNDARY_PATTERN = re.compile(r'<BdryName>\s*=\s*"([^"]+)"')
_CIRCUIT_PATTERN = re.compile(r'<CircuitName>\s*=\s*"([^"]+)"')


def inspect_fem_model(path: str | Path) -> dict[str, object]:
    model_path = Path(path)
    text = model_path.read_text(encoding="utf-8", errors="replace")
    depth_match = _DEPTH_PATTERN.search(text)
    return {
        "path": str(model_path),
        "depth_mm": float(depth_match.group(1)) if depth_match else None,
        "boundaries": _BOUNDARY_PATTERN.findall(text),
        "circuits": _CIRCUIT_PATTERN.findall(text),
    }


def validate_fem_model(
    path: str | Path,
    expected_depth_mm: float,
    sliding_band_name: str,
    circuit_names: list[str],
) -> list[str]:
    info = inspect_fem_model(path)
    errors: list[str] = []
    depth = info["depth_mm"]
    if depth is None:
        errors.append("FEM model has no [Depth] value.")
    elif abs(float(depth) - expected_depth_mm) > 1e-6:
        errors.append(
            f"FEM [Depth] is {depth} mm; config expects {expected_depth_mm} mm per slice."
        )

    boundaries = list(info["boundaries"])
    if sliding_band_name not in boundaries:
        errors.append(f'Boundary "{sliding_band_name}" is missing from FEM model.')

    circuits = list(info["circuits"])
    missing_circuits = [name for name in circuit_names if name not in circuits]
    if missing_circuits:
        errors.append(f"Missing circuit names: {missing_circuits}")
    return errors
