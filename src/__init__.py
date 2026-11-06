"""Reusable code for the Leeds crime hotspot analysis.

Modules:
    config    paths, crime categories, CRS and analysis parameters
    data      load, clean and filter police records; load or download venues
    geo       Leeds boundaries, point conversion, kernel density surfaces
    stats     counts per LSOA and Getis-Ord Gi* hotspot detection
    plotting  shared map and chart styling
"""
