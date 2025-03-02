import sys 
sys.path.append("code/")

import unittest 
from grid import Grid


class Test_cost(unittest.TestCase):
    def test_cost(self):
        n = 2
        m = 3
        value = [[1, 2, 3], [4, 5, 6]]
        color = [[0, 1, 2], [3, 4, 0]]
        grid = Grid(n, m, value=value, color=color)
        pair1=((0,0),(1,0)) #Cost of 3
        pair2=((0,2),(1,2)) #Cost of 3
        pair3=((0,0),(0,1)) #Cost of 1
        self.assertEqual(grid.cost(pair1), 3)
        self.assertEqual(grid.cost(pair2), 3)
        self.assertEqual(grid.cost(pair3), 1)

if __name__ == '__main__':
    unittest.main()
