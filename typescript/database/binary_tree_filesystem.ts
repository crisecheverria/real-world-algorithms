interface FileNode {
    name: string;
    isDirectory: boolean;
    size: number;
    modified: Date;
    children: Map<string, FileNode>;
    parent?: FileNode;
}

class FileSystem {
    private root: FileNode;

    constructor() {
        this.root = {
            name: '/',
            isDirectory: true,
            size: 0,
            modified: new Date(),
            children: new Map()
        };
    }

    createDirectory(path: string): boolean {
        const parts = path.split('/').filter(part => part.length > 0);
        let current = this.root;

        for (const part of parts) {
            if (current.children.has(part)) {
                const child = current.children.get(part)!;
                if (!child.isDirectory) {
                    throw new Error(`File exists with name ${part}`);
                }
                current = child;
            } else {
                const newDir: FileNode = {
                    name: part,
                    isDirectory: true,
                    size: 0,
                    modified: new Date(),
                    children: new Map(),
                    parent: current
                };
                current.children.set(part, newDir);
                current = newDir;
            }
        }
        return true;
    }

    createFile(path: string, size: number): boolean {
        const lastSlash = path.lastIndexOf('/');
        const dirPath = path.substring(0, lastSlash) || '/';
        const fileName = path.substring(lastSlash + 1);

        if (dirPath !== '/') {
            this.createDirectory(dirPath);
        }

        let current = this.root;
        if (dirPath !== '/') {
            const parts = dirPath.split('/').filter(part => part.length > 0);
            for (const part of parts) {
                current = current.children.get(part)!;
            }
        }

        if (current.children.has(fileName)) {
            throw new Error(`File already exists: ${fileName}`);
        }

        const newFile: FileNode = {
            name: fileName,
            isDirectory: false,
            size,
            modified: new Date(),
            children: new Map(),
            parent: current
        };

        current.children.set(fileName, newFile);
        return true;
    }

    list(path: string): string[] {
        let current = this.root;
        if (path !== '/') {
            const parts = path.split('/').filter(part => part.length > 0);
            for (const part of parts) {
                if (!current.children.has(part)) {
                    return [];
                }
                current = current.children.get(part)!;
            }
        }

        return Array.from(current.children.keys()).sort();
    }

    printTree(node: FileNode = this.root, indent: string = ''): void {
        const nodeType = node.isDirectory ? 'DIR' : `FILE (${node.size} bytes)`;
        console.log(`${indent}${node.name} [${nodeType}]`);

        const children = Array.from(node.children.entries()).sort();
        for (const [_, child] of children) {
            this.printTree(child, indent + '  ');
        }
    }

    getSize(path: string): number {
        let current = this.root;
        if (path !== '/') {
            const parts = path.split('/').filter(part => part.length > 0);
            for (const part of parts) {
                if (!current.children.has(part)) {
                    return 0;
                }
                current = current.children.get(part)!;
            }
        }

        if (!current.isDirectory) {
            return current.size;
        }

        let totalSize = 0;
        const calculateSize = (node: FileNode): void => {
            if (!node.isDirectory) {
                totalSize += node.size;
            } else {
                for (const child of node.children.values()) {
                    calculateSize(child);
                }
            }
        };

        calculateSize(current);
        return totalSize;
    }
}

class BTreeNode<T> {
    keys: number[] = [];
    values: T[] = [];
    children: BTreeNode<T>[] = [];
    isLeaf: boolean = true;

    constructor(isLeaf: boolean = true) {
        this.isLeaf = isLeaf;
    }
}

class BTree<T> {
    private root: BTreeNode<T>;
    private degree: number;

    constructor(degree: number) {
        this.degree = degree;
        this.root = new BTreeNode<T>();
    }

    search(key: number): T | null {
        return this.searchNode(this.root, key);
    }

    private searchNode(node: BTreeNode<T>, key: number): T | null {
        let i = 0;
        while (i < node.keys.length && key > node.keys[i]) {
            i++;
        }

        if (i < node.keys.length && key === node.keys[i]) {
            return node.values[i];
        }

        if (node.isLeaf) {
            return null;
        }

        return this.searchNode(node.children[i], key);
    }

    insert(key: number, value: T): void {
        if (this.isFull(this.root)) {
            const newRoot = new BTreeNode<T>(false);
            newRoot.children.push(this.root);
            this.splitChild(newRoot, 0);
            this.root = newRoot;
        }
        this.insertNonFull(this.root, key, value);
    }

    private isFull(node: BTreeNode<T>): boolean {
        return node.keys.length === 2 * this.degree - 1;
    }

    private insertNonFull(node: BTreeNode<T>, key: number, value: T): void {
        let i = node.keys.length - 1;

        if (node.isLeaf) {
            node.keys.push(0);
            node.values.push(value);

            while (i >= 0 && key < node.keys[i]) {
                node.keys[i + 1] = node.keys[i];
                node.values[i + 1] = node.values[i];
                i--;
            }
            node.keys[i + 1] = key;
            node.values[i + 1] = value;
        } else {
            while (i >= 0 && key < node.keys[i]) {
                i--;
            }
            i++;

            if (this.isFull(node.children[i])) {
                this.splitChild(node, i);
                if (key > node.keys[i]) {
                    i++;
                }
            }
            this.insertNonFull(node.children[i], key, value);
        }
    }

