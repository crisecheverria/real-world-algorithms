class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def starts_with(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results = []

        def dfs(n, path):
            if n.is_end:
                results.append(path)
            for c, child in n.children.items():
                dfs(child, path + c)

        dfs(node, prefix)
        return results

# Unit test
trie = Trie()
trie.insert("apple")
trie.insert("app")
trie.insert("apply")
print(trie.starts_with("app"))  # ['apple', 'app', 'apply']
