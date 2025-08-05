import time
from typing import Dict, List, Optional, Any
from datetime import datetime

class FileNode:
    def __init__(self, name: str, is_directory: bool = False, size: int = 0):
        self.name = name
        self.is_directory = is_directory
        self.size = size
        self.modified = datetime.now()
        self.children: Dict[str, FileNode] = {}
        self.parent: Optional[FileNode] = None

class FileSystem:
    def __init__(self):
        self.root = FileNode("/", is_directory=True)

    def create_directory(self, path: str) -> bool:
        parts = [part for part in path.split("/") if part]
        current = self.root

        for part in parts:
            if part in current.children:
                child = current.children[part]
                if not child.is_directory:
                    raise ValueError(f"File exists with name {part}")
                current = child
            else:
                new_dir = FileNode(part, is_directory=True)
                new_dir.parent = current
                current.children[part] = new_dir
                current = new_dir
        
        return True

    def create_file(self, path: str, size: int) -> bool:
        last_slash = path.rfind("/")
        dir_path = path[:last_slash] if last_slash > 0 else "/"
        file_name = path[last_slash + 1:]

        if dir_path != "/":
            self.create_directory(dir_path)

        current = self.root
        if dir_path != "/":
            parts = [part for part in dir_path.split("/") if part]
            for part in parts:
                current = current.children[part]

        if file_name in current.children:
            raise ValueError(f"File already exists: {file_name}")

        new_file = FileNode(file_name, is_directory=False, size=size)
        new_file.parent = current
        current.children[file_name] = new_file
        return True

    def list_directory(self, path: str) -> List[str]:
        current = self.root
        if path != "/":
            parts = [part for part in path.split("/") if part]
            for part in parts:
                if part not in current.children:
                    return []
                current = current.children[part]

        return sorted(current.children.keys())

    def print_tree(self, node: Optional[FileNode] = None, indent: str = ""):
        if node is None:
            node = self.root

        node_type = "DIR" if node.is_directory else f"FILE ({node.size} bytes)"
        print(f"{indent}{node.name} [{node_type}]")

        for child_name in sorted(node.children.keys()):
            self.print_tree(node.children[child_name], indent + "  ")

    def get_total_size(self, path: str) -> int:
        current = self.root
        if path != "/":
            parts = [part for part in path.split("/") if part]
            for part in parts:
                if part not in current.children:
                    return 0
                current = current.children[part]

        def calculate_size(node: FileNode) -> int:
            if not node.is_directory:
                return node.size
            
            total = 0
            for child in node.children.values():
                total += calculate_size(child)
            return total

        return calculate_size(current)

    def find_files(self, pattern: str, node: Optional[FileNode] = None) -> List[str]:
        if node is None:
            node = self.root
        
        results = []
        if not node.is_directory and pattern.lower() in node.name.lower():
            results.append(self._get_full_path(node))
        
        for child in node.children.values():
            results.extend(self.find_files(pattern, child))
        
        return results

    def _get_full_path(self, node: FileNode) -> str:
        path_parts = []
        current = node
        while current and current.name != "/":
            path_parts.append(current.name)
            current = current.parent
        
        if not path_parts:
            return "/"
        
        return "/" + "/".join(reversed(path_parts))

class BTreeNode:
    def __init__(self, is_leaf: bool = True):
        self.keys: List[int] = []
        self.values: List[Any] = []
        self.children: List[BTreeNode] = []
        self.is_leaf = is_leaf

class BTree:
    def __init__(self, degree: int):
        self.root = BTreeNode()
        self.degree = degree

    def search(self, key: int) -> Optional[Any]:
        return self._search_node(self.root, key)

    def _search_node(self, node: BTreeNode, key: int) -> Optional[Any]:
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            return node.values[i]

        if node.is_leaf:
            return None

        return self._search_node(node.children[i], key)

    def insert(self, key: int, value: Any):
        if self._is_full(self.root):
            new_root = BTreeNode(is_leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
        
        self._insert_non_full(self.root, key, value)

    def _is_full(self, node: BTreeNode) -> bool:
        return len(node.keys) == 2 * self.degree - 1

    def _insert_non_full(self, node: BTreeNode, key: int, value: Any):
        i = len(node.keys) - 1

        if node.is_leaf:
            node.keys.append(0)
            node.values.append(None)
            
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            if self._is_full(node.children[i]):
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent: BTreeNode, index: int):
        full_child = parent.children[index]
        new_child = BTreeNode(is_leaf=full_child.is_leaf)
        mid = self.degree - 1

        new_child.keys = full_child.keys[mid + 1:]
        new_child.values = full_child.values[mid + 1:]
        full_child.keys = full_child.keys[:mid]
        full_child.values = full_child.values[:mid]

        if not full_child.is_leaf:
            new_child.children = full_child.children[mid + 1:]
            full_child.children = full_child.children[:mid + 1]

        parent.keys.insert(index, full_child.keys[mid])
        parent.values.insert(index, full_child.values[mid])
        parent.children.insert(index + 1, new_child)

    def get_all_values(self, node: Optional[BTreeNode] = None) -> List[tuple]:
        if node is None:
            node = self.root
        
        result = []
        for i in range(len(node.keys)):
            if not node.is_leaf:
                result.extend(self.get_all_values(node.children[i]))
            result.append((node.keys[i], node.values[i]))
        
        if not node.is_leaf:
            result.extend(self.get_all_values(node.children[-1]))
        
        return result

