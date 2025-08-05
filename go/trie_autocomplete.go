package main

import "fmt"

type TrieNode struct {
    children map[rune]*TrieNode
    isEnd    bool
}

type Trie struct {
    root *TrieNode
}

func NewTrie() *Trie {
    return &Trie{root: &TrieNode{children: make(map[rune]*TrieNode)}}
}

func (t *Trie) Insert(word string) {
    node := t.root
    for _, char := range word {
        if _, exists := node.children[char]; !exists {
            node.children[char] = &TrieNode{children: make(map[rune]*TrieNode)}
        }
        node = node.children[char]
    }
    node.isEnd = true
}

func (t *Trie) StartsWith(prefix string) []string {
    node := t.root
    for _, char := range prefix {
        if _, exists := node.children[char]; !exists {
            return []string{}
        }
        node = node.children[char]
    }

    var results []string
    var dfs func(*TrieNode, string)
    dfs = func(n *TrieNode, path string) {
        if n.isEnd {
            results = append(results, path)
        }
        for char, child := range n.children {
            dfs(child, path+string(char))
        }
    }

    dfs(node, prefix)
    return results
}

func main() {
    trie := NewTrie()
    trie.Insert("apple")
    trie.Insert("app")
    trie.Insert("apply")
    fmt.Println(trie.StartsWith("app")) // Expected: ["apple", "app", "apply"]
}
