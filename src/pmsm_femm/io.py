from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class OperatingPoint:
    case_id: str
    id_rms_a: float
    iq_rms_a: float
    description: str = ""

    @property
    def current_rms_a(self) -> float:
        return math.hypot(self.id_rms_a, self.iq_rms_a)

    @property
    def phase_advance_deg(self) -> float:
        return math.degrees(math.atan2(self.id_rms_a, self.iq_rms_a))


def read_operating_points(path: str | Path) -> list[OperatingPoint]:
    data = pd.read_csv(path)
    required = {"case_id", "id_rms_a", "iq_rms_a"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Operating-point CSV missing columns: {sorted(missing)}")
    if data["case_id"].duplicated().any():
        duplicates = data.loc[data["case_id"].duplicated(), "case_id"].tolist()
        raise ValueError(f"Duplicate case_id values: {duplicates}")

    points: list[OperatingPoint] = []
    for row in data.to_dict(orient="records"):
        description = row.get("description", "")
        points.append(
            OperatingPoint(
                case_id=str(row["case_id"]),
                id_rms_a=float(row["id_rms_a"]),
                iq_rms_a=float(row["iq_rms_a"]),
                description="" if pd.isna(description) else str(description),
            )
        )
    return points


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: str | Path, payload: object) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def safe_token(value: float) -> str:
    if float(value).is_integer():
        return str(int(value)).replace("-", "m")
    return f"{value:.6g}".replace("-", "m").replace(".", "p")
