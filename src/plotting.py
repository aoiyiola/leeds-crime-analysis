"""Shared map and chart styling, so every figure looks like part of the same project."""
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm

from . import config

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
})

KDE_CMAP = LinearSegmentedColormap.from_list("kde", config.KDE_PALETTE)


def map_axes(boundary: gpd.GeoDataFrame, title: str, basemap: bool = True, figsize=(10, 9)):
    """Create a map figure framed on Leeds, with an optional light street basemap."""
    fig, ax = plt.subplots(figsize=figsize)
    xmin, ymin, xmax, ymax = boundary.total_bounds
    pad = 0.03 * (xmax - xmin)
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)
    ax.set_axis_off()
    ax.set_title(title)
    if basemap:
        add_basemap(ax)
    return fig, ax


def add_basemap(ax) -> None:
    """Add light grey Esri tiles under the map (no API key needed). Skipped when offline."""
    try:
        import contextily as ctx

        ctx.add_basemap(ax, crs=config.CRS_BNG, source=ctx.providers.Esri.WorldGrayCanvas,
                        attribution_size=6)
    except Exception as exc:  # no internet, or contextily missing
        print(f"Basemap skipped ({type(exc).__name__})")


def kde_norm():
    """Logarithmic colour scale shared by every density map.

    Crime density ranges from a few incidents per km² in rural areas to almost 10,000
    in the city centre, so a log scale keeps both suburban and central detail visible.
    """
    return LogNorm(vmin=config.KDE_LOG_RANGE[0], vmax=config.KDE_LOG_RANGE[1], clip=True)


def draw_lsoas(ax, lsoas: gpd.GeoDataFrame, outline_width: float = 1.2) -> None:
    """Thin LSOA boundaries plus a stronger Leeds district outline."""
    lsoas.boundary.plot(ax=ax, color="#555555", linewidth=0.25, alpha=0.6, zorder=3)
    gpd.GeoSeries([lsoas.union_all()], crs=lsoas.crs).boundary.plot(
        ax=ax, color="#222222", linewidth=outline_width, zorder=4)


def save(fig, name: str, folder: Path = config.FIGURES_DIR) -> Path:
    """Save a figure as PNG to results/figures and return its path."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    print(f"Saved {path.relative_to(config.PROJECT_ROOT)}")
    return path
