from grid import Grid
from solver_version_finale import *
import time

data_path = "./input/"
file_name = data_path + "grid03.in" 

g = Grid.grid_from_file(file_name,read_values=True)
# #print(g)
# g.plot()


# sg = SolverGreedy(g)
# sg.run()
# #print((sg.pairs))
# print("The score of the Greedy Solver is : ", sg.score()) # For the grid4, the score of this methode is higher than the score of the Bipart Solver. In fact, the Greedy solver is only locally optimal (at each step, the least expensive pair is chosen) but not globally optimal.

# sb = SolverBipart(g)
# sb.run()
# #print((sb.pairs))
# print("The score of the Bipart Solver is : ", sb.score())

# sf = Solverfinal_bis(g)
# sf.run()
# #print((sf.pairs))
# print("The score of the final Solver is : ", sf.score())

    # sp = SolverScipy(g)
    # sp.run()
    # print((sp.pairs))
    # print("The score of the final Solver is : ", sp.score())
    # g.plot()

all_grid_index = ["00","01","02","03","04","05","11","12","13","14","15","16","17","18","19"]#,"21","22","23","24","25","26","27","28","29"]


for grid_index in all_grid_index:
    start_time = time.time()
    file_name = data_path + "grid" + grid_index + ".in"
    g = Grid.grid_from_file(file_name, read_values=True)
    sp = SolverHongrois(g)
    sp.run()
    end_time = time.time()
    print(f"temps d'executition de la grid {grid_index} est : {end_time - start_time:.2f} seconds")
