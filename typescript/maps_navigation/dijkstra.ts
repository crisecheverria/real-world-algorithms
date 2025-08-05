type Edge = { to: string; weight: number };
type Graph = Record<string, Edge[]>;

function dijkstra(graph: Graph, start: string): Record<string, number> {
  const distances: Record<string, number> = {};
  const visited: Set<string> = new Set();
  const pq: [string, number][] = [[start, 0]];

  for (const node in graph) distances[node] = Infinity;
  distances[start] = 0;

  while (pq.length > 0) {
    pq.sort((a, b) => a[1] - b[1]);
    const [current, dist] = pq.shift()!;
    if (visited.has(current)) continue;
    visited.add(current);

    for (const edge of graph[current]) {
      const newDist = dist + edge.weight;
      if (newDist < distances[edge.to]) {
        distances[edge.to] = newDist;
        pq.push([edge.to, newDist]);
      }
    }
  }

  return distances;
}

// Unit test
const graph: Graph = {
  A: [{ to: "B", weight: 1 }, { to: "C", weight: 4 }],
  B: [{ to: "C", weight: 2 }, { to: "D", weight: 5 }],
  C: [{ to: "D", weight: 1 }],
  D: []
};

console.log(dijkstra(graph, "A")); // Expected: { A: 0, B: 1, C: 3, D: 4 }
