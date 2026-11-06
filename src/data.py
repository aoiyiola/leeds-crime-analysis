"""Loading, cleaning and filtering the crime and venue data."""
from pathlib import Path
import time

import pandas as pd
import requests

from . import config

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


# --- Police crime records -----------------------------------------------------
def load_police_data(folder: Path = config.POLICE_DIR) -> pd.DataFrame:
    """Read and stack every monthly ``*-street.csv`` file under ``folder``."""
    files = sorted(Path(folder).rglob("*-street.csv"))
    if not files:
        raise FileNotFoundError(
            f"No *-street.csv files found in {folder}. See data/README.md for download steps."
        )
    frames = [pd.read_csv(f) for f in files]
    merged = pd.concat(frames, ignore_index=True)
    print(f"Read {len(files)} monthly files -> {len(merged):,} records")
    return merged


def clean_police_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop records that cannot be mapped and columns the analysis doesn't use.

    * ``Latitude``/``Longitude``/``LSOA`` are missing together for records the police
      could not geolocate, so those rows are removed.
    * ``Context`` is always empty, and ``Reported by``/``Falls within`` are always
      "West Yorkshire Police".
    """
    essential = ["Latitude", "Longitude", "LSOA name", "Crime type", "Month"]
    cleaned = df.dropna(subset=essential).drop(columns=["Context", "Reported by", "Falls within"])
    print(f"Removed {len(df) - len(cleaned):,} records without a location -> {len(cleaned):,} remain")
    return cleaned.reset_index(drop=True)


def filter_leeds(df: pd.DataFrame) -> pd.DataFrame:
    """Keep records whose LSOA belongs to the Leeds local authority.

    LSOA names start with the district name (e.g. "Leeds 111B"), so this is an exact
    administrative filter. It avoids the errors of clipping by a bounding box near
    the borders with Bradford, Kirklees, Calderdale and Wakefield.
    """
    leeds = df[df["LSOA name"].str.startswith(config.LEEDS_LSOA_PREFIX)].copy()
    print(f"Leeds records: {len(leeds):,} ({len(leeds) / len(df):.1%} of West Yorkshire)")
    return leeds.reset_index(drop=True)


def filter_safety_crimes(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only the four personal-safety crime categories."""
    safety = df[df["Crime type"].isin(config.SAFETY_CRIMES)].copy()
    print(f"Safety-related records: {len(safety):,} ({len(safety) / len(df):.1%} of Leeds crime)")
    return safety.reset_index(drop=True)


# --- Nightlife venues (OpenStreetMap) ------------------------------------------
def _overpass_query(amenity: str) -> str:
    return f"""
    [out:json][timeout:90];
    area["name"="Leeds"]["admin_level"="8"]["boundary"="administrative"]->.leeds;
    (
      node["amenity"="{amenity}"](area.leeds);
      way["amenity"="{amenity}"](area.leeds);
      relation["amenity"="{amenity}"](area.leeds);
    );
    out center;
    """


def fetch_venues(amenities=config.VENUE_TYPES, pause_s: float = 2.0) -> pd.DataFrame:
    """Download pubs, bars and nightclubs in Leeds from the Overpass API.

    Ways and relations (buildings drawn as outlines) are reduced to their centre point.
    """
    rows = []
    for amenity in amenities:
        response = requests.post(OVERPASS_URL, data={"data": _overpass_query(amenity)}, timeout=120)
        response.raise_for_status()
        for el in response.json()["elements"]:
            lat = el.get("lat", el.get("center", {}).get("lat"))
            lon = el.get("lon", el.get("center", {}).get("lon"))
            if lat is None or lon is None:
                continue
            rows.append({
                "amenity_type": amenity,
                "osm_id": el["id"],
                "name": el.get("tags", {}).get("name", "Unnamed"),
                "latitude": lat,
                "longitude": lon,
            })
        print(f"  {amenity}: {sum(r['amenity_type'] == amenity for r in rows):,}")
        time.sleep(pause_s)  # be polite to the public API
    return pd.DataFrame(rows)


def load_venues(path: Path = config.VENUES_RAW, refresh: bool = False) -> pd.DataFrame:
    """Load the saved venue extract, or download a fresh one.

    OpenStreetMap changes daily, so the saved extract is used by default to keep the
    results reproducible. Pass ``refresh=True`` to download the current data instead.
    """
    path = Path(path)
    if path.exists() and not refresh:
        venues = pd.read_csv(path)
        print(f"Loaded {len(venues):,} venues from {path.name}")
    else:
        print("Downloading venues from the Overpass API...")
        venues = fetch_venues()
        path.parent.mkdir(parents=True, exist_ok=True)
        venues.to_csv(path, index=False)
        print(f"Saved {len(venues):,} venues to {path}")
    return venues
