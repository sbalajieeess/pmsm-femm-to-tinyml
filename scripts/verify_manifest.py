from __future__ import annotations

import argparse
import json
from pathlib import Path

from pmsm_femm.io import sha256_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify files against a SHA-256 input manifest.")
    parser.add_argument("--manifest", default="reference/input_manifest.json")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    manifest_path = (root / args.manifest).resolve()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    failures: list[str] = []
    for item in payload["files"]:
        relative = Path(item["path"])
        path = root / relative
        if not path.is_file():
            failures.append(f"missing: {relative.as_posix()}")
            continue
        actual_size = path.stat().st_size
        actual_hash = sha256_file(path)
        if actual_size != int(item["bytes"]):
            failures.append(
                f"size mismatch: {relative.as_posix()} expected={item['bytes']} "
                f"actual={actual_size}"
            )
        if actual_hash != item["sha256"]:
            failures.append(
                f"sha256 mismatch: {relative.as_posix()} expected={item['sha256']} "
                f"actual={actual_hash}"
            )

    if failures:
        print("Manifest verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(f"Manifest verification passed for {len(payload['files'])} files.")


if __name__ == "__main__":
    main()
