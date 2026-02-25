from __future__ import annotations
from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf
from typing import Dict, Optional, Tuple

from .models import Station, Line, Edge, Leg, Route

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

class Router:
    def __init__(self, stations: Dict[str, Station], lines: Dict[str, Line], adj: Dict[str, list[Edge]]):
        self.stations = stations
        self.lines = lines
        self.adj = adj
        self.name_to_id = {s.name: s.id for s in stations.values()}

    def route(
        self,
        start_name: str,
        end_name: str,
        transfer_penalty_minutes: int = 0,
    ) -> Optional[Route]:
        start_id = self.name_to_id.get(start_name)
        end_id = self.name_to_id.get(end_name)
        if start_id is None or end_id is None:
            return None
        if start_id == end_id:
            return Route([start_id], [], 0, 0)

        # Distances are keyed by (station_id, prev_line_id)
        dist: Dict[tuple[str, Optional[str]], float] = {}
        prev: Dict[tuple[str, Optional[str]], tuple[tuple[str, Optional[str]], Edge]] = {}

        pq: list[tuple[float, str, Optional[str]]] = []
        start_key = (start_id, None)
        dist[start_key] = 0.0
        heappush(pq, (0.0, start_id, None))

        best_end_key: Optional[tuple[str, Optional[str]]] = None
        best_end_cost = inf

        while pq:
            cost, u, prev_line = heappop(pq)
            key = (u, prev_line)
            if cost != dist.get(key, inf):
                continue

            if u == end_id and cost < best_end_cost:
                best_end_cost = cost
                best_end_key = key
                # don’t early-break: a different prev_line might be cheaper if penalties exist

            for e in self.adj.get(u, []):
                penalty = 0
                if prev_line is not None and e.line_id != prev_line:
                    penalty = transfer_penalty_minutes

                nxt_key = (e.to_id, e.line_id)
                nxt_cost = cost + e.minutes + penalty
                if nxt_cost < dist.get(nxt_key, inf):
                    dist[nxt_key] = nxt_cost
                    prev[nxt_key] = (key, e)
                    heappush(pq, (nxt_cost, e.to_id, e.line_id))

        if best_end_key is None:
            return Route([], [], 0, 0)

        # Reconstruct
        station_ids: list[str] = []
        legs: list[Leg] = []
        cur = best_end_key
        while cur != start_key:
            station_ids.append(cur[0])
            back = prev.get(cur)
            if back is None:
                return Route([], [], 0, 0)
            (pkey, edge) = back
            legs.append(Leg(from_id=pkey[0], to_id=edge.to_id, line_id=edge.line_id, minutes=edge.minutes))
            cur = pkey
        station_ids.append(start_id)

        station_ids.reverse()
        legs.reverse()

        total_minutes = sum(l.minutes for l in legs)
        transfers = _count_transfers(legs)
        return Route(station_ids, legs, total_minutes, transfers)
