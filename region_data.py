"""
region_data.py

This file contains all static, real-world configuration data for regions.
It deliberately contains NO algorithms and NO rendering logic.

Keeping this data separate improves readability, maintainability, and allows
the simulation and rendering systems to remain generic.
"""

# -----------------------------------------------------------------------------
# Region configuration
# -----------------------------------------------------------------------------
# population: approximate real-world population (used for ratios)
# healthcare_score: 0.0–1.0 where higher = stronger healthcare infrastructure
# airports_open: initial airport availability state

REGION_CONFIG = {
    "greenland_and_iceland": {
        "population": 1_000_000,
        "healthcare_score": 0.85,
        "airports_open": True,
    },
    "canada": {
        "population": 39_000_000,
        "healthcare_score": 0.85,
        "airports_open": True,
    },
    "usa": {
        "population": 335_000_000,
        "healthcare_score": 0.75,
        "airports_open": True,
    },
    "central_america": {
        "population": 50_000_000,
        "healthcare_score": 0.55,
        "airports_open": True,
    },
    "south_america": {
        "population": 430_000_000,
        "healthcare_score": 0.60,
        "airports_open": True,
    },

    "uk": {
        "population": 70_000_000,
        "healthcare_score": 0.85,
        "airports_open": True,
    },
    "europe": {
        "population": 450_000_000,
        "healthcare_score": 0.82,
        "airports_open": True,
    },
    "scandinavia": {
        "population": 30_000_000,
        "healthcare_score": 0.90,
        "airports_open": True,
    },
    "russia": {
        "population": 145_000_000,
        "healthcare_score": 0.65,
        "airports_open": True,
    },

    "africa": {
        "population": 1_400_000_000,
        "healthcare_score": 0.45,
        "airports_open": True,
    },
    "middle_east": {
        "population": 300_000_000,
        "healthcare_score": 0.60,
        "airports_open": True,
    },
    "west_asia": {
        "population": 250_000_000,
        "healthcare_score": 0.60,
        "airports_open": True,
    },

    "india": {
        "population": 1_430_000_000,
        "healthcare_score": 0.55,
        "airports_open": True,
    },
    "south_asia": {
        "population": 700_000_000,
        "healthcare_score": 0.55,
        "airports_open": True,
    },
    "southeast_asia": {
        "population": 680_000_000,
        "healthcare_score": 0.60,
        "airports_open": True,
    },
    "east_asia": {
        "population": 210_000_000,
        "healthcare_score": 0.70,
        "airports_open": True,
    },
    "china": {
        "population": 1_410_000_000,
        "healthcare_score": 0.70,
        "airports_open": True,
    },

    "oceania": {
        "population": 45_000_000,
        "healthcare_score": 0.85,
        "airports_open": True,
    },
}

# -----------------------------------------------------------------------------
# Land connections (adjacency list)
# -----------------------------------------------------------------------------
# Defines which regions share land borders.
# This structure is symmetric by design and will be used for land-based spread.

LAND_CONNECTIONS = {
    "greenland_and_iceland": ["canada"],

    "canada": ["usa", "greenland_and_iceland"],
    "usa": ["canada", "central_america"],
    "central_america": ["usa", "south_america"],
    "south_america": ["central_america"],

    "uk": ["europe"],
    "scandinavia": ["europe", "russia"],
    "europe": ["uk", "scandinavia", "russia", "middle_east", "africa"],
    "russia": ["scandinavia", "europe", "west_asia", "china", "east_asia"],

    "africa": ["europe", "middle_east"],
    "middle_east": ["europe", "africa", "west_asia", "south_asia"],
    "west_asia": ["middle_east", "south_asia", "india", "china", "russia"],

    "south_asia": ["middle_east", "west_asia", "india", "southeast_asia"],
    "india": ["south_asia", "west_asia", "china", "southeast_asia"],
    "southeast_asia": ["south_asia", "india", "china", "east_asia"],
    "china": ["india", "west_asia", "russia", "southeast_asia", "east_asia"],
    "east_asia": ["china", "southeast_asia", "russia"],

    "oceania": [],
}


REGION_ID_HEX = {
    "greenland_and_iceland": "ff0000ff",
    "china": "00ff00ff",
    "east_asia": "446f00ff",
    "oceania": "0000ffff",
    "southeast_asia": "ffff00ff",
    "india": "ff00ffff",
    "south_asia": "00ffffff",
    "west_asia": "800000ff",
    "russia": "008000ff",
    "scandinavia": "000080ff",
    "uk": "ff8000ff",
    "europe": "80ff00ff",
    "middle_east": "00ff80ff",
    "africa": "0080ffff",
    "usa": "8000ffff",
    "canada": "ff0080ff",
    "south_america": "808000ff",
    "central_america": "008080ff",
}