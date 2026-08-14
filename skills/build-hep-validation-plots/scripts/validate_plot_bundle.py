#!/usr/bin/env python3
"""Validate the mechanical contract of a HEP validation plot bundle."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path


ALLOWED_NORMALIZATIONS = {"none", "unit_area", "density"}


def finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate(payload: dict, pdf_path: Path | None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in ("schema_version", "plot", "selection", "provenance", "series"):
        if key not in payload:
            errors.append(f"missing top-level field: {key}")

    plot = payload.get("plot", {})
    selection = payload.get("selection", {})
    provenance = payload.get("provenance", {})
    series = payload.get("series", [])

    if not isinstance(plot, dict):
        errors.append("plot must be an object")
        plot = {}
    if not isinstance(selection, dict) or not selection.get("expression"):
        errors.append("selection.expression is required")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
        provenance = {}
    else:
        for key in ("created_at", "inputs", "code_revision", "command", "negative_weights"):
            if key not in provenance:
                errors.append(f"provenance.{key} is required")

    normalization = plot.get("normalization")
    if normalization not in ALLOWED_NORMALIZATIONS:
        errors.append(f"plot.normalization must be one of {sorted(ALLOWED_NORMALIZATIONS)}")
    for key in ("id", "kind", "title", "x_label", "y_label", "x_range"):
        if key not in plot:
            errors.append(f"plot.{key} is required")
    x_range = plot.get("x_range")
    if not (
        isinstance(x_range, list)
        and len(x_range) == 2
        and all(finite_number(x) for x in x_range)
        and x_range[0] < x_range[1]
    ):
        errors.append("plot.x_range must contain two increasing finite numbers")

    if not isinstance(series, list) or not series:
        errors.append("series must be a non-empty list")
        series = []

    reference_edges: list[float] | None = None
    bin_count: int | None = None
    for index, item in enumerate(series):
        prefix = f"series[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        for key in ("name", "role", "bin_edges", "sumw", "sumw2"):
            if key not in item:
                errors.append(f"{prefix}.{key} is required")
        edges = item.get("bin_edges", [])
        sumw = item.get("sumw", [])
        sumw2 = item.get("sumw2", [])
        if not isinstance(edges, list) or len(edges) < 2 or not all(finite_number(x) for x in edges):
            errors.append(f"{prefix}.bin_edges must contain at least two finite numbers")
            continue
        if any(right <= left for left, right in zip(edges, edges[1:])):
            errors.append(f"{prefix}.bin_edges must be strictly increasing")
        current_bins = len(edges) - 1
        if not isinstance(sumw, list) or len(sumw) != current_bins or not all(finite_number(x) for x in sumw):
            errors.append(f"{prefix}.sumw must contain one finite value per bin")
        if not isinstance(sumw2, list) or len(sumw2) != current_bins or not all(finite_number(x) for x in sumw2):
            errors.append(f"{prefix}.sumw2 must contain one finite value per bin")
        elif any(value < 0 for value in sumw2):
            errors.append(f"{prefix}.sumw2 contains a negative variance")
        if isinstance(sumw, list) and sumw and all(finite_number(x) and x == 0 for x in sumw):
            errors.append(f"{prefix} is empty")
        if reference_edges is None:
            reference_edges = edges
            bin_count = current_bins
        elif edges != reference_edges:
            errors.append(f"{prefix}.bin_edges do not match the first series")

    derived_panel = plot.get("derived_panel")
    if derived_panel is not None:
        if not isinstance(derived_panel, dict) or not derived_panel.get("kind"):
            errors.append("plot.derived_panel.kind is required")
        if not isinstance(derived_panel, dict) or not derived_panel.get("uncertainty_scheme"):
            errors.append("plot.derived_panel.uncertainty_scheme is required")
        derived = payload.get("derived")
        if not isinstance(derived, dict):
            errors.append("derived is required when plot.derived_panel is present")
        elif bin_count is not None:
            for key in ("values", "variances", "valid"):
                values = derived.get(key)
                if not isinstance(values, list) or len(values) != bin_count:
                    errors.append(f"derived.{key} must contain one entry per bin")
            variances = derived.get("variances", [])
            valid = derived.get("valid", [])
            values = derived.get("values", [])
            for i in range(min(len(values), len(variances), len(valid))):
                if not isinstance(valid[i], bool):
                    errors.append(f"derived.valid[{i}] must be boolean")
                elif valid[i]:
                    if not finite_number(values[i]):
                        errors.append(f"derived.values[{i}] must be finite when valid")
                    if not finite_number(variances[i]) or variances[i] < 0:
                        errors.append(f"derived.variances[{i}] must be finite and non-negative when valid")
                elif values[i] is not None or variances[i] is not None:
                    warnings.append(f"derived bin {i} is invalid but retains a numeric value")

    if pdf_path is None:
        errors.append("a vector PDF path is required")
    elif not pdf_path.is_file():
        errors.append(f"PDF does not exist: {pdf_path}")
    elif pdf_path.read_bytes()[:5] != b"%PDF-":
        errors.append(f"file is not a PDF: {pdf_path}")
    elif shutil.which("pdfimages"):
        result = subprocess.run(
            ["pdfimages", "-list", str(pdf_path)], capture_output=True, text=True, check=False
        )
        rows = [line for line in result.stdout.splitlines() if line.strip() and line.lstrip()[0].isdigit()]
        if rows:
            warnings.append("PDF contains embedded raster images; verify that plotted marks remain vector")
    else:
        warnings.append("pdfimages is unavailable; vector-content inspection was skipped")

    if provenance.get("negative_weights") is True:
        warnings.append("negative weights are declared; confirm cancellation and effective statistics")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path", type=Path, help="machine-readable plot sidecar")
    parser.add_argument("--pdf", type=Path, required=True, help="matching vector PDF")
    args = parser.parse_args()

    try:
        payload = json.loads(args.json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read JSON sidecar: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("ERROR: JSON root must be an object", file=sys.stderr)
        return 2

    errors, warnings = validate(payload, args.pdf)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"OK: plot bundle passed with {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
