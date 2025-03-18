import pygame
import sys
from grid import Grid 
from solver import SolverEmpty

class PygameGrid:
    def __init__(self, grid, cell_size=100, solver=None):
        self.grid = grid
        if solver is None:
            solver = SolverEmpty(grid)
        self.solver = solver
        self.cell_size = cell_size
        self.width = grid.m * cell_size
        self.height = grid.n * cell_size
        self.border = 75
        self.colors = [(255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 128, 0), (0, 0, 0)]  # white, red, blue, green, black
        pygame.init()
        self.screen = pygame.display.set_mode((self.width + 2*self.border, self.height + 2*self.border))
        self.font = pygame.font.Font(None, 36)
        self.clicked_cells = set()  # Store clicked cells
        self.linked_cells = set()  # Store linked cells
        self.used_cells = set() # Store used cells
        self.time_start_event = None # Store the time when the print event starts
        self.text_event = None # Store the text to print

    def draw_grid(self):
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
                text = self.font.render(str(self.grid.value[i][j]), True, (0, 0, 0))
                self.screen.blit(text, (self.border + j * self.cell_size + self.cell_size // 3, 
                                        self.border + i * self.cell_size + self.cell_size // 3))
        
        # Draw lines between linked cells
        for (i1, j1), (i2, j2) in self.solver.pairs:
            pygame.draw.line(self.screen, (0, 0, 0), 
                             (j1 * self.cell_size + self.border + self.cell_size // 2, i1 * self.cell_size + self.border + self.cell_size // 2), 
                             (j2 * self.cell_size + self.border + self.cell_size // 2, i2 * self.cell_size + self.border + self.cell_size // 2), 5)
        
        # Draw coordinates
        for i in range(self.grid.n):
            text = self.font.render(str(i), True, (0, 0, 0))
            self.screen.blit(text, (self.border//2, self.border + i * self.cell_size + self.cell_size // 3))
        for j in range(self.grid.m):
            text = self.font.render(str(j), True, (0, 0, 0))
            self.screen.blit(text, (self.border + j * self.cell_size + self.cell_size // 3, self.border//3))

        #Draw score on the bottom left of the screen
        score = self.solver.score()
        text = self.font.render(f"Score: {score}", True, (0, 0, 0))
        self.screen.blit(text, (self.border//2, self.height + self.border*1.25))
        
        #Draw the event text on the bottom of the screen
        if self.text_event is not None:
            text = pygame.font.SysFont('Arial', 30).render(self.text_event, True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.width//2 + self.border, self.height + self.border*1.5))
            self.screen.blit(text, text_rect)
            if pygame.time.get_ticks() - self.time_start_event > 1000:
                self.text_event = None
                self.time_start_event = None
        
    def handle_click(self, pos):
        x, y = pos
        col = (x - self.border) // self.cell_size
        row = (y - self.border) // self.cell_size
        if 0 <= row < self.grid.n and 0 <= col < self.grid.m and self.grid.color[row][col] != 4:
            if (row, col) in self.clicked_cells:
                self.clicked_cells.remove((row, col))  # go back to normal
            elif (row, col) in self.used_cells:
                self.time_start_event=pygame.time.get_ticks()
                self.text_event = "Cell already used"
                self.clicked_cells.clear()
            else:
                self.clicked_cells.add((row, col))  # mark cell in red
                if len(self.clicked_cells) == 2:
                    i1, j1 = self.clicked_cells.pop()
                    i2, j2 = self.clicked_cells.pop()
                    if self.grid.is_valid_pair(i1, j1, i2, j2):
                        self.solver.pairs.append(((i1, j1), (i2, j2)))
                        self.used_cells.add((i1, j1))
                        self.used_cells.add((i2, j2))
                    else: #clicked_cell empty because of len 2 with 2 pop
                        self.time_start_event=pygame.time.get_ticks()
                        self.text_event = "Invalid pair"
        elif 0 <= row < self.grid.n and 0 <= col < self.grid.m and self.grid.color[row][col] == 4:
            self.time_start_event=pygame.time.get_ticks()
            self.text_event = "Forbidden cell"
            self.clicked_cells.clear()

    def is_finished(self):#Check if the game is finished
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
     
       
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

            self.draw_grid()
            
            # Draw clear button
            button_pos_x= self.width + self.border//2
            button_pos_y = self.height + 1.25 * self.border
            button_rect = pygame.draw.rect(self.screen, (200, 200, 200), 
                                         (button_pos_x, button_pos_y, 70, 30))
            button_text = self.font.render("Clear", True, (0, 0, 0))
            self.screen.blit(button_text, (button_pos_x+5, button_pos_y+3))
            
            # Handle clear button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    self.clicked_cells.clear()
                    self.solver.pairs.clear()
                    self.used_cells.clear()
                    self.time_start_event = pygame.time.get_ticks()
                    self.text_event = "Reset"
            if self.is_finished():
                self.time_start_event = pygame.time.get_ticks()
                self.text_event = "Game finished"
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    grid = Grid.grid_from_file("input/grid05.in", read_values=True)
    game = PygameGrid(grid,cell_size=60)
    game.run()
