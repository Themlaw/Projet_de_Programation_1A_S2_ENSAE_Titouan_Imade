import pygame
import sys
from grid import Grid 
from solver import SolverEmpty
import math

class PygameGrid():
    def __init__(self):
        self.grid = Grid(3,4)
        self.solver = SolverEmpty(self.grid)
        self.cell_size = 100
        self.width = self.grid.m * self.cell_size
        self.height = self.grid.n * self.cell_size
        self.border = 75
        self.colors = [(255, 255, 255), (255, 0, 0), (0, 0, 255), (0, 128, 0), (0, 0, 0)]  # white, red, blue, green, black
        pygame.init()
        self.screen = pygame.display.set_mode((self.width + 2*self.border, self.height + 2*self.border),pygame.RESIZABLE)
        self.width = self.width + 2*self.border
        self.height = self.height + 2*self.border
        self.text_font = pygame.font.SysFont('Arial', 30) #We differentiate the font for texte and cell/coordinate 
        self.cell_font = pygame.font.SysFont('Arial', 30)
        self.clicked_cells = []  # Store clicked cells
        self.linked_cells = set()  # Store linked cells
        self.used_cells = set() # Store used cells
        self.time_start_event = None # Store the time when the print event starts
        self.text_event = None # Store the text to print
        self.buttons = {} # Store the buttons
        self.main_menu = True # Check if the main menu is displayed
        self.button_width, self.button_height = 200, 30
        self.base_button_height = 50 # Base height of the buttons for the resize 
        self.scroll_offset = 0
        self.scroll_speed = 20
        self.offset_button = 10 #Create a gap between buttons on the main menu
        self.max_scroll = -(len(self.buttons) * (self.button_height ) - self.height)
        self.scrollbar_width = 10
        self.all_grid_index = ["00","01","02","03","04","05","11","12","13","14","15","16","17","18","19","21","22","23","24","25","26","27","28","29"]

    def adjust_for_resize(self):
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
        
        # Draw lines between linked cells
        for (i1, j1), (i2, j2) in self.solver.pairs:
            pygame.draw.line(self.screen, (0, 0, 0), 
                             (j1 * self.cell_size + self.border + self.cell_size // 2, i1 * self.cell_size + self.border + self.cell_size // 2), 
                             (j2 * self.cell_size + self.border + self.cell_size // 2, i2 * self.cell_size + self.border + self.cell_size // 2), 5)
        
        # Draw coordinates
        for i in range(self.grid.n):
            text = self.cell_font.render(str(i), True, (0, 0, 0))
            self.screen.blit(text, (self.border//2, self.border + i * self.cell_size + self.cell_size // 3))
        for j in range(self.grid.m):
            text = self.cell_font.render(str(j), True, (0, 0, 0))
            self.screen.blit(text, (self.border + j * self.cell_size + self.cell_size // 3, self.border//3))

        #Draw score on the bottom left of the screen
        score = self.solver.score()
        text = self.text_font.render(f"Score: {score}", True, (0, 0, 0))
        self.screen.blit(text, (self.border//2, self.height - self.border+20))
        
        #Draw the event text on the bottom of the screen
        if self.text_event is not None:
            text = self.text_font.render(self.text_event, True, (0, 0, 0))
            text_rect = text.get_rect(center=(self.width//2, self.height - self.border*0.5))
            self.screen.blit(text, text_rect)
            if pygame.time.get_ticks() - self.time_start_event > 1000:
                self.text_event = None
                self.time_start_event = None

    def draw_buttons(self):
        if self.main_menu:
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
                self.buttons[button_name] = [button,self.switch_to_grid_button,index]
        
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
            
            
            #We add a menu button on the top right cornet pf the screen to go back to the main menu
            menu_text = self.text_font.render("Menu", True, (0, 0, 0))
            menu_width, menu_height = menu_text.get_width() + text_padding * 2, menu_text.get_height() + text_padding
            menu_button_x = self.width - menu_width - 10
            menu_button_y = 10
            menu_button = pygame.draw.rect(self.screen, (200, 200, 200),
                                            (menu_button_x, menu_button_y, menu_width, menu_height))
            self.screen.blit(menu_text, (menu_button_x+text_padding, menu_button_y+text_padding/2))
            self.buttons["menu_button"] = [menu_button, self.menu_button, None]
    
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
            elif len(self.clicked_cells) == 0: # We add the first cell every time
                self.clicked_cells.append((row, col))
            elif len(self.clicked_cells) == 1 and ((row, col) in self.used_cells or self.clicked_cells[0] in self.used_cells): #If one of the cell is already used
                if ((row,col),self.clicked_cells[0]) in self.solver.pairs or (self.clicked_cells[0],(row,col)) in self.solver.pairs: #if we reclick on a matched pair
                    self.time_start_event=pygame.time.get_ticks()
                    self.text_event = "Pair undo"
                    self.used_cells.remove((row,col))
                    self.used_cells.remove(self.clicked_cells[0])
                    if ((row,col),self.clicked_cells[0]) in self.solver.pairs:
                        self.solver.pairs.remove(((row,col),self.clicked_cells[0]))
                    else:
                        self.solver.pairs.remove(((self.clicked_cells[0],(row,col))))
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
            
    def clear_button(self,**kwargs):
        self.clicked_cells.clear()
        self.solver.pairs.clear()
        self.used_cells.clear()
        self.time_start_event = pygame.time.get_ticks()
        self.text_event = "Reset"
    
    def switch_to_grid_button(self,grid_index,**kwargs):
        self.grid = Grid.grid_from_file("./input/grid"+grid_index+".in", read_values=True)
        self.solver = SolverEmpty(self.grid)
        self.main_menu = False
        self.adjust_for_resize()
        self.clicked_cells.clear()
    
    def show_solution_button(self,**kwargs):
        self.time_start_event = pygame.time.get_ticks()
        self.text_event = "Showing solution"
    
    def menu_button(self,**kwargs):
        self.main_menu = True
        self.draw_buttons()
        self.width, self.height = 550, 450
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.adjust_for_resize()
        self.clicked_cells.clear()
        self.solver.pairs.clear()
        self.used_cells.clear()
    
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
        self.draw_buttons()
        self.adjust_for_resize()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.main_menu:
                        # for button in self.buttons:
                        #     if self.buttons[button][0].collidepoint(event.pos):
                        #         self.buttons[button][1](self.buttons[button][2])
                        pass
                    else:
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
            
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in self.buttons:
                        if self.buttons[button][0].collidepoint(event.pos) and self.buttons[button][2] is not None:
                            self.buttons[button][1](self.buttons[button][2]) # Call the button function
                        elif self.buttons[button][0].collidepoint(event.pos):
                            self.buttons[button][1]()
            
            if self.main_menu:
                self.screen.fill((138,32,100))
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
    game = PygameGrid()
    game.run()
