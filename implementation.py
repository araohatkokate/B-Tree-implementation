import time
import matplotlib.pyplot as plt
import random

class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t  # Minimum degree
        self.keys = []  # Keys in the node
        self.children = []  # Child pointers
        self.leaf = leaf  # True if node is a leaf
        self.num_keys = 0  # Number of keys in the node


class BTree:
    def __init__(self, t):
        self.root = BTreeNode(t, leaf=True)  # Start with an empty root
        self.t = t  # Minimum degree

    def search(self, key):
        return self._search(self.root, key)

    def _search(self, node, key):
        i = 0
        while i < node.num_keys and key > node.keys[i]:
            i += 1
        if i < node.num_keys and key == node.keys[i]:
            return node, i
        if node.leaf:
            return None
        return self._search(node.children[i], key)

    def insert(self, key):
        root = self.root
        if root.num_keys == 2 * self.t - 1:
            new_root = BTreeNode(self.t)
            new_root.children.append(root)
            new_root.leaf = False
            self._split_child(new_root, 0)
            self._insert_nonfull(new_root, key)
            self.root = new_root
        else:
            self._insert_nonfull(root, key)

    def _insert_nonfull(self, node, key):
        i = node.num_keys - 1
        if node.leaf:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
            node.num_keys += 1
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if node.children[i].num_keys == 2 * self.t - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_nonfull(node.children[i], key)

    def _split_child(self, parent, i):
        t = self.t
        child = parent.children[i]
        new_node = BTreeNode(t, child.leaf)
        parent.keys.insert(i, child.keys[t - 1])
        parent.children.insert(i + 1, new_node)
        parent.num_keys += 1

        new_node.keys = child.keys[t:]
        new_node.children = child.children[t:]
        child.keys = child.keys[:t - 1]
        child.children = child.children[:t]
        child.num_keys = t - 1
        new_node.num_keys = len(new_node.keys)

    def delete(self, key):
        self._delete(self.root, key)

    def _delete(self, node, key):
        t = self.t
        i = 0
        while i < node.num_keys and key > node.keys[i]:
            i += 1

        # Case 1: Key is in this node
        if i < node.num_keys and key == node.keys[i]:
            if node.leaf:
                node.keys.pop(i)
                node.num_keys -= 1
            else:
                if len(node.children[i].keys) >= t:
                    pred = self._get_predecessor(node, i)
                    node.keys[i] = pred
                    self._delete(node.children[i], pred)
                elif len(node.children[i + 1].keys) >= t:
                    succ = self._get_successor(node, i)
                    node.keys[i] = succ
                    self._delete(node.children[i + 1], succ)
                else:
                    self._merge(node, i)
                    self._delete(node.children[i], key)
        # Case 2: Key is not in this node
        elif not node.leaf:
            child = node.children[i]
            if child.num_keys == t - 1:
                self._fix_underflow(node, i)
            self._delete(child, key)

    def _get_predecessor(self, node, i):
        current = node.children[i]
        while not current.leaf:
            current = current.children[-1]
        return current.keys[-1]

    def _get_successor(self, node, i):
        current = node.children[i + 1]
        while not current.leaf:
            current = current.children[0]
        return current.keys[0]

    def _merge(self, node, i):
        child = node.children[i]
        sibling = node.children[i + 1]
        child.keys.append(node.keys.pop(i))
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        node.children.pop(i + 1)
        node.num_keys -= 1
        child.num_keys += len(sibling.keys) + 1

    def _fix_underflow(self, node, i):
        if i > 0 and len(node.children[i - 1].keys) >= self.t:
            self._borrow_from_left(node, i)
        elif i < len(node.keys) and len(node.children[i + 1].keys) >= self.t:
            self._borrow_from_right(node, i)
        else:
            if i < len(node.keys):
                self._merge(node, i)
            else:
                self._merge(node, i - 1)

    def _borrow_from_left(self, parent, i):
        child = parent.children[i]
        sibling = parent.children[i - 1]
        child.keys.insert(0, parent.keys[i - 1])
        parent.keys[i - 1] = sibling.keys.pop(-1)
        if not sibling.leaf:
            child.children.insert(0, sibling.children.pop(-1))
        child.num_keys += 1
        sibling.num_keys -= 1

    def _borrow_from_right(self, parent, i):
        child = parent.children[i]
        sibling = parent.children[i + 1]
        child.keys.append(parent.keys[i])
        parent.keys[i] = sibling.keys.pop(0)
        if not sibling.leaf:
            child.children.append(sibling.children.pop(0))
        child.num_keys += 1
        sibling.num_keys -= 1

#Benchmark Function
def benchmark_btree_cumulative(btree, num_operations):
    # Initialize cumulative times
    total_insert_time = 0
    total_search_time = 0
    total_delete_time = 0

    insert_times = []
    search_times = []
    delete_times = []

    # Generate a list of random keys to ensure consistency for search and delete
    keys = [random.randint(1, 1000000) for _ in range(num_operations)]

    # Warm-up: perform initial operations to stabilize performance
    for _ in range(1000):
        btree.insert(random.randint(1, 1000000))

    # Benchmark insertion
    for key in keys:
        start_time = time.time()
        btree.insert(key)
        total_insert_time += time.time() - start_time
        insert_times.append(total_insert_time)

    # Benchmark search
    for key in keys:
        start_time = time.time()
        btree.search(key)
        total_search_time += time.time() - start_time
        search_times.append(total_search_time)

    # Benchmark deletion
    for key in keys:
        start_time = time.time()
        btree.delete(key)
        total_delete_time += time.time() - start_time
        delete_times.append(total_delete_time)

    return insert_times, search_times, delete_times

# Create B-Tree and run benchmarks
t = 100  # Degree
btree = BTree(t)

num_operations = 10000  # Increase operations for visible trends
insert_times, search_times, delete_times = benchmark_btree_cumulative(btree, num_operations)

# Plot cumulative results
plt.figure(figsize=(12, 8))
plt.plot(range(num_operations), insert_times, label="Cumulative Insertion Time", color='blue')
plt.plot(range(num_operations), search_times, label="Cumulative Search Time", color='green')
plt.plot(range(num_operations), delete_times, label="Cumulative Deletion Time", color='red')
plt.xlabel("Number of Operations")
plt.ylabel("Cumulative Time (seconds)")
plt.title("B-Tree Operations Benchmark")
plt.legend()
plt.grid(True)
plt.show()
