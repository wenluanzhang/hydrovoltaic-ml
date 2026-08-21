"""
paper_style.py

Shared plotting style utilities for the hydrovoltaic-ML manuscript.

Design principles
-----------------
1. Python generates clean single-panel data plots.
2. Adobe Illustrator is used for final multi-panel assembly, labels, and minor layout refinement.
3. Colors carry consistent meanings across figures:
   - descriptor palette: categorical grouping for dataset descriptors, used in Figures 1, 2, and 5.
   - regime palette: low-R / high-R resistance regimes, used in Figures 4 and 6.
   - model palette: neutral model comparison, descriptor highlight, and ablation loss, used in Figures 3 and 6.
4. Box + scatter plots use colored raw data points and hollow black boxplots.
   The scatter points are the main data layer; the boxplot is the summary layer.

Typical usage
-------------
from paper_style import *

set_paper_style()
fig, ax = plt.subplots(figsize=FIG_SIZES["single"])
plot_hollow_box_colored_scatter(...)
save_figure(fig, out_dir, "fig2A_final_mechanism_label_vs_performance")
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt


# =============================================================================
# Figure sizes
# =============================================================================

FIG_SIZES = {
    # Standard single panel used for most 2-category / 3-category plots
    "single": (3.35, 2.65),

    # Wider single panel for 5-category plots or long y labels
    "wide": (4.65, 2.65),

    # Taller panel for SHAP / descriptor importance plots
    "tall": (3.95, 3.05),

    # Larger panel for combined subpanels such as Fig. 1C
    "combined_2x2": (7.2, 5.4),

    # Reporting-completeness style horizontal bar plot
    "availability": (5.8, 3.8),

    # Long ranked virtual-design candidates
    "ranked": (5.15, 3.85),
}


# =============================================================================
# Core colors
# =============================================================================

COLORS = {
    "black": "#000000",
    "dark_gray": "#4D4D4D",
    "gray": "#8C8C8C",
    "light_gray": "#C7C7C7",
    "very_light_gray": "#EFEFEF",

    # Okabe-Ito / colorblind-friendly family
    "blue": "#0072B2",
    "sky_blue": "#56B4E9",
    "green": "#009E73",
    "orange": "#E69F00",
    "vermillion": "#D55E00",
    "purple": "#CC79A7",
    "yellow": "#F0E442",
}


# Descriptor palette: categorical grouping, not favorable/limited meaning.
# Used mainly in Figures 1, 2, and 5.
DESCRIPTOR_COLORS = {
    "proton": "#B08C5A",
    "other_cation": "#4C9A8A",
    "anion": "#6C8EBF",

    "porous": "#B08C5A",
    "film": "#6C8EBF",
    "hydrogel": "#4C9A8A",
    "hydrogel + porous": "#A07CB8",
    "hydrogel + film": "#7F7F7F",
    "hydrogel_+_porous": "#A07CB8",
    "hydrogel_+_film": "#7F7F7F",

    "ion_gradient": "#5B7DB1",
    "streaming": "#A07CB8",
    "ion gradient": "#5B7DB1",

    "without_inorganic_electrolyte": "#B08C5A",
    "with_inorganic_electrolyte": "#4C9A8A",

    "missing": "#C7C7C7",
}


# Resistance-regime palette: this palette carries physical/design meaning.
# Use only where low-R/high-R regimes are explicitly discussed.
REGIME_COLORS = {
    "low_R": "#009E73",
    "low_R_fill": "#BFD8CF",
    "high_R": "#D55E00",
    "high_R_fill": "#E7D3BE",
    "threshold": "#8C8C8C",
}


# Model/ML palette, used mainly in Figures 3 and 6.
MODEL_COLORS = {
    "neutral": "#8C8C8C",
    "neutral_light": "#BDBDBD",
    "neutral_fill": "#EFEFEF",
    "descriptor": "#009E73",
    "descriptor_fill": "#BFD8CF",
    "loss": "#D55E00",
    "loss_fill": "#E7D3BE",
    "reference": "#D0D0D0",
    "highlight": "#000000",
}


# =============================================================================
# Standard plotting constants
# =============================================================================

SCATTER_SIZE = 14
SCATTER_ALPHA = 0.70
JITTER_SCALE = 0.045

BOX_WIDTH = 0.45
BOX_LINEWIDTH = 1.25
MEDIAN_LINEWIDTH = 1.35
CAP_LINEWIDTH = 1.35

REFERENCE_LINEWIDTH = 1.0
R_THRESHOLD = -1.0


# =============================================================================
# Global matplotlib style
# =============================================================================

def set_paper_style() -> None:
    """Apply manuscript-wide matplotlib style."""
    mpl.rcParams.update({
        "font.family": "Arial",
        "font.size": 8.5,
        "font.weight": "normal",

        "mathtext.fontset": "custom",
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",

        "axes.linewidth": 1.0,
        "axes.labelsize": 9.5,
        "axes.titlesize": 10,
        "axes.labelweight": "normal",
        "axes.titleweight": "normal",

        "xtick.labelsize": 8.0,
        "ytick.labelsize": 8.5,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 4,
        "ytick.major.size": 4,
        "xtick.major.width": 1.0,
        "ytick.major.width": 1.0,

        "lines.linewidth": 1.2,
        "lines.markersize": 4,

        "legend.fontsize": 7.8,
        "legend.frameon": False,

        # Illustrator-friendly vector output
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",

        "savefig.dpi": 600,
        "figure.dpi": 150,
        "axes.grid": False,
    })


def format_ax(ax: plt.Axes, mirror: bool = True) -> plt.Axes:
    """Apply common axis formatting."""
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
        spine.set_color(COLORS["black"])

    ax.spines["top"].set_visible(mirror)
    ax.spines["right"].set_visible(mirror)

    ax.tick_params(
        direction="out",
        width=1.0,
        length=4,
        color=COLORS["black"],
        top=False,
        right=False,
    )

    return ax


def save_figure(
    fig: plt.Figure,
    out_dir: str | Path,
    name: str,
    formats: Sequence[str] = ("pdf", "svg", "png"),
    dpi: int = 600,
    pad_inches: float = 0.03,
) -> None:
    """Save a figure in publication-friendly formats."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for ext in formats:
        path = out_dir / f"{name}.{ext}"
        if ext.lower() == "png":
            fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=pad_inches)
        else:
            fig.savefig(path, bbox_inches="tight", pad_inches=pad_inches)
        print(f"Saved: {path}")


