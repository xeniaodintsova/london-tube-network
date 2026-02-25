from __future__ import annotations
import argparse
from .load import load_network
from .router import Router

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/london.json")
    ap.add_argument("start")
    ap.add_argument("end")
    ap.add_argument("--transfer-penalty", type=int, default=0)
    ap.add_argument("--algo", choices=["dijkstra", "astar"], default="dijkstra")
    ap.add_argument("--show-stats", action="store_true")
    ap.add_argument("--heuristic-max-kmph", type=float, default=120.0)
    
    args = ap.parse_args()

    stations, lines, adj = load_network(args.data)
    r = Router(stations, lines, adj)

    if args.algo == "astar":
        route, stats = r.route_astar(
            args.start,
            args.end,
            args.transfer_penalty,
            args.heuristic_max_kmph,
        )
    else:
        route, stats = r.route_dijkstra(
            args.start,
            args.end,
            args.transfer_penalty,
        )
        
    if route is None or not route.station_ids:
        print("No route found.")
        return

    if args.show_stats:
        print(f"[{args.algo}] expanded={stats.expanded} pushed={stats.pushed}")

    print(f"Total minutes: {route.total_minutes} | transfers: {route.transfers}")

    for sid in route.station_ids:
        print(" -", stations[sid].name)


if __name__ == "__main__":
    main()
