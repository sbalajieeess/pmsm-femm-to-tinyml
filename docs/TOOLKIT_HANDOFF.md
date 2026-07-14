# Shared-toolkit handoff

The accepted FEMM output is `femm_truth_map_v1.csv`. Validate it with the sibling toolkit:

```powershell
pmsm-map-validate --input runs\RUN_ID\femm_truth_map_v1.csv --report runs\RUN_ID\validation.json
pmsm-map-visualize --input runs\RUN_ID\femm_truth_map_v1.csv --output-dir runs\RUN_ID\plots
```

Never add FEMM-specific filename parsing or solver automation to the shared toolkit.
