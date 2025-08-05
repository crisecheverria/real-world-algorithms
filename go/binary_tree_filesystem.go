package main

import (
	"fmt"
	"sort"
	"strings"
	"time"
)

type FileNode struct {
	name     string
	isDir    bool
	size     int64
	modified time.Time
	children map[string]*FileNode
	parent   *FileNode
}

func NewFileNode(name string, isDir bool, size int64) *FileNode {
	return &FileNode{
		name:     name,
		isDir:    isDir,
		size:     size,
		modified: time.Now(),
		children: make(map[string]*FileNode),
	}
}

type FileSystem struct {
	root *FileNode
}

func NewFileSystem() *FileSystem {
	root := NewFileNode("/", true, 0)
	return &FileSystem{root: root}
}

func (fs *FileSystem) CreateDir(path string) error {
	parts := strings.Split(strings.Trim(path, "/"), "/")
	current := fs.root
	
	for _, part := range parts {
		if part == "" {
			continue
		}
		
		if child, exists := current.children[part]; exists {
			if !child.isDir {
				return fmt.Errorf("file exists with name %s", part)
			}
			current = child
		} else {
			newDir := NewFileNode(part, true, 0)
			newDir.parent = current
			current.children[part] = newDir
			current = newDir
		}
	}
	return nil
}

func (fs *FileSystem) CreateFile(path string, size int64) error {
	lastSlash := strings.LastIndex(path, "/")
	dirPath := path[:lastSlash]
	fileName := path[lastSlash+1:]
	
	if dirPath == "" {
		dirPath = "/"
	}
	
	fs.CreateDir(dirPath)
	
	current := fs.root
	if dirPath != "/" {
		parts := strings.Split(strings.Trim(dirPath, "/"), "/")
		for _, part := range parts {
			if part != "" {
				current = current.children[part]
			}
		}
	}
	
	if _, exists := current.children[fileName]; exists {
		return fmt.Errorf("file already exists: %s", fileName)
	}
	
	newFile := NewFileNode(fileName, false, size)
	newFile.parent = current
	current.children[fileName] = newFile
	return nil
}

func (fs *FileSystem) List(path string) []string {
	current := fs.root
	if path != "/" {
		parts := strings.Split(strings.Trim(path, "/"), "/")
		for _, part := range parts {
			if part != "" {
				if child, exists := current.children[part]; exists {
					current = child
				} else {
					return nil
				}
			}
		}
	}
	
	var result []string
	for name := range current.children {
		result = append(result, name)
	}
	sort.Strings(result)
	return result
}

func (fs *FileSystem) PrintTree(node *FileNode, indent string) {
	if node == nil {
		node = fs.root
	}
	
	nodeType := "DIR"
	if !node.isDir {
		nodeType = fmt.Sprintf("FILE (%d bytes)", node.size)
	}
	
	fmt.Printf("%s%s [%s]\n", indent, node.name, nodeType)
	
	var names []string
	for name := range node.children {
		names = append(names, name)
	}
	sort.Strings(names)
	
	for _, name := range names {
		fs.PrintTree(node.children[name], indent+"  ")
	}
}

type BTreeNode struct {
	keys     []int
	values   []string
	children []*BTreeNode
	leaf     bool
}

type BTree struct {
	root   *BTreeNode
	degree int
}

func NewBTree(degree int) *BTree {
	return &BTree{
		root:   &BTreeNode{leaf: true},
		degree: degree,
	}
}

func (bt *BTree) Search(key int) (string, bool) {
	return bt.searchNode(bt.root, key)
}

func (bt *BTree) searchNode(node *BTreeNode, key int) (string, bool) {
	i := 0
	for i < len(node.keys) && key > node.keys[i] {
		i++
	}
	
	if i < len(node.keys) && key == node.keys[i] {
		return node.values[i], true
	}
	
	if node.leaf {
		return "", false
	}
	
	return bt.searchNode(node.children[i], key)
}

func (bt *BTree) Insert(key int, value string) {
	if bt.isFull(bt.root) {
		newRoot := &BTreeNode{leaf: false}
		newRoot.children = append(newRoot.children, bt.root)
		bt.splitChild(newRoot, 0)
		bt.root = newRoot
	}
	bt.insertNonFull(bt.root, key, value)
}

func (bt *BTree) isFull(node *BTreeNode) bool {
	return len(node.keys) == 2*bt.degree-1
}

func (bt *BTree) insertNonFull(node *BTreeNode, key int, value string) {
	i := len(node.keys) - 1
	
	if node.leaf {
		node.keys = append(node.keys, 0)
		node.values = append(node.values, "")
		
		for i >= 0 && key < node.keys[i] {
			node.keys[i+1] = node.keys[i]
			node.values[i+1] = node.values[i]
			i--
		}
		node.keys[i+1] = key
		node.values[i+1] = value
	} else {
		for i >= 0 && key < node.keys[i] {
			i--
		}
		i++
		
		if bt.isFull(node.children[i]) {
			bt.splitChild(node, i)
			if key > node.keys[i] {
				i++
			}
		}
		bt.insertNonFull(node.children[i], key, value)
	}
}

