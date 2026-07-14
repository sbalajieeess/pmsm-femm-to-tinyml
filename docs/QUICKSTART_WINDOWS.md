# Windows Team Quick Start

## Clone and enter the repository

```powershell
git clone https://github.com/YOUR_OWNER/pmsm-fem-reproducible-pipeline.git
cd pmsm-fem-reproducible-pipeline
```

## Bootstrap once

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\bootstrap_windows.ps1
```

## Start each new terminal

```powershell
cd path\to\pmsm-fem-reproducible-pipeline
.\.venv\Scripts\Activate.ps1
```

## Mandatory pre-run checks

```powershell
python scripts\check_environment.py --config configs\one_eighth_100C.toml
python scripts\verify_manifest.py --manifest reference\input_manifest.json
pytest
```

## First reproduction run

```powershell
scripts\run_smoke_100C.cmd
```

Expected outcome: two completed operating points, eight loaded solves, eight q-axis reference solves, and a `summary.csv` under `runs\smoke_100C`.

## Coarse-map reproduction

```powershell
scripts\run_coarse_100C.cmd
```

Do not run a dense map until the smoke and coarse-map outputs have been reviewed against the approved reference release.

## Common failure checks

| Symptom | Check |
|---|---|
| `No module named femm` | Reinstall FEMM Python support and rerun `bootstrap_windows.ps1`. |
| FEM model contract failure | Check `[Depth]`, `slidingBand`, and U/V/W circuit names against the config. |
| Existing run directory | Use a new `--run-id` or archive/remove the old directory. |
| FEMM windows remain open | Confirm `hide_window=true`; terminate orphaned FEMM processes only after the current point has stopped. |
| Numerical change after code/model edit | Preserve both manifests, compare raw slice files, and document the change in the pull request. |
