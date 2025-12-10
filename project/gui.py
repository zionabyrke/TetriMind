from settings import *
import time
import random

pygame.init()
"""
    pwede pala global mga instantiation ng classes
    pero variables, di pala pwede hahahhaa
"""

# game screen window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT+40))
pygame.display.set_caption("TetriMind")

clock = pygame.time.Clock()
font_title = pygame.font.SysFont("consolas", APPNAME_SIZE)
font_header = pygame.font.SysFont("consolas", 18)
font_style = pygame.font.SysFont("consolas", 12)

# surfaces 
playfield_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
preview_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT*PREVIEW_HEIGHT_FRACTION - PADDING))
score_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT*SCORE_HEIGHT_FRACTION))
controls_surface = pygame.Surface((LEFTBAR_WIDTH, CONTROLS_HEIGHT))
scoring_surface = pygame.Surface((LEFTBAR_WIDTH, SCORING_HEIGHT))
ghost_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

#buttons
pause_rect = pygame.Rect(RIGHTBAR_WIDTH + PADDING*2, GAME_HEIGHT+APPNAME_SIZE+PADDING,
                GAME_WIDTH//3, 30 ) #30 height
reset_rect = pygame.Rect(pause_rect.x + GAME_WIDTH//3, GAME_HEIGHT+APPNAME_SIZE+PADDING,
                GAME_WIDTH//3, 30 ) #30 height
menu_rect = pygame.Rect(pause_rect.x + (GAME_WIDTH//3)*2, GAME_HEIGHT+APPNAME_SIZE+PADDING,
                GAME_WIDTH//3, 30 ) #30 height

class Gui:
    def __init__(self):
        self.color_matrix = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
        self.running = True
        self.paused = False
        self.pause_label = "Pause"

        self.held_keys = []
        self.hold_delay = 0

    def run(self, game):
        while self.running:
            dt = clock.tick(FRAMEPERSEC)
            self.get_input(game)

            ### GAME LOGIC SECTION
            if not self.paused: #update only if not paused
                game.update(dt, self.color_matrix)
                game.update_clock(dt)
                self.pause_label = "Pause"
            else: 
                self.pause_label = "Resume"

            self.display_section(game)

            pygame.display.update()
        pygame.quit()

    def get_input(self, game):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # pause , reset button
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if pause_rect.collidepoint(event.pos):
                    self.paused = not self.paused
                if reset_rect.collidepoint(event.pos):
                    game.reset(game.bag.seed)
                    self.__init__()
                if menu_rect.collidepoint(event.pos):
                    pass # MENU SCREEN HERE
            elif self.paused == True:
                continue # no moving actions till resumed
            elif event.type == pygame.KEYDOWN:
                # Left, right, and down keys can be held down, rotation and hard drop can't be held
                if event.key == pygame.K_LEFT:
                    self.held_keys.append(MOVE_LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.held_keys.append(MOVE_RIGHT)
                elif event.key == pygame.K_DOWN:
                    self.held_keys.append(MOVE_DOWN)
                # Move variables are mapped to their corresponding pygame.key in settings.py
                # So this will move tetromino based on pressed key
                game.move_tetromino(event.key, self.color_matrix)
            elif event.type == pygame.KEYUP:
                self.hold_delay = 0
                if event.key == pygame.K_LEFT:
                    self.held_keys.remove(MOVE_LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.held_keys.remove(MOVE_RIGHT)
                elif event.key == pygame.K_DOWN:
                    self.held_keys.remove(MOVE_DOWN)

        # Move based on held key
        if self.held_keys:
            self.hold_delay += 1
            # Delay for 10 frames before player can fully hold, so it doesn't go too fast
            if self.hold_delay > 10:
                game.move_tetromino(self.held_keys[-1], self.color_matrix)

    def display_section(self, game):
        ### DISPLAY SECTION
        screen.fill(GRAY)
        playfield_surface.fill(BLACK)
        preview_surface.fill(BLACK)
        score_surface.fill(BLACK)
        controls_surface.fill(BLACK)
        scoring_surface.fill(BLACK)

        # Title text
        title_text = font_title.render("TETRIMIND", True, LINE_COLOR)
        screen.blit(title_text, (RIGHTBAR_WIDTH+PADDING*2 + (GAME_WIDTH-title_text.get_width())/2, PADDING/2))

        playfield(game, playfield_surface, self.color_matrix)
        screen.blit(playfield_surface, (RIGHTBAR_WIDTH + PADDING * 2, PADDING+APPNAME_SIZE))

        panels(game)
        buttons(self.pause_label)


# recycleable GLOBAL helpers
def playfield(game, surface, color_matrix, human=True):
    # playfield blocks 
    for y, row in enumerate(color_matrix):
        for x, color in enumerate(row):
            if color != BLACK:
                pygame.draw.rect(surface, color,
                                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # should be here so that
    # gridlines overshows the blocks
    # current tetromino shape
    if game.current_piece:
        shape = game.current_piece.get_shape_array()
        # tetromino piece
        for dx, dy in shape:
            pygame.draw.rect(surface, game.current_piece.color,
                            ((game.current_piece.coord[0] + dx) * CELL_SIZE,
                            (game.current_piece.coord[1] + dy) * CELL_SIZE,
                            CELL_SIZE, CELL_SIZE))

        # ghost piece
        if human:
            ghost_coords = game.ghost_piece()
            ghost_color = pygame.Color(game.current_piece.color)
            ghost_color.a = 64 #25% x 255 = 64 adjust
            ghost_surface.fill(ghost_color)
            for gx, gy in ghost_coords:
                surface.blit(ghost_surface, (gx*CELL_SIZE, gy*CELL_SIZE))

    # next tetromino piece
    if game.next_piece:
        shape = game.next_piece.get_shape_array()
        for x, y in shape:
            pygame.draw.rect(preview_surface, game.next_piece.color,
                            ((x*CELL_SIZE)+(45), PADDING+(y*CELL_SIZE)+30,
                            CELL_SIZE, CELL_SIZE))
    # draw gridlines
    for col in range(1, COLUMNS):
        x = col * CELL_SIZE
        pygame.draw.line(surface, GRAY, (x, 0), (x, GAME_HEIGHT), 1)
    for row in range(1, ROWS):
        y = row * CELL_SIZE
        pygame.draw.line(surface, GRAY, (0, y), (GAME_WIDTH, y), 1)
    
def panels(game):
    # texts
    score_text = font_header.render("     SCORE:", True, LINE_COLOR)
    score_amount = font_header.render(f"       {game.player_score}", True, LINE_COLOR)
    level_text = font_header.render(f"     LEVEL: {game.game_level}", True, LINE_COLOR)
    time_text = font_header.render(f"     TIME: %02d:%02d" % ((game.elapsed_time//1000)//60, (game.elapsed_time//1000)%60), True, LINE_COLOR)
    preview_text = font_header.render("     NEXT", True, LINE_COLOR)
    # draw control and surface text line by line
    for x, text in enumerate(CONTROLS_TEXT):
        controls_text = font_style.render(text, True, LINE_COLOR)
        controls_surface.blit(controls_text, (PADDING, PADDING+(x*20)))

    for x, text in enumerate(SCORING_TEXT):
        scoring_text = font_style.render(text, True, LINE_COLOR)
        scoring_surface.blit(scoring_text, (PADDING, PADDING+(x*20)))

    score_surface.blit(score_text, (PADDING, PADDING))
    score_surface.blit(score_amount, (PADDING, PADDING+30))
    score_surface.blit(level_text, (PADDING, PADDING + 80))
    score_surface.blit(time_text, (PADDING, PADDING + 130))
    preview_surface.blit(preview_text, (PADDING, PADDING))

    score_rect = score_surface.get_rect(topleft=(PADDING, PADDING+APPNAME_SIZE))
    preview_rect = preview_surface.get_rect(
        bottomleft=(PADDING, score_rect.bottom + preview_surface.get_height() + PADDING))
    controls_rect = controls_surface.get_rect(topright=(WINDOW_WIDTH-PADDING, PADDING+APPNAME_SIZE))
    scoring_rect = scoring_surface.get_rect(bottomright=(WINDOW_WIDTH-PADDING, +CONTROLS_HEIGHT+SCORING_HEIGHT+PADDING*2+APPNAME_SIZE))

    screen.blit(score_surface, score_rect)
    screen.blit(preview_surface, preview_rect)
    screen.blit(controls_surface, controls_rect)
    screen.blit(scoring_surface, scoring_rect)

def buttons(pause_label):
    # button box
    pygame.draw.rect(screen, BLACK, pause_rect) #fill
    pygame.draw.rect(screen, GRAY, pause_rect, 4) #4px border/gaps
    pause_text= font_header.render(pause_label, True, LINE_COLOR)
    screen.blit(pause_text, (pause_rect.x + (pause_rect.width-pause_text.get_width())// 2, 
                            pause_rect.y + (pause_rect.height-pause_text.get_height())// 2))

    pygame.draw.rect(screen, BLACK, reset_rect)#fill
    pygame.draw.rect(screen, GRAY, reset_rect, 4)#4px border/gaps
    reset_text= font_header.render("Reset", True, LINE_COLOR)
    screen.blit(reset_text, (reset_rect.x + (reset_rect.width-reset_text.get_width())// 2,
                            reset_rect.y + (reset_rect.height-reset_text.get_height())// 2))

    pygame.draw.rect(screen, BLACK, menu_rect)#fill
    pygame.draw.rect(screen, GRAY, menu_rect, 4)#4px border/gaps
    menu_text = font_header.render("Menu", True, LINE_COLOR)
    screen.blit(menu_text , (menu_rect.x + (menu_rect.width-menu_text.get_width())// 2,
                            menu_rect.y + (menu_rect.height-menu_text.get_height())// 2 ))