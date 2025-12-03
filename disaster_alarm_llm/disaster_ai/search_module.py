
import heapq
import json
from collections import defaultdict
import math


def load_graph(path="data/city_graph_55_nodes.json"):

    with open(path, "r") as f:
        return json.load(f)




def uniform_cost_search(graph, start, goal):
    pq = [(0, start, [])]               
    visited = set()

    while pq:
        cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)

        path = path + [node]

        if node == goal:
            return path, cost

        # Expand neighbors
        for neighbor, weight in graph[node]["neighbors"].items():
            heapq.heappush(pq, (cost + weight, neighbor, path))

    return None, float("inf")




def future_risk_heuristic(graph, node, goal):

    base_distance = graph[node].get("straight_line_dist_to_goal", 1)

    flood_risk = graph[node].get("flood_risk", 0)
    bridge_risk = graph[node].get("bridge_collapse_risk", 0)
    traffic_risk = graph[node].get("traffic_delay_factor", 0)

    return base_distance + flood_risk + bridge_risk + traffic_risk




def astar_search(graph, start, goal):
    pq = [(0, start, [])]
    visited = set()

    while pq:
        total_cost, node, path = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)

        path = path + [node]

        if node == goal:
            return path, total_cost

        for neigh, weight in graph[node]["neighbors"].items():

            
            g_cost = weight
            h_cost = future_risk_heuristic(graph, neigh, goal)

            f_cost = g_cost + h_cost

            heapq.heappush(pq, (total_cost + f_cost, neigh, path))

    return None, float("inf")



class MultiModalGraph:
    def __init__(self):
        self.coords = {}
        
        self.adj = defaultdict(list)
        
        self.node_risk = defaultdict(lambda: 1.0)
        self.node_blocked = defaultdict(lambda: False)

    def add_node(self, name, xy, node_type):
        self.coords[name] = tuple(map(float, xy))

    def set_node_risk(self, name, risk_score=1.0, calamity=False):
        self.node_risk[name] = float("inf") if calamity else float(risk_score)
        self.node_blocked[name] = bool(calamity)

    def _euclid(self, u, v):
        (x1, y1) = self.coords[u]
        (x2, y2) = self.coords[v]
        return math.hypot(x1 - x2, y1 - y2)

    def add_edge(self, u, v, mode, time_min, cost, delay_prob, comfort, undirected=True):
        dist = self._euclid(u, v)
        edge = dict(to=v, mode=mode, time_min=float(time_min), cost=float(cost),
                    delay_prob=float(delay_prob), comfort=float(comfort), distance_km=dist)
        self.adj[u].append(edge)
        if undirected:
            back = dict(to=u, mode=mode, time_min=float(time_min), cost=float(cost),
                        delay_prob=float(delay_prob), comfort=float(comfort), distance_km=dist)
            self.adj[v].append(back)
