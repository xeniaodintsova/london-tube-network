from __future__ import annotations
from __future__ import annotations
from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf, radians, sin, cos, sqrt, atan2
from typing import Dict, Optional, Tuple

from .models import Station, Line, Edge, Leg, Route


@dataclass(frozen=True)
class SearchStats:
    expanded: int
    pushed: int

    
@dataclass(frozen=True)
class _State:
    station_id: str
    prev_line_id: Optional[str]  # used for transfer counting/penalties

def _count_transfers(legs: list[Leg]) -> int:
    transfers = 0
    prev = None
    for leg in legs:
        if prev is not None and leg.line_id != prev:
            transfers += 1
        prev = leg.line_id
    return transfers

def _haversine_km(a: Station, b: Station) -> float:
    R = 6371.0
    lat1, lon1 = radians(a.lat), radians(a.lon)
    lat2, lon2 = radians(b.lat), radians(b.lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * R * atan2(sqrt(h), sqrt(1 - h))


class Router:
    def __init__(self, stations: Dict[str, Station], lines: Dict[str, Line], adj: Dict[str, list[Edge]]):
        self.stations = stations
        self.lines = lines
        self.adj = adj
        self.name_to_id = {s.name: s.id for s in stations.values()}

    def route(self, start_name: str, end_name: str, transfer_penalty_minutes: int = 0):
        route, _ = self.route_dijkstra(start_name, end_name, transfer_penalty_minutes)
        return route

    def route_dijkstra(self, start_name: str, end_name: str, transfer_penalty_minutes: int = 0):
        return self._search(start_name, end_name, transfer_penalty_minutes, use_astar=False)

    def route_astar(
        self,
        start_name: str,
        end_name: str,
        transfer_penalty_minutes: int = 0,
        heuristic_max_kmph: float = 120.0,
    ):
        return self._search(
            start_name,
            end_name,
            transfer_penalty_minutes,
            use_astar=True,
            heuristic_max_kmph=heuristic_max_kmph,
        )

    def _search(
        self,
        start_name: str,
        end_name: str,
        transfer_penalty_minutes: int,
        use_astar: bool,
        heuristic_max_kmph: float = 120.0,
    ):
        start_id = self.name_to_id.get(start_name)
        end_id = self.name_to_id.get(end_name)

        if start_id is None or end_id is None:
            return None, SearchStats(0, 0)

        if start_id == end_id:
            return Route([start_id], [], 0, 0), SearchStats(0, 0)

        def heuristic(u: str):
            if not use_astar:
                return 0
            dist_km = _haversine_km(self.stations[u], self.stations[end_id])
            return (dist_km / heuristic_max_kmph) * 60

        dist: Dict[tuple[str, Optional[str]], float] = {}
        prev: Dict[tuple[str, Optional[str]], tuple[tuple[str, Optional[str]], Edge]] = {}

        pq = []
        start_key = (start_id, None)
        dist[start_key] = 0.0
        heappush(pq, (heuristic(start_id), 0.0, start_id, None))

        expanded = 0
        pushed = 1

        best_end_key = None
        best_cost = inf

        while pq:
            _, cost, u, prev_line = heappop(pq)
            key = (u, prev_line)

            if cost != dist.get(key, inf):
                continue

            expanded += 1

            if u == end_id and cost < best_cost:
                best_cost = cost
                best_end_key = key

            for e in self.adj.get(u, []):
                penalty = 0
                if prev_line and e.line_id != prev_line:
                    penalty = transfer_penalty_minutes

                nxt = (e.to_id, e.line_id)
                new_cost = cost + e.minutes + penalty

                if new_cost < dist.get(nxt, inf):
                    dist[nxt] = new_cost
                    prev[nxt] = (key, e)
                    heappush(pq, (new_cost + heuristic(e.to_id), new_cost, e.to_id, e.line_id))
                    pushed += 1

        if best_end_key is None:
            return None, SearchStats(expanded, pushed)

        # reconstruct
        station_ids = []
        legs = []
        cur = best_end_key

        while cur != start_key:
            station_ids.append(cur[0])
            back = prev[cur]
            pkey, edge = back
            legs.append(Leg(pkey[0], edge.to_id, edge.line_id, edge.minutes))
            cur = pkey

        station_ids.append(start_id)
        station_ids.reverse()
        legs.reverse()

        route = Route(
            station_ids=station_ids,
            legs=legs,
            total_minutes=sum(l.minutes for l in legs),
            transfers=_count_transfers(legs),
        )

        return route, SearchStats(expanded, pushed)
