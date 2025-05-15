import sys

import collections
import heapq

keys_char = [chr(i) for i in range(ord('a'), ord('z') + 1)]
doors_char = [k.upper() for k in keys_char]


def get_input():
    """Чтение данных из стандартного ввода."""
    keys = []
    doors = []
    robots = []
    data = []
    for x, line in enumerate(sys.stdin):
        data_line = []
        for y, item in enumerate(line):
            data_line.append(item)
            if item in keys_char:
                keys.append({'key': item, 'x': x, 'y': y})
            if item in doors_char:
                doors.append({'door': item, 'x': x, 'y': y})
            if item == '@':
                robots.append({'x': x, 'y': y})
        data.append(data_line)
    return data, doors, keys, robots


class Node:
    def __init__(self, x, y, symb = None):
        self.chain = []
        self.x = x
        self.y = y
        self.symb = symb

    def add_node(self, node, steps):
        self.chain.append((node, steps))
        node.chain.append((self, steps))

class Tree:

    def __init__(self, data):
        self.start = None
        self.data = data
        self.keys = []
        self.doors = []
        self.paths = dict()
        self.symb_node = dict()

    def remove_linear_nodes(self):
        all_nodes = set()
        queue = collections.deque([self.start])

        while queue:
            current = queue.popleft()
            if current in all_nodes:
                continue
            all_nodes.add(current)
            for neighbor, _ in current.chain:
                if neighbor not in all_nodes:
                    queue.append(neighbor)

        change = True
        while change:
            change = False
            for node in list(all_nodes):
                if node == self.start:
                    continue
                if len(node.chain) == 1 and not node.symb:
                    neighbor, _ = node.chain[0]
                    neighbor.chain = [(n, s) for n, s in neighbor.chain if n != node]
                    all_nodes.remove(node)
                    change = True

        for node in list(all_nodes):
            while len(node.chain) == 2 and not node.symb:
                (node1, len1), (node2, len2) = node.chain

                node1.chain = [(n, l) for n, l in node1.chain if n != node]
                node2.chain = [(n, l) for n, l in node2.chain if n != node]

                flen = len1 + len2
                node1.chain.append((node2, flen))
                node2.chain.append((node1, flen))

                all_nodes.remove(node)
                break

    def build_paths(self):
        symb_to_nodes = self.symb_node

        for key_symb in self.keys + ['@']:
            node = symb_to_nodes[key_symb]
            can_path = {}
            visited = set()
            queue = collections.deque()
            queue.append((node, 0, []))
            start_symb = node.symb

            while queue:
                node, dist, doors = queue.popleft()
                if node in visited:
                    continue
                visited.add(node)

                symb = node.symb
                if symb is not None and symb in self.keys and symb != start_symb:
                    can_path[symb] = (dist, list(doors))

                for nodes, step in node.chain:
                    new_doors = list(doors)
                    if nodes.symb is not None and nodes.symb in self.doors:
                        new_doors.append(nodes.symb)
                    queue.append((nodes, dist + step, new_doors))
            for end_symb, (length, doors) in can_path.items():
                if end_symb != key_symb:
                    self.paths[(key_symb, end_symb)] = (length, doors)
                    self.paths[(end_symb, key_symb)] = (length, list(doors))

    def draw(self, x, y):
        queue = collections.deque()
        queue.append((x, y, 0, None, 0, 0))
        visited = set()

        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]

        while queue:
            cx, cy, dist, parent, px, py = queue.popleft()

            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            def is_opposite(dx1, dy1, dx2, dy2):
                return dx1 == -dx2 and dy1 == -dy2

            now_char = self.data[cx][cy]

            if now_char in doors_char:
                self.doors.append(now_char)
            elif now_char in keys_char:
                self.keys.append(now_char)

            ways = [
                (self.data[cx + dx][cy + dy], dx, dy)
                for dx, dy in directions
                if 0 <= cx + dx < len(self.data) and 0 <= cy + dy < len(self.data[0])
            ]

            can_dir = [(dx, dy) for val, dx, dy in ways if val != '#']

            if now_char not in ['#', '.', '@']:
                new_node = Node(cx, cy, now_char)
                self.symb_node[now_char] = new_node
                parent.add_node(new_node, dist)
                for dx, dy in can_dir:
                    if not is_opposite(px, py, dx, dy):
                        queue.append((cx + dx, cy + dy, 1, new_node, dx, dy))

            elif len(can_dir) > 2:
                new_node = Node(cx, cy)
                parent.add_node(new_node, dist)
                for dx, dy in can_dir:
                    if not is_opposite(px, py, dx, dy):
                        queue.append((cx + dx, cy + dy, 1, new_node, dx, dy))

            else:
                if parent is None:
                    self.start = Node(cx, cy, '@')
                    self.symb_node['@'] = self.start
                    for dx, dy in can_dir:
                        queue.append((cx + dx, cy + dy, 1, self.start, dx, dy))
                else:
                    for dx, dy in can_dir:
                        if not is_opposite(px, py, dx, dy):
                            queue.append((cx + dx, cy + dy, dist + 1, parent, dx, dy))


def find_min_steps(trees):
    key_to_bit = {}
    bit_to_key = {}
    tree_paths = []
    starts = []

    bit = 0
    for tree in trees:
        starts.append(tree.start.symb or '@')
        tree_paths.append(tree.paths)
        for k in tree.keys:
            if k not in key_to_bit:
                key_to_bit[k] = 1 << bit
                bit_to_key[1 << bit] = k
                bit += 1

    total_keys = len(key_to_bit)
    all_keys_mask = (1 << total_keys) - 1

    queue = [(0, (tuple(starts), 0))]
    seen = {}

    while queue:
        steps, (positions, keys_mask) = heapq.heappop(queue)
        if keys_mask == all_keys_mask:
            return steps

        if (positions, keys_mask) in seen and seen[(positions, keys_mask)] <= steps:
            continue
        seen[(positions, keys_mask)] = steps

        for i, pos in enumerate(positions):
            tree_path = tree_paths[i]
            for k, bitk in key_to_bit.items():
                if keys_mask & bitk:
                    continue

                path = tree_path.get((pos, k))
                if not path:
                    continue
                dist, doors = path

                if any(d.lower() not in key_to_bit or not (keys_mask & key_to_bit[d.lower()]) for d in doors):
                    continue

                new_positions = list(positions)
                new_positions[i] = k
                new_keys_mask = keys_mask | bitk
                heapq.heappush(queue, (steps + dist, (tuple(new_positions), new_keys_mask)))

    return -1

def solve(data, robots):
    trees = []
    for i in robots:
        robot_tree = Tree(data)
        robot_tree.draw(i['x'], i['y'])
        trees.append(robot_tree)
    for i in trees:
        i.remove_linear_nodes()
        i.build_paths()
    return find_min_steps(trees)

def main():
    data, doors, keys, robots = get_input()
    result = solve(data, robots)
    print(result)

if __name__ == '__main__':
    main()
