from grid import Grid
from copy import deepcopy 
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
    def run(self):
        pass



class SolverGreedy(Solver):

    def remove(self, pair : tuple, p : list) -> list: # removes the element pair in the list p 
        l = []
        (a1,a2) = pair
        for (b1,b2) in p: 
            if b1 != a1 and b1 != a2 and b2 != a1 and b2 != a2:
                l.append((b1,b2))
        return l

    def index_min(self, l : list) -> int: # returns the index of the minimum of l 
        if l == []:
            return (0,0)
        m,ind=l[0],0
        for k in range(len(l)):
            if m>l[k]:
                m, ind = l[k], k
        return ind
    

    def run(self): # solves the grid using the greedy method : at each step, the least expensive pair is chosen 
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
                interating (self.remove(pair,G),sol) # we start again, the programm will stop because G will be empty at some point

        interating(G,[])
    


class SolverBipart(Solver):
    
    def is_even(self, pair : tuple) -> bool: # returns True if pair[0] + pair[1] is even or, otherwise, returns False 
        return (  (pair[0] + pair[1]) %2  == 0 )
    
    def adjacency_dictionary(self, p : list) -> dict: # Builds the adjacency dictionary of p
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
        return dC.get(vertex,[]) == []
    
    def extended_graph(self, C : list, G : list) -> dict:# returns an extended graph of G in order to find an augmenting path
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
   
    def exists_path(self, G: dict, s: int, p: int, visited: list, path :list): # Returns a path from s to p if it exists, otherwise, returns None
        if s == p:
            path.append(s)
            return self.rev(path)  # we have finished

        visited.append(s)
        for neighbour in G[s]:
            if neighbour not in visited:
                found = self.exists_path(G, neighbour, p, visited, path)
                if found is not None:
                    path.append(s)  # there is a path from this neighbour to p (because fond is not None) so s is added to the final path
                    return self.rev(path)  # path must be reversed because we added in the wrong sense

        return None  # no paths have been found
        
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

    def augmenting_path(self, C : list, G : list) -> tuple[bool, list]: # returns an augmenting_path using the extended graph and its path from s (source) to p (sink)
        dgc = self.extended_graph(C, G)
        return self.exists_path(dgc, -inf, inf, [], [])
    
    def symmetric_difference(self, path : list, C : list) -> list : # returns the symmetric difference of path and C which contains the elements that are not shared
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
        G = self.grid.all_pairs()
        C = []
        while self.augmenting_path(C,G) is not None : # Stops when self.augmenting_path(C,G) is None ie no more paths have been found in the extended graph
            pa = (self.augmenting_path(C,G))[1:-1] # If a path exists in the extended graph, we use "[1:-1]" to remove the source and the sink from the actual path in G
            C = self.symmetric_difference(pa, C)  # then the new matching consists of elements which were in the previous matching but not in the path, or elements which were in the path but not in the previous matching. According to the extended graph definition, the cardinality of the new matching is higher than that of the previous one.  
        self.pairs = C
        
         
        
