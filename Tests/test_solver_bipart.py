import sys 
sys.path.append("code/")

import unittest 
from grid import Grid
from solver import *

class Test_SolverGreedy(unittest.TestCase):
    def test_basic_function(self): # just to check the basic fontions
        grid = Grid.grid_from_file("input/grid01.in",read_values=True) 

        self.assertEqual(grid.is_forbidden(0,1), True)
        self.assertEqual(grid.is_forbidden(0,0), False)

        s = SolverBipart(grid)
        self.assertEqual(s.is_even((0,0)), True)
        self.assertEqual(s.is_even((0,1)), False)

        C = [((0,2),(1,2))]
        self.assertEqual(s.is_free((0,2), s.adjacency_dictionary(C)) , False)
        self.assertEqual(s.is_free((0,1), s.adjacency_dictionary(C)) , True)

        l = [1, 2, 3, 4]
        lrev = [4, 3, 2, 1]
        self.assertEqual(s.rev(l), lrev)

        path = [1, 2, 3]
        edges = [(1, 2), (2, 3)]
        self.assertEqual(s.edges(path), edges)

        C = []
        path = [(0, 2), (1, 2), (1, 3), (1, 4)]
        sym_diff = s.edges(path) # because C is empty 
        self.assertEqual(s.symmetric_difference(path,C), sym_diff)

        C = [((0, 2), (1, 2))]
        path = [(0, 2), (1, 2), (1, 3), (1, 4)]
        sym_diff = [((1, 2), (1, 3)), ((1, 3), (1, 4))] # because the first edge ((0, 2), (1, 2)) is shared only the others are put in C
        self.assertEqual(s.symmetric_difference(path,C), sym_diff)
    
    def test_bipart_run(self): #Test if the programm runs without errors
        grid = Grid.grid_from_file("input/grid01.in",read_values=True) 
        s = SolverBipart(grid)
        try:
            s.run()
        except Exception as e:
            self.fail(f"s.run() raised an exception: {e}")
    

if __name__ == '__main__':
    unittest.main()
