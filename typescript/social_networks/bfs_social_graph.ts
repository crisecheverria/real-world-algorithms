const socialGraph: Record<string, string[]> = {
  Alice: ["Bob", "Charlie"],
  Bob: ["Alice", "Diana"],
  Charlie: ["Alice", "Diana"],
  Diana: ["Bob", "Charlie"]
};

function bfs(graph: Record<string, string[]>, start: string) {
  const visited = new Set<string>();
  const queue = [start];
  const result: string[] = [];

  while (queue.length > 0) {
    const node = queue.shift()!;
    if (visited.has(node)) continue;
    visited.add(node);
    result.push(node);
    for (const neighbor of graph[node]) {
      if (!visited.has(neighbor)) queue.push(neighbor);
    }
  }

  return result;
}

// Unit test
console.log(bfs(socialGraph, "Alice")); // Expected: ["Alice", "Bob", "Charlie", "Diana"]
