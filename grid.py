from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import numpy as np
"""
This is the grid module. It contains the Grid class and its associated methods.
"""
class Grid():
    
    """
    A class representing the grid. 

    Attributes: 
    -----------
    n: int
        Number of lines in the grid
    m: int
        Number of columns in the grid
    color: list[list[int]]
        The color of each grid cell: value[i][j] is the value in the cell (i, j), i.e., in the i-th line and j-th column. 
        Note: lines are numbered 0..n-1 and columns are numbered 0..m-1.
    value: list[list[int]]
        The value of each grid cell: value[i][j] is the value in the cell (i, j), i.e., in the i-th line and j-th column. 
        Note: lines are numbered 0..n-1 and columns are numbered 0..m-1.
    colors_list: list[char]
        The mapping between the value of self.color[i][j] and the corresponding color
    """
    

    def __init__(self, n, m, color=[], value=[]):
        """
        Initializes the grid.

        Parameters: 
        -----------
        n: int
            Number of lines in the grid
        m: int
            Number of columns in the grid
        color: list[list[int]]
            The grid cells colors. Default is empty (then the grid is created with each cell having color 0, i.e., white).
        value: list[list[int]]
            The grid cells values. Default is empty (then the grid is created with each cell having value 1).
        
        The object created has an attribute colors_list: list[char], which is the mapping between the value of self.color[i][j] and the corresponding color
        """
        self.n = n
        self.m = m
        if not color:
            color = [[0 for j in range(m)] for i in range(n)]            
        self.color = color
        if not value:
            value = [[1 for j in range(m)] for i in range(n)]            
        self.value = value
        self.colors_list = ['w', 'r', 'b', 'g', 'k']

    def __str__(self): 
        """
        Prints the grid as text.
        """
        output = f"The grid is {self.n} x {self.m}. It has the following colors:\n"
        for i in range(self.n): 
            output += f"{[self.colors_list[self.color[i][j]] for j in range(self.m)]}\n"
        output += f"and the following values:\n"
        for i in range(self.n): 
            output += f"{self.value[i]}\n"
        return output

    def __repr__(self): 
        """
        Returns a representation of the grid with number of rows and columns.
        """
        return f"<grid.Grid: n={self.n}, m={self.m}>"

    def plot(self): 
        """
        Plots a visual representation of the grid.
        """
        grid = np.array(self.color)
        cmap = ListedColormap(['white', 'red', 'blue' , 'green', 'black'])
        plt.imshow(grid, cmap=cmap, extent=[0, self.m, 0, self.n], origin='upper')
        plt.xticks(np.arange(0, self.m + 1, 1)) 
        plt.yticks(np.arange(0, self.n + 1, 1)) 
        v=self.value.copy() 
        v.reverse()# issue because matrix is numerated from top to bottom but a grid is from bottom to top
        def border_of_cell(x,y): #To mark the border of each cell
            rect = plt.Rectangle((x-.5, y-.5), 1,1, fill=False, color = "black", lw=1)
            ax = plt.gca()
            ax.add_patch(rect)
            return rect
        
        for i in range(self.n):
            for j in range(self.m):
                    border_of_cell(j+0.5,i+0.5)
                    plt.text(j + 0.5, i + 0.5, v[i][j], ha='center', va='center', color='black', fontsize=12)
                    
        
        plt.xticks([])
        plt.yticks([])
        #To add the coordinates we first changes the border to avoid plotting on the cells
        plt.xlim(-0.5, self.m + 0.5)
        plt.ylim(-0.5, self.n + 0.5)

        # We ass the line numbers
        for i in range(self.n):
            plt.text(-0.2, i + 0.5, str(self.n - 1 - i), ha='right', va='center', fontsize=12)

        #The the rows
        for j in range(self.m):
            plt.text(j + 0.5, self.n + 0.2, str(j), ha='center', va='bottom', fontsize=12)

        plt.show()
        
    def is_forbidden(self, i: int, j: int) -> bool :
        """
        Returns True is the cell (i, j) is black and False otherwise
        """
        return self.color[i][j] == 4

    def cost(self, pair : tuple[tuple[int]]) -> int:
        """
        Returns the cost of a pair
 
        Parameters: 
        -----------
        pair: tuple[tuple[int]]
            A pair in the format ((i1, j1), (i2, j2))

        Output: 
        -----------
        cost: int
            the cost of the pair defined as the absolute value of the difference between their values
        """
        return abs(self.value[pair[0][0]][pair[0][1]] - self.value[pair[1][0]][pair[1][1]])

    def is_valid_pair(self, i1 : int,j1 : int, i2: int, j2: int) -> bool:
        valid = (0 <= i1 < self.n) and (0 <= j1 < self.m) and (0 <= i2 < self.n) and (0 <= j2 < self.m) and (i1 != i2 or j1 != j2) # All coordinate are valid
        valid = valid and (not self.is_forbidden(i1, j1)) and (not self.is_forbidden(i2, j2)) # Both cells are not black
        valid = valid and (abs(i1 - i2) + abs(j1 - j2) == 1) # The cells are adjacent
        #We check the validity of the colors
        valid = valid and (self.color[i1][j1] == 0 or self.color[i2][j2] == 0 or # If white all pair color valid except black
                           (self.color[i1][j1] == 1 and self.color[i2][j2] == 1) or # red with red
                           (self.color[i1][j1] == 2 and self.color[i2][j2] == 1)  or (self.color[i1][j1]==1 and self.color[i2][j2]==2)  or # red with blue
                           (self.color[i1][j1] == 2 and self.color[i2][j2] == 2) or # Blue with Blue 
                           (self.color[i1][j1] == 3 and self.color[i2][j2] == 3) # Green with green
                           )
        return valid

    def all_pairs(self) -> list:
        """
        Returns a list of all pairs of cells that can be taken together. 

        Outputs a list of tuples of tuples [(c1, c2), (c1', c2'), ...] where each cell c1 etc. is itself a tuple (i, j)
        """
        pairs = []
        for i in range(self.n):
            for j in range(self.m): 
                if self.is_valid_pair(i, j, i+1, j): # True if both cells are not black
                    pairs.append(((i, j), (i+1, j)))
                    
                if self.is_valid_pair(i, j, i, j+1): # Same as above
                    pairs.append(((i, j), (i, j+1)))
                    
        return pairs
    



    @classmethod
    def grid_from_file(cls, file_name, read_values=False): 
        """
        Creates a grid object from class Grid, initialized with the information from the file file_name.
        
        Parameters: 
        -----------
        file_name: str
            Name of the file to load. The file must be of the format: 
            - first line contains "n m" 
            - next n lines contain m integers that represent the colors of the corresponding cell
            - next n lines [optional] contain m integers that represent the values of the corresponding cell
        read_values: bool
            Indicates whether to read values after having read the colors. Requires that the file has 2n+1 lines

        Output: 
        -------
        grid: Grid
            The grid
        """
        with open(file_name, "r") as file:
            n, m = map(int, file.readline().split())
            color = [[] for i_line in range(n)]
            for i_line in range(n):
                line_color = list(map(int, file.readline().split()))
                if len(line_color) != m: 
                    raise Exception("Format incorrect")
                for j in range(m):
                    if line_color[j] not in range(5):
                        raise Exception("Invalid color")
                color[i_line] = line_color

            if read_values:
                value = [[] for i_line in range(n)]
                for i_line in range(n):
                    line_value = list(map(int, file.readline().split()))
                    if len(line_value) != m: 
                        raise Exception("Format incorrect")
                    value[i_line] = line_value
            else:
                value = []

            grid = Grid(n, m, color, value)
        return grid
