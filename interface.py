import pygame
import tkinter as tk
from tkinter import messagebox
from grid import Grid 
from solver_version_finale import SolverScipy, SolverEmpty, Solver
import math
from copy import deepcopy
from typing import Union


class PygameGame():
    r"""
    A base class for creating Pygame-based grid games with interactive features.
    This class provides the fundamental structure for the grid game, including
    display management, user interaction handling, and game state tracking. It defines basic
    features like cell selection, solution display, and grid menu navigation.
    
    Parameters
    ----------
    None

    Attributes
    ----------
    grid : Grid
        A grid object representing the game board check the documentation of the grid class for more details, 
        it is initialized with a 3x4 grid to handle feature necessary before choosing a grid but this grid is not used in the game
    solver : SolverScipy
        Solver object for computing solutions to the grid game check the documentation of the solver class for more details,
        by default it used the scipy linear sum assignment solver to function because it is the more efficient 
    cell_size : int
        Size of each cell in pixels by default it is set at 100 but this value is dynamically changed to match the size of the window
    width : int
        Total width of the game window including borders
    height : int
        Total height of the game window including borders
    border : int
        Border size around the grid to allow for UI elements and spacing
    running : bool
        Flag indicating if the game is running, if false the game is closed
    colors : list of tuple
        RGB color tuples for cell coloring
    screen : pygame.Surface
        Main game display surface
    text_font : pygame.font.Font
        Font for general text display like the UI
    cell_font : pygame.font.Font
        Font for cell numbers
    clicked_cells : list of tuple
        Currently selected cells for linking
    linked_cells : set of tuple of tuple
        Pairs of all the cells that are currenly connected in the game
    used_cells : set of tuple
        All cells that are currently used in connections
    time_start_event : float
        Timestamp for event timing when we want to display a message for a certain time
    text_event : str
        Current event text to display
    buttons : dict of list of *args 
        Storage for current UI button objects and their functions
    grid_menu : bool
        Flag indicating if main menu is displayed to switch between the grid menu and the game
    solution_displayed : bool
        Flag indicating if solution is visible to prevent multiple displays and calculation of the solution
    scroll_offset : int
        Current vertical scroll position
    max_scroll : int
        Maximum scroll limit
        
    Methods
    -------
    adjust_for_resize()
        Adjusts display elements for window resizing
    draw_grid()
        Renders the game grid with their colors, values and coordinates
    draw_event_text(center_position)
        Displays event text at specified position
    draw_score(position, list_of_pairs, score_text=None)
        Draw the score at the position given associated with the list of pairs given
    draw_line_between_cells(list_pair, color=(0,0,0))
        Draws lines betxeen all connected paired cells
    draw_main_menu_buttons()
        Renders all the buttons in the main menu and in the game
    score(pairs)
        Calculates score for a given list of pairs depending on the grid
    Notes
    -----
    The game window is resizable and includes scrollable menus for grid selection.
    Coordinates use (row, column) format for grid navigation.
    This class serves as the foundation for a Pygame-based game with a grid system. It initializes all necessary
    components for the game including the grid, display settings, and interaction tracking.
    Somme methods used in the base class are not implemented and must be implemented in the child class
    """
    def __init__(self):
        r"""
        Initialize the base PygameGame class with grid, solver, display settings and game state variables.

        Creates a 3x4 grid and initializes display settings like colors, fonts, window size etc.
        Also sets up data structures to track clicked cells, linked cells and game state.
        """
        self.grid = Grid(3,4)
        self.solver = SolverScipy(self.grid)
        self.cell_size = 100
        self.width = self.grid.m * self.cell_size
        self.height = self.grid.n * self.cell_size
        self.border = 125
        self.running = True

        pygame.init()
        self.colors = [(255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 128, 0), (0, 0, 0)]  # white, red, blue, green, black
        self.screen = pygame.display.set_mode((self.width + 2*self.border, self.height + 2*self.border),pygame.RESIZABLE)
        self.width = self.width + 2*self.border
        self.height = self.height + 2*self.border
        self.text_font = pygame.font.SysFont('Arial', 30) #We differentiate the font for texte and cell/coordinate 
        self.cell_font = pygame.font.SysFont('Arial', 30)
        self.clicked_cells = []  # Store the two first clicked cells to check if they are valid pairs
        self.linked_cells = set()  # Store all linked cells
        self.used_cells = set() # Store all used cells
        self.time_start_event = None # Store the time when the print event starts
        self.text_event = None # Store the text to print
        self.buttons = {} # Store the buttons
        self.grid_menu = True # Check if the main menu is displayed
        self.solution_displayed = False # Check if the solution is displayed
        self.button_width, self.button_height = 200, 30
        self.base_button_height = 50 # Base height of the buttons for the resize 
        self.scroll_offset = 0
        self.scroll_speed = 20
        self.offset_button = 10 #Create a gap between buttons on the main menu
        self.max_scroll = -(len(self.buttons) * (self.button_height ) - self.height)
        self.scrollbar_width = 10
        self.all_grid_index = ["00","01","02","03","04","05","11","12","13","14","15","16","17","18","19","21","22","23","24","25","26","27","28","29"]

    def adjust_for_resize(self):
        r"""Adjust the display elements for window resizing.

        This method recalculates the cell size, button sizes, font sizes, 
        and other UI elements to accommodate a resized window.
        """

        self.cell_size = min((self.width - 2*self.border)//self.grid.m,
                            (self.height - 2*self.border)//self.grid.n)
        self.button_width = self.width // 2
        self.button_height = max(self.base_button_height, self.height // len(self.buttons))
        self.max_scroll = -(len(self.buttons) * (self.button_height ) - self.height)
        font_size = min(int(self.cell_size * 0.35), 50)  # 35% of cell size, capped at 50
        self.cell_font = pygame.font.SysFont('Arial', max(12,  font_size))
        # Adjust text font size logarithmically based on cell size, with base size of 30
        text_font_size = int(33 * math.log(max(self.cell_size/5, 20), 30)**2)
        self.text_font = pygame.font.SysFont('Arial', max(12, min(50, text_font_size)))

    def draw_grid(self):
        r"""Render the game grid on the screen.

        This method draws the grid cells, their values, and their coordinates.
        Each cell's color is determined by the grid's color attribute, and 
        cell values are displayed at the center of each cell.
        """

        self.screen.fill((255, 255, 255))
        
        # Draw grid rectangles and values
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                color = self.colors[self.grid.color[i][j]]
                pygame.draw.rect(self.screen, color, 
                                 (j * self.cell_size + self.border, i * self.cell_size + self.border, self.cell_size, self.cell_size))
                color = (255, 0, 0) if (i, j) in self.clicked_cells else (0,0,0)
                pygame.draw.rect(self.screen, color, 
                                 (j * self.cell_size + self.border, i * self.cell_size + self.border, self.cell_size, self.cell_size), 1)
                
                text = self.cell_font.render(str(self.grid.value[i][j]), True, (0, 0, 0))
                self.screen.blit(text, (self.border + j * self.cell_size + self.cell_size //2.5, 
                                        self.border + i * self.cell_size + self.cell_size/3))
        
        # Draw coordinates
        for i in range(self.grid.n):
            text = self.cell_font.render(str(i), True, (0, 0, 0))
            self.screen.blit(text, (self.border//2, self.border + i * self.cell_size + self.cell_size // 3))
        for j in range(self.grid.m):
            text = self.cell_font.render(str(j), True, (0, 0, 0))
            self.screen.blit(text, (self.border + j * self.cell_size + self.cell_size // 3, self.border//3))
    
    def draw_event_text(self, center_position : tuple[int,int]):
        r"""Display event text at the specified position on the screen.

        This method shows the event message stored in self.text_event at the
        provided center_position. The message is cleared after 1 second.

        Parameters
        ----------
        center_position : tuple of int
            The (x, y) coordinates where the event text should be displayed.
        """

        if self.text_event is not None:
            text = self.text_font.render(self.text_event, True, (0, 0, 0))
            text_rect = text.get_rect(center=center_position)
            self.screen.blit(text, text_rect)
            if pygame.time.get_ticks() - self.time_start_event > 1000:
                self.text_event = None
                self.time_start_event = None

    def draw_score(self, position : tuple[int,int], list_of_pairs : list[tuple[int,int]], score_text : Union[None,str] = None):
        r"""Draw the score on the screen at the specified position.

        This method calculates the score based on the list of pairs and 
        draws the score text at the specified position on the screen. If 
        `score_text` is provided, it is displayed as a prefix to the score.

        Parameters
        ----------
        position : tuple of int
            The (x, y) coordinates where the score should be displayed.
        list_of_pairs : list of tuple
            The list of pairs that make up the current solution.
        score_text : str, optional
            An optional prefix text to display before the score.
        """

        #Draw score on the bottom left of the screen
        score = self.score(list_of_pairs)
        if score_text is None:
            text = self.text_font.render(f"Score: {score}", True, (0, 0, 0))
        else:
            text = self.text_font.render(score_text+str(score), True, (0, 0, 0))
        self.screen.blit(text, position) #(self.border//2, self.height - self.border+20)

    def draw_line_between_cells(self, list_pair : list[tuple[tuple[int,int],tuple[int,int]]], color =(0, 0, 0)):
        r"""Draw lines between pairs of cells on the grid.

        This method draws lines between the pairs of cells in list_pair.
        Optionally, the color of the lines can be customized.

        Parameters
        ----------
        list_pair : list of tuple of tuple of int
            The list of pairs of cell coordinates (each pair consisting of two tuples).
        color : tuple of int, optional
            The RGB color of the lines (default is black).

        """

        for (i1, j1), (i2, j2) in list_pair:
            pygame.draw.line(self.screen, color, 
                             (j1 * self.cell_size + self.border + self.cell_size // 2, i1 * self.cell_size + self.border + self.cell_size // 2), 
                             (j2 * self.cell_size + self.border + self.cell_size // 2, i2 * self.cell_size + self.border + self.cell_size // 2), 5)

    def drawn_all(self):
        r"""Draw all elements on the screen.
        This method is a placeholder and should be implemented in subclasses."""
        
        pass

    def draw_main_menu_buttons(self):
        r"""Draw the main menu buttons.

        This method renders the buttons in the main menu. Each button is
        assigned a function, store in the self.buttons dictionnary and is finally drawn on the screen.
        """

        self.buttons = {}
        y_pos = self.scroll_offset
        colors = [(255, 255, 200),  (255, 250, 190), (255, 245, 180), (255, 240, 170), (255, 235, 160), (255, 230, 150), (255, 225, 140), (255, 220, 130), 
                  (255, 215, 120), (255, 210, 110),  (255, 200, 100), (255, 190, 90), (255, 180, 80), (255, 170, 70),(255, 160, 60),  (255, 150, 50),  (255, 140, 40),  
                  (255, 130, 30),  (255, 120, 20),  (255, 110, 10),  (240, 100, 0),  (220, 90, 0),  (200, 80, 0),  (180, 70, 0)]
        color_index = 0
        text_color = (0, 0, 0)
        for index in self.all_grid_index:
            # Dessiner les boutons
            button_name = "Grid "+index
            button = pygame.draw.rect(self.screen, colors[color_index], (self.width // 4, y_pos, self.button_width, self.button_height-self.offset_button))
            text_surface = self.text_font.render(button_name, True, text_color)
            self.screen.blit(text_surface, (self.width // 4 + 10, y_pos+10-self.offset_button))
            y_pos += self.button_height
            if color_index < len(colors)-1:
                color_index += 1
            if int(index)>13:
                text_color = (255, 255, 255)
            self.buttons[button_name] = [button,self.switch_to_grid_button,[index]]
            
        text_padding = 10  # Padding around text
        menu_text = self.text_font.render("Menu", True, (0, 0, 0))
        menu_width, menu_height = menu_text.get_width() + text_padding * 2, menu_text.get_height() + text_padding
        menu_button_x = self.width - menu_width - 10
        menu_button_y = 10
        menu_button = pygame.draw.rect(self.screen, (117, 223, 155),
                                        (menu_button_x, menu_button_y, menu_width, menu_height))
        self.screen.blit(menu_text, (menu_button_x+text_padding, menu_button_y+text_padding/2))
        self.buttons["menu_button"] = [menu_button, self.quit_game_button, None]

    def draw_scrollbar(self):
        r"""Draw the scrollbar in the menu.

        This method calculates and draws a vertical scrollbar based on the
        current scroll offset and the total number of menu items.
        """

        # Calculer la hauteur de la barre de défilement
        scrollbar_height = self.height * (self.height / (len(self.buttons) * self.button_height))
        scrollbar_pos_y = -self.scroll_offset * (self.height / (len(self.buttons) * self.button_height))
        # Dessiner la barre de défilement à droite
        pygame.draw.rect(self.screen, (100, 100, 100), (self.width - self.scrollbar_width, scrollbar_pos_y, self.scrollbar_width, scrollbar_height))

    def score(self, pairs : list[tuple[int,int]]) -> int: # We want to minimize the score
        r"""Calculate the score for a given list of pairs.

        This method calculates the score by summing the cost of each valid pair, 
        defined as the absolute difference between their values, and the value of
        all unlinked cells in the grid. The score is minimized
        to encourage the optimal selection of pairs.

        Parameters
        ----------
        pairs : list of tuple
            The list of pairs that make up the current solution.

        Returns
        -------
        int
            The total score for the given list of pairs.
        """

        score = 0
        color_grid = deepcopy(self.grid.color)
        
        for pair in pairs:
            # We add to the score the cost of each pair
            score += self.grid.cost(pair) 
            # Each cell already counted is colored in black
            color_grid[pair[0][0]][pair[0][1]] = 4 
            color_grid[pair[1][0]][pair[1][1]] = 4
        
        for i in range(self.grid.n): 
            for j in range(self.grid.m):
                if color_grid[i][j] != 4:
                    score += self.grid.value[i][j]
                     # We add the individual value of each cell that is not black/already counted
        
        return score
    

    def quit_game_button(self):
        r"""Quit the game.

        This method sets the running flag to False, stopping the game loop
        and quitting the game.
        """

        self.running = False

    def reset_grid(self):
        r"""Reset the grid to its initial state.

        This method clears the clicked cells, linked cells, and used cells,
        and sets the solution_displayed flag to False, resetting the game state.
        """

        self.clicked_cells.clear()
        self.linked_cells.clear()
        self.used_cells.clear()
        self.solution_displayed = False

    def clear_button(self):
        r"""Reset the game and display a "Reset" event message.

        This method clears the game state and displays the "Reset" event message
        at the bottom of the screen.
        """

        self.reset_grid()
        self.time_start_event = pygame.time.get_ticks()
        self.text_event = "Reset"
    

    def switch_to_grid_button(self,grid_index : str):
        r"""Switch the grid to a new one based on the selected index.

        This method loads a grid from a file based on the given grid_index, 
        updates the solver, and switches from the main menu to the selected grid.

        Parameters
        ----------
        grid_index : str
            The index of the grid to load (e.g., "00", "01", etc.).
        """

        self.grid = Grid.grid_from_file("./input/grid"+grid_index+".in", read_values=True)
        self.solver = SolverScipy(self.grid)
        self.grid_menu = False
        self.adjust_for_resize()
        self.clicked_cells.clear()
    
    def show_solution_button(self):
        r"""Show the solution for the current grid.

        This method computes and displays the solution for the current grid 
        using the solver. It also clears any existing linked and used cells.
        """

        if self.solution_displayed:
            self.time_start_event = pygame.time.get_ticks()
            self.text_event = "Solution already displayed"
        else:
            self.time_start_event = pygame.time.get_ticks()
            self.text_event = "Calculating solution"
            self.draw_all()
            pygame.display.flip()
            self.clicked_cells.clear()
            self.linked_cells.clear()
            self.used_cells.clear()
            self.solver.pairs=list(self.linked_cells)
            self.solver.run()
            for ((i1, j1), (i2, j2)) in self.solver.pairs:
                self.used_cells.add((i1, j1))
                self.used_cells.add((i2, j2))
                self.linked_cells.add(((i1, j1), (i2, j2)))
            self.solution_displayed = True


    def menu_button(self):
        r"""Display a confirmation message before quitting the game.

        This method shows a dialog box asking if the user is sure they want to quit
        the game. If the user confirms, it returns to the main menu and resets the 
        game state.
        """

        answer = messagebox.askquestion("Quit Game", "Are you sure you want to quit, all unsave progress will be reset")
        if answer == "yes":
            self.grid_menu = True
            self.draw_buttons()
            self.width, self.height = 550, 450
            self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
            self.adjust_for_resize()
            self.clicked_cells.clear()
            self.linked_cells.clear()
            self.used_cells.clear()
            self.solution_displayed = False
            
    def is_finished(self) -> bool: 
        r"""Check if the game is finished.

        This method checks if all cells have been used in valid pairs, indicating
        that the game has been completed. It returns True if the game is finished,
        and False otherwise.

        Returns
        -------
        bool
            True if the game is finished, False otherwise.
        """

        finished = True
        for i in range(self.grid.n):
            for j in range(self.grid.m):
                if self.grid.color[i][j] != 4 and (i, j) not in self.used_cells:
                    if i-1>0 and (i-1,j) not in self.used_cells and self.grid.is_valid_pair(i, j, i-1, j):
                        finished = False
                    if j-1>0 and (i,j-1) not in self.used_cells and self.grid.is_valid_pair(i, j, i, j-1):
                        finished = False
                    if i+1<self.grid.n and (i+1,j) not in self.used_cells and self.grid.is_valid_pair(i, j, i+1, j):
                        finished = False
                    if j+1<self.grid.m and (i,j+1) not in self.used_cells and self.grid.is_valid_pair(i, j, i, j+1):
                        finished = False
        return finished
     

class PygameSoloGame(PygameGame):
    
    def __init__(self):
        super().__init__()


    def handle_cell_click(self, pos : tuple[int,int]):
        r"""Handle a cell click event.

        This method processes the user's click on the grid, updating the clicked 
        cells, linking valid pairs, and handling invalid selections or already used cells.

        Parameters
        ----------
        pos : tuple of int
            The (x, y) coordinates of the mouse click.

        """

        x, y = pos
        col = (x - self.border) // self.cell_size
        row = (y - self.border) // self.cell_size
        if 0 <= row < self.grid.n and 0 <= col < self.grid.m and self.grid.color[row][col] != 4:
            if (row, col) in self.clicked_cells:
                self.clicked_cells.remove((row, col))  # go back to normal
            elif len(self.clicked_cells) == 0: # We add the first cell every time
                self.clicked_cells.append((row, col))
            elif len(self.clicked_cells) == 1 and ((row, col) in self.used_cells or self.clicked_cells[0] in self.used_cells): #If one of the cell is already used
                if ((row,col),self.clicked_cells[0]) in self.linked_cells or (self.clicked_cells[0],(row,col)) in self.linked_cells: #if we reclick on a matched pair
                    self.time_start_event=pygame.time.get_ticks()
                    self.text_event = "Pair undo"
                    self.used_cells.remove((row,col))
                    self.used_cells.remove(self.clicked_cells[0])
                    if ((row,col),self.clicked_cells[0]) in self.linked_cells:
                        self.linked_cells.remove(((row,col),self.clicked_cells[0]))
                    else:
                        self.linked_cells.remove(((self.clicked_cells[0],(row,col))))
                    self.clicked_cells.clear()
                else:
                    self.time_start_event=pygame.time.get_ticks()
                    self.text_event = "Cell already used"
                    self.clicked_cells.clear()
                
            else:
                self.clicked_cells.append((row, col))  # mark cell in red
                if len(self.clicked_cells) == 2:
                    i1, j1 = self.clicked_cells.pop()
                    i2, j2 = self.clicked_cells.pop()
                    if self.grid.is_valid_pair(i1, j1, i2, j2):
                        self.linked_cells.add(((i1, j1), (i2, j2)))
                        self.used_cells.add((i1, j1))
                        self.used_cells.add((i2, j2))
                    else: #clicked_cell empty because of len 2 with 2 pop
                        self.time_start_event=pygame.time.get_ticks()
                        self.text_event = "Invalid pair"
        elif 0 <= row < self.grid.n and 0 <= col < self.grid.m and self.grid.color[row][col] == 4:
            self.time_start_event=pygame.time.get_ticks()
            self.text_event = "Forbidden cell"
            self.clicked_cells.clear()

    def draw_buttons(self):
        r"""Draw the game action buttons.

        This method renders the action buttons like "Reset", "Show solution", 
        and "Menu" in the game view and adjusts their positions based on 
        screen size.
        """

        if self.grid_menu:
            self.draw_main_menu_buttons()
        
        else:
            self.buttons = {}
            # Get the size of the text to adapt the button size
            clear_text = self.text_font.render("Reset", True, (0, 0, 0))
            solution_text = self.text_font.render("Show solution", True, (0, 0, 0))
            text_padding = 10  # Padding around text

            # Size buttons based on text
            clear_width, clear_height = clear_text.get_width() + text_padding * 2, clear_text.get_height() + text_padding 
            solution_width, solution_height = solution_text.get_width() + text_padding * 2, solution_text.get_height() + text_padding
            if clear_width < solution_width:
                clear_offset = (solution_width - clear_width)/2 # Offset to center the buttons 
                solution_offset = 0
            else:
                clear_offset = 0
                solution_offset = (clear_width - solution_width)/2
               
        
            # Position buttons at bottom right corner
            clear_button_x = self.width - max(clear_width, solution_width) - 10 + clear_offset
            clear_button_y = self.height - (2 * clear_height + 15)
            clear_button = pygame.draw.rect(self.screen, (200, 200, 200),
                                          (clear_button_x, clear_button_y, 
                                           clear_width, clear_height))
            self.screen.blit(clear_text, (clear_button_x+text_padding, clear_button_y+text_padding/2))
            self.buttons["clear_button"] = [clear_button, self.clear_button, None]

            solution_button_x = self.width - max(clear_width, solution_width) - 10 + solution_offset
            solution_button_y = self.height - (2 * solution_height + 15) + clear_height + 5
            solution_button = pygame.draw.rect(self.screen, (200, 200, 200),
                                            (solution_button_x, solution_button_y, solution_width, solution_height))
            self.screen.blit(solution_text, (solution_button_x+text_padding, solution_button_y+text_padding/2))
            self.buttons["solution_button"] = [solution_button, self.show_solution_button, None]
            
            
            #Menu button to go back to the main menu
            menu_text = self.text_font.render("Menu", True, (0, 0, 0))
            menu_width, menu_height = menu_text.get_width() + text_padding * 2, menu_text.get_height() + text_padding
            menu_button_x = self.width - menu_width - 10
            menu_button_y = 10
            menu_button = pygame.draw.rect(self.screen, (200, 200, 200),
                                            (menu_button_x, menu_button_y, menu_width, menu_height))
            self.screen.blit(menu_text, (menu_button_x+text_padding, menu_button_y+text_padding/2))
            self.buttons["menu_button"] = [menu_button, self.menu_button, None]
    
    def draw_all(self):
        r"""Draw the entire game state.

        This method linked all the drawing component in one drawing function
        """

        self.draw_grid()
        self.draw_line_between_cells(self.linked_cells)
        self.draw_buttons()
        self.draw_event_text((self.width//2, self.height - self.border*0.5))
        self.draw_score((self.border//2, self.height - self.border+20), self.linked_cells)

    def run(self):
        r"""Run the game loop.

        This is the mainloop of the game. Every frame of running, we check for pygame event such as 
        mouse click, window resize, etc. and call the appropriate function. We also draw the game elements
        such as the grid, buttons, and event text depending on the current state of the game.

        """

        self.draw_buttons()
        self.adjust_for_resize()
        while self.running:
            if self.grid_menu:
                self.screen.fill((138,32,100))
                self.draw_buttons()
                self.draw_scrollbar()
                                                                                                                                                                                                                                                                               
            else: #If we display a grid
                self.draw_all()
                if self.is_finished():
                    self.time_start_event = pygame.time.get_ticks()
                    self.text_event = "Game finished"
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if self.buttons[button][0].collidepoint(event.pos) and self.buttons[button][2] is not None:
                            self.buttons[button][1](*self.buttons[button][2]) # Call the button function
                        elif self.buttons[button][0].collidepoint(event.pos):
                            self.buttons[button][1]()
                    if not self.grid_menu: 
                        self.handle_cell_click(event.pos)
                if event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    # self.width, self.height = self.width + 2*self.border, self.height + 2*self.border
                    self.adjust_for_resize()
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.scroll_offset = min(self.scroll_offset + self.scroll_speed, 0)  # Défilement vers le haut
                    elif event.y < 0:
                        self.scroll_offset = max(self.scroll_offset - self.scroll_speed, self.max_scroll)  # Défilement vers le bas            
            
            pygame.display.flip()
        pygame.quit()
    
class PygameTwoPlayerGame(PygameGame):
    def __init__(self):
        super().__init__()
        self.wich_turn = 0 # 0 for player 0 and 1 for player 1
        self.player0_pairs = set()
        self.player1_pairs = set()
        self.players_pairs = [self.player0_pairs, self.player1_pairs] # List of pairs for each player
    
    def reset_grid(self):
        super().reset_grid()
        self.player0_pairs.clear()
        self.player1_pairs.clear()
        self.wich_turn = 0 # 0 for player 0 and 1 for player 1

    def handle_cell_click(self, pos):
        x, y = pos
        col = (x - self.border) // self.cell_size
        row = (y - self.border) // self.cell_size
        if 0 <= row < self.grid.n and 0 <= col < self.grid.m and self.grid.color[row][col] != 4:
            if (row, col) in self.clicked_cells:
                self.clicked_cells.remove((row, col))  # go back to normal
            elif len(self.clicked_cells) == 0: # We add the first cell every time
                self.clicked_cells.append((row, col))
            elif len(self.clicked_cells) == 1 and ((row, col) in self.used_cells or self.clicked_cells[0] in self.used_cells):
                self.time_start_event=pygame.time.get_ticks()
                self.text_event = "Cell already used"
                self.clicked_cells.clear()     
            else:
                self.clicked_cells.append((row, col))  # mark cell in red
                if len(self.clicked_cells) == 2:
                    i1, j1 = self.clicked_cells.pop()
                    i2, j2 = self.clicked_cells.pop()
                    if self.grid.is_valid_pair(i1, j1, i2, j2):
                        self.linked_cells.add(((i1, j1), (i2, j2)))
                        self.players_pairs[self.wich_turn].add(((i1, j1), (i2, j2))) # Add the pair to the current player 
                        self.used_cells.add((i1, j1))
                        self.used_cells.add((i2, j2))
                        self.wich_turn = 1-self.wich_turn
                    else: #clicked_cell empty because of len 2 with 2 pop
                        self.time_start_event=pygame.time.get_ticks()
                        self.text_event = "Invalid pair"
                        
        elif 0 <= row < self.grid.n and 0 <= col < self.grid.m and self.grid.color[row][col] == 4:
            self.time_start_event=pygame.time.get_ticks()
            self.text_event = "Forbidden cell"
            self.clicked_cells.clear()

    def draw_buttons(self):
        if self.grid_menu:
            self.draw_main_menu_buttons()
        
        else:
            self.buttons = {}
            text_padding = 10  # Padding around text

            #Forfeit button to forfeit the game
            forfeit_text = self.text_font.render("Forfeit", True, (0, 0, 0))
            forfeit_width, forfeit_height = forfeit_text.get_width() + text_padding * 2, forfeit_text.get_height() + text_padding
            forfeit_button_x = self.width - forfeit_width - 10
            forfeit_button_y = self.height - forfeit_height - 10
            forfeit_button = pygame.draw.rect(self.screen, (200, 200, 200),
                                            (forfeit_button_x, forfeit_button_y, forfeit_width, forfeit_height))
            self.screen.blit(forfeit_text, (forfeit_button_x+text_padding, forfeit_button_y+text_padding/2))
            self.buttons["forfeit_button"] = [forfeit_button, self.end_current_game, [self.players_pairs[self.wich_turn], self.wich_turn]]
            
            #Menu button to go back to the main menu
            menu_text = self.text_font.render("Menu", True, (0, 0, 0))
            menu_width, menu_height = menu_text.get_width() + text_padding * 2, menu_text.get_height() + text_padding
            menu_button_x = self.width - menu_width - 10
            menu_button_y = 10
            menu_button = pygame.draw.rect(self.screen, (200, 200, 200),
                                            (menu_button_x, menu_button_y, menu_width, menu_height))
            self.screen.blit(menu_text, (menu_button_x+text_padding, menu_button_y+text_padding/2))
            self.buttons["menu_button"] = [menu_button, self.menu_button, None]
    
    def draw_all(self):
        self.draw_grid()
        self.draw_line_between_cells(self.linked_cells)
        self.draw_buttons()
        self.draw_event_text((self.width//2, self.height - self.border*0.25))
        self.draw_score((self.border//2, self.height - self.border), self.player0_pairs, score_text="Score of player 0 : ")
        self.draw_score((self.border//2, self.height - self.border+40), self.player1_pairs, score_text="Score of player 1 : ")

    def end_current_game(self, list_of_pairs: list[tuple[int,int]], player: Union[int, None] = 0, text_to_print: Union[str, None] = None):
        r"""End the current game and display the result.

        This method ends the game, displays the winner or a draw message, and 
        provides options to either start a new game or return to the main menu.

        Parameters
        ----------
        list_of_pairs : list of tuple of int
            The list of pairs that make up the current solution.
        player : int, optional
            The index of the player who forfeited the game (default is 0).
        text_to_print : str, optional
            Custom message to display at the end of the game (default is None).
        """

        if text_to_print is None:
            text_to_print = f"Player {player} forfeits the game, the player {1-player} wins with a score of {self.score(list_of_pairs)}"
        # Wait for button click
        waiting = True
        while waiting:
            self.draw_all()
            if self.is_finished():
                self.time_start_event = pygame.time.get_ticks()
                self.text_event = "Game finished"
            grey_overlay = pygame.Surface(self.screen.get_size())
            grey_overlay.fill((128, 128, 128))
            grey_overlay.set_alpha(180)  # Transparency for visual effect
            self.screen.blit(grey_overlay, (0, 0))

            # Adjust font size based on screen size
            font_size = max(24, min(self.screen.get_width() // 20, 72))-2  # Scale font size dynamically
            font = pygame.font.SysFont(None, font_size)
            text = font.render(text_to_print, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)

            # Display buttons for "New Game" and "Menu"
            button_font = self.text_font
            button_padding = 10

            # New Game button
            new_game_text = button_font.render("New Game", True, (255, 255, 255))
            new_game_width, new_game_height = new_game_text.get_width() + button_padding * 2, new_game_text.get_height() + button_padding
            new_game_button_x = self.screen.get_width() // 2 - new_game_width - 10
            new_game_button_y = self.screen.get_height() // 2 + text_rect.height + 20
            new_game_button = pygame.draw.rect(self.screen, (0, 128, 0),
                            (new_game_button_x, new_game_button_y, new_game_width, new_game_height))
            self.screen.blit(new_game_text, (new_game_button_x + button_padding, new_game_button_y + button_padding / 2))

            # Menu button
            menu_text = button_font.render("Menu", True, (255, 255, 255))
            menu_width, menu_height = menu_text.get_width() + button_padding * 2, menu_text.get_height() + button_padding
            menu_button_x = self.screen.get_width() // 2 + 10
            menu_button_y = new_game_button_y
            menu_button = pygame.draw.rect(self.screen, (128, 0, 0),
                            (menu_button_x, menu_button_y, menu_width, menu_height))
            self.screen.blit(menu_text, (menu_button_x + button_padding, menu_button_y + button_padding / 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    # self.width, self.height = self.width + 2*self.border, self.height + 2*self.border
                    self.adjust_for_resize()
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.scroll_offset = min(self.scroll_offset + self.scroll_speed, 0)  # Défilement vers le haut
                    elif event.y < 0:
                        self.scroll_offset = max(self.scroll_offset - self.scroll_speed, self.max_scroll)  # Défilement vers le bas            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_button.collidepoint(event.pos):
                        self.reset_grid()
                        waiting = False  
                        self.grid_menu = False
                    elif menu_button.collidepoint(event.pos):
                        self.reset_grid()
                        self.grid_menu = True
                        waiting = False

            pygame.display.flip()


class PygamePlayerVsPlayerGame(PygameTwoPlayerGame):
    def run(self):
        self.draw_buttons()
        self.adjust_for_resize()
        while self.running:
            self.text_event = "Tour du joueur " + str(self.wich_turn)
            self.time_start_event = pygame.time.get_ticks()
            if self.grid_menu:
                self.screen.fill((138,32,100))
                self.draw_buttons()
                self.draw_scrollbar()
                                                                                                                                                                                                                                                                               
            else: #If we display a grid
                self.draw_all()
                if self.is_finished():
                    if self.score(self.player0_pairs) < self.score(self.player1_pairs):
                        self.time_start_event = pygame.time.get_ticks()
                        self.end_current_game(self.players_pairs[0], text_to_print=f"Player {0} wins with a score of {self.score(self.players_pairs[0])}")
                    elif self.score(self.player0_pairs) == self.score(self.player1_pairs):
                        self.time_start_event = pygame.time.get_ticks()
                        self.end_current_game(self.players_pairs[0], text_to_print=f"Egalité des joueurs avec un score de {self.score(self.players_pairs[0])}")
                    else:
                        self.time_start_event = pygame.time.get_ticks()
                        self.end_current_game(self.players_pairs[1], text_to_print=f"Player {1} wins with a score of {self.score(self.players_pairs[1])}")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if self.buttons[button][0].collidepoint(event.pos) and self.buttons[button][2] is not None:
                            self.buttons[button][1](*self.buttons[button][2]) # Call the button function
                        elif self.buttons[button][0].collidepoint(event.pos):
                            self.buttons[button][1]()
                    if not self.grid_menu: 
                        self.handle_cell_click(event.pos)
                if event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    # self.width, self.height = self.width + 2*self.border, self.height + 2*self.border
                    self.adjust_for_resize()
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.scroll_offset = min(self.scroll_offset + self.scroll_speed, 0)  # Défilement vers le haut
                    elif event.y < 0:
                        self.scroll_offset = max(self.scroll_offset - self.scroll_speed, self.max_scroll)  # Défilement vers le bas            
                

            pygame.display.flip()
        pygame.quit()


    
class GameMenu:
    def __init__(self):
        self.master = tk.Tk()
        self.master.title("Le jeu des cases")
        self.master.protocol("WM_DELETE_WINDOW", self.quit_game)  # Handle window close event
        
        # Triple la taille de la police
        self.master.option_add("*Font", ("Arial", 24))

        # Définir la taille de la fenêtre et la centrer
        window_width = 800
        window_height = 600
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculer la position pour centrer la fenêtre
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        # Définir la géométrie de la fenêtre
        self.master.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')
        
        # Variables settings
        self.sound_effect = tk.BooleanVar(value=True)
        self.music_volume = tk.IntVar(value=50)
        self.computer_level = tk.IntVar(value=1)

        # Frames
        self.main_frame = tk.Frame(self.master)
        self.play_frame = tk.Frame(self.master)
        self.settings_frame = tk.Frame(self.master)
        self.credits_frame = tk.Frame(self.master)


    def clear_frames(self):
        for frame in (self.main_frame, self.play_frame, self.settings_frame, self.credits_frame):
            for widget in frame.winfo_children():
                widget.destroy()
            frame.pack_forget()

    def build_main_menu(self):
        self.clear_frames()
        self.main_frame.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)
        
        # Titre du jeu
        title = tk.Label(self.main_frame, text="Le jeu des cases", font=("Arial", 32))
        title.pack(pady=20)
        
        # Boutons du menu principal
        tk.Button(self.main_frame, text="Play", command=self.show_play_menu).pack(pady=10)
        tk.Button(self.main_frame, text="Settings", command=self.show_settings_menu).pack(pady=10)
        tk.Button(self.main_frame, text="Credits", command=self.show_credits_menu).pack(pady=10)
        tk.Button(self.main_frame, text="Quit game", command=self.quit_game).pack(pady=10)

        
    def show_play_menu(self):
        self.clear_frames()
        self.play_frame.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)
        
        # Titre du menu Play
        title = tk.Label(self.play_frame, text="Play Menu", font=("Arial", 32))
        title.pack(pady=30)

        # Modes de jeu
        modes = [
            ("Solo game", self.solo_game),
            ("two player game", self.two_player_game),
            ("Player versus computer", "Player versus computer"),
            ("Computer versus computer", "Computer versus computer")
        ]
        for text, function in modes:
            tk.Button(self.play_frame, text=text, command=function).pack(pady=15)
        
        # Bouton Back en haut à droite
        back_button = tk.Button(self.play_frame, text="Back", command=self.build_main_menu)
        back_button.place(relx=1.0, rely=0.0, x=-10, y=10, anchor='ne')

    def show_settings_menu(self):
        self.clear_frames()
        self.settings_frame.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)

        # Titre du menu Settings
        title = tk.Label(self.settings_frame, text="Settings", font=("Arial", 32))
        title.pack(pady=25)

        # Sound effect
        tk.Checkbutton(self.settings_frame, text="Sound effect on", variable=self.sound_effect,
                    command=lambda: print("Sound effect:", self.sound_effect.get())).pack(pady=10)

        # Music volume
        tk.Scale(self.settings_frame, from_=0, to=100, orient=tk.HORIZONTAL, variable=self.music_volume,
                label="Music volume", command=lambda val: print("Music volume:", val)).pack(pady=10)

        # Computer level
        tk.Label(self.settings_frame, text="Computer level:").pack(pady=10)
        level_frame = tk.Frame(self.settings_frame)
        level_frame.pack(pady=10)
        for i in range(1, 8):
            tk.Radiobutton(level_frame, text=str(i), variable=self.computer_level, value=i,
                        command=lambda i=i: print("Computer level:", i)).pack(side=tk.LEFT, padx=5)

        # Bouton Back en haut à droite
        back_button = tk.Button(self.settings_frame, text="Back", command=self.build_main_menu)
        back_button.place(relx=1.0, rely=0.0, x=-10, y=10, anchor='ne')

    def show_credits_menu(self):
        self.clear_frames()
        self.credits_frame.pack(padx=20, pady=20, expand=True, fill=tk.BOTH)

        # Titre des crédits
        title = tk.Label(self.credits_frame, text="Credits", font=("Arial", 32))
        title.pack(pady=20)

        # Crédit
        tk.Label(self.credits_frame, text="liraum opsa").pack(pady=20)

        # Bouton Back en haut à droite
        back_button = tk.Button(self.credits_frame, text="Back", command=self.build_main_menu)
        back_button.place(relx=1.0, rely=0.0, x=-10, y=10, anchor='ne')

    def solo_game(self):
        game = PygameSoloGame()
        self.master.withdraw()  # Hide the Tkinter window
        game.run()
        self.master.deiconify()  # Show the Tkinter window again
        self.build_main_menu()  # Rebuild the main menu after the game ends

    def two_player_game(self):
        game = PygamePlayerVsPlayerGame()
        self.master.withdraw()
        game.run()
        self.master.deiconify()
        self.build_main_menu()

    def quit_game(self):
        answer = messagebox.askquestion("Quit Game", "Are you sure you want to quit, all unsave progress will be reset")
        if answer == "yes":
            self.master.quit()
    
    def mainloop(self):
        r"""Start the Tkinter main loop for the game menu.

        This method starts the Tkinter main loop to display the game menu and
        allow user interaction with it.
        """

        self.build_main_menu()
        self.master.mainloop()

if __name__ == "__main__":
    menu = GameMenu()
    menu.mainloop()