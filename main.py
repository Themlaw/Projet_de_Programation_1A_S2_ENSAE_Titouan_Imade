from grid import Grid
from solver import *

data_path = "../input/"
file_name = data_path + "grid11.in" 

g = Grid.grid_from_file(file_name,read_values=True)
#print(g)
#g.plot()


sg = SolverGreedy(g)
sg.run()
#print((sg.pairs))
print("The score of the Greedy Solver is : ", sg.score()) # For the grid4, the score of this methode is higher than the score of the Bipart Solver. In fact, the Greedy solver is only locally optimal (at each step, the least expensive pair is chosen) but not globally optimal.

sb = SolverBipart(g)
sb.run()
#print((sb.pairs))
print("The score of the Bipart Solver is : ", sb.score())

#g.plot()

sf = SolverHungarian(g)
sf.run()
#print((sf.pairs))
print("The score of the Hungarian Solver is : ", sf.score()) 

s = SolverScipy(g)
s.run()
print("The score of the Scipy Solver is : ",s.score())