class DecisionNode:
    def __init__(self, feature: str = None, threshold: float = None, 
                 value: str = None, is_leaf: bool = False):
        self.feature = feature
        self.threshold = threshold
        self.left: Optional[DecisionNode] = None
        self.right: Optional[DecisionNode] = None
        self.value = value
        self.is_leaf = is_leaf

class DecisionTree:
    def __init__(self):
        self.root: Optional[DecisionNode] = None

    def build_loan_approval_tree(self):
        """Build a decision tree for loan approval based on age, income, and credit score"""
        self.root = DecisionNode(feature="age", threshold=30.0)
        
        # Left subtree (age <= 30)
        self.root.left = DecisionNode(feature="income", threshold=50000.0)
        self.root.left.left = DecisionNode(value="reject", is_leaf=True)
        self.root.left.right = DecisionNode(value="approve", is_leaf=True)
        
        # Right subtree (age > 30)
        self.root.right = DecisionNode(feature="credit_score", threshold=700.0)
        self.root.right.left = DecisionNode(value="review", is_leaf=True)
        self.root.right.right = DecisionNode(value="approve", is_leaf=True)

    def predict(self, features: Dict[str, float]) -> str:
        if not self.root:
            raise ValueError("Tree not built yet")
        return self._traverse(self.root, features)

    def _traverse(self, node: DecisionNode, features: Dict[str, float]) -> str:
        if node.is_leaf:
            return node.value

        feature_value = features[node.feature]
        if feature_value <= node.threshold:
            return self._traverse(node.left, features)
        return self._traverse(node.right, features)

    def print_tree(self, node: Optional[DecisionNode] = None, indent: str = ""):
        if node is None:
            node = self.root

        if node.is_leaf:
            print(f"{indent}-> {node.value}")
        else:
            print(f"{indent}{node.feature} <= {node.threshold}?")
            print(f"{indent}├─ Yes:")
            self.print_tree(node.left, indent + "│  ")
            print(f"{indent}└─ No:")
            self.print_tree(node.right, indent + "   ")

def demonstrate_binary_trees():
    print("=== File System Example ===")
    fs = FileSystem()
    fs.create_directory("/home/user")
    fs.create_directory("/home/user/documents")
    fs.create_file("/home/user/documents/readme.txt", 1024)
    fs.create_file("/home/user/documents/photo.jpg", 2048576)
    fs.create_file("/home/user/documents/report.pdf", 512000)
    fs.create_directory("/var/log")
    fs.create_file("/var/log/system.log", 4096)
    fs.create_file("/var/log/error.log", 2048)

    print("File system structure:")
    fs.print_tree()

    print(f"\nFiles in /home/user/documents:")
    files = fs.list_directory("/home/user/documents")
    for file in files:
        print(f"  {file}")

    print(f"\nTotal size of /home/user: {fs.get_total_size('/home/user')} bytes")
    
    print(f"\nFind files containing 'log':")
    log_files = fs.find_files("log")
    for file_path in log_files:
        print(f"  {file_path}")

    print("\n=== Database B-Tree Example ===")
    btree = BTree(degree=3)
    
    # Insert user records
    users = [
        (1, "Alice Johnson"),
        (3, "Bob Smith"), 
        (7, "Charlie Brown"),
        (10, "David Wilson"),
        (11, "Eve Davis"),
        (13, "Frank Miller"),
        (14, "Grace Lee"),
        (15, "Henry Taylor"),
        (18, "Ivy Chen"),
        (16, "Jack Robinson"),
        (19, "Kate Adams"),
        (24, "Liam Garcia")
    ]
    
    for user_id, name in users:
        btree.insert(user_id, f"User: {name}")

    print(f"Search user ID 10: {btree.search(10)}")
    print(f"Search user ID 15: {btree.search(15)}")
    print(f"Search user ID 99: {btree.search(99) or 'Not found'}")
    
    print(f"\nAll users in B-tree (sorted by ID):")
    all_users = btree.get_all_values()
    for user_id, user_data in sorted(all_users):
        print(f"  ID {user_id}: {user_data}")

    print("\n=== Decision Tree Example ===")
    dt = DecisionTree()
    dt.build_loan_approval_tree()

    print("Loan approval decision tree:")
    dt.print_tree()

    test_cases = [
        {"age": 25, "income": 45000, "credit_score": 650, "description": "Young, low income, medium credit"},
        {"age": 25, "income": 60000, "credit_score": 750, "description": "Young, good income, high credit"},
        {"age": 35, "income": 40000, "credit_score": 600, "description": "Older, low income, low credit"},
        {"age": 40, "income": 80000, "credit_score": 800, "description": "Older, high income, excellent credit"},
        {"age": 28, "income": 35000, "credit_score": 720, "description": "Young, very low income, high credit"},
        {"age": 45, "income": 90000, "credit_score": 680, "description": "Older, high income, medium credit"}
    ]

    print(f"\nLoan approval predictions:")
    for case in test_cases:
        features = {k: v for k, v in case.items() if k != "description"}
        result = dt.predict(features)
        print(f"{case['description']} -> {result}")

if __name__ == "__main__":
    demonstrate_binary_trees()