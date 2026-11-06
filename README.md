# Crime Hotspots and Nightlife in Leeds

**Do crime clusters in Leeds line up with pubs, bars and nightclubs?**

**Yes, in the city centre.** Leeds has one dominant, statistically significant hotspot of personal-safety crime, and it sits on the densest cluster of nightlife venues. Away from the centre, an area's number of venues barely predicts its crime level.

A geospatial analysis of **111,549 police records** (2023–2024) and **715 venues**, built from free public data in Python.

![Crime density with pubs, bars and nightclubs overlaid, for the Leeds district and a 5 km city-centre zoom](results/figures/kde_venue_overlay.png)

## The problem

Police have limited officers to cover a large city. Knowing exactly where risk is concentrated lets them patrol proactively instead of reacting after incidents. **Where should Leeds focus its resources to have the biggest impact on public safety?**

## Data

- **Crime:** 24 monthly files from [data.police.uk](https://data.police.uk), West Yorkshire Police, Jan 2023 – Dec 2024 (642,403 records)
- **Venues:** pubs, bars and nightclubs from [OpenStreetMap](https://www.openstreetmap.org) via the Overpass API
- **Boundaries:** ONS LSOA 2021 boundaries (488 small census areas in Leeds)

Sources and licences: [data/README.md](data/README.md)

## Approach

1. **[Prepare](notebooks/01_data_preparation.ipynb):** merge, clean and filter to the four crime types that threaten personal safety in Leeds (642,403 → 111,549 records).
2. **[Map](notebooks/02_hotspot_mapping.ipynb):** Kernel Density Estimation to find where crime concentrates, then measure how much that area overlaps the venue clusters.
3. **[Test](notebooks/03_hotspot_significance.ipynb):** Getis-Ord Gi\* hotspot analysis to confirm the clusters are statistically significant, not chance.
4. **[Time](notebooks/04_temporal_patterns.ipynb):** crime-type breakdown and seasonal trends.

## Key findings

- **The hotspot and the nightlife overlap.** The densest 10% of Leeds contains **65% of incidents** and **52% of venues**, and overlaps the venue hotspot **3.9×** more than chance would give.
- **It's statistically significant.** Hot-spot areas cover **6% of Leeds** but hold **30% of incidents**. The four city-centre LSOAs stay significant even after correcting for multiple testing.
- **It's a city-centre effect.** Across all areas, venue count and crime are only weakly linked (ρ = 0.15), so not every neighbourhood with a pub is a risk.
- **Violence drives the risk.** Violence and sexual offences make up **78%** of incidents.
- **Crime is seasonal and falling.** Incidents peak in May, and 2024 was **7% lower** than 2023.

![Getis-Ord Gi* hot and cold spot map](results/figures/getis_ord_hotspots.png)

## Recommendations

1. **Prioritise the four city-centre LSOAs** (Leeds 111A, 111B, 111C, 111E), which hold about 9% of all incidents.
2. **Focus on violence prevention there**, working with venue licensing, door staff and late-night transport.
3. **Increase cover from spring into summer**, when incidents peak.

## Limitations

- Police data is monthly, so incidents can't be tied to nightlife hours.
- The overlap shows association, not cause: the centre also has the most people, shops and transport.
- Police locations are approximate (moved to anonymous map points for privacy).

## Tools

Python · pandas · GeoPandas · scikit-learn · PySAL · SciPy · Matplotlib · Folium · Jupyter

---

## About

I'm **Afees Iyiola**, a **data analyst** with an MSc in Applied Artificial Intelligence and Data Analytics. I work across the full analysis workflow, from collecting and cleaning messy real-world data to analysing it and presenting the results as clear, decision-ready insight.

**Core skills**
- **Python data analysis:** pandas, NumPy, GeoPandas and Jupyter; cleaning and merging large datasets, collecting data from APIs, and statistical testing
- **Data visualisation:** Matplotlib and Folium; maps, charts and visual storytelling that make findings easy to act on

---

*Crime data: © Crown copyright, Open Government Licence v3.0. Venue data: © OpenStreetMap contributors, ODbL. Boundaries: ONS, Open Government Licence v3.0. Basemap: © Esri.*