# =============================================================================
# Basic annotations and reference lines
# =============================================================================

def add_panel_label(
    ax: plt.Axes,
    label: str,
    x: float = -0.16,
    y: float = 1.12,
    fontsize: float = 13,
) -> None:
    """Add panel label if needed. Usually final labels are added in Illustrator."""
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=fontsize,
        fontweight="bold",
        color=COLORS["black"],
    )


def add_zero_line(ax: plt.Axes, axis: str = "y", color: str | None = None) -> None:
    """Add a dashed zero reference line."""
    color = color or MODEL_COLORS["reference"]
    if axis == "y":
        ax.axhline(0, linestyle="--", linewidth=REFERENCE_LINEWIDTH, color=color, zorder=1)
    elif axis == "x":
        ax.axvline(0, linestyle="--", linewidth=REFERENCE_LINEWIDTH, color=color, zorder=1)
    else:
        raise ValueError("axis must be 'x' or 'y'")


def add_R_threshold_line(
    ax: plt.Axes,
    y: float = R_THRESHOLD,
    label: bool = True,
) -> None:
    """Add the resistance-regime threshold line at log(R) = -1."""
    ax.axhline(
        y,
        linestyle="--",
        linewidth=REFERENCE_LINEWIDTH,
        color=REGIME_COLORS["threshold"],
        zorder=1,
    )

    if label:
        ax.text(
            0.98,
            y + 0.08,
            r"$\log(R)=-1$",
            transform=ax.get_yaxis_transform(),
            ha="right",
            va="bottom",
            fontsize=7.5,
            color=COLORS["dark_gray"],
        )


def shade_R_regimes(
    ax: plt.Axes,
    threshold: float = R_THRESHOLD,
    xmin: float | None = None,
    xmax: float | None = None,
    alpha: float = 0.65,
) -> None:
    """Shade low-R and high-R regions in an x-axis log(R) plot."""
    if xmin is None or xmax is None:
        xmin, xmax = ax.get_xlim()

    ax.axvspan(
        xmin,
        threshold,
        facecolor=REGIME_COLORS["low_R_fill"],
        alpha=alpha,
        lw=0,
        zorder=0,
    )
    ax.axvspan(
        threshold,
        xmax,
        facecolor=REGIME_COLORS["high_R_fill"],
        alpha=alpha,
        lw=0,
        zorder=0,
    )


# =============================================================================
# Box + scatter plots
# =============================================================================

