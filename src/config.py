"""Project-wide paths and analysis settings.

Every notebook imports from here, so a setting only ever needs changing in one place.
"""
from pathlib import Path

# --- Paths -----------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
MAPS_DIR = PROJECT_ROOT / "results" / "maps"

POLICE_DIR = RAW_DIR / "police"                  # 24 monthly *-street.csv files
VENUES_RAW = RAW_DIR / "leeds_social_venues.csv"  # OpenStreetMap extract
LSOA_BOUNDARIES = RAW_DIR / "lsoa_ons.geojson"    # ONS LSOA 2021 boundaries

CRIMES_CLEAN = PROCESSED_DIR / "leeds_safety_crimes.csv"
VENUES_CLEAN = PROCESSED_DIR / "leeds_venues.csv"
LSOA_STATS = PROCESSED_DIR / "leeds_lsoa_stats.geojson"

# --- Study definition --------------------------------------------------------
STUDY_PERIOD = ("2023-01", "2024-12")
LEEDS_LSOA_PREFIX = "Leeds "  # ONS LSOA names look like "Leeds 111B"

# Crime categories that most directly threaten personal safety.
SAFETY_CRIMES = [
    "Violence and sexual offences",
    "Anti-social behaviour",
    "Robbery",
    "Theft from the person",
]

VENUE_TYPES = ["pub", "bar", "nightclub"]  # OSM amenity=* tags

# --- Coordinate reference systems ------------------------------------------
CRS_WGS84 = "EPSG:4326"  # latitude / longitude, as published
CRS_BNG = "EPSG:27700"   # British National Grid, in metres: used for all distance work

# --- Analysis parameters ----------------------------------------------------
KDE_BANDWIDTH_M = 300    # Gaussian kernel bandwidth (metres)
KDE_CELL_SIZE_M = 100    # resolution of the density grid (metres)
KDE_LOG_RANGE = (10, 10_000)  # colour scale limits, incidents per km² (log scale)
TOP_SHARE_PCT = 10       # "hotspot area" = top 10% of cells by density

GI_PERMUTATIONS = 9_999  # permutations for Gi* pseudo p-values (smallest possible p = 0.0001)
GI_ALPHA = 0.05          # significance level
RANDOM_SEED = 42

# --- Plot style ---------------------------------------------------------------
CRIME_COLOURS = {
    "Violence and sexual offences": "#1b6ca8",
    "Anti-social behaviour": "#e8a33d",
    "Robbery": "#c0392b",
    "Theft from the person": "#7d3c98",
}
VENUE_STYLE = {  # marker, colour
    "pub": ("o", "#00796b"),
    "bar": ("s", "#3b6ea8"),
    "nightclub": ("^", "#7b1fa2"),
}
KDE_PALETTE = ["#dbe9fb", "#7fb3ff", "#ffb84d", "#e4572e"]  # low -> high
