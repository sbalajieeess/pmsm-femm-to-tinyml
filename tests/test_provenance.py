from pathlib import Path

from pmsm_femm.provenance import capture_environment


def test_environment_capture_has_required_fields() -> None:
    environment = capture_environment(Path(__file__).resolve().parents[1])
    assert environment["python_version"]
    assert environment["system"]
    assert "numpy" in environment["package_versions"]
