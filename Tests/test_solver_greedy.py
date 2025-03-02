import sys 
sys.path.append("code/")

import unittest 
from grid import Grid
from solver import *

class Test_SolverGreedy(unittest.TestCase):
    def test_greedy_basic_function(self): # just to check the basic fontions
        grid = Grid.grid_from_file("input/grid00.in",read_values=True) 
        s = SolverGreedy(grid)

        l1 = [12, 14, 5, 23, 82, 1, 7]
        self.assertEqual(s.index_min(l1), 5)#Test the index_min function in solver greedy

        l2 = [(1,2), (3,4), (5,6)]
        L2 = [(3,4), (5,6)]
        self.assertEqual(s.remove((1,2),l2), L2) #Test the remove function in solver greedy
    
    def test_greedy_run(self): #Test if the programm runs without errors
        grid = Grid.grid_from_file("input/grid00.in",read_values=True) 
        s = SolverGreedy(grid)
        try:
            s.run()
        except Exception as e:
            self.fail(f"s.run() raised an exception: {e}")
        
        

if __name__ == '__main__':
    unittest.main()