class Solverfinal_bis(Solver):

    def __init__(self, grid : Grid):
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
            
    def minimum2(self, l: list) -> int:
            m, ind = l[0], np.inf
            for k in range(len(l)):
                if m > l[k]:
                    m, ind = l[k], k
            return m
    
    def convertir(self,numero):
        colonne = numero % self.grid.m
        ligne = numero // self.grid.m
        return ligne, colonne

    
    def initialisation(self,M):
        infini = float("inf")
        s = M.shape[0]
        min_ligne = [self.minimum2(M[i, :]) for i in range(s)]
        for i in range(s):
            if min_ligne[i]<infini:
                M[i, :] -= min_ligne[i]
        s = M.shape[1]
        min_colonne = [self.minimum2(M[:, j]) for j in range(s)]
        for j in range(s):
            if min_colonne[j]<infini:
                M[:, j] -= min_colonne[j]

    def nombre_zero_barre(self,M, barre):
            d = {}
            s = M.shape[0]
            for i in range(s):
                n = 0
                for j in range(s):
                    if M[i,j] == 0 and not barre.get((i,j), False):
                        n += 1
                d[i] = n
            return d 

    def minimu(self,d, deja_vu):
        m, i = float("inf"),-1
        for (k,v) in d.items() :
            if v < m and v>0 and k not in deja_vu:
                m, i = v, k
        return i


     

    def etape1(self,M, cellule_barre, cellule_encadree):
        s = M.shape[0]
        avance = True
        deja_vu = []
        while avance: 
            avance = False
            d = self.nombre_zero_barre(M, cellule_barre)
            ligne = self.minimu(d, deja_vu)
            deja_vu.append(ligne)
            col = None
            b = False

            for j in range(s):
                if M[ligne, j] == 0 and not b and not cellule_barre.get((ligne,j), False): # à améliore
                    cellule_encadree[(ligne,j)] = True
                    b = True
                    avance = True
                    col = j 
            if col != None:
                for j in range(s): 
                    if M[ligne,j] == 0:
                        if j != col: 
                            cellule_barre[(ligne,j)] = True
            if col != None:
                for i in range(s):
                    if M[i,col] == 0: 
                        if i != ligne:
                            avance = True
                            cellule_barre[(i,col)] = True
            d = self.nombre_zero_barre(M, cellule_barre)
            if self.minimu(d, deja_vu) == -1: 
                avance = False
        if len(cellule_encadree) == s:
            return cellule_encadree, True # ie un par ligne/colonne         
       
        return  cellule_encadree, cellule_barre

    def aucun_zero_encadre(self,M, i, cellule_encadree):
        s = M.shape[0]
        for j in range(s):
            if cellule_encadree.get((i,j), False):
                return False
        return True
    
     
      
    def etape2(self,M, cellule_encadree, cellule_barre):
        s = M.shape[0]
        ligne_croix = {}
        colonne_croix = {}
        avance = True
        r = 0
        while avance and r < 10:  
            avance = False
            for i in range(s):
                n = 0
                for j in range(s):
                    if M[i,j] == 0 and cellule_encadree.get((i,j), False):
                        n+=1
                if n == 0:
                    if not ligne_croix.get(i, False):
                        ligne_croix[i] = True # mettre croix sur ligne aucun zero encadre
                        avance = True
            for j in range(s):
                for i in range(s):
                    if ligne_croix.get(i, False) and cellule_barre.get((i,j), False):
                            if not colonne_croix.get(j, False):
                                colonne_croix[j] = True # mettre croix sur colonne où zero barre sur ligne crois
                                avance = True
            for i in range(s):
                for j in range(s):
                    if colonne_croix.get(j,False) and cellule_encadree.get((i,j), False):
                        if not ligne_croix.get(j,False):
                            ligne_croix[i] = True # mettre croix sur ligne ou zero encadre sur colonne marquee
                            avance = True
            r += 1
        return ligne_croix, colonne_croix
        


    def etape3(self, M, ligne_croix, colonne_croix):
        s = M.shape[0]
        m = 10000 
        for i in range(s): 
            for j in range(s):
                if ligne_croix.get(i, False) and not colonne_croix.get(j, False) and M[i,j] < m : # cellules non traversées par un trait, on cherche le min
                    m = M[i,j]
        #print("maaa", m)
        for i in range(s):
            for j in range(s):
                if ligne_croix.get(i,False) and not colonne_croix.get(j, False): # soustrait pour ces cases
                    M[i,j] -= m
                if not ligne_croix.get(i,False) and colonne_croix.get(j, False): #plus pour celles traversées 2 fois(ie ligne et colonne croix)
                    M[i,j] += m

    def valeur_affectation(self,M, cellule_encadree):
        s = 0
        l = []
        for (i,j) in cellule_encadree.keys(): 
            
            if (i,j) not in l and (j,i) not in l:
                s += M[i,j]
                print("s_value", s, i, j)
                l.append((i,j))
               
        return s, l


    def final_solution(self,result):
        for ((a,b),(c,d)) in result:
            if self.grid.is_valid_pair(a,b,c,d):
                self.pairs.append(((a,b),(c,d)))

   
    def run(self):
            M = np.array(self.matrice)
            
            M_work = np.copy(M)

            self.initialisation(M_work)
           
            cellule_encadree, cellule_barre = self.etape1(M_work,{},{})
            r = 0
            while self.etape1(M_work,{},{})[1] != True  :
                #print(self.etape1(M_work,{},{}))
                #print("valuestar", self.valeur_affectation(M, cellule_encadree))
                cellule_encadree, cellule_barre =  self.etape1(M_work,{},{})
                #print(cellule_encadree, cellule_barre)
                ligne_croix, colonne_croix =  self.etape2(M_work, cellule_encadree, cellule_barre)
                self.etape3(M_work, ligne_croix, colonne_croix)
                #print("len",len(cellule_encadree))
            
                #print(ligne_croix, colonne_croix)
                #print("value", self.valeur_affectation(M, cellule_encadree))
                #print(M_work)
                r += 1
            cellule_encadree, cellule_barre =  self.etape1(M_work,{},{})  
            ligne_croix, colonne_croix =  self.etape2(M_work, cellule_encadree, cellule_barre)
            self.etape3(M_work, ligne_croix, colonne_croix)
            
            pairs_list = list(cellule_encadree.keys())
            result = []
            for (i,j) in pairs_list:
                result.append(((self.cases_paires[i][0],self.cases_paires[i][1]),(self.cases_impaires[j][0],self.cases_impaires[j][1])))
            self.final_solution(result)
            
            # lignes, colonnes = linear_sum_assignment(M)
            # self.pairs = list([(self.cases_paires[lignes[i]],self.cases_impaires[colonnes[i]]) for i in range(len(lignes))])
            # print(s.score2())