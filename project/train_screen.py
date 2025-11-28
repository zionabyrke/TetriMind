### RUN THIS SCRIPT FOR TRAINING ONLY"""" 
from settings import *
from game import Playfield, GameInfo
from agent import Agent
from gen_algo import RLGenAlgo

import json # model saving
# load model
model_weights = None
with open("rlga_v1.json", "r") as f:
    model_weights = json.load(f)

pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH+RIGHTBAR_WIDTH+PADDING*3, GAME_HEIGHT+APPNAME_SIZE+PADDING*2))
pygame.display.set_caption("Training Arc")
clock = pygame.time.Clock()

#objects
info = GameInfo()
field = Playfield(info)
info.field = field 
agent = Agent(info)
GA = RLGenAlgo(info, generations=20, population_size=12)

colorMatrix = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
font_title = pygame.font.SysFont("consolas", APPNAME_SIZE)
font_small = pygame.font.SysFont("consolas", 14)

#surfaces
playfield_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
sidebar_surface = pygame.Surface((RIGHTBAR_WIDTH, GAME_HEIGHT))

piece_per_second = 1
move_time = 0
cleared = 0

##### GA GENERATION LOOP
for g in range(GA.generations):
    best_score, best_weights = GA.run_generation()
    best_final = GA.get_best_final()

    # reset for visual sim
    visual_info = GameInfo()
    visual_env = Playfield(visual_info)
    visual_info.field = visual_env
    visual_agent = Agent(visual_info)

    # set weights
    visual_agent.set_eval_function(lambda f: GA.evaluate_field(f, model_weights))

    ### game loop
    running = True
    pieces = 0
    move_time = 0
    colorMatrix = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    while running:
        dt = clock.tick(FRAMEPERSEC)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                quit()

        visual_env.update(dt, colorMatrix)
        visual_info.updateGameInfo(dt)

        if visual_env.game_over:
            #new generations
            break

        # stop when piece limit is reached
        if pieces >= 50:
            break

        h, b, colHeights = visual_agent.getGameState()  # game states
        temp = " ".join(map(str, colHeights)) #no space and brackets

        ######   visual_agent actions HERE
        if(move_time <= piece_per_second):
            move_time += dt/1000
        else:
            move_time = 0   # reset move time
            _, action = visual_agent.chooseAction(visual_env, depth=2) # recursion = piece lookahead
            visual_env.moveTetromino(action[0], colorMatrix)
            for dx in range(abs(action[1])):
                if action[1] < 0:
                    visual_env.moveTetromino(MOVE_LEFT, colorMatrix)
                else:
                    visual_env.moveTetromino(MOVE_RIGHT, colorMatrix)
            visual_env.moveTetromino(action[2], colorMatrix)

            pieces += 1  

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
        if visual_env.currentPiece:
            shape_current = visual_env.currentPiece.getShapeArray()
            shape_next = visual_env.nextPiece.getShapeArray()
            preview_cell = CELL_SIZE // 1.5  # smaller display

            for dx, dy in shape_current:
                px, py = (visual_env.currentPiece.coord[0] + dx) * CELL_SIZE, (visual_env.currentPiece.coord[1] + dy) * CELL_SIZE
                pygame.draw.rect(playfield_surface, visual_env.currentPiece.color, (px, py, CELL_SIZE, CELL_SIZE))

            for px, py in shape_next:
                # Draw the next piece preview
                pygame.draw.rect(sidebar_surface, visual_env.nextPiece.color, 
                (PADDING+30+px * preview_cell, PADDING+70+py * preview_cell, preview_cell, preview_cell))

        # sidebar
        title_text = font_title.render("TETRIMIND", True, LINE_COLOR)
        score_text = font_small.render(f"Score: {visual_info.playerScore}", True, LINE_COLOR)
        level_text = font_small.render(f"Level: {visual_info.gameLevel}", True, LINE_COLOR)
        preview_text = font_small.render(f"Next Piece:", True, LINE_COLOR)
        states_text = [f"Holes: {h}", f"Bumpiness: {b}", "Heights:", f"{temp}"]
        for x, text in enumerate(states_text):
            state_text = font_small.render(text, True, LINE_COLOR)
            sidebar_surface.blit(state_text, (PADDING, PADDING+150+(x*20)))

        ga_y = PADDING + 150 + len(states_text) * 20 + 20  # position below states_text
        gen_text = font_small.render(f"GENERATION: {g+1}", True, LINE_COLOR)
        sidebar_surface.blit(gen_text, (PADDING, ga_y))
        ga_y += 20

        cleared_text = font_small.render(f"LINES CLEARED: {visual_env.lines_cleared_so_far}", True, LINE_COLOR)
        sidebar_surface.blit(cleared_text, (PADDING, ga_y))
        ga_y += 20
        
        sidebar_surface.blit(score_text, (PADDING, PADDING))
        sidebar_surface.blit(level_text, (PADDING, PADDING+16))
        sidebar_surface.blit(preview_text, (PADDING, PADDING+16+16))
        screen.blit(playfield_surface, (PADDING, PADDING + APPNAME_SIZE))
        screen.blit(sidebar_surface, (GAME_WIDTH + PADDING * 2, PADDING + APPNAME_SIZE))
        screen.blit(title_text, (PADDING, PADDING))

        pygame.display.update()

    # save model
    with open("rlga_v1.json", "w") as f:
        json.dump(best_final, f, indent=4)
    
