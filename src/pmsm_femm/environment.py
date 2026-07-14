from __future__ import annotations

import argparse
import importlib.util
import platform
import sys
from pathlib import Path

from .config import load_config
from .model_validation import inspect_fem_model, validate_fem_model


def check_environment(config_path: str | Path) -> int:
    config = load_config(config_path)
    checks: list[tuple[str, bool, str]] = []

    checks.append(("Python >= 3.11", sys.version_info >= (3, 11), sys.version.split()[0]))
    checks.append(("Windows host", platform.system() == "Windows", platform.platform()))
    for package in ("numpy", "pandas", "scipy", "matplotlib", "femm"):
        found = importlib.util.find_spec(package) is not None
        checks.append((f"Python module: {package}", found, "found" if found else "missing"))

    model = config.model_path
    checks.append(("FEM model exists", model.is_file(), str(model)))
    lua = config.resolve(config.raw["femm"]["mesh_lua"])
    checks.append(("Mesh Lua exists", lua.is_file(), str(lua)))

    model_errors: list[str] = []
    if model.is_file():
        model_errors = validate_fem_model(
            model,
            expected_depth_mm=float(config.raw["motor"]["stack_length_mm_per_slice"]),
            sliding_band_name=str(config.raw["femm"]["sliding_band_name"]),
            circuit_names=[str(value) for value in config.raw["femm"]["circuit_names"]],
        )
        info = inspect_fem_model(model)
        checks.append(("FEM model contract", not model_errors, str(info)))

    print(f"Configuration: {config.source_path}")
    print(f"Run name:      {config.run_name}\n")
    for name, passed, detail in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}: {detail}")
    for error in model_errors:
        print(f"       - {error}")

    failures = [name for name, passed, _ in checks if not passed]
    if failures:
        print("\nEnvironment is not ready for a FEMM run.")
        return 1
    print("\nEnvironment is ready for a FEMM run.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the local FEMM pipeline environment.")
    parser.add_argument("--config", default="configs/one_eighth_100C.toml")
    args = parser.parse_args()
    raise SystemExit(check_environment(args.config))


if __name__ == "__main__":
    main()
