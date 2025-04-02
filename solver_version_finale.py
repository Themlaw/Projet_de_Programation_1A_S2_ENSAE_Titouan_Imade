from grid import Grid
from copy import deepcopy 
import matplotlib.pyplot as plt
import numpy as np
from math import inf
from scipy.optimize import linear_sum_assignment
from collections import deque



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

    def score(self) -> int: # We want to minimize the score
        """
        Computes of the list of pairs in self.pairs
        """
        score = 0
        color_grid = deepcopy(self.grid.color)
        
        for pair in self.pairs:
            # We add to the score the cost of each pair
            score += self.grid.cost(pair) 
            # Each cell already counted is colored in black
            color_grid[pair[0][0]][pair[0][1]] = 4 
            color_grid[pair[1][0]][pair[1][1]] = 4
        
        for i in range(self.grid.n): 
            for j in range(self.grid.m):
                if color_grid[i][j] != 4:
                    score += self.grid.value[i][j]
                     # We add the individual value of each cell that is not black/already counted
        
        return score
     

class SolverEmpty(Solver):
    """ 
    An empty solver that does nothing 
    """
    def run(self):
        """
        A placeholder method for an empty solver, does nothing.
        """
        pass



class SolverGreedy(Solver):
    """
    A solver class implementing the Greedy algorithm for solving the assignment problem.

    The algorithm iteratively selects the least expensive pair at each step and adds it to the solution.
    The goal is to minimize the total cost by choosing the least costly pair among the available ones.

    Attributes
    ----------
    grid : Grid
        The grid object containing the value and color data.
    pairs : list of tuple
        A list of pairs of cells representing the solution.

    Methods
    -------
    remove(pair : tuple, p : list) -> list
        Removes the specified pair from the list `p`.
    
    index_min(l : list) -> int
        Returns the index of the minimum element in the list `l`.
    
    run() -> None
        Solves the assignment problem using the greedy algorithm by iteratively selecting the least expensive pair.
    """
    def remove(self, pair : tuple, p : list) -> list: # removes the element pair in the list p 
        """
        Removes the element pair in the list p.

        Parameters
        ----------
        pair : tuple
            A tuple of two tuples representing a pair.
        p : list of tuple
            List of pairs.

        Returns
        -------
        list of tuple
            The updated list of pairs after removing the given pair.
        """
        l = []
        (a1,a2) = pair
        for (b1,b2) in p: 
            if b1 != a1 and b1 != a2 and b2 != a1 and b2 != a2:
                l.append((b1,b2))
        return l

    def index_min(self, l : list) -> int: # returns the index of the minimum of l 
        """
        Returns the index of the minimum of l.

        Parameters
        ----------
        l : list of int
            List of integer values.

        Returns
        -------
        int
            Index of the minimum element in l.
        """
        if l == []:
            return (0,0)
        m,ind=l[0],0
        for k in range(len(l)):
            if m>l[k]:
                m, ind = l[k], k
        return ind
    

    def run(self): # solves the grid using the greedy method : at each step, the least expensive pair is chosen 
        """
        Solves the grid using the greedy method: at each step, the least expensive pair is chosen.

        This method iteratively finds and removes the least costly pair from the list of all pairs.
        """
        sol = []
        G = self.grid.all_pairs()
        d = {}
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                d[(i,j)] = False
                 
        # Iterative version
        while G:
            l = [self.grid.cost(pair) for pair in G]
            ind = self.index_min(l) # get index of minimum cost
            pair = G[ind]           # get pair with minimum cost
            d[pair[0]] = True
            d[pair[1]] = True
            sol.append(pair)
            G = self.remove(pair, G) # remove pair and its connected edges
            
        self.pairs = sol

    



