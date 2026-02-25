import pytest

from tube_router.load import load_network
from tube_router.router import Router


@pytest.fixture(scope="session")
def network():
    stations, lines, adj = load_network("data/london.json")
    return stations, lines, adj


@pytest.fixture(scope="session")
def router(network):
    stations, lines, adj = network
    return Router(stations, lines, adj)


def _route_station_names(route, stations):
    return [stations[sid].name for sid in route.station_ids]


@pytest.mark.parametrize(
    "start,end,expected_names",
    [
        (
            "Elephant & Castle",
            "Old Street",
            ["Elephant & Castle", "Borough", "London Bridge", "Bank", "Moorgate", "Old Street"],
        ),
        (
            "Covent Garden",
            "Green Park",
            ["Covent Garden", "Leicester Square", "Piccadilly Circus", "Green Park"],
        ),
        (
            "St. John's Wood",
            "Russell Square",
            [
                "St. John's Wood",
                "Baker Street",
                "Bond Street",
                "Oxford Circus",
                "Tottenham Court Road",
                "Holborn",
                "Russell Square",
            ],
        ),
        (
            "South Kensington",
            "Kentish Town",
            [
                "South Kensington",
                "Sloane Square",
                "Victoria",
                "Green Park",
                "Oxford Circus",
                "Warren Street",
                "Euston",
                "Camden Town",
                "Kentish Town",
            ],
        ),
    ],
)
def test_dijkstra_shortest_paths_match_expected(network, router, start, end, expected_names):
    stations, _, _ = network
    route, stats = router.route_dijkstra(start, end, transfer_penalty_minutes=0)

    assert route is not None
    assert route.station_ids, "Expected a non-empty route"
    assert _route_station_names(route, stations) == expected_names

    # basic sanity on stats
    assert stats.expanded >= 1
    assert stats.pushed >= 1


def test_same_station_returns_zero_length_route(network, router):
    stations, _, _ = network
    route, _ = router.route_dijkstra("Covent Garden", "Covent Garden")
    assert route is not None
    assert _route_station_names(route, stations) == ["Covent Garden"]
    assert route.total_minutes == 0
    assert route.transfers == 0
    assert route.legs == []


def test_invalid_station_returns_none(router):
    route, _ = router.route_dijkstra("Miaow Park", "South Kensington")
    assert route is None


def test_route_is_contiguous_in_adjacency(network, router):
    stations, _, adj = network
    route, _ = router.route_dijkstra("Elephant & Castle", "Old Street", transfer_penalty_minutes=0)
    assert route is not None

    for a, b in zip(route.station_ids, route.station_ids[1:]):
        assert any(e.to_id == b for e in adj[a]), f"Missing edge {stations[a].name} -> {stations[b].name}"


def test_total_time_equals_sum_of_leg_minutes(router):
    route, _ = router.route_dijkstra("Covent Garden", "Green Park", transfer_penalty_minutes=0)
    assert route is not None
    assert route.total_minutes == sum(leg.minutes for leg in route.legs)


def test_transfers_equals_number_of_line_changes(router):
    route, _ = router.route_dijkstra("South Kensington", "Kentish Town", transfer_penalty_minutes=0)
    assert route is not None

    transfers = 0
    prev_line = None
    for leg in route.legs:
        if prev_line is not None and leg.line_id != prev_line:
            transfers += 1
        prev_line = leg.line_id

    assert route.transfers == transfers


def test_astar_matches_dijkstra_total_minutes(router):
    pairs = [
        ("Covent Garden", "Green Park"),
        ("Elephant & Castle", "Old Street"),
        ("South Kensington", "Kentish Town"),
        ("St. John's Wood", "Russell Square"),
    ]

    for s, t in pairs:
        d, _ = router.route_dijkstra(s, t, transfer_penalty_minutes=0)
        a, _ = router.route_astar(s, t, transfer_penalty_minutes=0)

        assert d is not None and a is not None
        assert a.total_minutes == d.total_minutes
