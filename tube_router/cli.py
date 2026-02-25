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
    args = ap.parse_args()

    stations, lines, adj = load_network(args.data)
    r = Router(stations, lines, adj)
    route = r.route(args.start, args.end, transfer_penalty_minutes=args.transfer_penalty)

    if route is None or not route.station_ids:
        print("No route found.")
        return

    print(f"Total minutes: {route.total_minutes} | transfers: {route.transfers}")
    print("Stations:")
    for sid in route.station_ids:
        print(" -", stations[sid].name)

    print("\nLegs:")
    for leg in route.legs:
        print(f" - {stations[leg.from_id].name} -> {stations[leg.to_id].name} "
              f"({lines[leg.line_id].name}, {leg.minutes}m)")

if __name__ == "__main__":
    main()