    private splitChild(parent: BTreeNode<T>, index: number): void {
        const fullChild = parent.children[index];
        const newChild = new BTreeNode<T>(fullChild.isLeaf);
        const mid = this.degree - 1;

        newChild.keys = fullChild.keys.splice(mid + 1);
        newChild.values = fullChild.values.splice(mid + 1);

        if (!fullChild.isLeaf) {
            newChild.children = fullChild.children.splice(mid + 1);
        }

        parent.keys.splice(index, 0, fullChild.keys[mid]);
        parent.values.splice(index, 0, fullChild.values[mid]);
        parent.children.splice(index + 1, 0, newChild);

        fullChild.keys.pop();
        fullChild.values.pop();
    }
}

interface DecisionNode {
    feature?: string;
    threshold?: number;
    left?: DecisionNode;
    right?: DecisionNode;
    value?: string;
    isLeaf: boolean;
}

class DecisionTree {
    private root?: DecisionNode;

    buildTree(): void {
        this.root = {
            feature: 'age',
            threshold: 30,
            isLeaf: false,
            left: {
                feature: 'income',
                threshold: 50000,
                isLeaf: false,
                left: {
                    value: 'reject',
                    isLeaf: true
                },
                right: {
                    value: 'approve',
                    isLeaf: true
                }
            },
            right: {
                feature: 'creditScore',
                threshold: 700,
                isLeaf: false,
                left: {
                    value: 'review',
                    isLeaf: true
                },
                right: {
                    value: 'approve',
                    isLeaf: true
                }
            }
        };
    }

    predict(features: { age: number; income: number; creditScore: number }): string {
        if (!this.root) {
            throw new Error('Tree not built yet');
        }
        return this.traverse(this.root, features);
    }

    private traverse(node: DecisionNode, features: Record<string, number>): string {
        if (node.isLeaf) {
            return node.value!;
        }

        const featureValue = features[node.feature!];
        if (featureValue <= node.threshold!) {
            return this.traverse(node.left!, features);
        }
        return this.traverse(node.right!, features);
    }

    printTree(node: DecisionNode = this.root!, indent: string = ''): void {
        if (node.isLeaf) {
            console.log(`${indent}-> ${node.value}`);
        } else {
            console.log(`${indent}${node.feature} <= ${node.threshold}?`);
            console.log(`${indent}├─ Yes:`);
            this.printTree(node.left!, indent + '│  ');
            console.log(`${indent}└─ No:`);
            this.printTree(node.right!, indent + '   ');
        }
    }
}

function demonstrateBinaryTrees(): void {
    console.log('=== File System Example ===');
    const fs = new FileSystem();
    fs.createDirectory('/home/user');
    fs.createDirectory('/home/user/documents');
    fs.createFile('/home/user/documents/readme.txt', 1024);
    fs.createFile('/home/user/documents/photo.jpg', 2048576);
    fs.createDirectory('/var/log');
    fs.createFile('/var/log/system.log', 4096);

    console.log('File system structure:');
    fs.printTree();

    console.log('\nFiles in /home/user/documents:');
    const files = fs.list('/home/user/documents');
    files.forEach(file => console.log(`  ${file}`));

    console.log(`\nTotal size of /home/user: ${fs.getSize('/home/user')} bytes`);

    console.log('\n=== Database B-Tree Example ===');
    const btree = new BTree<string>(3);
    const records = [
        [1, 'User: Alice'],
        [3, 'User: Bob'],
        [7, 'User: Charlie'],
        [10, 'User: David'],
        [11, 'User: Eve'],
        [13, 'User: Frank'],
        [14, 'User: Grace'],
        [15, 'User: Henry'],
        [18, 'User: Ivy'],
        [16, 'User: Jack'],
        [19, 'User: Kate'],
        [24, 'User: Liam']
    ];

    records.forEach(([key, value]) => btree.insert(key as number, value as string));

    console.log(`Search key 10: ${btree.search(10)}`);
    console.log(`Search key 15: ${btree.search(15)}`);
    console.log(`Search key 99: ${btree.search(99) || 'Not found'}`);

    console.log('\n=== Decision Tree Example ===');
    const dt = new DecisionTree();
    dt.buildTree();

    console.log('Decision tree structure:');
    dt.printTree();

    const testCases = [
        { age: 25, income: 45000, creditScore: 650, description: 'Young, low income, medium credit' },
        { age: 25, income: 60000, creditScore: 750, description: 'Young, good income, high credit' },
        { age: 35, income: 40000, creditScore: 600, description: 'Older, low income, low credit' },
        { age: 40, income: 80000, creditScore: 800, description: 'Older, high income, excellent credit' }
    ];

    console.log('\nLoan approval predictions:');
    testCases.forEach(testCase => {
        const result = dt.predict(testCase);
        console.log(`${testCase.description} -> ${result}`);
    });
}

if (require.main === module) {
    demonstrateBinaryTrees();
}

export { FileSystem, BTree, DecisionTree };