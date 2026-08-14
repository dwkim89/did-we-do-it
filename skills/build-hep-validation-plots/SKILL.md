---
name: build-hep-validation-plots
description: Create reproducible HEP validation plots from histogram or binned analysis outputs, including data/MC overlays, ratio or scale-factor panels, statistical uncertainties, consistent comparison settings, vector PDF output, and machine-readable JSON sidecars. Use when producing or regenerating scientific validation figures. Do not diagnose physics anomalies, change event selections, or place plots into presentation slides.
---

# Build HEP Validation Plots

Produce reviewable plots whose visual result and numerical content can be checked independently. Read [references/plot-contract.md](references/plot-contract.md) before implementing or running a plotting workflow.

## Workflow

1. Confirm the requested observable, samples, selection, category, binning, normalization, axis range, and comparison panel. Ask the user before choosing any material detail that is unclear.
2. Preserve the supplied event selection and weights. Do not repair, reinterpret, or optimize them silently.
3. Build every histogram from explicit bin edges. Store per-bin `sumw` and `sumw2`; never recover uncertainty from rounded plotted values.
4. Apply one declared normalization scheme consistently to every compared series. For unit-area shapes, propagate the uncertainty of the normalization and retain the induced bin covariance when it affects a derived comparison.
5. Draw statistical uncertainty on every applicable result:
   - unnormalized yields: error bars or bands from `sqrt(sumw2)`;
   - normalized shapes: propagated uncertainty after normalization;
   - data/MC ratios: data uncertainty and MC uncertainty band, or one explicitly labeled combined uncertainty;
   - efficiencies and scale factors: use the covariance appropriate to nested numerator/denominator selections and propagate both efficiency uncertainties into the scale factor.
6. Keep binning, normalization, axis ranges, labels, units, selection, and category identical across a claimed comparison. If they differ, stop or label the result as an unmatched comparison.
7. Write a vector PDF and a JSON sidecar following the plot contract. Record the full selection and provenance beside each plot in the JSON; add a compact source note to the figure without crowding the data.
8. Run the bundle validator:

```bash
python3 skills/build-hep-validation-plots/scripts/validate_plot_bundle.py \
  PATH/plot.json --pdf PATH/plot.pdf
```

9. Inspect the PDF at presentation size. Confirm readable labels, visible uncertainties, unclipped legends, and no misleading empty or logarithmic regions.
10. Hand the checked PDF and JSON to `build-weekly-beamer` when the figure is needed in a weekly deck. Invoke `hep-cutflow-and-qa` separately when interpretation or anomaly diagnosis is requested.

## Required Checks

- Reject non-finite bin edges, contents, variances, weights, ratios, or scale factors.
- Reject non-increasing or inconsistent bin edges and mismatched series lengths.
- Flag empty histograms and zero denominators; never draw undefined ratio points as zero.
- Reject negative variances. Permit negative MC weights only when provenance declares them and `sumw2` remains valid.
- Verify that every compared series uses the declared normalization and displayed range.
- Verify that uncertainties exist for all plotted series and derived panels.
- Treat materially different selections, categories, binning, normalization, or axes as inconsistent comparisons.
- Fail when provenance, selection, or vector PDF output is missing.

## Boundaries

- Own plot construction, numerical sidecars, and mechanical plot validation.
- Do not decide whether a discrepancy is physical; hand that work to `hep-cutflow-and-qa`.
- Do not select the meeting narrative or edit Beamer files; hand finished artifacts to `build-weekly-beamer`.
- Do not summarize transcripts or alter reviewed meeting evidence.
