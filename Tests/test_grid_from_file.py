# This will work if ran from the root folder (the folder in which there is the subfolder code/)
import sys 
sys.path.append("code/")

import unittest 
from grid import Grid
from solver import *

class Test_GridLoading(unittest.TestCase):
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
        b = (solver.score() <= grid.n*grid.m) # if we decide not to link any cell, the score would be maximum (and not optimal) and equal to n*m 
        self.assertEqual(b, True)




if __name__ == '__main__':
    unittest.main()

