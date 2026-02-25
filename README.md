# london-tube-network
# 🚇 London Tube Routing Engine
A Python routing engine for the London Underground that computes optimal travel paths between stations using graph algorithms.
Supports Dijkstra and A* search, with transfer-aware routing and detailed journey outputs.

## ✨ Features
🔍 Shortest path using Dijkstra and A*

🔁 Optional transfer penalties (fewer line changes)

🧠 Structured route output:
stations
total travel time
number of transfers

## 🗂 Project Structure
london-tube-network/
├── src/
│   └── tube_router/
│       ├── models.py
│       ├── load.py
│       ├── router.py
│       └── cli.py
├── tests/
├── data/
│   └── london.json
├── requirements.txt
├── pytest.ini
└── README.md

## 🚀 Installation
git clone https://github.com/xeniaodintsova/london-tube-network.git
cd london-tube-network
pip install -r requirements.txt

## 🧪 Running Tests
pytest -q

Tests cover:
correct shortest paths
route validity
transfer counting
A* vs Dijkstra equivalence 

## 🧭 Usage
PYTHONPATH=src python -m tube_router.cli "Covent Garden" "Green Park"

### Options
--algo dijkstra|astar
--transfer-penalty <int>
--show-stats
--heuristic-max-kmph <float>

### Example
python -m tube_router.cli "Stockwell" "Ealing Broadway" --algo astar --show-stats

router
