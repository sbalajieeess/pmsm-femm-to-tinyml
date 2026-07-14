# Team Handover Checklist

## Repository owner

- [ ] Publish as a private GitHub repository.
- [ ] Replace `CODEOWNERS` placeholder.
- [ ] Add team members with least-required permissions.
- [ ] Protect `main` and require CI/review.
- [ ] Upload the frozen full result archive to the v0.1.0 release.

## Each reproducing engineer

- [ ] Clone to a short local Windows path.
- [ ] Install Python and FEMM.
- [ ] Run `bootstrap_windows.ps1`.
- [ ] Run environment and manifest checks.
- [ ] Run unit tests.
- [ ] Run the two-point 100 °C smoke test.
- [ ] Record FEMM/Python/Windows versions and machine specification.
- [ ] Compare the smoke summary with the approved release baseline.
- [ ] Report failures through the GitHub issue template with run artifacts.

## Before a new map

- [ ] Geometry/material model reviewed.
- [ ] New immutable config committed.
- [ ] Operating-point CSV reviewed.
- [ ] No-load and smoke anchors accepted.
- [ ] Coarse map accepted.
- [ ] Disk space and retention location confirmed.
- [ ] Run ID follows the naming convention.

## Before using data for MTPA/MTPV or TinyML

- [ ] Solver completeness checked.
- [ ] Torque sign and dq conventions confirmed.
- [ ] Units and RMS/peak conventions confirmed.
- [ ] Temperature and Vdc metadata present.
- [ ] Duplicate/missing operating points checked.
- [ ] FEMM-versus-Elmer validation status recorded.
- [ ] Dataset schema version frozen.
