# HEP validation plot contract

Each plot must have a vector PDF and a JSON sidecar containing enough information to reproduce and audit the displayed numbers.

## Minimum JSON structure

```json
{
  "schema_version": "1.0",
  "plot": {
    "id": "stable-plot-id",
    "kind": "data_mc_overlay",
    "title": "Observable after selection",
    "x_label": "Observable [unit]",
    "y_label": "Events / bin",
    "x_range": [0.0, 1.0],
    "normalization": "none",
    "derived_panel": {
      "kind": "data_over_mc",
      "uncertainty_scheme": "data_points_plus_mc_band"
    }
  },
  "selection": {
    "expression": "machine-readable or exact textual selection",
    "category": "unconverted, negative endcap",
    "weight": "event weight expression"
  },
  "provenance": {
    "created_at": "ISO-8601 timestamp",
    "inputs": ["input file or dataset identifier"],
    "code_revision": "git commit or version",
    "command": "reproduction command",
    "negative_weights": false
  },
  "series": [
    {
      "name": "Data",
      "role": "data",
      "bin_edges": [0.0, 0.5, 1.0],
      "sumw": [12.0, 8.0],
      "sumw2": [12.0, 8.0]
    }
  ],
  "derived": {
    "values": [],
    "variances": [],
    "valid": []
  }
}
```

Use `normalization` values `none`, `unit_area`, or `density`. A density additionally divides by bin width. A derived panel may be omitted. When it is present, `values`, `variances`, and `valid` must have one entry per bin; use `null` and `false` for undefined bins.

## Statistical uncertainty

For an unnormalized weighted bin, store

`Y_i = sum(w)` and `Var(Y_i) = sum(w^2)`.

For an unweighted count, this reduces to the usual Poisson variance. Never use `sqrt(sumw)` as the uncertainty for a weighted sample.

For a unit-area shape with `p_i = Y_i / S` and `S = sum(Y)`, propagate the uncertainty of both `Y_i` and `S`. For statistically independent input bins,

`Var(p_i) = ((S-Y_i)^2 V_i + Y_i^2 (V_total-V_i)) / S^4`,

where `V_i = sumw2_i` and `V_total = sum(V_i)`. Preserve bin-to-bin covariance when a later calculation uses the normalized bins.

For an independent ratio `R = A/B`,

`Var(R) = Var(A)/B^2 + A^2 Var(B)/B^4`.

Do not evaluate it where `B = 0`. For the conventional data/MC display, show data uncertainty on the ratio points and MC uncertainty as a band around one; do not also fold the same MC term into the points unless the figure is explicitly labeled as a combined uncertainty.

For an efficiency whose numerator is a subset of its denominator, account for their covariance. Use a binomial interval for unweighted events or a documented weighted-efficiency prescription based on effective counts or bootstrap/resampling. Do not treat numerator and denominator as independent. Propagate independent data and MC efficiency uncertainties into a scale factor; document correlations if they are shared.

## Comparison rules

A controlled comparison requires identical observable definition, category, selection except for the explicitly studied change, bin edges, normalization, displayed axis range, and units. Record the studied change separately. If any other dimension differs, label the plots as contextual rather than before/after evidence.

## Output rules

- Prefer PDF primitives for axes, text, markers, lines, and uncertainty bands.
- Keep numerical values at useful precision in JSON; round only display labels.
- Put units in axis labels and define category/selection in the caption or source note.
- Use stable plot identifiers and deterministic file names.
- Never embed private raw event records in the JSON sidecar.