class SolverBipart(Solver):
    """
    A solver class implementing the Bipartite Matching algorithm.

    This algorithm finds the maximum matching in a bipartite graph using augmenting paths.
    The graph is represented by pairs of cells in a grid, and the algorithm attempts to match 
    cells from one set (even-indexed cells) to another set (odd-indexed cells).

    Attributes
    ----------
    grid : Grid
        The grid object containing the value and color data.
    paires : list of tuple
        A list of all possible pairs of cells in the grid.
    
    Methods
    -------
    is_even(pair : tuple) -> bool
        Returns True if the sum of the pair's indices is even, False otherwise.
    
    adjacency_dictionary(p : list) -> dict
        Builds and returns an adjacency dictionary for the given list of pairs.
    
    is_free(vertex : tuple, dC : dict) -> bool
        Returns True if the vertex is free (not part of a matching), otherwise returns False.
    
    extended_graph(C : list, G : list) -> dict
        Returns an extended graph used to find augmenting paths in the matching process.
    
    exists_path(G : dict, s : int, p : int, visited : list, path : list) -> list
        Searches for a path from source `s` to sink `p` in the graph `G`.
    
    rev(l : list) -> list
        Reverses the order of the elements in the given list.
    
    edges(path : list) -> list
        Returns the edges that compose the given path.
    
    augmenting_path(C : list, G : list) -> tuple
        Finds and returns an augmenting path in the extended graph.
    
    symmetric_difference(path : list, C : list) -> list
        Returns the symmetric difference between the path and the current matching `C`.
    
    run() -> None
        Solves the bipartite matching problem by iteratively finding augmenting paths and updating the matching.
    """
    def is_even(self, pair : tuple) -> bool: # returns True if pair[0] + pair[1] is even or, otherwise, returns False 
        """
        Returns True if pair[0] + pair[1] is even, otherwise returns False.

        Parameters
        ----------
        pair : tuple
            A tuple of two integers.

        Returns
        -------
        bool
            True if the sum of pair elements is even, False otherwise.
        """
        return (  (pair[0] + pair[1]) %2  == 0 )
    
    def adjacency_dictionary(self, p : list) -> dict: # Builds the adjacency dictionary of p
        """
        Builds the adjacency dictionary of p.

        Parameters
        ----------
        p : list of tuple
            A list of pairs.

        Returns
        -------
        dict
            A dictionary where keys are pairs and values are lists of adjacent pairs.
        """
        # d[(i,j)] = list of neighbours of the cell (i,j)
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
        """
        Returns True if the vertex is out of C, otherwise returns False.

        Parameters
        ----------
        vertex : tuple
            A tuple representing a vertex.
        dC : dict
            A dictionary containing pairs as keys and their neighbours as values.

        Returns
        -------
        bool
            True if the vertex is free, False otherwise.
        """
        return dC.get(vertex,[]) == []
    
    def extended_graph(self, C : list, G : list) -> dict:# returns an extended graph of G in order to find an augmenting path
        """
        Returns an extended graph of G in order to find an augmenting path.

        Parameters
        ----------
        C : list of tuple
            A list of pairs.
        G : list of tuple
            A list of all pairs.

        Returns
        -------
        dict
            The extended graph represented as an adjacency dictionary.
        """
        dC = self.adjacency_dictionary(C)
        s, p = -inf, inf
        dgc = {} 
        for i in range(self.grid.n):
             for j in range(self.grid.m):
                  dgc[(i,j)] = [] #initialisation
        dgc[s] = []
        dgc[p] = []
        for (vertex1, vertex2) in G: 
            if self.is_free(vertex1,dC) and self.is_even(vertex1): # if vertex1 is free and even then an edge is created from s to vertex1
                    dgc[s].append(vertex1)

            if self.is_free(vertex2,dC) and self.is_even(vertex2): # same for vertex2
                    dgc[s].append(vertex2)

            if self.is_free(vertex1,dC) and not(self.is_even(vertex1)): # if vertex1 is free and odd then an edge is created from vertex1 to p
                        dgc[vertex1].append(p)

            if self.is_free(vertex2,dC) and not(self.is_even(vertex2)):  # same for vertex2
                        dgc[vertex2].append(p)
            
        for (vertex1, vertex2) in C:        # edges in C 
            if self.is_even(vertex1):        # if vertex1 is even then vertex2 is odd 
                dgc[vertex2].append(vertex1) # then, because we are in C, edges which links an even vertex and an odd vertex are oriented from odd to even 

            else:                            # same if vertex1 is odd
                dgc[vertex1].append(vertex2) 
        
        for (vertex1,vertex2) in G: 
            if (vertex1,vertex2) not in C:      # edges in G but not in C
                if self.is_even(vertex1):  
                    dgc[vertex1].append(vertex2) # because we are not in C, edges are oriented from even to odd

                else:                           # same if vertex1 is odd
                    dgc[vertex2].append(vertex1)
        return dgc                               # dgc is an adjacency dictionary which contains oriented edges and two new vertices (s and p)

    def rev(self, l : list) -> list: # reverses l 
        """
        Reverses the list l.

        Parameters
        ----------
        l : list
            A list to be reversed.

        Returns
        -------
        list
            The reversed list.
        """ 
        L = []
        for k in range(len(l)):
            L.append(l[len(l)-1-k])
        return L
        
    def exists_path(self, G: dict, s: int, p: int, visited: list, path :list): # Returns a path from s to p if it exists, otherwise, returns None
        """
        Returns a path from s to p if it exists, otherwise returns None.

        Parameters
        ----------
        G : dict
            The graph represented as an adjacency dictionary.
        s : int
            The source node.
        p : int
            The sink node.
        visited : list
            List of visited nodes.
        path : list
            The current path.

        Returns
        -------
        list
            A list representing the path from s to p, or an empty list if no path exists.
        """
        queue = deque([s])
        visited = {s: None}
        while queue:
            u = queue.popleft()
            if u in G: # listes des sommets adj
                for v in G[u]: 
                    if v not in visited:
                        visited[v] = u
                        queue.append(v)
                        if v == p: 
                            path = []
                            while v != None:
                                path.append(v) 
                                v = visited[v]
                            return list(self.rev(path))
        return []
        
    

    def edges(self, path : list) -> list: # returns the edges which compose the path
        """
        Returns the edges which compose the path.

        Parameters
        ----------
        path : list
            A list of nodes.

        Returns
        -------
        list of tuple
            A list of edges as tuples (node1, node2).
        """
        L = []
        for k in range(len(path)-1):
            L.append((path[k], path[k+1]))
        return L

    def augmenting_path(self, C : list, G : list) -> tuple[bool, list]: # returns an augmenting_path using the extended graph and its path from s (source) to p (sink)
        """
        Returns an augmenting path using the extended graph.

        Parameters
        ----------
        C : list of tuple
            A list of pairs.
        G : list of tuple
            A list of all pairs.

        Returns
        -------
        tuple
            A tuple where the first element is a boolean indicating if a path exists,
            and the second element is the path (list).
        """
        dgc = self.extended_graph(C, G)
        return self.exists_path(dgc, -inf, inf, [], [])
    
    def symmetric_difference(self, path : list, C : list) -> list : # returns the symmetric difference of path and C which contains the elements that are not shared
        """
        Returns the symmetric difference of path and C, which contains the elements that are not shared.

        Parameters
        ----------
        path : list
            A list of edges in the path.
        C : list of tuple
            A list of pairs.

        Returns
        -------
        list of tuple
            The symmetric difference of path and C.
        """
        nC = []
        A = self.edges(path)
        B = C
        for edge in A : # we are looking for edges which are in the path but not in C
            (s1,s2) = edge
            if (s1,s2) not in B and (s2,s1) not in B:
                nC.append(edge)
               
        for edge in B: # we are looking for edges which are in C but not in the path
            (s1,s2) = edge
            if edge not in A and (s2,s1) not in A:
                nC.append(edge)
        return nC


    def run(self): # Solves the grid using the maximum matching problem approach
        """
        Solves the grid using the maximum matching problem approach.

        This method iteratively finds augmenting paths and updates the current matching until no more augmenting paths are found.
        """
        G = self.grid.all_pairs()
        C = []
        pa = self.augmenting_path(C,G)
        while pa != [] : # Stops when self.augmenting_path(C,G) is None ie no more paths have been found in the extended graph
            ch = (pa)[1:-1] # If a path exists in the extended graph, we use "[1:-1]" to remove the source and the sink from the actual path in G
            C = self.symmetric_difference(ch, C)
            pa =  self.augmenting_path(C,G)  # then the new matching consists of elements which were in the previous matching but not in the path, or elements which were in the path but not in the previous matching. According to the extended graph definition, the cardinality of the new matching is higher than that of the previous one.  
        self.pairs = C
            
