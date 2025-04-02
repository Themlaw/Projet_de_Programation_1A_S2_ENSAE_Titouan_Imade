from grid import Grid
from solver import *
import time
import numpy as np

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
#We test all grid with scipy 
# for grid_index in all_grid_index:
#     file_name = data_path + "grid"+grid_index+".in" 
#     g = Grid.grid_from_file(file_name,read_values=True)
#     sp = SolverGreedy(g)
#     sp.run()
#     print(grid_index)
#     print("The score of the final Solver for grid"+grid_index+" is : ", sp.score())
    


import matplotlib.pyplot as plt

avg_run_times = []
avg_scores = []

for grid_index in all_grid_index:
    file_name = data_path + "grid"+grid_index+".in" 
    g = Grid.grid_from_file(file_name,read_values=True)
    
    grid_times = []
    grid_scores = []
    
    for _ in range(10):  # Run 10 times for each grid
        start_time = time.time()
        sp = SolverGreedy(g)
        sp.run()
        end_time = time.time()
        
        grid_times.append((end_time - start_time) * 1000)  # Convert to milliseconds
        grid_scores.append(sp.score())
    
    avg_run_times.append(np.mean(grid_times))
    avg_scores.append(np.mean(grid_scores))

plt.figure(figsize=(10, 6))
plt.plot(all_grid_index, avg_run_times, 'b-o')
plt.xlabel('Grid Index')
plt.ylabel('Average Running Time (milliseconds)')
plt.title('SolverGreedy Average Running Time per Grid (10 runs)')
plt.xticks(rotation=45)
plt.grid(True)
plt.show()
