# Repository governance

**Canonical repository:** the copy owned by Balaji S.

Team members work in forks and submit pull requests. Direct work on `main` is not
accepted. Every numerical change must include the command used, the input/config hash,
the output summary, and a comparison against the current accepted baseline.

## Branch naming

- `feature/...` for new capabilities
- `fix/...` for corrections
- `model/...` for geometry or material additions
- `docs/...` for documentation-only work

## Generated data

Solver meshes, VTU files, FEMM answer files, logs, plots, trained models, and large CSV
grids belong in release assets or an approved data store, not normal Git history.
