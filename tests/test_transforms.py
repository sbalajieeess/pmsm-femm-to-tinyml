import math

import pytest

from pmsm_femm.transforms import abc_to_dq, dq_to_abc, electrical_to_mechanical_angle


@pytest.mark.parametrize(
    ("d_value", "q_value", "angle_deg"),
    [
        (0.0, 0.0, 0.0),
        (-30.0, 100.0, 0.0),
        (-120.0, 160.0, 37.5),
        (15.5, -42.25, -83.0),
    ],
)
def test_dq_abc_round_trip(d_value: float, q_value: float, angle_deg: float) -> None:
    abc = dq_to_abc(d_value, q_value, angle_deg)
    recovered = abc_to_dq(*abc, angle_deg)
    assert recovered[0] == pytest.approx(d_value, abs=1e-10)
    assert recovered[1] == pytest.approx(q_value, abs=1e-10)
    assert sum(abc) == pytest.approx(0.0, abs=1e-10)


def test_electrical_to_mechanical_angle() -> None:
    assert electrical_to_mechanical_angle(40.0, 4) == pytest.approx(10.0)
    with pytest.raises(ValueError):
        electrical_to_mechanical_angle(10.0, 0)


def test_current_magnitude_is_preserved_in_orthogonal_frame() -> None:
    d_value, q_value = -30.0, 100.0
    a_value, b_value, c_value = dq_to_abc(d_value, q_value, 17.0)
    abc_rms_equivalent = math.sqrt((2.0 / 3.0) * (a_value**2 + b_value**2 + c_value**2))
    assert abc_rms_equivalent == pytest.approx(math.hypot(d_value, q_value))
