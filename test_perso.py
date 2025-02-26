def dfs_paths_iteratif(graph, start):
    stack = [(start, [start])]
    chemins = []
    while stack:
        node, path = stack.pop()
        chemins.append(path)
        for neighbor in reversed(graph[node]):
            if neighbor not in path:  # éviter les cycles
                stack.append((neighbor, path + [neighbor]))
    return chemins

# Exemple de graphe
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}

chemins = dfs_paths_iteratif(graph, 'A')
for chemin in chemins:
    print(chemin)
