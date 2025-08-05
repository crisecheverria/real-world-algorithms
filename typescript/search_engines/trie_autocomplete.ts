class TrieNode {
  children: Record<string, TrieNode> = {};
  isEnd = false;
}

class Trie {
  root = new TrieNode();

  insert(word: string) {
    let node = this.root;
    for (const char of word) {
      if (!node.children[char]) node.children[char] = new TrieNode();
      node = node.children[char];
    }
    node.isEnd = true;
  }

  startsWith(prefix: string): string[] {
    let node = this.root;
    for (const char of prefix) {
      if (!node.children[char]) return [];
      node = node.children[char];
    }

    const results: string[] = [];
    const dfs = (n: TrieNode, path: string) => {
      if (n.isEnd) results.push(path);
      for (const [char, child] of Object.entries(n.children)) {
        dfs(child, path + char);
      }
    };

    dfs(node, prefix);
    return results;
  }
}

// Unit test
const trie = new Trie();
trie.insert("apple");
trie.insert("app");
trie.insert("apply");
console.log(trie.startsWith("app")); // Expected: ["apple", "app", "apply"]
