from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Station:
    id: str
    name: str
    lat: float
    lon: float
    zones: frozenset[int]

@dataclass(frozen=True)
class Line:
    id: str
    name: str

@dataclass(frozen=True)
class Edge:
    to_id: str
    line_id: str
    minutes: int

@dataclass(frozen=True)
class Leg:
    from_id: str
    to_id: str
    line_id: str
    minutes: int

@dataclass(frozen=True)
class Route:
    station_ids: list[str]
    legs: list[Leg]
    total_minutes: int
    transfers: int
