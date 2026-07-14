from __future__ import annotations

import math


def dq_to_abc(
    d_value: float,
    q_value: float,
    rotor_angle_deg: float,
) -> tuple[float, float, float]:
    """Inverse Park + inverse Clarke using the legacy FEMM pipeline convention."""
    angle = math.radians(rotor_angle_deg)
    alpha = d_value * math.cos(angle) - q_value * math.sin(angle)
    beta = q_value * math.cos(angle) + d_value * math.sin(angle)
    a_value = alpha
    b_value = (-alpha + math.sqrt(3.0) * beta) / 2.0
    c_value = (-alpha - math.sqrt(3.0) * beta) / 2.0
    return a_value, b_value, c_value


def abc_to_dq(
    a_value: float,
    b_value: float,
    c_value: float,
    rotor_angle_deg: float,
) -> tuple[float, float]:
    """Clarke + Park using the legacy convention.

    The historical solver data contains a small zero-sequence component, so the
    transform follows the legacy implementation and does not reject non-zero A+B+C.
    """
    del c_value
    alpha = a_value
    beta = (a_value + 2.0 * b_value) / math.sqrt(3.0)
    angle = math.radians(rotor_angle_deg)
    d_value = alpha * math.cos(angle) + beta * math.sin(angle)
    q_value = beta * math.cos(angle) - alpha * math.sin(angle)
    return d_value, q_value


def electrical_to_mechanical_angle(electrical_angle_deg: float, pole_pairs: int) -> float:
    if pole_pairs <= 0:
        raise ValueError("pole_pairs must be positive.")
    return electrical_angle_deg / pole_pairs
