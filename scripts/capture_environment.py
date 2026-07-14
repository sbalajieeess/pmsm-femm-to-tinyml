from __future__ import annotations

import argparse
from pathlib import Path

from pmsm_femm.config import find_repo_root
from pmsm_femm.io import write_json
from pmsm_femm.provenance import capture_environment


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture local reproducibility metadata.")
    parser.add_argument("--output", default="environment.json")
    args = parser.parse_args()

    root = find_repo_root()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    write_json(output, capture_environment(root))
    print(f"Wrote {output.resolve()}")


if __name__ == "__main__":
    main()
