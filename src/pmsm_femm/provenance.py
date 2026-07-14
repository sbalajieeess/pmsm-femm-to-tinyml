from __future__ import annotations

import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path


def _package_version(distribution: str) -> str | None:
    try:
        return metadata.version(distribution)
    except metadata.PackageNotFoundError:
        return None


def git_commit(repo_root: str | Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(repo_root),
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() or None


def capture_environment(repo_root: str | Path) -> dict[str, object]:
    distributions = ("pmsm-fem-pipeline", "pyfemm", "numpy", "pandas", "scipy", "matplotlib")
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "git_commit": git_commit(repo_root),
        "package_versions": {
            distribution: _package_version(distribution) for distribution in distributions
        },
    }