class SolverHungarian(Solver):
    """
    A solver class implementing the Hungarian algorithm for solving the assignment problem.

    Attributes
    ----------
    valeurs : ndarray
        The grid of values.
    couleurs : ndarray
        The grid of colors.
    cases_paires : list of tuple
        List of coordinates for the even cells (i + j) % 2 == 0.
    cases_impaires : list of tuple
        List of coordinates for the odd cells (i + j) % 2 == 1.
    paires : list of tuple
        All pairs of cells in the grid.
    matrice : ndarray
        The matrix representing the cost of matching even and odd cells.
    """

    def __init__(self, grid: Grid):
        """
        Initializes the solver using the Hungarian algorithm.

        Parameters
        ----------
        grid : Grid
            The grid object containing the value and color data.
        """
        super().__init__(grid)
        n = grid.n 
        m = grid.m 

        # Initialize the value and color grids from the input grid
        self.valeurs = grid.value
        self.couleurs = grid.color

        # Identify even and odd cells based on (i + j) % 2
        self.cases_paires = [(i,j) for i in range(n) for j in range(m) if (i+j)%2 == 0]
        self.cases_impaires = [(i,j) for i in range(n) for j in range(m) if (i+j)%2 == 1]

        # All pairs of cells in the grid
        self.paires = grid.all_pairs()

        # Initialize cost matrix for assignment
        y = len(self.cases_paires)
        z = len(self.cases_impaires)
        self.matrice = np.zeros([y, z])    

        # Fill the cost matrix based on the difference in values
        for ((a, b), (c, d)) in self.paires:
            if (a + b) % 2 == 0:
                g = self.valeurs[a][b]
                h = self.valeurs[c][d]
                self.matrice[self.cases_paires.index((a, b))][self.cases_impaires.index((c, d))] = abs(g - h) - g - h
            if (c + d) % 2 == 0:
                g = self.valeurs[a][b]
                h = self.valeurs[c][d]
                self.matrice[self.cases_paires.index((c, d))][self.cases_impaires.index((a, b))] = abs(g - h) - g - h

        # Shift matrix to ensure all entries are non-negative
        self.matrice = self.matrice + abs(np.min(self.matrice))

        # If there are more pairs than impairs, pad the matrix with zeros
        if y > z:
            self.matrice = np.vstack([self.matrice, np.zeros((y - z, y))])

    def initialisation(self, M):
        """
        Performs the initialization step for the Hungarian algorithm.

        Parameters
        ----------
        M : ndarray
            The matrix to be initialized by subtracting the row and column minima.
        """
        # Subtract the minimum value of each row from all elements in that row
        row_min = np.min(M, axis=1)
        M -= row_min[:, np.newaxis]

        # Subtract the minimum value of each column from all elements in that column
        col_min = np.min(M, axis=0)
        M -= col_min

    def unslashed_zero(self, M, slashed): 
        """
        Returns a dictionary with the number of zero entries per row that are not blocked.

        Parameters
        ----------
        M : ndarray
            The cost matrix.
        slashed : dict
            A dictionary indicating blocked cells.

        Returns
        -------
        dict
            A dictionary with row indices as keys and the count of zeros as values.
        """
        s = M.shape[0]
        d = {}
        for i in range(s):
            n = 0
            b = False
            for j in range(s):
                if M[i, j] == 0 and (i, j) not in slashed:
                    n += 1
                    b = True
                if b:
                    d[i] = n
        return d 

    def index_min(self, d, deja_vu): 
        """
        Returns the index of the minimum value from the dictionary that has not been visited.

        Parameters
        ----------
        d : dict
            A dictionary of row indices and zero counts.
        deja_vu : list
            A list of visited row indices.

        Returns
        -------
        int
            The index of the row with the minimum zero count.
        """
        m, i = 10000, -1
        for (key, value) in d.items():
            if value < m and key not in deja_vu:
                m, i = value, key
        return i 

    def step1(self, M):
        """
        Executes the first step of the Hungarian algorithm.

        Parameters
        ----------
        M : ndarray
            The cost matrix.

        Returns
        -------
        tuple
            A tuple containing two elements:
            - encadre : dict
                A dictionary of marked cells.
            - barre : dict
                A dictionary of blocked cells.
        """
        slashed = {}
        s = M.shape[0]
        outlined = {}            
        visited = []
        a = True 
        while a:
            # Count zeros in each row and find row with minimum zeros
            l1, l2 = len(outlined), len(slashed)
            d = self.unslashed_zero(M, slashed)
            row = self.index_min(d, visited)
            visited.append(row)

            # Find the first zero in the row and outline the corresponding column
            b = False
            col = -1
            for j in range(s):
                if M[row, j] == 0 and (row, j) not in slashed and not b:
                    outlined[(row, j)] = True
                    b = True
                    col = j

            if b:
                # Mark slashed cells in the row and column
                for j in range(s):
                    if j != col and M[row, j] == 0:
                        slashed[(row, j)] = True

                for i in range(s):
                    if i != row and M[i, col] == 0:
                        slashed[(i, col)] = True

            # Continue until no more zeros are uncovered
            d = self.unslashed_zero(M, slashed)
            if self.index_min(d, visited) == -1:
                a = False

            # If no progress is made, terminate
            if len(outlined) == l1 and len(slashed) == l2:
                a = False

            # If all rows are outlined, return
            if len(outlined) == s:
                return outlined, True
                    
        return outlined, slashed

    def final_solution(self, result):
        """
        Finalizes the solution by storing the valid pairs.

        Parameters
        ----------
        result : list of tuple
            The list of valid pairs of cells.
        """
        for ((a, b), (c, d)) in result:
            if self.grid.is_valid_pair(a, b, c, d):
                self.pairs.append(((a, b), (c, d)))

    def step2(self, M):
        """
        Executes the second step of the Hungarian algorithm.

        Parameters
        ----------
        M : ndarray
            The cost matrix.

        Returns
        -------
        tuple
            A tuple containing two dictionaries:
            - ligne_marquee : dict
                A dictionary of marked rows.
            - colonne_marquee : dict
                A dictionary of marked columns.
        """
        s = M.shape[0]
        outlined, slashed = self.step1(M)
        marked_row, marked_col = {}, {}

        # Mark rows that do not have any outlined zeros
        for i in range(s):
            n = 0
            for j in range(s):
                if (i, j) in outlined:
                    n += 1
            if n == 0:
                marked_row[i] = True

        b = True
        while b:
            # Mark columns corresponding to slashed cells in marked rows
            l1, l2 = len(marked_row), len(marked_col)
            for j in range(s):
                for i in range(s):
                    if (i, j) in slashed and i in marked_row:
                        marked_col[j] = True
            if len(marked_row) == l1 and len(marked_col) == l2:
                b = False

        return marked_row, marked_col

    def step3(self, M):
        """
        Executes the third step of the Hungarian algorithm.

        Parameters
        ----------
        M : ndarray
            The cost matrix.
        """
        marked_row, marked_col = self.step2(M)
        s = M.shape[0]
        m = 100000
        for i in range(s):
            for j in range(s):
                if i in marked_row and j not in marked_col and M[i, j] < m:
                    m = M[i, j]

        # Adjust the matrix values based on the minimum value found
        for i in range(s):
            for j in range(s):
                if i in marked_row and j not in marked_col:
                    M[i, j] -= m
                if i not in marked_row and j in marked_col:
                    M[i, j] += m

    def run(self):
        """
        Solves the assignment problem using the Hungarian algorithm.

        The method performs the necessary steps to compute the optimal assignment, 
        including matrix initialization and applying the Hungarian algorithm steps iteratively.
        """
        M = np.array(self.matrice)
        M_work = np.copy(M)
        
        # Initialize the matrix
        self.initialisation(M_work)

        # Iteratively apply the Hungarian algorithm steps
        while self.step1(M_work)[1] != True:
            self.step3(M_work)

        # Extract the result from the outlined pairs
        outlined = self.step1(M_work)[0]
        pairs_list = list(outlined.keys())
        result = []

        for (i, j) in pairs_list:
            result.append(((self.cases_paires[i][0], self.cases_paires[i][1]), 
                           (self.cases_impaires[j][0], self.cases_impaires[j][1])))

        # Finalize the solution
        self.final_solution(result)