def plot_hollow_box_colored_scatter(
    ax: plt.Axes,
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    order: Sequence[str],
    label_map: Mapping[str, str],
    color_map: Mapping[str, str],
    title: str,
    ylabel: str,
    ylim: tuple[float, float],
    rotate: float = 0,
    show_n: bool = True,
    seed: int = 42,
    zero_line: bool = False,
    R_threshold_line: bool = False,
) -> plt.Axes:
    """
    Standard final style for grouped distribution plots.

    Visual logic:
    - colored scatter points = group/category identity
    - hollow black box = distribution summary
    - no box fill, so raw points remain visible

    Use for:
    - Fig. 2A/B/C: value_col = log_P_est, zero_line=True
    - Fig. 4B: value_col = log_P_est, zero_line=True, regime colors
    - Fig. 5A/B/C: value_col = log_R, R_threshold_line=True
    """
    d = df.dropna(subset=[group_col, value_col]).copy()
    present_groups = set(d[group_col].astype(str))
    order = [g for g in order if g in present_groups]

    if not order:
        raise ValueError(f"No requested groups from {order} found in column {group_col!r}.")

    data = [
        d.loc[d[group_col].astype(str) == g, value_col].dropna().values
        for g in order
    ]
    positions = np.arange(1, len(order) + 1)

    rng = np.random.default_rng(seed)

    # Raw scatter points
    for i, g in enumerate(order, start=1):
        y = d.loc[d[group_col].astype(str) == g, value_col].dropna().values
        x = rng.normal(loc=i, scale=JITTER_SCALE, size=len(y))

        ax.scatter(
            x,
            y,
            s=SCATTER_SIZE,
            color=color_map.get(g, COLORS["gray"]),
            alpha=SCATTER_ALPHA,
            edgecolor="none",
            zorder=3,
        )

    # Hollow boxplot
    box = ax.boxplot(
        data,
        positions=positions,
        widths=BOX_WIDTH,
        patch_artist=True,
        showfliers=False,
        medianprops=dict(
            color=COLORS["black"],
            linewidth=MEDIAN_LINEWIDTH,
            zorder=8,
        ),
        boxprops=dict(
            linewidth=BOX_LINEWIDTH,
            color=COLORS["black"],
            zorder=7,
        ),
        whiskerprops=dict(
            linewidth=BOX_LINEWIDTH,
            color=COLORS["black"],
            zorder=7,
        ),
        capprops=dict(
            linewidth=CAP_LINEWIDTH,
            color=COLORS["black"],
            zorder=8,
        ),
    )

    for patch in box["boxes"]:
        patch.set_facecolor("none")
        patch.set_edgecolor(COLORS["black"])
        patch.set_linewidth(BOX_LINEWIDTH)
        patch.set_zorder(7)

    for element in ["whiskers", "caps", "medians"]:
        for artist in box[element]:
            artist.set_zorder(8)

    if zero_line:
        add_zero_line(ax, axis="y")

    if R_threshold_line:
        add_R_threshold_line(ax, y=R_THRESHOLD, label=True)

    if show_n:
        n_y = ylim[0] + 0.25 if R_threshold_line else ylim[0] + 0.12 * (ylim[1] - ylim[0])
        for i, g in enumerate(order, start=1):
            n = d.loc[d[group_col].astype(str) == g, value_col].dropna().shape[0]
            ax.text(
                i,
                n_y,
                f"n={n}",
                ha="center",
                va="bottom",
                fontsize=7.5,
                color=COLORS["dark_gray"],
                zorder=9,
            )

    labels = [label_map.get(g, g) for g in order]
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=rotate, ha="right" if rotate else "center")

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(ylim)

    format_ax(ax, mirror=True)
    return ax


# =============================================================================
# Lollipop / dot plots
# =============================================================================

def plot_lollipop(
    ax: plt.Axes,
    y_labels: Sequence[str],
    values: Sequence[float],
    colors: Sequence[str] | str,
    xlabel: str,
    title: str,
    xlim: tuple[float, float] | None = None,
    zero_line: bool = False,
    linewidth: float = 1.25,
    markersize: float = 4.5,
) -> plt.Axes:
    """Standard horizontal lollipop plot."""
    values = np.asarray(values, dtype=float)
    y = np.arange(len(values))

    if isinstance(colors, str):
        colors = [colors] * len(values)

    for i, (val, color) in enumerate(zip(values, colors)):
        ax.hlines(
            y=i,
            xmin=0,
            xmax=val,
            linewidth=linewidth,
            color=color,
            zorder=2,
        )
        ax.plot(
            val,
            i,
            "o",
            markersize=markersize,
            color=color,
            zorder=3,
        )

    if zero_line:
        add_zero_line(ax, axis="x", color=COLORS["gray"])

    ax.set_yticks(y)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel(xlabel)
    ax.set_title(title)

    if xlim is not None:
        ax.set_xlim(xlim)

    format_ax(ax, mirror=True)
    return ax


