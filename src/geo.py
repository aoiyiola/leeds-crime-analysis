"""Geometry helpers: Leeds boundaries, point conversion and kernel density surfaces."""
from dataclasses import dataclass
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from sklearn.neighbors import KernelDensity

from . import config


def load_leeds_lsoas(path: Path = config.LSOA_BOUNDARIES) -> gpd.GeoDataFrame:
    """Return the Leeds LSOA polygons in British National Grid."""
    lsoas = gpd.read_file(path)
    leeds = lsoas[lsoas["LSOA21NM"].str.startswith(config.LEEDS_LSOA_PREFIX)]
    leeds = leeds[["LSOA21CD", "LSOA21NM", "geometry"]].to_crs(config.CRS_BNG).reset_index(drop=True)
    print(f"Leeds LSOAs: {len(leeds)} (of {len(lsoas):,} in England and Wales)")
    return leeds


def to_points(df: pd.DataFrame, lon: str, lat: str) -> gpd.GeoDataFrame:
    """Convert a table with longitude/latitude columns to points in British National Grid."""
    geometry = gpd.points_from_xy(df[lon], df[lat], crs=config.CRS_WGS84)
    return gpd.GeoDataFrame(df, geometry=geometry).to_crs(config.CRS_BNG)


@dataclass
class DensitySurface:
    """A kernel density estimate on a regular grid, clipped to the study area."""

    values: np.ndarray   # incidents (or venues) per km²; NaN outside Leeds
    extent: tuple        # (xmin, xmax, ymin, ymax) in BNG metres, for imshow
    cell_size: float

    def inside(self) -> np.ndarray:
        return self.values[np.isfinite(self.values)]


def density_surface(
    points: gpd.GeoDataFrame,
    boundary: gpd.GeoDataFrame,
    bandwidth: float = config.KDE_BANDWIDTH_M,
    cell_size: float = config.KDE_CELL_SIZE_M,
) -> DensitySurface:
    """Estimate point density with a Gaussian kernel, clipped to ``boundary``.

    The result is scaled from a probability density to *points per km²*, so the
    colour bar on a map has real units.
    """
    area = boundary.union_all()
    xmin, ymin, xmax, ymax = area.bounds
    xs = np.arange(xmin + cell_size / 2, xmax, cell_size)
    ys = np.arange(ymin + cell_size / 2, ymax, cell_size)
    xx, yy = np.meshgrid(xs, ys)

    inside = shapely.contains_xy(area, xx, yy)  # only evaluate cells inside Leeds

    xy = np.column_stack([points.geometry.x, points.geometry.y])
    kde = KernelDensity(bandwidth=bandwidth, kernel="gaussian", rtol=1e-6).fit(xy)

    values = np.full(xx.shape, np.nan)
    log_density = kde.score_samples(np.column_stack([xx[inside], yy[inside]]))
    values[inside] = np.exp(log_density) * len(xy) * 1e6  # per m² -> per km²

    extent = (xs[0] - cell_size / 2, xs[-1] + cell_size / 2, ys[0] - cell_size / 2, ys[-1] + cell_size / 2)
    return DensitySurface(values=values, extent=extent, cell_size=cell_size)


def top_area_mask(surface: DensitySurface, top_pct: float = config.TOP_SHARE_PCT) -> np.ndarray:
    """Boolean grid marking the densest ``top_pct``% of cells inside Leeds."""
    threshold = np.percentile(surface.inside(), 100 - top_pct)
    return np.isfinite(surface.values) & (surface.values >= threshold)


def hotspot_overlap(a: DensitySurface, b: DensitySurface, top_pct: float = config.TOP_SHARE_PCT) -> dict:
    """How much of surface ``a``'s densest area is also among ``b``'s densest area.

    If the two patterns were unrelated, about ``top_pct``% overlap would be expected
    by chance, so the ratio to that baseline is the headline figure.
    """
    top_a, top_b = top_area_mask(a, top_pct), top_area_mask(b, top_pct)
    shared = int((top_a & top_b).sum())
    overlap_pct = 100 * shared / int(top_a.sum())
    return {
        "top_pct": top_pct,
        "cells_in_top_area": int(top_a.sum()),
        "shared_cells": shared,
        "overlap_pct": round(overlap_pct, 1),
        "times_chance": round(overlap_pct / top_pct, 1),
    }


def share_of_points_in_area(points: gpd.GeoDataFrame, surface: DensitySurface, mask: np.ndarray) -> float:
    """Percentage of ``points`` that fall inside the grid cells flagged by ``mask``."""
    xmin, _, ymin, _ = surface.extent
    col = ((points.geometry.x - xmin) // surface.cell_size).astype(int)
    row = ((points.geometry.y - ymin) // surface.cell_size).astype(int)
    valid = (row >= 0) & (row < mask.shape[0]) & (col >= 0) & (col < mask.shape[1])
    hits = mask[row[valid], col[valid]]
    return round(100 * hits.sum() / len(points), 1)
