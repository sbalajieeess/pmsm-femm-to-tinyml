# PMSM FEMM to TinyML

Reproducible FEMM pipeline for four-skew PMSM electromagnetic truth-map generation.

```text
FEMM model + operating points
  -> four independent skew-slice solves
  -> torque and abc flux extraction
  -> dq flux / Ld / Lq post-processing
  -> canonical FEMM truth map
  -> pmsm-map-ml-toolkit
  -> visualization / MTPA-MTPV / NN / pruning / quantization / C export
```

## Important scope

This repository owns FEMM execution and FEMM-specific post-processing. Solver-independent
visualization and ML code belongs in the separate `pmsm-map-ml-toolkit` repository.

## Windows setup

```powershell
cd D:\FEM_PMSM\GitHub\pmsm-femm-to-tinyml
.\scripts\bootstrap_windows.ps1
.\.venv\Scripts\Activate.ps1
python scripts\check_environment.py --config configs\one_eighth_100C.toml
pytest
scripts\run_smoke_100C.cmd
```

Install the shared toolkit from the sibling checkout:

```powershell
pip install -e D:\FEM_PMSM\GitHub\pmsm-map-ml-toolkit
```

Convert a summarized FEMM map to the common schema:

```powershell
python scripts\export_canonical_truth_map.py `
  --input runs\YOUR_RUN\summary.csv `
  --output runs\YOUR_RUN\femm_truth_map_v1.csv `
  --geometry-id oneEighth_reference_v1
```

The historical scripts are retained under `legacy/femm_skew` for traceability; new team work
should use configuration files and supported scripts instead of editing hard-coded paths.
