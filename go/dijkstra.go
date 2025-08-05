package main

import (
    "container/heap"
    "fmt"
)

type Edge struct {
    to     string
    weight int
}

type Item struct {
    node     string
    distance int
}

type PriorityQueue []Item

func (pq PriorityQueue) Len() int { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool {
    return pq[i].distance < pq[j].distance
}
func (pq PriorityQueue) Swap(i, j int) {
    pq[i], pq[j] = pq[j], pq[i]
}
func (pq *PriorityQueue) Push(x any) {
    *pq = append(*pq, x.(Item))
}
func (pq *PriorityQueue) Pop() any {
    old := *pq
    n := len(old)
    item := old[n-1]
    *pq = old[0 : n-1]
    return item
}

func dijkstra(graph map[string][]Edge, start string) map[string]int {
    dist := map[string]int{}
    visited := map[string]bool{}
    for node := range graph {
        dist[node] = 1 << 30 // infinity
    }
    dist[start] = 0

    pq := &PriorityQueue{}
    heap.Init(pq)
    heap.Push(pq, Item{node: start, distance: 0})

    for pq.Len() > 0 {
        current := heap.Pop(pq).(Item)
        if visited[current.node] {
            continue
        }
        visited[current.node] = true

        for _, edge := range graph[current.node] {
            newDist := dist[current.node] + edge.weight
            if newDist < dist[edge.to] {
                dist[edge.to] = newDist
                heap.Push(pq, Item{node: edge.to, distance: newDist})
            }
        }
    }

    return dist
}

func main() {
    graph := map[string][]Edge{
        "A": {{"B", 1}, {"C", 4}},
        "B": {{"C", 2}, {"D", 5}},
        "C": {{"D", 1}},
        "D": {},
    }

    fmt.Println(dijkstra(graph, "A")) // Expected: map[A:0 B:1 C:3 D:4]
}
