from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_values(text: str) -> list[float]:
    values = [float(token.strip()) for token in text.split(",") if token.strip()]
    if not values:
        raise argparse.ArgumentTypeError("Provide at least one comma-separated value.")
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an Id/Iq operating-point grid CSV.")
    parser.add_argument("--ids", required=True, help="Comma-separated Id RMS values")
    parser.add_argument("--iqs", required=True, help="Comma-separated Iq RMS values")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    rows: list[dict[str, float | str]] = []
    case_number = 1
    for iq_rms in parse_values(args.iqs):
        for id_rms in parse_values(args.ids):
            rows.append(
                {
                    "case_id": f"P{case_number:04d}",
                    "id_rms_a": id_rms,
                    "iq_rms_a": iq_rms,
                    "description": "generated grid",
                }
            )
            case_number += 1

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"Wrote {len(rows)} points to {output.resolve()}")


if __name__ == "__main__":
    main()
