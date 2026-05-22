# paper_style.py
# Shared plotting style for the hydrovoltaic ML manuscript

from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt


# Main palette
COLORS = {
    "black": "#000000",
    "dark_gray": "#4D4D4D",
    "gray": "#8C8C8C",
    "light_gray": "#C7C7C7",
    "very_light_gray": "#EFEFEF",

    # Your preferred publication palette
    "vermillion": "#D55E00",
    "orange": "#E69F00",
    "green": "#009E73",
    "sky_blue": "#56B4E9",
    "blue": "#0072B2",
    "purple": "#CC79A7",
    "yellow": "#F0E442",
}

# Semantic colors for this paper
SEMANTIC = {
    # Main regime colors
    "favorable": "#009E73",      # low-R point color
    "limited": "#D55E00",        # high-R point color

    # Soft fill colors used consistently for regime background and box fill
    "favorable_fill": "#BFD8CF", # soft green fill
    "limited_fill": "#E7D3BE",   # soft warm fill

    # Neutral colors
    "raw_data": "#BDBDBD",
    "trend": "#000000",
    "reference": "#D0D0D0",
}

FIG_SIZES = {
    "single": (3.35, 2.65),
    "wide": (6.8, 2.8),
    "two_panel": (6.8, 2.8),
    "four_panel": (7.2, 5.6),
    "square": (3.2, 3.2),
}


def set_paper_style(context="panel"):
    """
    Set matplotlib style for manuscript figures.
    """
    if context == "panel":
        base_font = 8.5
        label_font = 9.5
        title_font = 10.0
        legend_font = 8.0
    elif context == "combined":
        base_font = 9.0
        label_font = 10.0
        title_font = 10.5
        legend_font = 8.5
    else:
        raise ValueError("context must be 'panel' or 'combined'")

    mpl.rcParams.update({
        "font.family": "Arial",
        "font.size": base_font,
        "font.weight": "normal",

        "mathtext.fontset": "custom",
        "mathtext.rm": "Arial",
        "mathtext.it": "Arial:italic",
        "mathtext.bf": "Arial:bold",

        "axes.linewidth": 1.0,
        "axes.labelsize": label_font,
        "axes.titlesize": title_font,
        "axes.labelweight": "normal",
        "axes.titleweight": "normal",

        "xtick.labelsize": base_font,
        "ytick.labelsize": base_font,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 4,
        "ytick.major.size": 4,
        "xtick.major.width": 1.0,
        "ytick.major.width": 1.0,
        "xtick.minor.size": 2,
        "ytick.minor.size": 2,
        "xtick.minor.width": 0.8,
        "ytick.minor.width": 0.8,

        "lines.linewidth": 1.2,
        "lines.markersize": 4,

        "legend.fontsize": legend_font,
        "legend.frameon": False,
        "legend.handlelength": 1.5,
        "legend.borderaxespad": 0.4,

        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.03,
        "savefig.dpi": 600,

        "figure.dpi": 150,
        "axes.grid": False,
    })


def format_ax(ax, mirror=True, top_right_ticks=False):
    """
    Consistent axis styling.
    """
    for spine in ax.spines.values():
        spine.set_linewidth(1.0)
        spine.set_color(COLORS["black"])

    if mirror:
        ax.spines["top"].set_visible(True)
        ax.spines["right"].set_visible(True)
    else:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    ax.tick_params(
        direction="out",
        width=1.0,
        length=4,
        color=COLORS["black"],
        top=top_right_ticks,
        right=top_right_ticks
    )
    ax.tick_params(which="minor", direction="out", width=0.8, length=2)
    return ax


def add_zero_line(ax, axis="y"):
    """
    Add light dashed zero/reference line.
    """
    if axis == "y":
        ax.axhline(0, color=SEMANTIC["reference"], linestyle="--", linewidth=1.0, zorder=0)
    elif axis == "x":
        ax.axvline(0, color=SEMANTIC["reference"], linestyle="--", linewidth=1.0, zorder=0)
    else:
        raise ValueError("axis must be 'x' or 'y'")


def add_vertical_threshold(ax, x, label=None, color="#AFAFAF"):
    """
    Add vertical threshold line, e.g., log(R) = -1.
    """
    ax.axvline(x, color=color, linestyle="--", linewidth=1.0, zorder=0)
    if label is not None:
        ymin, ymax = ax.get_ylim()
        ax.text(
            x, ymax - 0.05*(ymax - ymin), label,
            ha="left", va="top",
            fontsize=8, color=color
        )


def shade_regimes(ax, threshold=-1.0,
                  low_color="#009E73", high_color="#D55E00",
                  alpha=0.06):
    """
    Add subtle background shading for low-R and high-R regimes.
    """
    xmin, xmax = ax.get_xlim()
    ax.axvspan(xmin, threshold, color=low_color, alpha=alpha, lw=0, zorder=0)
    ax.axvspan(threshold, xmax, color=high_color, alpha=alpha, lw=0, zorder=0)


def add_panel_label(ax, label, x=-0.16, y=1.12, fontsize=13):
    """
    Add panel label such as A, B, C, D.
    """
    ax.text(
        x, y, label,
        transform=ax.transAxes,
        ha="left", va="top",
        fontsize=fontsize,
        fontweight="bold",
        color=COLORS["black"]
    )


def save_figure(fig, out_dir, name, formats=("pdf", "eps", "png")):
    """
    Save figure in multiple formats.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for fmt in formats:
        path = out_dir / f"{name}.{fmt}"
        if fmt == "png":
            fig.savefig(path, dpi=600, bbox_inches="tight")
        else:
            fig.savefig(path, bbox_inches="tight")
        saved.append(path)

    return saved
