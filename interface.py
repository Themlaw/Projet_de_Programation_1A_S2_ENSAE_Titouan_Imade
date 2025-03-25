import pygame
import sys
from grid import Grid 
from solver import SolverEmpty

class PygameGrid():
    def __init__(self, grid, cell_size=100, solver=None):
        self.grid = grid
        if solver is None:
            self.solver = SolverEmpty(grid)
        self.cell_size = cell_size
        self.width = grid.m * cell_size
        self.height = grid.n * cell_size
        self.border = 75
        self.colors = [(255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 128, 0), (0, 0, 0)]  # white, red, blue, green, black
        pygame.init()
        self.screen = pygame.display.set_mode((self.width + 2*self.border, self.height + 2*self.border),pygame.RESIZABLE)
        self.width = self.width + 2*self.border
        self.height = self.height + 2*self.border
        self.font = pygame.font.SysFont('Arial', 30)
        self.clicked_cells = set()  # Store clicked cells
        self.linked_cells = set()  # Store linked cells
        self.used_cells = set() # Store used cells
        self.time_start_event = None # Store the time when the print event starts
        self.text_event = None # Store the text to print
        self.buttons = {} # Store the buttons
        self.main_menu = False # Check if the main menu is displayed
        self.button_width, self.button_height = 200, 40
        self.scroll_offset = 0
        self.scroll_speed = 20
        self.max_scroll = -(len(self.buttons) * self.button_height - self.height)
        self.scrollbar_width = 10

    def adjust_for_resize(self):
        # Adapter la taille des boutons en fonction de la largeur de l'écran
        self.button_width = self.width // 2
        self.button_height = max(40, self.height // len(self.buttons))  # Assurez-vous que la hauteur des boutons ne soit pas trop petite
        self.max_scroll = -(len(self.buttons) * self.button_height - self.height)


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
                                        self.border + i * self.cell_size + self.cell_size/4))
        
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
            text = self.font.render(self.text_event, True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.width//2 + self.border, self.height + self.border*1.5))
            self.screen.blit(text, text_rect)
            if pygame.time.get_ticks() - self.time_start_event > 1000:
                self.text_event = None
                self.time_start_event = None

    def draw_buttons(self):
        if self.main_menu:
            y_pos = self.scroll_offset
            for button_text in self.buttons:
                # Dessiner les boutons
                pygame.draw.rect(self.screen, (50, 150, 255), (self.width // 4, y_pos, self.button_width, self.button_height))
                text_surface = self.font.render(button_text, True, (255, 255, 255))
                self.screen.blit(text_surface, (self.width // 4 + 10, y_pos + 10))
                y_pos += self.button_height+10
        
        else:
            self.buttons = {}
            # Draw clear button
            clear_button_x = self.width + self.border/2+20
            clear_button_y = self.height + 1.09 * self.border
            clear_button = pygame.draw.rect(self.screen, (200, 200, 200), 
                                         (clear_button_x, clear_button_y, 55, 30))
            clear_text = pygame.font.SysFont('Arial', 20).render("Reset", True, (0, 0, 0))
            self.screen.blit(clear_text, (clear_button_x+5, clear_button_y+2))
            
            self.buttons["clear_button"] = [clear_button, self.clear_button]
            
            # Draw show solution button
            solution_button_x = self.width + self.border/4+10
            solution_button_y = self.height + 1.55 * self.border
            solution_button = pygame.draw.rect(self.screen, (200, 200, 200), 
                                         (solution_button_x, solution_button_y, 110, 30))
            solution_text = pygame.font.SysFont('Arial', 20).render("Show solution", True, (0, 0, 0))
            self.screen.blit(solution_text, (solution_button_x+3, solution_button_y+1))
            
            self.buttons["solution_button"] = [solution_button,self.show_solution_button]
    
    def draw_scrollbar(self):
        # Calculer la hauteur de la barre de défilement
        scrollbar_height = self.height * (self.height / (len(self.buttons) * self.button_height))
        scrollbar_pos_y = -self.scroll_offset * (self.height / (len(self.buttons) * self.button_height))
        # Dessiner la barre de défilement à droite
        pygame.draw.rect(self.screen, (100, 100, 100), (self.width - self.scrollbar_width, scrollbar_pos_y, self.scrollbar_width, scrollbar_height))

    
    def handle_cell_click(self, pos):
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
            
    def clear_button(self):
        self.clicked_cells.clear()
        self.solver.pairs.clear()
        self.used_cells.clear()
        self.time_start_event = pygame.time.get_ticks()
        self.text_event = "Reset"
    
    def show_solution_button(self):
        self.time_start_event = pygame.time.get_ticks()
        self.text_event = "Showing solution"
    
    def handle_cell_click(self,pos):
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
        all_grid_index = ["00","01","02","03","04","05","11","12","13","14","15","16","17","18","19","21","22","23","24","25","26","27","28","29"]
        for index in all_grid_index:
            self.buttons["Grid "+index] = [pygame.Rect(self.width // 4, 0, self.button_width, self.button_height)]
        self.adjust_for_resize()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_cell_click(event.pos)
                if event.type == pygame.VIDEORESIZE:
                    self.width, self.height = event.size
                    self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                    self.adjust_for_resize()
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        self.scroll_offset = min(self.scroll_offset + self.scroll_speed, 0)  # Défilement vers le haut
                    elif event.y < 0:
                        self.scroll_offset = max(self.scroll_offset - self.scroll_speed, self.max_scroll)  # Défilement vers le bas
            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if self.buttons[button][0].collidepoint(event.pos):
                            self.buttons[button][1]() # Call the button function
            
            if self.main_menu:
                self.screen.fill((0,0,0))
                self.draw_buttons()
                self.draw_scrollbar()
                                                                                                                                                                                                                                                                                                   
            else: #If we display a grid
                self.draw_grid()
                self.draw_buttons()
                if self.is_finished():
                    self.time_start_event = pygame.time.get_ticks()
                    self.text_event = "Game finished"

            pygame.display.flip()
        pygame.quit()



if __name__ == "__main__":
    grid = Grid.grid_from_file("input/grid05.in", read_values=True)
    game = PygameGrid(grid,cell_size=60)
    game.run()
