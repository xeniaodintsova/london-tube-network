import pytest

from tube.map import TubeMap
from network.path import PathFinder


@pytest.fixture(scope="session")
def tubemap():
    tm = TubeMap()
    tm.import_from_json("data/london.json")
    return tm


@pytest.fixture(scope="session")
def pathfinder(tubemap):
    return PathFinder(tubemap)


@pytest.mark.parametrize(
    "start,end,expected",
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
            ["St. John's Wood", "Baker Street", "Bond Street", "Oxford Circus",
             "Tottenham Court Road", "Holborn", "Russell Square"],
        ),
        (
            "South Kensington",
            "Kentish Town",
            ["South Kensington", "Sloane Square", "Victoria", "Green Park",
             "Oxford Circus", "Warren Street", "Euston", "Camden Town", "Kentish Town"],
        ),
    ],
)
def test_shortest_paths_match_expected(pathfinder, start, end, expected):
    stations = pathfinder.get_shortest_path(start, end)
    assert stations is not None
    assert [s.name for s in stations] == expected


def test_same_station_returns_single_station(pathfinder):
    stations = pathfinder.get_shortest_path("Covent Garden", "Covent Garden")
    assert stations is not None
    assert len(stations) == 1
    assert stations[0].name == "Covent Garden"


def test_invalid_station_returns_none(pathfinder):
    stations = pathfinder.get_shortest_path("Miaow Park", "South Kensington")
    assert stations is None


def test_returned_path_is_contiguous_in_graph(pathfinder):
    """
    Extra robustness: every consecutive pair in the returned path
    must be connected in the built neighbour graph.
    """
    stations = pathfinder.get_shortest_path("Elephant & Castle", "Old Street")
    assert stations is not None
    ids = [pathfinder.station_name_to_id[s.name] for s in stations]

    for a, b in zip(ids, ids[1:]):
        assert b in pathfinder.graph.get(a, {}), f"{a} -> {b} missing from graph"


def test_total_time_is_consistent_with_edges(pathfinder):
    """
    Sanity check: the total time computed from the returned path’s edges
    should be finite and > 0 for distinct stations.
    """
    stations = pathfinder.get_shortest_path("Covent Garden", "Green Park")
    assert stations is not None
    ids = [pathfinder.station_name_to_id[s.name] for s in stations]

    total = 0
    for a, b in zip(ids, ids[1:]):
        t = pathfinder._edge_travel_time(a, b)
        assert t is not None
        total += t

    assert total > 0