# =============================================================================
# Errorbar model-comparison plots
# =============================================================================

def plot_cv_errorbar(
    ax: plt.Axes,
    labels: Sequence[str],
    means: Sequence[float],
    stds: Sequence[float],
    ylabel: str,
    title: str,
    ylim: tuple[float, float] | None = None,
    rotation: float = 25,
) -> plt.Axes:
    """Standard model-comparison errorbar plot."""
    x = np.arange(len(labels))

    ax.errorbar(
        x,
        means,
        yerr=stds,
        fmt="o",
        color=COLORS["black"],
        ecolor=COLORS["gray"],
        elinewidth=1.0,
        capsize=3,
        markersize=4.5,
        markerfacecolor=COLORS["black"],
        markeredgecolor=COLORS["black"],
        zorder=3,
    )

    add_zero_line(ax, axis="y")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=rotation, ha="right" if rotation else "center")
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if ylim is not None:
        ax.set_ylim(ylim)

    format_ax(ax, mirror=True)
    return ax


# =============================================================================
# Count and availability bar plots
# =============================================================================

def barh_count_panel(
    ax: plt.Axes,
    df: pd.DataFrame,
    cat_col: str,
    count_col: str,
    percent_col: str,
    label_col: str,
    color_map: Mapping[str, str],
    title: str,
    xlabel: str = "Count",
) -> plt.Axes:
    """Horizontal count bar plot with count and percentage labels."""
    y = np.arange(len(df))
    colors = [color_map.get(v, COLORS["light_gray"]) for v in df[cat_col]]

    ax.barh(
        y,
        df[count_col],
        color=colors,
        edgecolor=COLORS["black"],
        linewidth=0.8,
        zorder=2,
    )

    ax.set_yticks(y)
    ax.set_yticklabels(df[label_col])
    ax.set_xlabel(xlabel)
    ax.set_title(title)

    xmax = max(float(df[count_col].max()) * 1.22, 5)
    ax.set_xlim(0, xmax)

    for i, row in enumerate(df.itertuples(index=False)):
        count = getattr(row, count_col)
        percent = getattr(row, percent_col)
        ax.text(
            count + 0.3,
            i,
            f"{count} ({percent:.0f}%)",
            va="center",
            ha="left",
            fontsize=7.2,
            color=COLORS["dark_gray"],
        )

    format_ax(ax, mirror=True)
    return ax


def availability_barh(
    ax: plt.Axes,
    df: pd.DataFrame,
    item_col: str = "variable_group",
    percent_col: str = "availability_percent",
    n_available_col: str = "n_available",
    n_total_col: str = "n_total",
    group_col: str | None = None,
    color_map: Mapping[str, str] | None = None,
    title: str = "Reporting completeness",
) -> plt.Axes:
    """Horizontal availability/completeness bar plot."""
    plot_df = df.sort_values(percent_col, ascending=True).reset_index(drop=True)
    y = np.arange(len(plot_df))

    if group_col is not None and color_map is not None:
        colors = [color_map.get(g, COLORS["gray"]) for g in plot_df[group_col]]
    else:
        colors = [COLORS["gray"]] * len(plot_df)

    ax.barh(
        y,
        plot_df[percent_col],
        color=colors,
        edgecolor=COLORS["black"],
        linewidth=0.8,
        zorder=2,
    )

    ax.set_yticks(y)
    ax.set_yticklabels(plot_df[item_col])
    ax.set_xlabel("Availability (%)")
    ax.set_title(title)
    ax.set_xlim(0, 105)

    for i, row in enumerate(plot_df.itertuples()):
        ax.text(
            getattr(row, percent_col) + 1,
            i,
            f"{getattr(row, n_available_col)}/{getattr(row, n_total_col)}",
            va="center",
            ha="left",
            fontsize=7.3,
            color=COLORS["dark_gray"],
        )

    ax.axvline(
        100,
        linestyle="--",
        linewidth=REFERENCE_LINEWIDTH,
        color=COLORS["light_gray"],
        zorder=1,
    )

    format_ax(ax, mirror=True)
    return ax


# =============================================================================
# Small utility helpers
# =============================================================================

def normalize_token(x: object) -> str:
    """Normalize category tokens for stable matching."""
    s = str(x).strip().lower()
    s = s.replace("_", " ")
    s = " ".join(s.split())
    return s


def short_label_from_token(x: object) -> str:
    """Create a readable label from a snake_case-ish token."""
    return str(x).replace("_", " ").replace("+", " + ").title()
