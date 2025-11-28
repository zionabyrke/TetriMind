from settings import *
from game import Playfield, GameInfo
from agent import Agent
import json # import model

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT + 40))
pygame.display.set_caption("TetriMind — Player vs AI")
clock = pygame.time.Clock()
H_SPACING = 40 #space between the fields

total_content_w = 2 * GAME_WIDTH + H_SPACING + 2 * RIGHTBAR_WIDTH
left_margin = (WINDOW_WIDTH - total_content_w) // 2
player_rightbar_x = left_margin + GAME_WIDTH + PADDING

#x position
ai_x = player_rightbar_x + RIGHTBAR_WIDTH + H_SPACING
ai_rightbar_x = ai_x + GAME_WIDTH + PADDING

# top vertical alignment
top_y = 4 * PADDING + APPNAME_SIZE

# Player component
info_p = GameInfo()
field_p = Playfield(info_p)
info_p.field = field_p

# AI components
info_ai = GameInfo()
field_ai = Playfield(info_ai)
info_ai.field = field_ai
agent_ai = Agent(info_ai)

colorMatrix_p = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
colorMatrix_ai = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]

held_keys = []
hold_delay = 0

# can have different font for different texts 
font_title = pygame.font.SysFont("consolas", APPNAME_SIZE)
font_header = pygame.font.SysFont("consolas", 18)
font = pygame.font.SysFont("consolas", 12)

# surfaces 
playfield_surface_p = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
preview_surface_p = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION - PADDING))
score_surface_p = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT * SCORE_HEIGHT_FRACTION))
ghost_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

playfield_surface_ai = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
preview_surface_ai = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT * PREVIEW_HEIGHT_FRACTION - PADDING))
score_surface_ai = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT * SCORE_HEIGHT_FRACTION))

