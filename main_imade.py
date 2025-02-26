from grid import Grid
from solver import *


data_path = "../input/"

file_name = data_path + "grid02.in"

g = Grid.grid_from_file(file_name,read_values=True)
print(g)

s = SolverGreedy(g)
print("greedyyy",s.glouton())

#print(s.score())



s2=SolverBipart(g)
#C=[((0,2),(1,2))]
#dgc=s2.graphe_augmente(C,g.all_pairs())

#print(s2.existe_chemin(dgc,-10000,10000,[],[-10000]))

g.plot()

print(s2.solution())




""""
G=s2.grid.all_pairs()

df={}

print("==========")
C=[]
ch=s2.chemin_augmentant(C,G)[1]
chemin=ch[1:-1]
print(chemin)
C=s2.difference_symetrique2(chemin,C,df)
print(C)
print("==========")

ch=s2.chemin_augmentant(C,G)[1]
chemin=ch[1:-1]
print(chemin)
C=s2.difference_symetrique2(chemin,C,df)
print(C)
print("==========")

ch=s2.chemin_augmentant(C,G)[1]
chemin=ch[1:-1]
print(chemin)
C=s2.difference_symetrique2(chemin,C,df)
print(C)
print("==========")

ch=s2.chemin_augmentant(C,G)[1]
chemin=ch[1:-1]
print(chemin)
C=s2.difference_symetrique2(chemin,C,df)
print(C)
print("==========")

ch=s2.chemin_augmentant(C,G)[1]
chemin=ch[1:-1]
print(chemin)
C=s2.difference_symetrique2(chemin,C,df)
print(C)
print("==========")

ch=s2.chemin_augmentant(C,G)[1]
chemin=ch[1:-1]
print(chemin)
C=s2.difference_symetrique2(chemin,C,df)
print(C)
print("==========")

ch=s2.chemin_augmentant(C,G)[1]
chemin=ch[1:-1]
print(chemin)
C=s2.difference_symetrique2(chemin,C,df)
print(C)
print("==========")

ch=s2.chemin_augmentant(C,G)[1]
chemin=ch[1:-1]
print(chemin)
C=s2.difference_symetrique2(chemin,C,df)
print(C)
print("==========")

ch=s2.chemin_augmentant(C,G)
print(ch)
print(df)

n=0

for i in range(4):
    for j in range(8):
        if not (i,j) in df:
            n+=1


print(n)""" #le score final




















































