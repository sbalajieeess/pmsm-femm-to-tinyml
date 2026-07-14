# Upgrade Roadmap

## v0.1 — Team reproducibility baseline

- config-driven FEMM four-slice runner
- model/input validation
- raw and summarized output
- SHA-256 provenance
- Windows quick start
- tests and GitHub CI
- public publishing workflow

## v0.2 — Numerical regression and diagnostics

- approved reference-point tolerance file
- automated result comparison report
- no-load/cogging supported entry point
- flux-density image selection
- richer environment capture
- restart/resume at operating-point level
- configurable sequential/limited point-level parallelism

## v0.3 — Geometry/material adapter

- explicit machine definition schema
- winding/material inventory extraction
- FEMM model-generation checks
- geometry version IDs and model cards
- separation of proprietary model inputs from reusable code

## v0.4 — Elmer 2D integration

- Gmsh physical-group contract
- SIF generation and validation
- three-stream sweep orchestration
- torque/flux/B extraction
- sparse FEMM-versus-Elmer comparison matrix
- convergence and compute-cost dashboard

## v0.5 — Map optimization and controller dataset

- validated interpolation policy
- MTPA/MTPV optimizer
- speed, Vdc, and temperature expansion
- current/voltage/thermal constraints
- controller-ready LUT export with schema versioning

## v0.6 — TinyML compression

- notebook-to-package training path
- deterministic train/validation split
- float and quantized metrics
- hybrid LUT boundary patching
- embedded C inference tests
- memory/latency/error release report

## Later — Sparse 3D validation

Use Elmer 3D only for selected anchors until storage, runtime, and extraction are controlled. Include automatic cleanup and artifact-retention policies from the start.