func (bt *BTree) splitChild(parent *BTreeNode, index int) {
	fullChild := parent.children[index]
	newChild := &BTreeNode{leaf: fullChild.leaf}
	
	mid := bt.degree - 1
	
	newChild.keys = make([]int, len(fullChild.keys[mid+1:]))
	copy(newChild.keys, fullChild.keys[mid+1:])
	newChild.values = make([]string, len(fullChild.values[mid+1:]))
	copy(newChild.values, fullChild.values[mid+1:])
	
	if !fullChild.leaf {
		newChild.children = make([]*BTreeNode, len(fullChild.children[mid+1:]))
		copy(newChild.children, fullChild.children[mid+1:])
		fullChild.children = fullChild.children[:mid+1]
	}
	
	parent.keys = append(parent.keys, 0)
	parent.values = append(parent.values, "")
	parent.children = append(parent.children, nil)
	
	for i := len(parent.keys) - 1; i > index; i-- {
		parent.keys[i] = parent.keys[i-1]
		parent.values[i] = parent.values[i-1]
		parent.children[i+1] = parent.children[i]
	}
	
	parent.keys[index] = fullChild.keys[mid]
	parent.values[index] = fullChild.values[mid]
	parent.children[index+1] = newChild
	
	fullChild.keys = fullChild.keys[:mid]
	fullChild.values = fullChild.values[:mid]
}

type DecisionNode struct {
	feature   string
	threshold float64
	left      *DecisionNode
	right     *DecisionNode
	value     string
	isLeaf    bool
}

type DecisionTree struct {
	root *DecisionNode
}

func NewDecisionTree() *DecisionTree {
	return &DecisionTree{}
}

func (dt *DecisionTree) BuildTree() {
	dt.root = &DecisionNode{
		feature:   "age",
		threshold: 30.0,
		left: &DecisionNode{
			feature:   "income",
			threshold: 50000.0,
			left: &DecisionNode{
				value:  "reject",
				isLeaf: true,
			},
			right: &DecisionNode{
				value:  "approve",
				isLeaf: true,
			},
		},
		right: &DecisionNode{
			feature:   "credit_score",
			threshold: 700.0,
			left: &DecisionNode{
				value:  "review",
				isLeaf: true,
			},
			right: &DecisionNode{
				value:  "approve",
				isLeaf: true,
			},
		},
	}
}

func (dt *DecisionTree) Predict(age float64, income float64, creditScore float64) string {
	return dt.traverse(dt.root, map[string]float64{
		"age":          age,
		"income":       income,
		"credit_score": creditScore,
	})
}

func (dt *DecisionTree) traverse(node *DecisionNode, features map[string]float64) string {
	if node.isLeaf {
		return node.value
	}
	
	featureValue := features[node.feature]
	if featureValue <= node.threshold {
		return dt.traverse(node.left, features)
	}
	return dt.traverse(node.right, features)
}

func main() {
	fmt.Println("=== File System Example ===")
	fs := NewFileSystem()
	fs.CreateDir("/home/user")
	fs.CreateDir("/home/user/documents")
	fs.CreateFile("/home/user/documents/readme.txt", 1024)
	fs.CreateFile("/home/user/documents/photo.jpg", 2048576)
	fs.CreateDir("/var/log")
	fs.CreateFile("/var/log/system.log", 4096)
	
	fmt.Println("File system structure:")
	fs.PrintTree(nil, "")
	
	fmt.Println("\nFiles in /home/user/documents:")
	files := fs.List("/home/user/documents")
	for _, file := range files {
		fmt.Printf("  %s\n", file)
	}

	fmt.Println("\n=== Database B-Tree Example ===")
	btree := NewBTree(3)
	btree.Insert(1, "Record 1")
	btree.Insert(3, "Record 3")
	btree.Insert(7, "Record 7")
	btree.Insert(10, "Record 10")
	btree.Insert(11, "Record 11")
	btree.Insert(13, "Record 13")
	btree.Insert(14, "Record 14")
	btree.Insert(15, "Record 15")
	btree.Insert(18, "Record 18")
	btree.Insert(16, "Record 16")
	btree.Insert(19, "Record 19")
	btree.Insert(24, "Record 24")
	
	if value, found := btree.Search(10); found {
		fmt.Printf("Found key 10: %s\n", value)
	}
	if value, found := btree.Search(15); found {
		fmt.Printf("Found key 15: %s\n", value)
	}
	if _, found := btree.Search(99); !found {
		fmt.Println("Key 99 not found (as expected)")
	}

	fmt.Println("\n=== Decision Tree Example ===")
	dt := NewDecisionTree()
	dt.BuildTree()
	
	testCases := []struct {
		age, income, creditScore float64
		description              string
	}{
		{25, 45000, 650, "Young, low income, medium credit"},
		{25, 60000, 750, "Young, good income, high credit"},
		{35, 40000, 600, "Older, low income, low credit"},
		{40, 80000, 800, "Older, high income, excellent credit"},
	}
	
	for _, tc := range testCases {
		result := dt.Predict(tc.age, tc.income, tc.creditScore)
		fmt.Printf("%s -> %s\n", tc.description, result)
	}
}