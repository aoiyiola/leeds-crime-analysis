# Data

Raw and processed data are not committed to this repository because of their size (about 250 MB). Follow the steps below to rebuild `data/raw/`. Running the notebooks then creates `data/processed/`.

```
data/raw/
├── police/                     # 24 folders: 2023-01/ … 2024-12/, each with *-west-yorkshire-street.csv
├── leeds_social_venues.csv     # OpenStreetMap venue extract
└── lsoa_ons.geojson            # ONS LSOA 2021 boundaries (England and Wales)
```

## 1. Crime records (data.police.uk)

1. Go to <https://data.police.uk/data/>.
2. Choose the date range **January 2023 to December 2024**.
3. Tick **West Yorkshire Police** and **Include crime data**.
4. Download and unzip the archive. Copy the monthly folders (`2023-01/` … `2024-12/`) into `data/raw/police/`.

Only the `*-street.csv` files are used: 24 files, 642,403 records.

**Licence:** Open Government Licence v3.0. Contains public sector information licensed under the Open Government Licence v3.0.

**Note:** for privacy, each record's location is moved to the nearest of a fixed set of anonymous map points, so coordinates are approximate.

## 2. Nightlife venues (OpenStreetMap)

Collected through the Overpass API with one query per venue type (`pub`, `bar`, `nightclub`):

```
[out:json][timeout:90];
area["name"="Leeds"]["admin_level"="8"]["boundary"="administrative"]->.leeds;
(
  node["amenity"="pub"](area.leeds);
  way["amenity"="pub"](area.leeds);
  relation["amenity"="pub"](area.leeds);
);
out center;
```

The saved extract has 715 venues (524 pubs, 177 bars, 14 nightclubs). The notebooks use this file so the results are reproducible. To download the current data instead, run `data.load_venues(refresh=True)` in notebook 01. OpenStreetMap changes over time, so the counts will differ slightly.

**Licence:** © OpenStreetMap contributors, available under the Open Database Licence (ODbL).

## 3. LSOA boundaries (ONS)

Download **Lower layer Super Output Areas (December 2021) Boundaries EW** as GeoJSON from the [ONS Open Geography Portal](https://geoportal.statistics.gov.uk) and save it as `data/raw/lsoa_ons.geojson`. The file covers all 35,672 LSOAs in England and Wales, and the code selects the 488 in Leeds by name (`LSOA21NM` starting with "Leeds").

**Licence:** Source: Office for National Statistics, licensed under the Open Government Licence v3.0. Contains OS data © Crown copyright and database right.
