import itertools
from grid import Grid
from copy import deepcopy 
import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
import numpy as np


class Solver:
    """
    A solver class. 

    Attributes: 
    -----------
    grid: Grid
        The grid
    pairs: list[tuple[tuple[int]]]
        A list of pairs, each being a tuple ((i1, j1), (i2, j2))
    """

    def __init__(self, grid):
        """
        Initializes the solver.

        Parameters: 
        -----------
        grid: Grid
            The grid
        """
        self.grid = grid
        self.pairs = list()

    def score(self):#We want to minimize the score
        """
        Computes of the list of pairs in self.pairs
        """
        score = 0
        color_grid = deepcopy(self.grid.color)
        for pair in self.pairs:
            #We add to the score the cost of each pair
            score += self.grid.cost(pair) 
            #Each cell already counted is colored in black
            color_grid[pair[0][0]][pair[0][1]] = 4 
            color_grid[pair[1][0]][pair[1][1]] = 4
        for i in range(self.grid.n): 
            for j in range(self.grid.m):
                if color_grid[i][j] != 4:
                    score += self.grid.value[i][j] #We add the individual value of each cell that is not black/already counted
        
        return score

class SolverEmpty(Solver):
    def run(self):
        pass


class SolverGreedy(Solver): #Idea : test all the possibilities and choose the best one
    def is_list_valid(self, list_of_pairs):#Checks if the list of pairs is valid
        color_grid = deepcopy(self.grid.color)
        for pair in list_of_pairs:
            if color_grid[pair[0][0]][pair[0][1]] == 4 or color_grid[pair[1][0]][pair[1][1]] == 4:
                return False #If one of the cell is black then the list is not valid
            #We color the cells in black to check for duplicate
            color_grid[pair[0][0]][pair[0][1]] = 4 
            color_grid[pair[1][0]][pair[1][1]] = 4
        return True #True if all the pair are valid
    
    def run(self):
        #We store all the possible combinations of pairs 
        all_pairs = self.grid.all_pairs()
        all_subsets =  [] 
        for i in range(len(all_pairs) + 1):
            for combination in itertools.combinations(all_pairs, i):
                list_of_pairs = list(combination)
                if self.is_list_valid(list_of_pairs):
                    all_subsets.append(list_of_pairs)
                    
        best_score = float('inf') #Ensure the best_subset is not None except if there is no valid subset
        best_subset = None

        #We check all valid sublist and keep the one with the lowest score
        for subset in all_subsets:
            self.pairs = subset
            current_score = self.score()
            if current_score < best_score:
                best_score = current_score
                best_subset = subset

        self.pairs = best_subset

class SolverFromHighest(Solver): #Idea : start with the highest value to minimize their impact on the score
    def run(self):
        # Get all positions sorted by value
        positions = []
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                if self.grid.color[i][j] != 4:
                    positions.append((i, j))
        positions.sort(key=lambda pos: self.grid.value[pos[0]][pos[1]], reverse=True)
        
        used = set()# Keep track of used cells
        for i, j in positions:
            if (i, j) in used:
                continue
                
            # Check adjacent cells (right, left, above, under)
            neighbors = []
            if j+1 < self.grid.m and (i, j+1) not in used and self.grid.color[i][j+1] != 4:
                neighbors.append((i, j+1))
            if j-1 >= 0 and (i, j-1) not in used and self.grid.color[i][j-1] != 4:
                neighbors.append((i, j-1))
            if i+1 < self.grid.n and (i+1, j) not in used and self.grid.color[i+1][j] != 4:
                neighbors.append((i+1, j))
            if i-1 >= 0 and (i-1, j) not in used and self.grid.color[i-1][j] != 4:
                neighbors.append((i-1, j))
                
            if neighbors:
                neighbors.sort(key=lambda pos: self.grid.value[pos[0]][pos[1]], reverse=True) # Sort neighbors by value and pick highest
                best_neighbor = neighbors[0]
                self.pairs.append(((i, j), best_neighbor))
                used.add((i, j))
                used.add(best_neighbor)


