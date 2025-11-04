from settings import *
from game import Playfield, GameInfo

pygame.init()
# game screen window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("TetriMind")

# components
clock = pygame.time.Clock()
info = GameInfo()
field = Playfield(info)
# can have different font for different texts 
font_title = pygame.font.SysFont("consolas", APPNAME_SIZE)
font_header = pygame.font.SysFont("consolas", 18)
font = pygame.font.SysFont("consolas", 12)

# surfaces (like a textbox)
playfield_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
preview_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT*PREVIEW_HEIGHT_FRACTION - PADDING))
score_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT*SCORE_HEIGHT_FRACTION))
controls_surface = pygame.Surface((LEFTBAR_WIDTH, CONTROLS_HEIGHT))
scoring_surface = pygame.Surface((LEFTBAR_WIDTH, SCORING_HEIGHT))

##### GAME LOOP
running = True
while running:
    dt = clock.tick(FRAMEPERSEC)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                field.moveTetromino("left")
            elif event.key == pygame.K_RIGHT:
                field.moveTetromino("right")
            elif event.key == pygame.K_DOWN:
                field.moveTetromino("down")
            elif event.key == pygame.K_z:
                field.moveTetromino("rotate_left")
            elif event.key == pygame.K_x:
                field.moveTetromino("rotate_right")
            elif event.key == pygame.K_SPACE:
                field.moveTetromino("hard_drop")

    ### GAME LOGIC SECTION
    field.update(dt)
    info.updateGameInfo()

    ### DISPLAY SECTION
    # fills
    screen.fill(GRAY)
    playfield_surface.fill(BLACK)
    preview_surface.fill(BLACK)
    score_surface.fill(BLACK)
    controls_surface.fill(BLACK)
    scoring_surface.fill(BLACK)

    # playfield blocks
    for y, row in enumerate(field.blockMatrix):
        for x, color in enumerate(row):
            if color:
                pygame.draw.rect(playfield_surface, color,
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # current tetromino shape
    if field.currentPiece:
        shape = field.currentPiece.getShapeArray()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(playfield_surface, field.currentPiece.color,
                                     ((field.currentPiece.coord[0] + x) * CELL_SIZE,
                                      (field.currentPiece.coord[1] + y) * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))

    # draw gridlines
    for col in range(1, COLUMNS):
        x = col * CELL_SIZE
        pygame.draw.line(playfield_surface, GRAY, (x, 0), (x, GAME_HEIGHT), 1)
    for row in range(1, ROWS):
        y = row * CELL_SIZE
        pygame.draw.line(playfield_surface, GRAY, (0, y), (GAME_WIDTH, y), 1)

    # score_surface's texts
    title_text = font_title.render("TETRIMIND", True, LINE_COLOR)
    screen.blit(title_text, (RIGHTBAR_WIDTH+PADDING*2 + (GAME_WIDTH-title_text.get_width())/2, PADDING/2))

    score_text = font_header.render(f"      SCORE\n        {info.playerScore}", True, LINE_COLOR)
    level_text = font_header.render(f"      LEVEL\n        {info.gameLevel}", True, LINE_COLOR)
    score_surface.blit(score_text, (PADDING, PADDING))
    score_surface.blit(level_text, (PADDING, PADDING + 80))

    controls_text = font.render(CONTROLS_TEXT, True, LINE_COLOR)
    controls_surface.blit(controls_text, (PADDING, PADDING))
    scoring_text = font.render(SCORING_TEXT, True, LINE_COLOR)
    scoring_surface.blit(scoring_text, (PADDING, PADDING))

    ## display surfaces
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
