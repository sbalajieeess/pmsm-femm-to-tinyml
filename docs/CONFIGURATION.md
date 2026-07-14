# Configuration Reference

## Rule: copy, then edit

For a new temperature or geometry, copy an existing TOML file, rename it clearly, and commit it with the corresponding approved model. Do not overwrite a historical config used by a released result set.

## `[run]`

| Key | Meaning |
|---|---|
| `name` | Human-readable run family. |
| `model` | Repository-relative or absolute `.FEM` path. Prefer repository-relative. |
| `output_root` | Generated run root; normally `runs`. |
| `parallel_workers` | Maximum simultaneous skew-slice FEMM processes. Four is natural for the four-slice model. |
| `continue_on_error` | Continue remaining points after a failed point. Keep `false` for acceptance runs. |
| `save_flux_density_bitmap` | Save a B-magnitude bitmap for each slice and point. Large-output option. |
| `save_mesh_text` | Reserved; must remain `false` in v0.1.0. |

## `[motor]`

- `temperature_c`: metadata for this material/model state.
- `symmetry_factor`: one-eighth model uses `8`.
- `pole_pairs`: supplied motor uses `4`.
- `stack_length_mm_total`: total active length represented by all slices.
- `stack_length_mm_per_slice`: must match the `.FEM` `[Depth]` field.
- `phase_resistance_mohm`: retained for future voltage/loss calculations; v0.1.0 speed estimate neglects resistance.

## `[inverter]`

`dc_voltage_v` is used in the analytical voltage/speed limit. It does not alter the static FEMM field solve.

## `[coordinates]`

- `d_axis_sliding_band_mech_deg`: mechanical offset aligning the model d-axis.
- `rotor_angle_elec_deg`: electrical solve angle.
- `torque_sign_to_positive_motoring`: use `-1` for the supplied model convention.

Changing coordinate signs or offsets requires a documented reference-point comparison.

## `[skew]`

`angles_mech_deg` defines the physical slices. The number of angles is the slice count and must be consistent with model depth and total stack length.

## `[femm]`

- `sliding_band_name`: must exist in the model.
- `circuit_names`: must match the model’s U/V/W circuits and phase order.
- `mesh_lua`: preserved future mesh sampling dependency.
- `smart_mesh`: maintain the validated setting unless a mesh study supports a change.
- `hide_window`: run FEMM hidden on team machines.

## New geometry checklist

1. Confirm ownership and approved storage location.
2. Add the `.FEM` model under a geometry-specific subfolder when multiple designs exist.
3. Create a new config; never repoint an old released config silently.
4. Confirm depth, symmetry, pole pairs, winding circuit names, sliding band, d-axis offset, magnet grade, steel curve, and temperature state.
5. Run environment validation.
6. Run no-load and two-point smoke checks.
7. Run the 20-point coarse map.
8. Compare against the design’s approved FEMM baseline and sparse Elmer anchors before a dense map.
