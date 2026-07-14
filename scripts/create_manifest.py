from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from pmsm_femm.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a SHA-256 manifest for repository inputs.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="reference/input_manifest.json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = sorted(
        [
            *root.glob("models/femm/*.FEM"),
            *root.glob("configs/*.toml"),
            *root.glob("examples/*.csv"),
        ]
    )
    payload = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": [
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in files
        ],
    }
    write_json(root / args.output, payload)
    print(f"Wrote {(root / args.output).resolve()}")


if __name__ == "__main__":
    main()
