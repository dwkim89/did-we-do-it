#!/usr/bin/env python3
"""Aggregate compatible shape JSON slices into one normalized comparison plot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--eta-bins", nargs="+", required=True)
    parser.add_argument("--pt-bins", nargs="+", required=True)
    parser.add_argument("--conversion", required=True)
    parser.add_argument("--variable", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--x-min", type=float, required=True)
    parser.add_argument("--x-max", type=float, required=True)
    parser.add_argument("--eta-label", required=True)
    parser.add_argument("--pt-label", required=True)
    parser.add_argument("--x-label", required=True)
    return parser.parse_args()


def add_arrays(total: np.ndarray | None, values: list[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    return array.copy() if total is None else total + array


def main() -> None:
    args = parse_args()
    edges: np.ndarray | None = None
    data = data_sumw2 = mc = mc_sumw2 = None
    data_photons = mc_photons = 0

    for eta_bin in args.eta_bins:
        for pt_bin in args.pt_bins:
            path = (
                args.input_root
                / eta_bin
                / pt_bin
                / args.conversion
                / f"{args.variable}.json"
            )
            payload = json.loads(path.read_text())
            candidate_edges = np.asarray(payload["bin_edges"], dtype=float)
            if edges is None:
                edges = candidate_edges
            elif not np.array_equal(edges, candidate_edges):
                raise ValueError(f"incompatible bin edges: {path}")
            data = add_arrays(data, payload["data"]["weighted_bin_content"])
            data_sumw2 = add_arrays(data_sumw2, payload["data"]["sumw2"])
            mc = add_arrays(mc, payload["mc"]["weighted_bin_content"])
            mc_sumw2 = add_arrays(mc_sumw2, payload["mc"]["sumw2"])
            data_photons += int(payload["data_photons"])
            mc_photons += int(payload["mc_photons"])

    assert edges is not None and data is not None and data_sumw2 is not None
    assert mc is not None and mc_sumw2 is not None
    widths = np.diff(edges)
    centers = (edges[:-1] + edges[1:]) / 2.0
    data_norm = float(np.sum(data))
    mc_norm = float(np.sum(mc))
    if data_norm <= 0 or mc_norm <= 0:
        raise ValueError("non-positive aggregate normalization")

    data_density = data / (data_norm * widths)
    mc_density = mc / (mc_norm * widths)
    data_error = np.sqrt(data_sumw2) / (data_norm * widths)
    mc_error = np.sqrt(mc_sumw2) / (mc_norm * widths)

    data_neff = np.divide(data**2, data_sumw2, out=np.zeros_like(data), where=data_sumw2 > 0)
    mc_neff = np.divide(mc**2, mc_sumw2, out=np.zeros_like(mc), where=mc_sumw2 > 0)
    ratio_mask = (data_neff >= 3) & (mc_neff >= 3) & (mc_density > 0) & (data_density > 0)
    ratio = np.divide(data_density, mc_density, out=np.full_like(data_density, np.nan), where=ratio_mask)
    ratio_error = np.full_like(data_density, np.nan)
    ratio_error[ratio_mask] = ratio[ratio_mask] * np.sqrt(
        (data_error[ratio_mask] / data_density[ratio_mask]) ** 2
        + (mc_error[ratio_mask] / mc_density[ratio_mask]) ** 2
    )

    fig, (ax, rax) = plt.subplots(
        2,
        1,
        figsize=(7.2, 5.3),
        gridspec_kw={"height_ratios": [3.0, 1.0], "hspace": 0.03},
        sharex=True,
    )
    ax.stairs(mc_density, edges, color="#D95F02", linewidth=1.7, label="MC (mc23a+d)")
    ax.fill_between(
        centers,
        mc_density - mc_error,
        mc_density + mc_error,
        step="mid",
        color="#D95F02",
        alpha=0.18,
        linewidth=0,
    )
    ax.errorbar(
        centers,
        data_density,
        yerr=data_error,
        fmt="o",
        color="black",
        markersize=2.8,
        linewidth=0.8,
        label="Data (2022+2023)",
    )
    ax.set_ylabel("Normalized density")
    ax.set_xlim(args.x_min, args.x_max)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.text(
        0.03,
        0.95,
        "ATLAS Work in Progress\n"
        f"ee$\\gamma$ + $\\mu\\mu\\gamma$, {args.conversion}, Tight ID + loose isolation\n"
        f"{args.pt_label}, {args.eta_label}\n"
        f"Data photons: {data_photons:,}; MC photons: {mc_photons:,}",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
    )

    rax.axhline(1.0, color="#D95F02", linewidth=1.0)
    rax.errorbar(
        centers[ratio_mask],
        ratio[ratio_mask],
        yerr=ratio_error[ratio_mask],
        fmt="o",
        color="black",
        markersize=2.5,
        linewidth=0.8,
    )
    rax.set_ylim(0.5, 1.5)
    rax.set_ylabel("Data / MC")
    rax.set_xlabel(args.x_label)
    rax.grid(axis="y", alpha=0.22)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
