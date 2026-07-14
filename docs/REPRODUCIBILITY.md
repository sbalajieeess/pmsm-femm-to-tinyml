# Reproducibility Standard

A result is reproducible only when another team member can identify the exact code, input model, configuration, operating points, solver environment, and output artifact.

## Minimum acceptance evidence

Keep these together:

- repository commit SHA or release tag
- `manifest.json`
- copied `config.toml`
- copied `operating_points.csv`
- `summary.csv`
- raw slice CSVs
- `failures.json`, when present
- Windows, Python, FEMM, and pyFEMM versions
- machine CPU/RAM and elapsed time

## Input immutability

`reference/input_manifest.json` records SHA-256 values for version-controlled FEM models, configs, and example operating-point CSVs.

Verify it with:

```powershell
python scripts\verify_manifest.py --manifest reference\input_manifest.json
```

When an intentional input changes, review the diff and regenerate the manifest in the same pull request:

```powershell
python scripts\create_manifest.py
```

## Result naming

Use run IDs in this form:

```text
<geometry>_<temperature>_<map-density>_<purpose>_v<revision>
```

Example:

```text
oneeighth_v5_100C_coarse20_acceptance_v1
```

Do not use ambiguous names such as `final`, `latest`, `new`, or `test2` for accepted results.

## Numerical comparison gates

A future approved baseline should define tolerances for:

- average torque and per-slice torque
- dq flux linkage
- `Ld` and `Lq`
- analytical-versus-FEA torque residual
- maximum B in selected regions
- runtime and result completeness

Until tolerances are formally approved, every solver-facing change requires engineering review of both raw and summarized values; CI passing alone does not establish electromagnetic equivalence.

## Determinism limitations

FEM mesh generation, solver versions, floating-point libraries, and host conditions can cause small differences. Therefore preserve software versions and compare against engineering tolerances rather than requiring byte-identical numerical CSV output.
