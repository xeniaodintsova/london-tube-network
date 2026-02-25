from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Tuple
from .models import Station, Line, Edge

def _parse_zones(zone_value) -> frozenset[int]:
    if zone_value in (None, "", "NULL"):
        return frozenset()
    z = str(zone_value).strip()
    if z.isdigit():
        return frozenset({int(z)})
    if z.endswith(".5") and z[:-2].isdigit():
        base = int(z[:-2])
        return frozenset({base, base + 1})
    try:
        return frozenset({int(round(float(z)))})
    except Exception:
        return frozenset()

def load_network(json_path: str | Path) -> tuple[Dict[str, Station], Dict[str, Line], Dict[str, list[Edge]]]:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))

    # Stations
    stations: Dict[str, Station] = {}
    for s in data.get("stations", []):
        sid = str(s.get("id", "")).strip()
        if not sid:
            continue
        stations[sid] = Station(
            id=sid,
            name=str(s.get("name", "")).strip(),
            lat=float(s.get("latitude", "nan")),
            lon=float(s.get("longitude", "nan")),
            zones=_parse_zones(s.get("zone")),
        )

    # Lines
    lines: Dict[str, Line] = {}
    for l in data.get("lines", []):
        lid = str(l.get("line", "")).strip()
        if not lid:
            continue
        lines[lid] = Line(id=lid, name=str(l.get("name", "")).strip())

    # Adjacency
    adj: Dict[str, list[Edge]] = {sid: [] for sid in stations.keys()}
    for c in data.get("connections", []):
        a = str(c.get("station1", "")).strip()
        b = str(c.get("station2", "")).strip()
        lid = str(c.get("line", "")).strip()
        try:
            minutes = int(str(c.get("time", "0")).strip())
        except ValueError:
            continue

        if a in stations and b in stations and lid in lines and minutes > 0:
            adj[a].append(Edge(to_id=b, line_id=lid, minutes=minutes))
            adj[b].append(Edge(to_id=a, line_id=lid, minutes=minutes))

    return stations, lines, adj
