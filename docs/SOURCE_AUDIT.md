# Supplied Source Audit

## Archive examined

`forBalaji.zip` was reorganized into this repository.

## Inventory findings

- 24 Python files plus FEMM Lua/group-support files
- three temperature-specific FEMM models: 20 °C, 60 °C, and 100 °C
- 12,770 generated CSV files
- 121 PNG files
- historical output trees mixed with reusable source
- absolute `C:\Work\...` paths in legacy entry scripts
- simulation, post-processing, plotting, and mode switches combined in single files
- Python caches and temporary/generated artifacts included

## What was preserved

The original reusable scripts are copied unchanged to `legacy/femm_skew/`, excluding cache files. Their purpose is traceability and comparison, not direct team operation.

## What was refactored

- paths moved into TOML config
- operating points moved into CSV
- environment/model checks added
- solver calls isolated in an adapter
- multiprocessing isolated in a runner
- post-processing made independently callable
- run provenance and hashes added
- tests, CI, contribution templates, and documentation added
- generated data excluded from source control by default

## Deliberate non-claims

- The refactor has been syntax-, unit-, and contract-tested in this package.
- A real FEMM solve must be validated on the team’s Windows/FEMM machine.
- The supplied archive did not contain the full current Elmer or TinyML implementation, so those are not claimed as executable in v0.1.0.
