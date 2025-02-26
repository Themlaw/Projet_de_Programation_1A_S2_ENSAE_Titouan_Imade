import itertools
from grid import Grid
from copy import deepcopy 
import networkx as nx
from networkx.algorithms import bipartite
import matplotlib.pyplot as plt
import numpy as np
from math import inf


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

def remove(pair : tuple, p : list) -> list: # removes the element pair in the list p 
    l = []
    (a1,a2) = pair
    for (b1,b2) in p: 
        if b1 != a1 and b1 != a2 and b2 != a1 and b2 != a2:
            l.append((b1,b2))
    return l




def index_min(l : list) -> int: # returns the index of the minimum of l 
        if l == []:
            return (0,0)
        m,ind=l[0],0
        for k in range(len(l)):
            if m>l[k]:
                m, ind = l[k], k
        return ind


class SolverGreedy(Solver):

    def index_min(self, l : list) -> int: # returns the index of the minimum of l 
        if l == []:
            return (0,0)
        m,ind=l[0],0
        for k in range(len(l)):
            if m>l[k]:
                m, ind = l[k], k
        return ind
    

    def run(self) -> list: # solves the grid with the greedy method : in each step, the less expensive pair is chosen 
        sol = []
        #self.pairs = self.grid.all_pairs()
        G = self.grid.all_pairs()
        #p = self.pairs
        d = {}
        for i in range(self.grid.n):
                    for j in range(self.grid.m):
                         d[(i,j)] = False
                 
        def interating(G, sol): # Iterates over a list
            if G == []: 
                self.pairs = sol
            if G != []:
                l = [self.grid.cost(pair) for pair in G] 
                ind = self.index_min(l) # thus, l[ind] is the minimum of l 
                pair = G[ind]           # thus, pair is the less expensive edge
                d[pair[0]] = True
                d[pair[1]] = True
                sol.append(pair)
                interating (remove(pair,G),sol) # we start again, the programm will stop because G will be empty at some point

        interating(G,[])
    