class SolverScipy(Solver):#We implement the solver using the linear_sum_assignment function from the scipy library to compare 
    """
    A solver class using the SciPy library's linear_sum_assignment function for solving the assignment problem.

    Attributes
    ----------
    valeurs : ndarray
        The grid of values.
    couleurs : ndarray
        The grid of colors.
    cases_paires : list of tuple
        List of coordinates for the even cells (i + j) % 2 == 0.
    cases_impaires : list of tuple
        List of coordinates for the odd cells (i + j) % 2 == 1.
    paires : list of tuple
        All pairs of cells in the grid.
    matrice : ndarray
        The matrix representing the cost of matching even and odd cells.
    """
    def __init__(self, grid : Grid):
        """
        Initializes the solver using the SciPy linear sum assignment.

        Parameters
        ----------
        grid : Grid
            The grid object containing the value and color data.
        """
        super().__init__(grid)
        n = grid.n 
        m = grid.m 

        self.valeurs=grid.value
        self.couleurs=grid.color

        self.cases_paires = [(i,j) for i in range(n) for j in range(m) if (i+j)%2==0]
        self.cases_impaires = [(i,j) for i in range(n) for j in range(m) if (i+j)%2==1]

        self.paires = grid.all_pairs()

        y = len(self.cases_paires)
        z = len(self.cases_impaires)
        self.matrice = np.zeros([y,z])     #plus de cases paires qu'impaires

        for ((a,b),(c,d)) in self.paires :
            if (a+b)%2==0:
                g = self.valeurs[a][b]
                h = self.valeurs[c][d]
                self.matrice[self.cases_paires.index((a,b))][self.cases_impaires.index((c,d))]=abs(g-h)-g-h
            if (c+d)%2==0:
                g = self.valeurs[a][b]
                h = self.valeurs[c][d]
                self.matrice[self.cases_paires.index((c,d))][self.cases_impaires.index((a,b))]=abs(g-h)-g-h

        self.matrice = self.matrice + abs(np.min(self.matrice))
        if y>z:
            self.matrice = np.vstack([self.matrice, np.zeros((y-z,y))])
            
    def final_solution(self,result):
        """
        Finalizes the solution by adding valid pairs to the list of pairs.

        Parameters
        ----------
        result : list of tuple
            The list of pairs that represent the solution.
        """
        for ((a,b),(c,d)) in result:
            if self.grid.is_valid_pair(a,b,c,d):
                self.pairs.append(((a,b),(c,d)))
                
    def run(self):
        """
        Solves the assignment problem using the SciPy linear_sum_assignment function.

        The method computes the optimal assignment by solving the linear sum assignment problem 
        using the scipy.optimize.linear_sum_assignment function.
        """
        M = np.array(self.matrice)
        lignes, colonnes = linear_sum_assignment(M)
        result = list([(self.cases_paires[lignes[i]],self.cases_impaires[colonnes[i]]) for i in range(len(lignes))])
        self.final_solution(result)
