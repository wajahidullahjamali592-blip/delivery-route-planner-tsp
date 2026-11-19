"""
Delivery Route Planner  (DAA Project)
-------------------------------------
Problem : A delivery rider starts at a depot, must visit every customer once
          and return to the depot. Find the shortest route (Travelling Salesman Problem).

Algorithms used
  1. Brute Force / Exhaustive Search : tries every possible route -> optimal, O((n-1)!)
  2. Nearest Neighbor (Greedy)       : always go to closest unvisited city -> fast, O(n^2), not always optimal
"""

import math
import random
import time
from itertools import permutations


# ---------------------------------------------------------------- helpers
def distance(a, b):
    """Euclidean distance between two points (x, y)."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def build_matrix(coords):
    """Pre-compute distance between every pair of cities."""
    n = len(coords)
    return [[distance(coords[i], coords[j]) for j in range(n)] for i in range(n)]


def route_length(route, dist):
    """Total length of a closed route (returns to the starting city)."""
    total = 0.0
    for i in range(len(route)):
        total += dist[route[i]][route[(i + 1) % len(route)]]
    return total


# ------------------------------------------------- 1) BRUTE FORCE (Exhaustive)
def tsp_brute_force(dist, start=0):
    """
    Generate every permutation of the remaining cities, calculate the length
    of each route and keep the minimum.
    Start city is fixed (a cycle can be rotated), so routes checked = (n-1)!
    Time  : O(n! ) ~ O((n-1)! * n)
    Space : O(n)   (itertools generates permutations one at a time)
    """
    n = len(dist)
    others = [c for c in range(n) if c != start]
    best_route, best_len, checked = None, float("inf"), 0

    for perm in permutations(others):
        route = (start,) + perm
        length = route_length(route, dist)
        checked += 1
        if length < best_len:
            best_len, best_route = length, route

    return list(best_route), best_len, checked


# ------------------------------------------------- 2) NEAREST NEIGHBOR (Greedy)
def tsp_nearest_neighbor(dist, start=0):
    """
    From the current city, always move to the closest unvisited city.
    Time  : O(n^2)   (n steps, each scans up to n cities)
    Space : O(n)
    """
    n = len(dist)
    visited = [False] * n
    route = [start]
    visited[start] = True
    current = start

    for _ in range(n - 1):
        nearest, nearest_d = None, float("inf")
        for city in range(n):
            if not visited[city] and dist[current][city] < nearest_d:
                nearest, nearest_d = city, dist[current][city]
        route.append(nearest)
        visited[nearest] = True
        current = nearest

    return route, route_length(route, dist)


# ---------------------------------------------------------------- display
def show_route(names, route):
    return " -> ".join(names[c] for c in route) + " -> " + names[route[0]]


def plot_routes(names, coords, bf_route, nn_route):
    """Draw both routes side by side (needs matplotlib, optional)."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("(matplotlib not installed - skipping graph. Run: pip install matplotlib)")
        return

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, route, title in ((axes[0], bf_route, "Brute Force (Optimal)"),
                             (axes[1], nn_route, "Nearest Neighbor (Greedy)")):
        if route is None:
            ax.set_title(title + "\nskipped (too many cities)")
            continue
        pts = [coords[c] for c in route] + [coords[route[0]]]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color="tab:blue")
        for i, (x, y) in enumerate(coords):
            ax.annotate(names[i], (x, y), textcoords="offset points", xytext=(5, 5))
        ax.scatter(*coords[route[0]], color="red", s=120, zorder=5, label="Depot")
        ax.set_title(title)
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    plt.show()


def compare_growth():
    """Shows how brute force time explodes while nearest neighbor stays tiny."""
    print("\n{:>4} {:>14} {:>14} {:>16}".format("n", "Brute (sec)", "NN (sec)", "Routes (n-1)!"))
    print("-" * 52)
    for n in range(4, 11):
        coords = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(n)]
        dist = build_matrix(coords)

        t = time.perf_counter(); _, _, checked = tsp_brute_force(dist); t_bf = time.perf_counter() - t
        t = time.perf_counter(); tsp_nearest_neighbor(dist);            t_nn = time.perf_counter() - t
        print("{:>4} {:>14.6f} {:>14.6f} {:>16}".format(n, t_bf, t_nn, checked))


# ---------------------------------------------------------------- input modes
SAMPLE_NAMES = ["Depot", "Shop A", "Shop B", "Shop C", "Shop D", "Shop E", "Shop F", "Shop G"]
SAMPLE_COORDS = [(50, 50), (10, 80), (30, 20), (80, 90), (90, 30), (65, 60), (20, 50), (45, 85)]


def read_custom():
    n = int(input("Number of locations (including depot, first one is depot): "))
    names, coords = [], []
    for i in range(n):
        name = input(f"  Name of location {i + 1}: ").strip() or f"Loc{i + 1}"
        x = float(input("    x coordinate: "))
        y = float(input("    y coordinate: "))
        names.append(name)
        coords.append((x, y))
    return names, coords


def main():
    print("=" * 55)
    print("        DELIVERY ROUTE PLANNER  (TSP - DAA Project)")
    print("=" * 55)
    print("1. Use sample data (8 locations)")
    print("2. Random locations")
    print("3. Enter my own locations")
    print("4. Show time growth: Brute Force vs Nearest Neighbor")
    choice = input("Choose (1-4): ").strip()

    if choice == "4":
        compare_growth()
        return
    if choice == "2":
        n = int(input("How many locations (incl. depot)? "))
        names = ["Depot"] + [f"Stop {i}" for i in range(1, n)]
        coords = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(n)]
    elif choice == "3":
        names, coords = read_custom()
    else:
        names, coords = SAMPLE_NAMES, SAMPLE_COORDS

    n = len(coords)
    if n < 2:
        print("Need at least 2 locations.")
        return
    dist = build_matrix(coords)

    # Nearest neighbor always runs
    t = time.perf_counter()
    nn_route, nn_len = tsp_nearest_neighbor(dist)
    nn_time = time.perf_counter() - t

    # Brute force only if n is small enough ( (n-1)! grows very fast )
    bf_route = None
    if n <= 11:
        t = time.perf_counter()
        bf_route, bf_len, checked = tsp_brute_force(dist)
        bf_time = time.perf_counter() - t
    else:
        print(f"\nBrute force skipped: {math.factorial(n - 1):,} routes is too many.")

    print("\n---------------- RESULTS ----------------")
    if bf_route:
        print(f"Brute Force      : {show_route(names, bf_route)}")
        print(f"   Distance = {bf_len:.2f} | Routes checked = {checked:,} | Time = {bf_time:.6f}s")
    print(f"Nearest Neighbor : {show_route(names, nn_route)}")
    print(f"   Distance = {nn_len:.2f} | Time = {nn_time:.6f}s")
    if bf_route:
        extra = (nn_len - bf_len) / bf_len * 100
        print(f"\nNearest Neighbor is {extra:.2f}% longer than the optimal route.")

    plot_routes(names, coords, bf_route, nn_route)


if __name__ == "__main__":
    main()
