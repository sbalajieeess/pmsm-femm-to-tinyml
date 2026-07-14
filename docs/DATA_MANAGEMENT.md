# Data and Artifact Management

## Store in Git

- Python source and tests
- TOML configs
- small operating-point CSVs
- approved small regression samples
- documentation and manifests
- compact plots used directly in review

## Do not store in normal Git history

- complete dense raw maps
- `.ans` files
- per-point bitmaps
- mesh exports
- repeated temporary `.FEM` worker copies
- Python caches
- large Elmer VTU/result directories
- trained model binaries unless the organization explicitly approves them

These items are excluded by `.gitignore`.

## Approved large-artifact pattern

Package a frozen result set separately with:

```text
result-archive/
├─ README.txt
├─ artifact_manifest.json
├─ environment.txt
├─ run_manifest.json
├─ summary.csv
└─ raw/...
```

Attach the archive to a tagged private GitHub Release or place it in the organization’s controlled artifact/data storage. Record the release URL or artifact identifier in the project report.

## Why the supplied folder became large

The source archive contained more than twelve thousand generated CSVs plus plots and solver artifacts. Growth came from the number of operating points and per-point outputs, not from Python source. Elmer VTU/mesh/checkpoint data can increase storage much faster than FEMM CSV summaries, so Elmer cleanup and retention rules must be stricter.

## Retention proposal

- Keep every accepted summary and manifest.
- Keep raw files for release baselines and failed/anomalous cases.
- Keep only selected field images for review.
- Delete temporary worker models and solver intermediates after successful verification.
- Preserve a frozen full archive at major geometry/material milestones.
