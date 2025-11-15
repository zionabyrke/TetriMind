from settings import *
from game import Playfield, GameInfo
from menu import show_menu

import time
import settings #module iba sa settings.py

pygame.init()

## Menu 
game_mode, ai_difficulty = show_menu()
# Small delay to ensure menu window closes cleanly
time.sleep(0.1)

# Re-initialize pygame display for the game
pygame.display.quit()
pygame.display.init()

# Initialize settings based on menu selection
settings.GAME_MODE = game_mode
settings.AI_DIFFICULTY = ai_difficulty

# game screen window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT+40))
pygame.display.set_caption("TetriMind")

# components
clock = pygame.time.Clock()
info = GameInfo()
field = Playfield(info)

colorMatrix = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
held_keys = []
hold_delay = 0

# can have different font for different texts 
font_title = pygame.font.SysFont("consolas", APPNAME_SIZE)
font_header = pygame.font.SysFont("consolas", 18)
font = pygame.font.SysFont("consolas", 12)

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

##### GAME LOOP
running = True
paused = False
while running:
    dt = clock.tick(FRAMEPERSEC)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # pause , reset button
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pause_rect.collidepoint(event.pos):
                paused = not paused
            if reset_rect.collidepoint(event.pos):
                pass # RESET METHOD HERE #########
            if menu_rect.collidepoint(event.pos):
                pass # MENU SCREEN HERE
        elif paused == True:
            continue # no moving actions till resumed
        elif event.type == pygame.KEYDOWN:
            # Left, right, and down keys can be held down, rotation and hard drop can't be held
            if event.key == pygame.K_LEFT:
                held_keys.append(MOVE_LEFT)
            elif event.key == pygame.K_RIGHT:
                held_keys.append(MOVE_RIGHT)
            elif event.key == pygame.K_DOWN:
                held_keys.append(MOVE_DOWN)
            # Move variables are mapped to their corresponding pygame.key in settings.py
            # So this will move tetromino based on pressed key
            field.moveTetromino(event.key, colorMatrix)
        elif event.type == pygame.KEYUP:
            hold_delay = 0
            if event.key == pygame.K_LEFT:
                held_keys.remove(MOVE_LEFT)
            elif event.key == pygame.K_RIGHT:
                held_keys.remove(MOVE_RIGHT)
            elif event.key == pygame.K_DOWN:
                held_keys.remove(MOVE_DOWN)

    # Move based on held key
    if held_keys:
        hold_delay += 1
        # Delay for 10 frames before player can fully hold, so it doesn't go too fast
        if hold_delay > 10:
            field.moveTetromino(held_keys[-1], colorMatrix)

    ### GAME LOGIC SECTION
    if not paused: #update only if not paused
        field.update(dt, colorMatrix)
        info.updateGameInfo(dt)
        pause_label = "Pause"
    else: 
        pause_label = "Resume"

    ### DISPLAY SECTION
    screen.fill(GRAY)
    playfield_surface.fill(BLACK)
    preview_surface.fill(BLACK)
    score_surface.fill(BLACK)
    controls_surface.fill(BLACK)
    scoring_surface.fill(BLACK)

    # playfield blocks 
    for y, row in enumerate(colorMatrix):
        for x, color in enumerate(row):
            if color != BLACK:
                pygame.draw.rect(playfield_surface, color,
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # current tetromino shape
    if field.currentPiece:
        shape = field.currentPiece.getShapeArray()
        ghost_coords = field.ghost_piece()
        ghost_color = pygame.Color(field.currentPiece.color)
        ghost_color.a = 64 #25% x 255 = 64 adjust

        # tetromino piece
        for dx, dy in shape:
            pygame.draw.rect(playfield_surface, field.currentPiece.color,
                             ((field.currentPiece.coord[0] + dx) * CELL_SIZE,
                              (field.currentPiece.coord[1] + dy) * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE))

        # ghost piece 
        ghost_surface.fill(ghost_color)
        for gx, gy in ghost_coords:
            playfield_surface.blit(ghost_surface, (gx*CELL_SIZE, gy*CELL_SIZE))
    
    # next tetromino piece
    if field.nextPiece:
        shape = field.nextPiece.getShapeArray()
        for x, y in shape:
            pygame.draw.rect(preview_surface, field.nextPiece.color,
                             ((x*CELL_SIZE)+(45), PADDING+(y*CELL_SIZE)+30,
                             CELL_SIZE, CELL_SIZE))

    # draw gridlines
    for col in range(1, COLUMNS):
        x = col * CELL_SIZE
        pygame.draw.line(playfield_surface, GRAY, (x, 0), (x, GAME_HEIGHT), 1)
    for row in range(1, ROWS):
        y = row * CELL_SIZE
        pygame.draw.line(playfield_surface, GRAY, (0, y), (GAME_WIDTH, y), 1)

    # Title text
    title_text = font_title.render("TETRIMIND", True, LINE_COLOR)
    screen.blit(title_text, (RIGHTBAR_WIDTH+PADDING*2 + (GAME_WIDTH-title_text.get_width())/2, PADDING/2))

    score_text = font_header.render("     SCORE:", True, LINE_COLOR)
    score_amount = font_header.render(f"       {info.playerScore}", True, LINE_COLOR)
    level_text = font_header.render(f"     LEVEL: {info.gameLevel}", True, LINE_COLOR)
    score_surface.blit(score_text, (PADDING, PADDING))
    score_surface.blit(score_amount, (PADDING, PADDING+30))
    score_surface.blit(level_text, (PADDING, PADDING + 80))
    time_text = font_header.render(f"     TIME: %02d:%02d" % ((info.elapsedTime//1000)//60, (info.elapsedTime//1000)%60), True, LINE_COLOR)
    score_surface.blit(time_text, (PADDING, PADDING + 130))

    preview_text = font_header.render("     NEXT", True, LINE_COLOR)
    preview_surface.blit(preview_text, (PADDING, PADDING))

    # draw control and surface text line by line
    for x, text in enumerate(CONTROLS_TEXT):
        controls_text = font.render(text, True, LINE_COLOR)
        controls_surface.blit(controls_text, (PADDING, PADDING+(x*20)))

    for x, text in enumerate(SCORING_TEXT):
        scoring_text = font.render(text, True, LINE_COLOR)
        scoring_surface.blit(scoring_text, (PADDING, PADDING+(x*20)))

    ## display surfaces
    screen.blit(playfield_surface, (RIGHTBAR_WIDTH + PADDING * 2, PADDING+APPNAME_SIZE))
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
    
    # score
    score_rect = score_surface.get_rect(topleft=(PADDING, PADDING+APPNAME_SIZE))
    screen.blit(score_surface, score_rect)
    # preview
    preview_rect = preview_surface.get_rect(
        bottomleft=(PADDING, score_rect.bottom + preview_surface.get_height() + PADDING))
    screen.blit(preview_surface, preview_rect)
    # controls
    controls_rect = controls_surface.get_rect(topright=(WINDOW_WIDTH-PADDING, PADDING+APPNAME_SIZE))
    screen.blit(controls_surface, controls_rect)
    # scoring
    scoring_rect = scoring_surface.get_rect(bottomright=(WINDOW_WIDTH-PADDING, +CONTROLS_HEIGHT+SCORING_HEIGHT+PADDING*2+APPNAME_SIZE))
    screen.blit(scoring_surface, scoring_rect)

    pygame.display.update()

pygame.quit()