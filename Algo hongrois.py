        
class Solverfinal_bis(Solver):

    def minimum2(self, l: list) -> int:
            m, ind = l[0], np.inf
            for k in range(len(l)):
                if m > l[k]:
                    m, ind = l[k], k
            return m

    def cellules_impaires(self):
        I = []
        for i in range(self.grid.n):
             for j in range(self.grid.m):
                if (i+j)%2 == 1: 
                    I.append((i,j))
        return I
    
    def cellules_paires(self):
        P = []
        for i in range(self.grid.n):
             for j in range(self.grid.m):
                if (i+j)%2 == 0: 
                    P.append((i,j))
        return P
    
    def convertir(self,numero):
        colonne = numero % self.grid.m
        ligne = numero // self.grid.m
        return ligne, colonne

    
    def matrice2(self):
        s = self.grid.n * self.grid.m
        M = np.full((s,s), 100, dtype=float)
        G = self.grid.all_pairs()
        for n1 in range(s):
            (i1,j1) = self.convertir(n1)
            for n2 in range(s):
                (i2,j2) = self.convertir(n2)
               
                if ((i1,j1),(i2,j2)) in G or ((i2,j2),(i1,j1)) in G:
                    
                    M[n1, n2] = self.grid.cost(((i1,j1),(i2,j2)))
                    M[n2, n1] = self.grid.cost(((i1,j1),(i2,j2)))
                if n1 == n2  :
                    if self.grid.color[i1][j1] == 4 : # ie noir
                        M[n1,n2] = 0
                        M[n2,n1] = 0
                    else :
                        M[n1,n2] = self.grid.value[i1][j1]
                        M[n2,n1] = self.grid.value[i1][j1]
                
        
        
        return M

    def matrice(self): # M[i,j] = poids de l'arête (numeroI, numeroJ)
        P = self.cellules_paires()
        I = self.cellules_impaires()
        s = max(len(P), len(I))
        M = np.full((s,s), 0, dtype=float)
        G = self.grid.all_pairs()
        
        for k in range(len(P)):
            for l in range(len(I)):
                (i1,i2) = P[k]
                (j1,j2) = I[l]
                if (P[k], I[l]) in G or (I[l], P[k]) in G : # ie arete valide
                    (i1,i2) = P[k]
                    (j1,j2) = I[l]
                    M[k,l] = self.grid.cost((P[k],I[l])) # idée : si adjacent mais pas liée -> mettre la somme, sinon = infini
                else : # ie arete non valide 
                    if abs(i1-j1) <= 1 and abs(i2-j2) <= 1 : 
                        if self.grid.color[i1][i2] == 4 : 
                            M[k,l] = self.grid.value[j1][j2]
                        if self.grid.color[j1][j2] == 4 : 
                            M[k,l] = self.grid.value[i1][i2]
                        if self.grid.color[j1][j2] == 4 and self.grid.color[i1][i2] == 4 : 
                            M[k,l] = 0
                        else : 
                            M[k,l] = self.grid.value[i1][i2] + self.grid.value[j1][j2]
                    else : 
                        M[k,l] = np.inf
        # comparer les algos entre eux
        
        #for i in range(len(P)):
            #(i1,j1) = P[i]
            #M[i,s] = self.grid.value[i1][j1]
         
        return M

    
    def initialisation(self,M):
        s = M.shape[0]
        min_ligne = [self.minimum2(M[i, :]) for i in range(s)]
        for i in range(s):
            if min_ligne[i]<1000:
                M[i, :] -= min_ligne[i]
        
        min_colonne = [self.minimum2(M[:, j]) for j in range(s)]
        for j in range(s):
            if min_colonne[j]<1000:
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
        m, i = 1000,-1
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




   
    def run(self):
            M = self.matrice()
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
            

            return  self.valeur_affectation(M, cellule_encadree), M_work
            



                
                            
                            
            

