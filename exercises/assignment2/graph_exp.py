import random
import time
import heapq
import csv

# Generates a random directed graph with V vertices and given density (0 to 1).
# Uses a random spanning tree to guarantee strong connectivity (edges in both directions),
# then adds additional random directed edges based on density.
def generate_connected_graph(V, density):
    graph = {i: [] for i in range(V)}
    matrix = [[float('inf')] * V for _ in range(V)]

    for i in range(V):
        matrix[i][i] = 0

    # Guarantee strong connectivity by creating a random spanning tree
    # with edges in BOTH directions:
    nodes = list(range(V))
    random.shuffle(nodes)

    for i in range(1, V):
        u = nodes[i]
        v = nodes[random.randint(0, i - 1)]
        w = random.randint(1, 100)

        # Forward edge
        graph[u].append((v, w))
        matrix[u][v] = w

        # Backward edge (ensures strong connectivity)
        w2 = random.randint(1, 100)
        graph[v].append((u, w2))
        matrix[v][u] = w2

    # Add additional directed edges based on density:
    for i in range(V):
        for j in range(V):
            if i != j and matrix[i][j] == float('inf'):
                if random.random() < density:
                    w = random.randint(1, 100)
                    graph[i].append((j, w))
                    matrix[i][j] = w

    return graph, matrix

# Runs Dijkstra's algorithm from a single source to all vertices.
# Uses a binary heap for the priority queue. O(E log V) per source.
def dijkstra(graph, start, V):
    dist = [float('inf')] * V
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[v] > d + w:
                dist[v] = d + w
                heapq.heappush(pq, (dist[v], v))

    return dist


# Runs Floyd-Warshall algorithm on the adjacency matrix.
# O(|V|^3) regardless of k.
def floyd_warshall(matrix):
    V = len(matrix)
    dist = [row[:] for row in matrix]

    for k in range(V):
        for i in range(V):
            for j in range(V):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist

# Randomly pick k source vertices from the graph for Dijkstra's algorithm.
def pick_sources(V, k):
    return random.sample(range(V), k)

# Verifies that Dijkstra's results match Floyd-Warshall for the given sources.
# Used as a correctness check during development.
def verify_correctness(graph, matrix, sources):
    fw = floyd_warshall(matrix)
    return all(
        all(abs(dist - expected) <= 1e-6 # Allow small floating-point errors
            for dist, expected in zip(dijkstra(graph, s, len(matrix)), fw[s])) # Compare Dijkstra's output to Floyd-Warshall for each source
        for s in sources
    )

def run_experiment():
    sizes = [50, 100, 200, 400]
    densities = {"sparse": 0.05, "medium": 0.2, "dense": 0.8}
    trials = 5

    #Correctness check with a small graph:
    g_test, m_test = generate_connected_graph(20, 0.3)
    assert verify_correctness(g_test, m_test, pick_sources(20, 5)), \
        "Correctness check failed."
    print("Correctness check passed.\n")

    results = []
    for V in sizes:
        for d_name, density in densities.items():
            k_values = [k for k in (1, 5, 10, 20, V // 4, V // 2) if k <= V]
            fw_times = []
            dj_times = {k: [] for k in k_values}

            for _ in range(trials):
                graph, matrix = generate_connected_graph(V, density)

                start = time.perf_counter()
                _ = floyd_warshall(matrix)
                fw_times.append(time.perf_counter() - start)

                for k in k_values:
                    sources = pick_sources(V, k)
                    start = time.perf_counter()
                    for s in sources:
                        dijkstra(graph, s, V)
                    dj_times[k].append(time.perf_counter() - start)

            avg_fw = sum(fw_times) / trials
            for k in k_values:
                avg_dj = sum(dj_times[k]) / trials
                faster = "Floyd-Warshall" if avg_fw < avg_dj else "Dijkstra"
                results.append((V, d_name, k, round(avg_dj, 6), round(avg_fw, 6), faster))
                print(f"V={V:>4}, density={d_name:<8}, k={k:>2} | "
                      f"Dijkstra={avg_dj:.4f}s | Floyd={avg_fw:.4f}s | "
                      f"Faster: {faster}")

    return results


def save_to_csv(results, filename="results.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["V", "density", "k", "avg_dijkstra_time",
                         "avg_floyd_time", "faster_algorithm"])
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    results = run_experiment()
    save_to_csv(results, "results.csv")