def build_bbsr_55_exact():
    g = MultiModalGraph()

    base_nodes = {
        "Biju Patnaik Airport": (0, 0),
        "Bhubaneswar Railway Station": (4, 1),
        "Master Canteen Square": (4, 2),
        "Jaydev Vihar": (6, 4),
        "KIIT University": (9, 7),
        "Chandrasekharpur": (9, 5),
        "Khandagiri": (-2, 2),
        "Old Town": (2, -2),
        "Acharya Vihar": (5, 3),
        "CRP Square": (5, 4),
    }
    for n, xy in base_nodes.items():
        g.add_node(n, xy, node_type="hub")
        g.set_node_risk(n, 1.0, False)

    
    clusters = {
        "Airport Cluster": ("Biju Patnaik Airport", [(-1.5, -0.5), (1.0, 0.8)]),                    
        "Old Town Cluster": ("Old Town", [(1.5, -3.2), (2.4, -1.1)]),                               
        "Station Cluster": ("Bhubaneswar Railway Station", [(3.2, 0.2), (4.8, 0.0)]),               
        "Master Canteen Cluster": ("Master Canteen Square", [(3.6, 2.8), (4.6, 2.7)]),              
        "CRP Cluster": ("CRP Square", [(5.6, 4.8), (4.5, 4.7)]),                                     
        "Jaydev Cluster": ("Jaydev Vihar", [(6.7, 3.3), (7.0, 4.9), (6.1, 5.0)]),                   
        "Chandrasekharpur Cluster": ("Chandrasekharpur", [(8.2, 5.8), (9.8, 4.2), (8.8, 4.6)]),     
        "KIIT Cluster": ("KIIT University", [(9.4, 7.9), (10.0, 6.2), (8.7, 6.8)]),                 
        "Khandagiri Cluster": ("Khandagiri", [(-2.8, 2.6), (-1.2, 2.9)]),                           
        "Acharya Cluster": ("Acharya Vihar", [(5.2, 3.8), ]),                                        
    }
    area_nodes_count = 0
    for cl_name, (anchor, points) in clusters.items():
        ax, ay = base_nodes[anchor]
        for i, (dx, dy) in enumerate(points, start=1):
            name = f"{cl_name} Area {i}"
            x, y = ax + dx, ay + dy
            g.add_node(name, (x, y), node_type="area")
            g.set_node_risk(name, 1.0, False)
            area_nodes_count += 1
    assert area_nodes_count == 22

    
    pois = {
        "Info City": (8.0, 3.5),
        "Nandankanan Gate": (11.0, 8.0),
        "Bapuji Nagar": (3.0, 0.5),
        "Saheed Nagar": (6.0, 2.5),
        "Baramunda Bus Stand": (0.0, 3.5),
        "Patia Square": (10.0, 6.0),
        "Rasulgarh": (7.0, 1.0),
        "Vani Vihar": (5.5, 2.0),
        "Fire Station Square": (6.5, 3.0),
        "Kalpana Square": (2.5, -1.0),
        "Ram Mandir Square": (4.3, 1.6),
        "Damana Square": (9.6, 5.6),
        "Niladri Vihar": (8.8, 6.4),
        
        "Nayapalli": (5.7, 4.6),
    }
 
    del pois["Bapuji Nagar"]

    for n, xy in pois.items():
        g.add_node(n, xy, node_type="area")
        g.set_node_risk(n, 1.0, False)

  
    hospitals = {
        "AIIMS Bhubaneswar": (-0.5, -1.0),
        "Capital Hospital": (3.6, 1.2),
        "SUM Hospital": (0.2, 4.2),
        "KIMS Hospital": (9.2, 6.6),
        "Apollo Hospitals": (6.2, 2.2),
        "CARE Hospital": (6.8, 3.6),
        "AMRI Hospital": (8.6, 5.4),
        "Hi-Tech Medical College": (10.8, 6.8),
        "KIIMS Hospital": (7.6, 4.4),
        "IMS & SUM Medical": (1.0, 3.2),
    }
    for h, xy in hospitals.items():
        g.add_node(h, xy, node_type="hospital")
        g.set_node_risk(h, 1.0, False)

    assert len(g.coords) == 55, f"Expected 55 nodes, got {len(g.coords)}"

  
    metro_chain = [
        "Old Town", "Kalpana Square", "Bhubaneswar Railway Station", "Master Canteen Square",
        "Vani Vihar", "Acharya Vihar", "CRP Square", "Jaydev Vihar",
        "Chandrasekharpur", "KIIT University", "Patia Square", "Nandankanan Gate"
    ]
    for u, v in zip(metro_chain, metro_chain[1:]):
        g.add_edge(u, v, "metro", time_min=6, cost=25, delay_prob=0.05, comfort=0.9)

    ring = [
        "Biju Patnaik Airport", "Baramunda Bus Stand", "Khandagiri", "Nayapalli",
        "CRP Square", "Fire Station Square", "Rasulgarh", "Biju Patnaik Airport"
    ]
    for u, v in zip(ring, ring[1:]):
        g.add_edge(u, v, "bus", time_min=10, cost=15, delay_prob=0.15, comfort=0.7)

    def connect_nearby(nodes_list, mode="cab", t=8, c=120, d=0.1, comf=0.8):
        for i in range(len(nodes_list)-1):
            g.add_edge(nodes_list[i], nodes_list[i+1], mode, t, c, d, comf)

    connect_nearby(["Bhubaneswar Railway Station", "Ram Mandir Square", "Master Canteen Square"],
                   mode="walk", t=7, c=0, d=0.0, comf=0.7)
    connect_nearby(["CRP Square", "Nayapalli", "Jaydev Vihar"], mode="cab", t=8, c=120, d=0.1, comf=0.8)
    connect_nearby(["Jaydev Vihar", "Saheed Nagar", "Vani Vihar"], mode="cab", t=8, c=110, d=0.1, comf=0.8)
    connect_nearby(["Chandrasekharpur", "Damana Square", "Niladri Vihar"], mode="cab", t=8, c=120, d=0.1, comf=0.8)
    connect_nearby(["Info City", "Chandrasekharpur"], mode="cab", t=10, c=130, d=0.12, comf=0.8)

    g.add_edge("Biju Patnaik Airport", "Bhubaneswar Railway Station", "bus", 20, 30, 0.2, 0.7)
    g.add_edge("Biju Patnaik Airport", "Old Town", "cab", 15, 200, 0.1, 0.8)
    g.add_edge("Biju Patnaik Airport", "Khandagiri", "cab", 20, 220, 0.1, 0.75)
    g.add_edge("Khandagiri", "CRP Square", "cab", 20, 220, 0.12, 0.75)

    hospital_links = [
        ("AIIMS Bhubaneswar", "Biju Patnaik Airport"),
        ("Capital Hospital", "Ram Mandir Square"),
        ("SUM Hospital", "Baramunda Bus Stand"),
        ("KIMS Hospital", "KIIT University"),
        ("Apollo Hospitals", "Vani Vihar"),
        ("CARE Hospital", "Fire Station Square"),
        ("AMRI Hospital", "Chandrasekharpur"),
        ("Hi-Tech Medical College", "Patia Square"),
        ("KIIMS Hospital", "Jaydev Vihar"),
        ("IMS & SUM Medical", "Khandagiri"),
    ]
    for h, hub in hospital_links:
        g.add_edge(h, hub, "cab", 10, 140, 0.1, 0.85)

    add_pairs = [
        ("Acharya Vihar", "Saheed Nagar"), ("CRP Square", "Nayapalli"),
        ("Jaydev Vihar", "Info City"), ("Chandrasekharpur", "Info City"),
        ("Patia Square", "Info City"), ("Ram Mandir Square", "Biju Patnaik Airport"),
        ("Kalpana Square", "Old Town"), ("Rasulgarh", "Saheed Nagar")
    ]
    for u, v in add_pairs:
        g.add_edge(u, v, "cab", 9, 110, 0.1, 0.8)

    short_walks = [
        ("Master Canteen Square", "Ram Mandir Square"),
        ("Vani Vihar", "Saheed Nagar"),
        ("CRP Square", "Nayapalli"),
        ("Jaydev Vihar", "Fire Station Square"),
        ("Chandrasekharpur", "Damana Square"),
        ("KIIT University", "KIMS Hospital"),
    ]
    for u, v in short_walks:
        g.add_edge(u, v, "walk", 6, 0, 0.0, 0.75)

    return g
