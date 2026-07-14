# Architecture

## Design objectives

The supported pipeline separates **domain inputs**, **solver orchestration**, **solver-specific calls**, **post-processing**, and **generated artifacts**. This is the main upgrade point over the supplied legacy package.

```text
TOML config + operating-point CSV + .FEM model
                    │
                    ▼
             Validation layer
                    │
                    ▼
         Operating-point orchestrator
                    │
       four slice processes in parallel
                    │
                    ▼
              FEMM adapter
          loaded + q-reference solve
                    │
                    ▼
             Raw slice CSVs
                    │
                    ▼
             Post-processing
                    │
                    ▼
       summary.csv + manifest.json
```

## Stable interfaces

### Configuration contract

TOML owns run parameters and coordinate conventions. Python source must not be edited for a different temperature, model path, voltage, skew set, symmetry, or worker count.

### Operating-point contract

CSV requires:

```text
case_id,id_rms_a,iq_rms_a,description
```

`case_id` is the stable human-readable join key across runs and later comparison tools.

### Raw FEMM result contract

Each `FL_and_Torque_*.csv` contains one row per skew slice, including loaded and q-reference phase currents, phase flux linkages, and torque.

### Summary contract

`summary.csv` contains one row per operating point with raw/positive torque, dq flux linkage, `Ld`, `Lq`, analytical torque split, and a no-resistance speed estimate.

### Run provenance contract

Each run records:

- copied config
- copied operating-point CSV
- model path and SHA-256
- skew angles and worker count
- pipeline version
- UTC timestamps
- completion/failure status

A future schema version should add FEMM version, pyFEMM version, Windows build, Python packages, CPU/RAM, and Git commit automatically.

## Parallelism policy

The FEMM adapter uses one process per physical skew slice, up to the configured worker count. Operating points are intentionally serial in v0.1.0. This prevents a 20-point map from unexpectedly launching 80 FEMM instances.

The project’s separate Elmer policy of three independent solver streams is not applied to FEMM. Elmer parallelism belongs in a future `elmer_runner.py` adapter and must be configured independently.

## Extension points

- `femm_adapter.py`: FEMM-specific API calls only.
- future `elmer_adapter.py`: SIF generation, mesh/case execution, extraction.
- future `comparison.py`: point-aligned FEMM/Elmer metrics.
- future `materials/` and `geometry/` schemas: model generation independent of a monolithic `.FEM` file.
- future `datasets/`: MTPA/MTPV and TinyML-ready schema versions.
