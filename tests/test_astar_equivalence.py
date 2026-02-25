from tube_router.load import load_network
from tube_router.router import Router

def test_astar_matches_dijkstra_cost():
    stations, lines, adj = load_network("data/london.json")
    r = Router(stations, lines, adj)

    pairs = [
        ("Covent Garden", "Green Park"),
        ("Elephant & Castle", "Old Street"),
        ("South Kensington", "Kentish Town"),
        ("St. John's Wood", "Russell Square"),
    ]

    for s, t in pairs:
        d_route, _ = r.route_dijkstra(s, t, transfer_penalty_minutes=0)
        a_route, _ = r.route_astar(s, t, transfer_penalty_minutes=0)
        assert d_route is not None and a_route is not None
        assert a_route.total_minutes == d_route.total_minutes