class SolverBipart(Solver):
    
    def is_even(self, pair : tuple) ->bool: # returns True if pair[0] + pair[1] is even or, otherwise, returns False 
        return (  (pair[0] + pair[1]) %2  == 0 )
    
    def adjacency_dictionnary(self, p : list) -> dict: #builds the adjacency dictionnary of p
        #d[(i,j)] = liste des sommets liés à (i,j)
        d = {}
        for (p1,p2) in p: 
            i1, j1 = p1[0], p1[1]
            i2, j2 = p2[0], p2[1]
            d[(i1,j1)] = []
            d[(i2,j2)] = []
        for (p1,p2) in p: 
            i1, j1 = p1[0], p1[1]
            i2, j2 = p2[0], p2[1]
            d[(i1,j1)].append((i2,j2))
            d[(i2,j2)].append((i1,j1))
        return d 
    
    def is_free(self, vertex : tuple, dC : dict) -> bool: # returns True if the vertex is out of C or, otherwise, returns False
        return dC.get(vertex,[]) == []
    
    def extended_graph(self, C : list, G : list) -> dict: # returns an extended graph of G in order to find an augmenting path
        dC = self.adjacency_dictionnary(C)
        s, p = -inf, inf
        d = self.adjacency_dictionnary(G)
        dgc = {} 
        for i in range(self.grid.n):
             for j in range(self.grid.m):
                  dgc[(i,j)] = [] #initialisation
        dgc[s] = []
        dgc[p] = []
        
        for (vertex1, vertex2) in G: 
            (i1,j1) = vertex1
            (i2,j2) = vertex2
            if self.is_free(vertex1,dC) and self.is_even(vertex1): # if vertex1 is free and even then an edge is created from s to vertex1
                dgc[s].append(vertex1)

            if self.is_free(vertex2,dC) and self.is_even(vertex2): # same as vertex1 for vertex2
                dgc[s].append(vertex2)

            elif self.is_free(vertex1,dC) and not(self.is_even(vertex1)): # if vertex1 is free and odd then an edge is created from vertex1 to p
                    dgc[vertex1].append(p)

            elif self.is_free(vertex2,dC) and not(self.is_even(vertex2)):  # same as vertex1 for vertex2
                    dgc[vertex2].append(p)
            
        for (vertex1, vertex2) in C: # edges in C
            (i1,j1) = vertex1
            (i2,j2) = vertex2
            if self.is_even(vertex1):        # if vertex1 is even then vertex2 is odd 
                dgc[vertex2].append(vertex1) # then, because we are in C, edges which links an even vertex and an odd vertex are oriented from odd to even 
            else:                            # same if vertex1 is odd
                dgc[vertex1].append(vertex2) 
        
        for (vertex1,vertex2) in G: 
            if (vertex1,vertex2) not in C: # edges in G but not in C
                if self.is_even(vertex1):  
                    dgc[vertex1].append(vertex2) # because we are not in C, edges are oriented from even to odd
                else:                           # same if vertex1 is odd
                    dgc[vertex2].append(vertex1)
        return dgc # dgc is an adjacency dictionnary which contains oriented edges and two new vertices (s and p)
    
    

    def exists_path(self, G: dict, s: int, p: int, visited: list, path: list) -> tuple[bool, list]: # returns a path from s to p in G if it exists or, otherwise, returns False
        if s == p: 
            path.append(s)
            return True # if s = p, the path [s] is right
        visited.append(s)
        for neighbour in G[s]:
            if neighbour not in visited:
                if self.exists_path(G, neighbour, p, visited, path): 
                    path.append(s)  # if there is a path from this neighbour to p, s is added to the final path
                    return True, self.rev(path) # path must be reversed because we added in the wrong sense 

        return False  # no paths have been found
    
    def rev(self, l : list) -> list: # reverses l  
        L = []
        for k in range(len(l)):
            L.append(l[len(l)-1-k])
        return L

    def edges(self, path : list) -> list: # returns the edges which compose the path
        L = []
        for k in range(len(path)-1):
            L.append((path[k], path[k+1]))
        return L

    def augmenting_path(self, C : list, G : list) -> tuple[bool, list]: # returns an augmenting_path thanks to the extented graph and its path from s (source) to p (sink)
        dgc = self.extended_graph(C, G)
        return self.exists_path(dgc, -inf, inf,[],[])
    
    def symmetric_difference(self, path : list, C : list, df : dict) -> list : # returns the symmetric difference of path and C which contains the elements that are not shared
        nC = []
        A = self.edges(path)
        B = C
        for edge in A : # we are looking for edges which are in the path but not in C
            (s1,s2) = edge
            if (s1,s2) not in B and (s2,s1) not in B:
                nC.append(edge)
                df[s1] = True
                df[s2] = True

        for edge in B: # we are looking for edges which are in C but not in the path
            (s1,s2) = edge
            if edge not in A and (s2,s1) not in A:
                nC.append(edge)
                df[s1] = True
                df[s2] = True
        return nC


    def run(self) -> tuple[list, int]: # returns the solution of the grid using a maximum matching 
        G = self.grid.all_pairs()
        C = []
        df = {} # this dictionnary allows us to directly know which vertices are linked, so we do not have to iterate over the solution to see if the vertex (i,j) is in it. 
        pa = self.rev((self.augmenting_path(C,G)[1]))
        
        while self.augmenting_path(C,G): # stops when self.augmenting_path(C,G) = False ie no paths have been found in the extended graph
            
            pa = self.rev((self.augmenting_path(C,G)[1]))
            path = pa[1:-1] # the source and the sink are removed from the real path in G
            C = self.symmetric_difference(path, C, df) #

        n = 0 # we are adding vertices which are not linked
        self.pairs = C
         
        
