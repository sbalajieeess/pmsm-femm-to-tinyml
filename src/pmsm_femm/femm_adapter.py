from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd

from .transforms import dq_to_abc, electrical_to_mechanical_angle


def _solve(
    femm: Any,
    model_file: Path,
    currents_peak_a: tuple[float, float, float],
    rotor_position_mech_deg: float,
    sliding_band_name: str,
    circuit_names: list[str],
    smart_mesh: bool,
    use_previous_solution: bool,
) -> tuple[tuple[float, float, float], float]:
    ia_peak, ib_peak, ic_peak = currents_peak_a
    femm.mi_setcurrent(circuit_names[0], ia_peak)
    femm.mi_setcurrent(circuit_names[1], ib_peak)
    femm.mi_setcurrent(circuit_names[2], ic_peak)

    femm.mi_modifyboundprop(sliding_band_name, 10, -rotor_position_mech_deg)
    if use_previous_solution:
        previous = str(model_file.with_suffix(".ans"))
        escaped = repr(previous).replace("x0", "")
        femm.mi_setprevious(escaped[1:-1])

    femm.mi_smartmesh(1 if smart_mesh else 0)
    femm.mi_createmesh()
    femm.mi_analyze(2)
    femm.mi_loadsolution()

    fluxes = tuple(float(femm.mo_getcircuitproperties(name)[2]) for name in circuit_names)
    torque = float(femm.mo_gapintegral(sliding_band_name, 0))
    return (fluxes[0], fluxes[1], fluxes[2]), torque


def simulate_slice(
    model_file: str,
    slice_index: int,
    point: dict[str, float],
    settings: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run loaded and q-axis reference solves for one physical skew slice."""
    try:
        import femm
    except ImportError as exc:  # pragma: no cover - Windows/FEMM only
        raise RuntimeError("The FEMM Python module is not installed in this environment.") from exc

    model_path = Path(model_file)
    hide_window = bool(settings["hide_window"])
    femm.openfemm(1 if hide_window else 0)
    try:
        femm.opendocument(str(model_path))

        id_rms = float(point["id_rms_a"])
        iq_rms = float(point["iq_rms_a"])
        rotor_angle_elec = float(settings["rotor_angle_elec_deg"])
        pole_pairs = int(settings["pole_pairs"])
        d_axis_offset = float(settings["d_axis_sliding_band_mech_deg"])
        skew_angle = float(point["skew_angle_mech_deg"])
        symmetry = int(settings["symmetry_factor"])
        circuit_names = [str(name) for name in settings["circuit_names"]]
        sliding_band = str(settings["sliding_band_name"])
        smart_mesh = bool(settings["smart_mesh"])

        current_rms = math.hypot(id_rms, iq_rms)
        phase_angle = math.degrees(math.atan2(id_rms, iq_rms))
        ia_rms, ib_rms, ic_rms = dq_to_abc(id_rms, iq_rms, rotor_angle_elec)
        root2 = math.sqrt(2.0)
        currents_peak = (ia_rms * root2, ib_rms * root2, ic_rms * root2)

        mech_angle = electrical_to_mechanical_angle(rotor_angle_elec, pole_pairs)
        rotor_position = d_axis_offset + mech_angle + skew_angle
        fluxes, torque = _solve(
            femm,
            model_path,
            currents_peak,
            rotor_position,
            sliding_band,
            circuit_names,
            smart_mesh,
            use_previous_solution=False,
        )

        ia_q_rms, ib_q_rms, ic_q_rms = dq_to_abc(0.0, iq_rms, rotor_angle_elec)
        q_currents_peak = (ia_q_rms * root2, ib_q_rms * root2, ic_q_rms * root2)
        q_fluxes, q_torque = _solve(
            femm,
            model_path,
            q_currents_peak,
            rotor_position,
            sliding_band,
            circuit_names,
            smart_mesh,
            use_previous_solution=True,
        )

        if bool(settings["save_flux_density_bitmap"]):
            femm.mo_zoomnatural()
            femm.mo_showdensityplot(1, 0, 1.6, 0, "bmag")
            bitmap = Path(settings["raw_dir"]) / (
                f"slice{slice_index + 1}_{point['case_id']}_Bmag.bmp"
            )
            femm.mo_savebitmap(str(bitmap))

        row = {
            "Worker": slice_index,
            "sliceNo": slice_index,
            "electricalAngle": rotor_angle_elec,
            "skewAngleMech": skew_angle,
            "IRMS_amps": current_rms,
            "currentAngle": phase_angle,
            "IqRMS": iq_rms,
            "IdRMS": id_rms,
            "Ia": currents_peak[0],
            "Ib": currents_peak[1],
            "Ic": currents_peak[2],
            "wa": fluxes[0] * symmetry,
            "wb": fluxes[1] * symmetry,
            "wc": fluxes[2] * symmetry,
            "torque": torque,
            "blockTorque": 0.0,
            "Ia_q": q_currents_peak[0],
            "Ib_q": q_currents_peak[1],
            "Ic_q": q_currents_peak[2],
            "wa_q": q_fluxes[0] * symmetry,
            "wb_q": q_fluxes[1] * symmetry,
            "wc_q": q_fluxes[2] * symmetry,
            "torque_q": q_torque,
            "blockTorque_q": 0.0,
        }
        return pd.DataFrame([row]), pd.DataFrame(columns=["sliceNo"])
    finally:
        femm.closefemm()
