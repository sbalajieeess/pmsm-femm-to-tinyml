from __future__ import annotations

import argparse
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from pmsm_femm.io import sha256_file, write_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Package a generated-results directory as a GitHub Release asset."
    )
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()
    if not source.is_dir():
        raise FileNotFoundError(source)
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                archive.write(path, path.relative_to(source.parent))

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "archive": str(output),
        "archive_bytes": output.stat().st_size,
        "archive_sha256": sha256_file(output),
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    write_json(manifest_path, manifest)
    print(f"Wrote {output}")
    print(f"Wrote {manifest_path}")
    print(f"SHA-256: {manifest['archive_sha256']}")


if __name__ == "__main__":
    main()
