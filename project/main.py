from settings import *
from game import Playfield, GameInfo
from menu import show_menu
import time

pygame.init()

# Menu 
game_mode, ai_difficulty = show_menu()

# Small delay to ensure menu window closes cleanly
time.sleep(0.1)

# Re-initialize pygame display for the game
pygame.display.quit()
pygame.display.init()

# Initialize settings based on menu selection
import settings
settings.GAME_MODE = game_mode
settings.AI_DIFFICULTY = ai_difficulty

# game screen window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("TetriMind")

# components
clock = pygame.time.Clock()
info = GameInfo()
field = Playfield(info)

# Initialize color matrix to track block colors
colorMatrix = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]

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

# GAME LOOP
running = True
while running:
    dt = clock.tick(FRAMEPERSEC)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == MOVE_LEFT:
                field.moveTetromino(MOVE_LEFT, colorMatrix)
            elif event.key == MOVE_RIGHT:
                field.moveTetromino(MOVE_RIGHT, colorMatrix)
            elif event.key == MOVE_DOWN:
                field.moveTetromino(MOVE_DOWN, colorMatrix)
            elif event.key == ROTATE_LEFT:
                field.moveTetromino(ROTATE_LEFT, colorMatrix)
            elif event.key == ROTATE_RIGHT:
                field.moveTetromino(ROTATE_RIGHT, colorMatrix)
            elif event.key == HARD_DROP:
                field.moveTetromino(HARD_DROP, colorMatrix)

    # GAME LOGIC SECTION
    field.update(dt, colorMatrix)
    info.updateGameInfo(dt)

    # DISPLAY SECTION
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

    # ghost piece 
    ghost_coords = field.ghost_piece()
    for x, y in ghost_coords:
        ghost_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
        ghost_surface.set_alpha(50)
        ghost_surface.fill(field.currentPiece.color)
        playfield_surface.blit(ghost_surface, (x * CELL_SIZE, y * CELL_SIZE))

    # current tetromino shape
    if field.currentPiece:
        shape = field.currentPiece.getShapeArray()
        for dx, dy in shape:
            x = field.currentPiece.coord[0] + dx
            y = field.currentPiece.coord[1] + dy
            pygame.draw.rect(playfield_surface, field.currentPiece.color,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

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

    # Score surface texts
    score_text = font_header.render("SCORE", True, LINE_COLOR)
    score_value = font_header.render(str(info.playerScore), True, LINE_COLOR)
    level_text = font_header.render("LEVEL", True, LINE_COLOR)
    level_value = font_header.render(str(info.gameLevel), True, LINE_COLOR)
    
    score_surface.blit(score_text, (PADDING + 40, PADDING))
    score_surface.blit(score_value, (PADDING + 50, PADDING + 30))
    score_surface.blit(level_text, (PADDING + 40, PADDING + 80))
    score_surface.blit(level_value, (PADDING + 60, PADDING + 110))

    # Next piece preview
    if field.nextPiece:
        preview_title = font_header.render("NEXT", True, LINE_COLOR)
        preview_surface.blit(preview_title, (PADDING + 60, PADDING))
        
        # Draw next piece centered in preview
        next_shape = field.nextPiece.getShapeArray()
        offset_x = 60
        offset_y = 60
        for dx, dy in next_shape:
            pygame.draw.rect(preview_surface, field.nextPiece.color,
                           ((dx * CELL_SIZE) + offset_x, 
                            (dy * CELL_SIZE) + offset_y, 
                            CELL_SIZE, CELL_SIZE))

    # Controls text
    y_offset = PADDING
    for line in CONTROLS_TEXT:
        text = font.render(line, True, LINE_COLOR)
        controls_surface.blit(text, (PADDING, y_offset))
        y_offset += 20

    # Scoring text
    y_offset = PADDING
    for line in SCORING_TEXT:
        text = font.render(line, True, LINE_COLOR)
        scoring_surface.blit(text, (PADDING, y_offset))
        y_offset += 20

    # display surfaces
    screen.blit(playfield_surface, (RIGHTBAR_WIDTH + PADDING * 2, PADDING+APPNAME_SIZE))
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