class SolverWithGraph(Solver):
    def __repr__(self): 
        
        all_pairs = set(self.grid.all_pairs())
        all_edge = []
        G = nx.Graph()
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                if (i+j)%2==0:
                    G.add_node((i,j), bipartite=0)
                else:
                    G.add_node((i,j), bipartite=1)
                all_edge.append((i,j))
        
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                if ((i,j),(i,j+1)) in all_pairs or ((i,j+1),(i,j)) in all_pairs:
                    G.add_edge((i,j),(i,j+1))
                if ((i,j),(i+1,j)) in all_pairs or ((i,j),(i+1,j)) in all_pairs:
                    G.add_edge((i,j),(i+1,j))
   
        pos = nx.spring_layout(G)  # compute node positions
        pos[(0,0)] = np.array([0, 2])  # fix position of (0,0) to upper right
        pos = nx.spring_layout(G, pos=pos, fixed=[(0,0)])  # recompute layout with fixed position
        nx.draw(G, pos=pos, with_labels=True, node_color='lightblue', 
               node_size=500, font_size=8)
        edge_labels = {(u, v): f"({u[0]},{u[1]})-({v[0]},{v[1]})" for u, v in G.edges()}
        nx.draw_networkx_edge_labels(G, pos=pos, font_size=6, label_pos=0.3, edge_labels=edge_labels)
        plt.show()


    def gridToGraph(self):
        list_weights = self.grid.value
        all_pairs = set(self.grid.all_pairs())
        G = {}
        G["s"] ={(i,j) : list_weights[i][j] for i in range(self.grid.n) for j in range(self.grid.m) if (i+j)%2==0}
        G["p"] = {(i,j) : list_weights[i][j] for i in range(self.grid.n) for j in range(self.grid.m) if (i+j)%2==1}
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                G[(i,j)] = {}
                if ((i,j),(i,j+1)) in all_pairs or ((i,j+1),(i,j)) in all_pairs:
                    G[(i,j)][(i,j+1)] = list_weights[i][j+1]
                if ((i,j),(i+1,j)) in all_pairs or ((i+1,j),(i,j)) in all_pairs:
                    G[(i,j)][(i+1,j)] = list_weights[i+1][j]
                if ((i,j),(i,j-1)) in all_pairs or ((i,j-1),(i,j)) in all_pairs:
                    G[(i,j)][(i,j-1)] = list_weights[i][j-1]
                if ((i,j),(i-1,j)) in all_pairs or ((i-1,j),(i,j)) in all_pairs:
                    G[(i,j)][(i-1,j)] = list_weights[i-1][j]

                if (i+j)%2==0:
                    G[(i,j)]["s"] = list_weights[i][j]
                if (i+j)%2==1:
                    G[(i,j)]["p"] = list_weights[i][j]
        return G

    def ford_fulkerson(self):
        #Creation of the residual graph
        G = self.gridTsoGraph()
        residual = {}
        residual["s"] = G["s"].copy()
        residual["p"] = {} #Nothing go after endpoint
        for node in G:
            if node not in ["s", "p"]:
                residual[node] = G[node].copy()

        # DFS to find an augmenting path 
        def dfs(u, t, visited, path):
            if u == t:
                return path
            for v, capacity in residual[u].items():
                if capacity > 0 and v not in visited:
                    visited.add(v)
                    res = dfs(v, t, visited, path + [(u, v)])
                    if res is not None:
                        return res
            return None

        max_flow = 0
        path = True
        solution = []
        while path is not None:#There is a finite number of path
            path = dfs("s", "p", set(["s"]), [])
            if path is not None:
                flow = min(residual[u][v] for u, v in path)
                max_flow += flow
                for u, v in path:
                    residual[u][v] -= flow
                    if v not in residual:
                        residual[v] = {}
                    if u not in residual[v]:
                        residual[v][u] = 0
                    residual[v][u] += flow
                    if type(u)==tuple and type(v)==tuple:#If both are real node
                        solution.append((u,v))
        return max_flow,solution

    def run(self):
        max_flow,solution = self.ford_fulkerson()
        return(solution)            
      


grid = Grid.grid_from_file("input\\grid00.in", read_values=False)
solvergraph = SolverWithGraph(grid)
print(solvergraph.run())
        


# grid = Grid.grid_from_file("input\\grid01.in",read_values=True)
# solvergreedy = SolverGreedy(grid)
# solvergreedy.run()
# print(solvergreedy.score(),solvergreedy.pairs)
# solverfromhighest = SolverFromHighest(grid)
# solverfromhighest.run()
# print(solverfromhighest.score(),solverfromhighest.pairs)
# print(grid)
