# This will work if ran from the root folder (the folder in which there is the subfolder code/)
import sys 
sys.path.append("code/")

import unittest 
from grid import Grid
from solver import *

class Test_GridLoading(unittest.TestCase):
    def test_greedy(self): # just to check the basic fontions
        grid = Grid.grid_from_file("input/grid00.in",read_values=True) 
        s = SolverGreedy(grid)

        l1 = [12, 14, 5, 23, 82, 1, 7]
        self.assertEqual(s.index_min(l1), 5)

        l2 = [(1,2), (3,4), (5,6)]
        L2 = [(3,4), (5,6)]
        self.assertEqual(s.remove((1,2),l2), L2 )

    def test_bipart(self): # just to check the basic fontions
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
        
    def test_grid0(self):
        grid = Grid.grid_from_file("input/grid00.in",read_values=True)
        self.assertEqual(grid.n, 2)
        self.assertEqual(grid.m, 3)
        self.assertEqual(grid.color, [[0, 0, 0], [0, 0, 0]])
        self.assertEqual(grid.value, [[5, 8, 4], [11, 1, 3]])


    def test_grid0_novalues(self):
        grid = Grid.grid_from_file("input/grid00.in",read_values=False)
        self.assertEqual(grid.n, 2)
        self.assertEqual(grid.m, 3)
        self.assertEqual(grid.color, [[0, 0, 0], [0, 0, 0]])
        self.assertEqual(grid.value, [[1, 1, 1], [1, 1, 1]])

    def test_grid1(self):
        grid = Grid.grid_from_file("input/grid01.in",read_values=True)
        self.assertEqual(grid.n, 2)
        self.assertEqual(grid.m, 3)
        self.assertEqual(grid.color, [[0, 4, 3], [2, 1, 0]])
        self.assertEqual(grid.value, [[5, 8, 4], [11, 1, 3]])

    def test_grid3(self):
        grid = Grid.grid_from_file("input/grid03.in",read_values=True)
        self.assertEqual(grid.n, 4)
        self.assertEqual(grid.m, 8)
        solver = SolverBipart(grid)
        solver.run()
        self.assertEqual(solver.score(), 2) # we can easily verify this
        invalid_edge = ((0,0),(0,1)) # this edge is invalid because (0,0) and (0,1) are black cells so they should not be in the solution 
        b = (invalid_edge not in solver.pairs) # type(b) =  bool
        self.assertEqual(b, True) # b must be True because invalid_edge should not be in the solution
    
    def test_grid11(self):
        grid = Grid.grid_from_file("input/grid11.in",read_values=True)
        self.assertEqual(grid.n, 10)
        self.assertEqual(grid.m, 20)
        solver = SolverBipart(grid)
        solver.run()
        self.assertEqual(type(solver.score()), int)
        b1 = (solver.score() <= grid.n*grid.m) # if we decide not to link any cell, the score would be maximum (and not optimal) and equal to n*m 
        self.assertEqual(b1, True)

        solverg = SolverGreedy(grid)
        b2 = (solver.score() <= solverg.score()) 
        self.assertEqual(b2, True) # because the Bipart Solver is more optimal than the Greedy one
    
   




if __name__ == '__main__':
    unittest.main()
