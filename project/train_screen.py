### RUN THIS SCRIPT FOR TRAINING ONLY"""" 
from settings import *
from game import Playfield, GameInfo
from agent import Agent

pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH+RIGHTBAR_WIDTH+PADDING*3, GAME_HEIGHT+APPNAME_SIZE+PADDING*2))
pygame.display.set_caption("Training Arc")
clock = pygame.time.Clock()

#objects
info = GameInfo()
field = Playfield(info)
info.field = field
agent = Agent(info)

colorMatrix = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
font_title = pygame.font.SysFont("consolas", APPNAME_SIZE)
font_small = pygame.font.SysFont("consolas", 14)

#surfaces
playfield_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
sidebar_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT))

### game loop
running = True
while running:
    dt = clock.tick(FRAMEPERSEC)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #game logic
    field.update(dt, colorMatrix)
    info.updateGameInfo(dt)
    h, b, colHeights = agent.getGameState()  # game states
    temp = " ".join(map(str, colHeights)) #no space and brackets

    ######   agent actions HERE
    action = agent.chooseAction(field)
    if action:
        field.moveTetromino(action, colorMatrix)

    screen.fill(GRAY)
    playfield_surface.fill(BLACK)
    sidebar_surface.fill(BLACK)

    # playfield blocks
    for y, row in enumerate(colorMatrix):
        for x, color in enumerate(row):
            if color:
                pygame.draw.rect(playfield_surface, color,
                                 (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # piece and preview only, no ghost piece
    if field.currentPiece:
        shape_current = field.currentPiece.getShapeArray()
        shape_next = field.nextPiece.getShapeArray()
        preview_cell = CELL_SIZE // 1.5  # smaller display

        for dx, dy in shape_current:
            px, py = (field.currentPiece.coord[0] + dx) * CELL_SIZE, (field.currentPiece.coord[1] + dy) * CELL_SIZE
            pygame.draw.rect(playfield_surface, field.currentPiece.color, (px, py, CELL_SIZE, CELL_SIZE))

        for px, py in shape_next:
            # Draw the next piece preview
            pygame.draw.rect(sidebar_surface, field.nextPiece.color, 
            (PADDING+30+px * preview_cell, PADDING+70+py * preview_cell, preview_cell, preview_cell))


    # sidebar
    title_text = font_title.render("TETRIMIND", True, LINE_COLOR)
    score_text = font_small.render(f"Score: {info.playerScore}", True, LINE_COLOR)
    level_text = font_small.render(f"Level: {info.gameLevel}", True, LINE_COLOR)
    preview_text = font_small.render(f"Next Piece:", True, LINE_COLOR)
    states_text = [f"Holes: {h}", f"Bumpiness: {b}", "Heights:", f"{temp}"]
    for x, text in enumerate(states_text):
        state_text = font_small.render(text, True, LINE_COLOR)
        sidebar_surface.blit(state_text, (PADDING, PADDING+150+(x*20)))

    sidebar_surface.blit(score_text, (PADDING, PADDING))
    sidebar_surface.blit(level_text, (PADDING, PADDING+16))
    sidebar_surface.blit(preview_text, (PADDING, PADDING+16+16))
    screen.blit(playfield_surface, (PADDING, PADDING + APPNAME_SIZE))
    screen.blit(sidebar_surface, (GAME_WIDTH + PADDING * 2, PADDING + APPNAME_SIZE))
    screen.blit(title_text, (PADDING, PADDING))

    pygame.display.update()

pygame.quit()
