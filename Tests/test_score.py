import sys 
sys.path.append("code/")

import unittest 
from grid import Grid
from solver import *

class Test_score(unittest.TestCase):
    def test_small_grid(self):
        n = 2
        m = 3
        value = [[1, 2, 3], [4, 5, 6]]
        color = [[0, 1, 2], [3, 4, 0]]
        grid = Grid(n, m, value=value, color=color)
        s = SolverEmpty(grid)
        s.pairs = [((0,0),(1,0)),((0,2),(1,2))]#We test one possibility of score 8
        self.assertEqual(s.score(), 8)


if __name__ == '__main__':
    unittest.main()