def _reconstruct_path(came_from, goal):
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path

def _extract_modes(graph: MultiModalGraph, path):
    modes = []
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        m = None
        for e in graph.adj[u]:
            if e["to"] == v:
                m = e["mode"]; break
        modes.append(m)
    return modes
def edge_weight(edge, w_time=1.0, w_cost=0.2, w_delay=30.0, w_discomfort=10.0):
    penalty_delay = edge["delay_prob"] * w_delay
    penalty_discomfort = (1.0 - edge["comfort"]) * w_discomfort
    return (w_time * edge["time_min"]
            + w_cost * edge["cost"]
            + penalty_delay
            + penalty_discomfort)
def ucs(graph: MultiModalGraph, start, goal, **weight_kwargs):
    if graph.node_blocked[start] or graph.node_blocked[goal]:
        return None, math.inf, []

    frontier = [(0.0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0.0}

    while frontier:
        g, current = heapq.heappop(frontier)

        if current == goal:
            break
        if graph.node_blocked[current]:
            continue

        for edge in graph.adj[current]:
            nxt = edge["to"]
            if graph.node_blocked[nxt]:
                continue
            w = edge_weight(edge, **weight_kwargs)
            new_cost = g + w
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                came_from[nxt] = current
                heapq.heappush(frontier, (new_cost, nxt))

    if goal not in came_from:
        return None, math.inf, []

    path = _reconstruct_path(came_from, goal)
    return path, cost_so_far[goal], _extract_modes(graph, path)




def heuristic(graph: MultiModalGraph, node, goal):
    r = graph.node_risk[node]
    if math.isinf(r) or graph.node_blocked[node]:
        return float("inf")
    return graph._euclid(node, goal) * max(1.0, r)

def astar(graph: MultiModalGraph, start, goal, **weight_kwargs):
    if graph.node_blocked[start] or graph.node_blocked[goal]:
        return None, math.inf, []

    start_h = heuristic(graph, start, goal)
    frontier = [(start_h, 0.0, start)]  # (f, g, node)
    came_from = {start: None}
    g_cost = {start: 0.0}

    while frontier:
        f, g, current = heapq.heappop(frontier)

        if current == goal:
            break
        if graph.node_blocked[current]:
            continue

        for edge in graph.adj[current]:
            nxt = edge["to"]
            if graph.node_blocked[nxt]:
                continue
            w = edge_weight(edge, **weight_kwargs)
            new_g = g + w
            if nxt not in g_cost or new_g < g_cost[nxt]:
                g_cost[nxt] = new_g
                came_from[nxt] = current
                h = heuristic(graph, nxt, goal)
                new_f = new_g + h
                heapq.heappush(frontier, (new_f, new_g, nxt))

    if goal not in came_from:
        return None, math.inf, []

    path = _reconstruct_path(came_from, goal)
    return path, g_cost[goal], _extract_modes(graph, path)

def run_search_module():
    g = build_bbsr_55_exact()

    g.set_node_risk("Master Canteen Square", risk_score=5.0, calamity=True)
    for n, r in [("Bhubaneswar Railway Station", 1.2),
                 ("Acharya Vihar", 1.3),
                 ("CRP Square", 1.15)]:
        g.set_node_risk(n, risk_score=r, calamity=False)

    start, goal = "Biju Patnaik Airport", "KIIT University"
    weights = dict(w_time=1.0, w_cost=0.2, w_delay=30.0, w_discomfort=10.0)

    ucs_path, ucs_cost, ucs_modes = ucs(g, start, goal, **weights)
    astar_path, astar_cost, astar_modes = astar(g, start, goal, **weights)


    recommended_route = "astar" if ucs_cost <= astar_cost else "ucs"

    return {
        "ucs": {
            "path": ucs_path,
            "modes": ucs_modes,
            "cost": ucs_cost,
        },
        "astar": {
            "path": astar_path,
            "modes": astar_modes,
            "cost": astar_cost,
        },
        "recommended_route": recommended_route,
    }




if __name__ == "__main__":

    results = run_search_module()

    print("\n--- UCS Result ---")
    print("Path:", results["ucs"]["path"])
    print("Cost:", results["ucs"]["cost"])

    print("\n--- A* Result (Future-Risk-Aware) ---")
    print("Path:", results["astar"]["path"])
    print("Cost:", results["astar"]["cost"])

    print("\nRecommended Route:", results["recommended_route"])
