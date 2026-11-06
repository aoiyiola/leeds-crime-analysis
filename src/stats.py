"""Area-level statistics: counts per LSOA and Getis-Ord Gi* hotspot detection."""
import geopandas as gpd
import numpy as np
import pandas as pd
from esda import fdr
from esda.getisord import G_Local
from libpysal.weights import Queen, fill_diagonal

from . import config

GI_CLASSES = [  # label, colour (diverging, ArcGIS-style confidence bins)
    ("Hot spot, 99% confidence", "#b2182b"),
    ("Hot spot, 95% confidence", "#ef8a62"),
    ("Hot spot, 90% confidence", "#fddbc7"),
    ("Not significant", "#f2f2f2"),
    ("Cold spot, 90% confidence", "#d1e5f0"),
    ("Cold spot, 95% confidence", "#67a9cf"),
    ("Cold spot, 99% confidence", "#2166ac"),
]


def count_points_per_area(
    areas: gpd.GeoDataFrame, points: gpd.GeoDataFrame, column: str
) -> gpd.GeoDataFrame:
    """Add a column counting how many ``points`` fall inside each area."""
    joined = gpd.sjoin(points[["geometry"]], areas[["LSOA21CD", "geometry"]], predicate="within")
    counts = joined.groupby("LSOA21CD").size()
    out = areas.copy()
    out[column] = out["LSOA21CD"].map(counts).fillna(0).astype(int)
    return out


def getis_ord_gi_star(
    areas: gpd.GeoDataFrame,
    column: str,
    permutations: int = config.GI_PERMUTATIONS,
    seed: int = config.RANDOM_SEED,
) -> gpd.GeoDataFrame:
    """Run Getis-Ord Gi* on ``column`` using Queen contiguity (areas sharing an edge or corner).

    Adds:
      * ``gi_z``   - standardised Gi* score (positive = surrounded by high values)
      * ``gi_p``   - pseudo p-value from ``permutations`` conditional permutations
      * ``gi_class`` - hot/cold spot at 90/95/99% confidence
      * ``gi_fdr_sig`` - still significant after a false discovery rate correction
        at ``config.GI_ALPHA`` (guards against testing hundreds of areas at once)
    """
    w = Queen.from_dataframe(areas, use_index=False)
    if w.islands:
        raise ValueError(f"{len(w.islands)} areas have no neighbours; check the boundary file")
    # Gi* (the "star") counts each area as its own neighbour: weight 1 on the diagonal,
    # then row-standardise so every area's neighbourhood sums to 1.
    w = fill_diagonal(w, 1.0)

    gi = G_Local(
        areas[column].to_numpy(dtype=float), w,
        transform="R", star=None, permutations=permutations, seed=seed, n_jobs=1,
    )

    out = areas.copy()
    out["gi_z"] = gi.Zs
    out["gi_p"] = gi.p_sim
    out["gi_class"] = [_classify(z, p) for z, p in zip(gi.Zs, gi.p_sim)]

    threshold = fdr(gi.p_sim, config.GI_ALPHA)
    out["gi_fdr_sig"] = gi.p_sim <= threshold
    return out


def _classify(z: float, p: float) -> str:
    side = "Hot spot" if z > 0 else "Cold spot"
    for confidence, alpha in ((99, 0.01), (95, 0.05), (90, 0.10)):
        if p <= alpha:
            return f"{side}, {confidence}% confidence"
    return "Not significant"


def summarise_gi(areas: gpd.GeoDataFrame) -> pd.DataFrame:
    """Count areas in each Gi* class, in legend order."""
    order = [label for label, _ in GI_CLASSES]
    counts = areas["gi_class"].value_counts().reindex(order, fill_value=0)
    return counts.rename_axis("Gi* class").reset_index(name="LSOAs")