#buttons
pause_rect = pygame.Rect((WINDOW_WIDTH - GAME_WIDTH)//2, GAME_HEIGHT + APPNAME_SIZE + PADDING*4,
                GAME_WIDTH//3, 30 ) #30 height
reset_rect = pygame.Rect(pause_rect.x + GAME_WIDTH//3, GAME_HEIGHT + APPNAME_SIZE + PADDING*4,
                GAME_WIDTH//3, 30 ) #30 height
menu_rect = pygame.Rect(pause_rect.x + (GAME_WIDTH//3)*2, GAME_HEIGHT + APPNAME_SIZE + PADDING*4,
                GAME_WIDTH//3, 30 ) #30 height

# Load GA model weights
with open("rlga_v1.json", "r") as f:
    ai_weights = json.load(f)

# loader
def evaluate_field_local(field):
    holes, bumpiness, heights = field.getFieldFeatures()
    maxH = max(heights)

    return (
        ai_weights.get("holes", 0)     * holes +
        ai_weights.get("bumpiness", 0) * bumpiness +
        ai_weights.get("maxHeight", 0) * maxH +
        ai_weights.get("line1", 0) * (1 if field.lines_cleared == 1 else 0) +
        ai_weights.get("line2", 0) * (1 if field.lines_cleared == 2 else 0) +
        ai_weights.get("line3", 0) * (1 if field.lines_cleared == 3 else 0) +
        ai_weights.get("line4", 0) * (1 if field.lines_cleared == 4 else 0) +
        ai_weights.get("tspin1", 0) * (1 if field.lines_cleared == 1 and getattr(field, "tspin", False) else 0) +
        ai_weights.get("tspin2", 0) * (1 if field.lines_cleared == 2 and getattr(field, "tspin", False) else 0) +
        ai_weights.get("tspin3", 0) * (1 if field.lines_cleared == 3 and getattr(field, "tspin", False) else 0) +
        ai_weights.get("perfectClear", 0) * (1 if all(sum(row) == 0 for row in field.blockMatrix) else 0)
    )
agent_ai.set_eval_function(evaluate_field_local)
AI_ACTION_INTERVAL = 1  # seconds per action (adjust for difficulty)
ai_action_accum = 0.0

##### GAME LOOP
running = True
paused = False
while running:
    # CHECK GAME OVER
    if field_p.game_over or field_ai.game_over:
        colorMatrix_p = [[field_p.currentPiece.color for _ in range(COLUMNS)] for _ in range(ROWS)]
        colorMatrix_ai = [[field_ai.currentPiece.color for _ in range(COLUMNS)] for _ in range(ROWS)]
        paused = True

    dt = clock.tick(FRAMEPERSEC)
    dt_s = dt / 1000.0 # convert to seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # buttons
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pause_rect.collidepoint(event.pos):
                paused = not paused
            if reset_rect.collidepoint(event.pos):
                # RESET BOTH PLAYER + AI
                info_p = GameInfo()
                field_p = Playfield(info_p)
                info_p.field = field_p
                colorMatrix_p = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]

                info_ai = GameInfo()
                field_ai = Playfield(info_ai)
                info_ai.field = field_ai
                colorMatrix_ai = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]

            if menu_rect.collidepoint(event.pos):
                running = False  # go back to menU (BREAK GAME LOOP)

        # block all controls when paused
        elif paused:
            continue

        # keyboard input (PLAYER ONLY)
        elif event.type == pygame.KEYDOWN:
            # add held keys for autorepeat
            if event.key == pygame.K_LEFT:
                held_keys.append(MOVE_LEFT)
            elif event.key == pygame.K_RIGHT:
                held_keys.append(MOVE_RIGHT)
            elif event.key == pygame.K_DOWN:
                held_keys.append(MOVE_DOWN)

            # apply the immediate move
            field_p.moveTetromino(event.key, colorMatrix_p)

        elif event.type == pygame.KEYUP:
            hold_delay = 0
            # remove held keys when released
            if event.key == pygame.K_LEFT and MOVE_LEFT in held_keys:
                held_keys.remove(MOVE_LEFT)
            elif event.key == pygame.K_RIGHT and MOVE_RIGHT in held_keys:
                held_keys.remove(MOVE_RIGHT)
            elif event.key == pygame.K_DOWN and MOVE_DOWN in held_keys:
                held_keys.remove(MOVE_DOWN)

    # Move based on held key
    if held_keys:
        hold_delay += 1
        # Delay for 10 frames before player can fully hold, so it doesn't go too fast
        if hold_delay > 10:
            field_p.moveTetromino(held_keys[-1], colorMatrix_p)

    ### GAME LOGIC SECTION (update both boards)
    if not paused: #update only if not paused
        # update player
        field_p.update(dt, colorMatrix_p)
        info_p.updateGameInfo(dt)

        # update ai
        field_ai.update(dt, colorMatrix_ai)
        info_ai.updateGameInfo(dt)

        # AI action timing
        ai_action_accum += dt_s
        if ai_action_accum >= AI_ACTION_INTERVAL:
            ai_action_accum -= AI_ACTION_INTERVAL

            _, action_ai = agent_ai.chooseAction(field_ai, depth=2)
            if action_ai:
                # apply action on AI field
                field_ai.moveTetromino(action_ai[0], colorMatrix_ai)
                for _ in range(abs(action_ai[1])):
                    if action_ai[1] < 0:
                        field_ai.moveTetromino(MOVE_LEFT, colorMatrix_ai)
                    else:
                        field_ai.moveTetromino(MOVE_RIGHT, colorMatrix_ai)
                field_ai.moveTetromino(action_ai[2], colorMatrix_ai)

    ### DISPLAY SECTION
    screen.fill(GRAY)
    playfield_surface_p.fill(BLACK)
    playfield_surface_ai.fill(BLACK)
    preview_surface_p.fill(BLACK)
    preview_surface_ai.fill(BLACK)
    score_surface_p.fill(BLACK)
    score_surface_ai.fill(BLACK)

    # playfield blocks 
    for y, row in enumerate(colorMatrix_p):
        for x, color in enumerate(row):
            if color != BLACK:
                pygame.draw.rect(playfield_surface_p, color,
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # current tetromino shape
    if field_p.currentPiece:
        shape = field_p.currentPiece.getShapeArray()
        ghost_coords = field_p.ghost_piece()
        ghost_color = pygame.Color(field_p.currentPiece.color)
        ghost_color.a = 64 #25% x 255 = 64 adjust

        # tetromino piece
        for dx, dy in shape:
            pygame.draw.rect(playfield_surface_p, field_p.currentPiece.color,
                             ((field_p.currentPiece.coord[0] + dx) * CELL_SIZE,
                              (field_p.currentPiece.coord[1] + dy) * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE))
        # ghost piece 
        ghost_surface.fill(ghost_color)
        for gx, gy in ghost_coords:
            playfield_surface_p.blit(ghost_surface, (gx * CELL_SIZE, gy * CELL_SIZE))

    # next tetromino piece
    if field_p.nextPiece:
        for x, y in field_p.nextPiece.getShapeArray():
            pygame.draw.rect(preview_surface_p, field_p.nextPiece.color,
                             ((x * CELL_SIZE) + 45, PADDING + (y * CELL_SIZE) + 30,
                              CELL_SIZE, CELL_SIZE))

    # AI playfield draw
    for y, row in enumerate(colorMatrix_ai):
        for x, color in enumerate(row):
            if color != BLACK:
                pygame.draw.rect(playfield_surface_ai, color,
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # current tetromino shape
    if field_ai.currentPiece:
        shape = field_ai.currentPiece.getShapeArray()
        for dx, dy in shape:
            pygame.draw.rect(playfield_surface_ai, field_ai.currentPiece.color,
                             ((field_ai.currentPiece.coord[0] + dx) * CELL_SIZE,
                              (field_ai.currentPiece.coord[1] + dy) * CELL_SIZE,
                              CELL_SIZE, CELL_SIZE))

    # next tetromino piece
    if field_ai.nextPiece:
        for x, y in field_ai.nextPiece.getShapeArray():
            pygame.draw.rect(preview_surface_ai, field_ai.nextPiece.color,
                             ((x * CELL_SIZE) + 45, PADDING + (y * CELL_SIZE) + 30,
                              CELL_SIZE, CELL_SIZE))

    # draw gridlines (both)
    for col in range(1, COLUMNS):
        x = col * CELL_SIZE
        pygame.draw.line(playfield_surface_p, GRAY, (x, 0), (x, GAME_HEIGHT), 1)
        pygame.draw.line(playfield_surface_ai, GRAY, (x, 0), (x, GAME_HEIGHT), 1)
    for row in range(1, ROWS):
        y = row * CELL_SIZE
        pygame.draw.line(playfield_surface_p, GRAY, (0, y), (GAME_WIDTH, y), 1)
        pygame.draw.line(playfield_surface_ai, GRAY, (0, y), (GAME_WIDTH, y), 1)

    # Title text
    title_text = font_title.render("TETRIMIND — PLAYER (LEFT)  vs  AI (RIGHT)", True, LINE_COLOR)
    screen.blit(title_text, ((WINDOW_WIDTH - title_text.get_width()) // 2, PADDING))

    # Player UI panels
    # Score block (player)
    score_text = font_header.render("     SCORE:", True, LINE_COLOR)
    score_amount = font_header.render(f"       {info_p.playerScore}", True, LINE_COLOR)
    level_text = font_header.render(f"     LEVEL: {info_p.gameLevel}", True, LINE_COLOR)
    time_text = font_header.render(f"     TIME: %02d:%02d" % ((info_p.elapsedTime//1000)//60, (info_p.elapsedTime//1000)%60), True, LINE_COLOR)
    score_surface_p.blit(score_text, (PADDING, PADDING))
    score_surface_p.blit(score_amount, (PADDING, PADDING+30))
    score_surface_p.blit(level_text, (PADDING, PADDING + 80))
    score_surface_p.blit(time_text, (PADDING, PADDING + 130))
    preview_surface_p.blit(font_header.render("     NEXT", True, LINE_COLOR), (PADDING, PADDING))

    # AI UI panels (mirror)
    score_text_ai = font_header.render("     AI SCORE:", True, LINE_COLOR)
    score_amount_ai = font_header.render(f"       {info_ai.playerScore}", True, LINE_COLOR)
    level_text_ai = font_header.render(f"     LEVEL: {info_ai.gameLevel}", True, LINE_COLOR)
    time_text_ai = font_header.render(f"     TIME: %02d:%02d" % ((info_ai.elapsedTime//1000)//60, (info_ai.elapsedTime//1000)%60), True, LINE_COLOR)
    score_surface_ai.blit(score_text_ai, (PADDING, PADDING))
    score_surface_ai.blit(score_amount_ai, (PADDING, PADDING+30))
    score_surface_ai.blit(level_text_ai, (PADDING, PADDING + 80))
    score_surface_ai.blit(time_text_ai, (PADDING, PADDING + 130))
    preview_surface_ai.blit(font_header.render("     NEXT", True, LINE_COLOR), (PADDING, PADDING))

    ## display surfaces
    screen.blit(playfield_surface_p, (left_margin, top_y))
    screen.blit(preview_surface_p, (player_rightbar_x, top_y))
    screen.blit(score_surface_p, (player_rightbar_x, top_y + preview_surface_p.get_height() + PADDING))
    # button box
    pygame.draw.rect(screen, BLACK, pause_rect) #fill
    pygame.draw.rect(screen, GRAY, pause_rect, 4) #4px border/gaps
    pause_text = font_header.render("Pause" if not paused else "Resume", True, LINE_COLOR)
    screen.blit(pause_text, (pause_rect.x + (pause_rect.width - pause_text.get_width()) // 2,
                            pause_rect.y + (pause_rect.height - pause_text.get_height()) // 2))
    pygame.draw.rect(screen, BLACK, reset_rect) #fill
    pygame.draw.rect(screen, GRAY, reset_rect, 4) #4px border/gaps
    reset_text = font_header.render("Reset", True, LINE_COLOR)
    screen.blit(reset_text, (reset_rect.x + (reset_rect.width - reset_text.get_width()) // 2,
                             reset_rect.y + (reset_rect.height - reset_text.get_height()) // 2))
    pygame.draw.rect(screen, BLACK, menu_rect) #fill
    pygame.draw.rect(screen, GRAY, menu_rect, 4) #4px border/gaps
    menu_text = font_header.render("Menu", True, LINE_COLOR)
    screen.blit(menu_text, (menu_rect.x + (menu_rect.width - menu_text.get_width()) // 2,
                            menu_rect.y + (menu_rect.height - menu_text.get_height()) // 2))

    # AI area (right)
    screen.blit(playfield_surface_ai, (ai_x, top_y))
    screen.blit(preview_surface_ai, (ai_rightbar_x, top_y))
    screen.blit(score_surface_ai, (ai_rightbar_x, top_y + preview_surface_ai.get_height() + PADDING))

    pygame.display.update()

pygame.quit()
