"""Supported game regions."""

from enum import Enum


class Region(str, Enum):
    BD = "BD"
    IND = "IND"
    ID = "ID"
    PK = "PK"
    SG = "SG"
    TH = "TH"
    VN = "VN"
    TW = "TW"
    ME = "ME"
    BR = "BR"
    SAC = "SAC"
    NA = "NA"
    US = "US"
    EU = "EU"
    RU = "RU"


REGION_NAMES: dict[Region, str] = {
    Region.BD: "Bangladesh",
    Region.IND: "India",
    Region.ID: "Indonesia",
    Region.PK: "Pakistan",
    Region.SG: "Singapore",
    Region.TH: "Thailand",
    Region.VN: "Vietnam",
    Region.TW: "Taiwan",
    Region.ME: "Middle East",
    Region.BR: "Brazil",
    Region.SAC: "South America",
    Region.NA: "North America",
    Region.US: "United States",
    Region.EU: "Europe",
    Region.RU: "Russia / CIS",
}

# Friendly aliases accepted in requests (case-insensitive).
REGION_ALIASES: dict[str, Region] = {
    "BANGLADESH": Region.BD,
    "IN": Region.IND,
    "INDIA": Region.IND,
    "INDONESIA": Region.ID,
    "PAKISTAN": Region.PK,
}


def parse_region(value: str) -> Region:
    key = value.strip().upper()
    if key in REGION_ALIASES:
        return REGION_ALIASES[key]
    return Region(key)
