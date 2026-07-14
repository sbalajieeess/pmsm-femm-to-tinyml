from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PipelineConfig:
    repo_root: Path
    source_path: Path
    raw: dict[str, Any]

    @property
    def run_name(self) -> str:
        return str(self.raw["run"]["name"])

    @property
    def model_path(self) -> Path:
        return self.resolve(self.raw["run"]["model"])

    @property
    def output_root(self) -> Path:
        return self.resolve(self.raw["run"]["output_root"])

    @property
    def skew_angles(self) -> list[float]:
        return [float(value) for value in self.raw["skew"]["angles_mech_deg"]]

    @property
    def parallel_workers(self) -> int:
        return int(self.raw["run"]["parallel_workers"])

    def resolve(self, path_value: str | Path) -> Path:
        path = Path(path_value)
        return path if path.is_absolute() else (self.repo_root / path).resolve()


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "configs").exists():
            return candidate
    raise FileNotFoundError("Repository root not found; run from inside the cloned repository.")


def load_config(path: str | Path) -> PipelineConfig:
    config_path = Path(path).resolve()
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)
    root = find_repo_root(config_path.parent)
    validate_config_dict(raw)
    return PipelineConfig(repo_root=root, source_path=config_path, raw=raw)


def validate_config_dict(raw: dict[str, Any]) -> None:
    required_sections = {"run", "motor", "inverter", "coordinates", "skew", "femm"}
    missing = required_sections.difference(raw)
    if missing:
        raise ValueError(f"Missing configuration sections: {sorted(missing)}")

    angles = raw["skew"].get("angles_mech_deg", [])
    if not angles:
        raise ValueError("At least one skew angle is required.")

    workers = int(raw["run"].get("parallel_workers", 0))
    if workers < 1:
        raise ValueError("parallel_workers must be >= 1.")

    if int(raw["motor"]["symmetry_factor"]) < 1:
        raise ValueError("symmetry_factor must be >= 1.")
    if int(raw["motor"]["pole_pairs"]) < 1:
        raise ValueError("pole_pairs must be >= 1.")
