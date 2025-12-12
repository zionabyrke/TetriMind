### RUN THIS SCRIPT FOR TRAINING ONLY"""" 
from settings import *
from gui import *
from game import Game, Bag, Tetromino
from agent import Agent

testing_seed = 5

pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH+RIGHTBAR_WIDTH+PADDING*3, GAME_HEIGHT+APPNAME_SIZE+PADDING*2))
pygame.display.set_caption("Training Arc")

#objects
bag = Bag(testing_seed)
game = Game(bag)
agent = Agent(game)

### TESTING ###
# T spin check
#game.current_piece = Tetromino("Z")
game.current_piece = Tetromino("T")
game.block_matrix = [
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,1],
        [1,1,1,1,1,0,0,0,1,1],
        [1,1,1,1,1,1,0,1,1,1]
        ]

"""
    SUPERCLASS
    do not modify playfield and display_section pag di need
    ===>>>> inherited by ga_train_screen
"""
class Trainer(RendererSolo):
    def __init__(self, screen):
        super().__init__(screen)

    def run(self, seed, game, agent):
        ### testing color matrix ###
        for y in range(ROWS):
            for x in range(COLUMNS):
                if game.block_matrix[y][x] == 1:
                    self.color_matrix[y][x] = RED

        # game loop
        while self.running:
            # Removed pygame clock tick delay of framespersec to get faster training
            dt = self.clock.tick(FRAMEPERSEC)

            if game.game_over:
                print("Game Over")
                exit()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            #game logic
            game.update(dt, self.color_matrix)

            ######   agent actions HERE
            agent.moves_instant(game, agent, dt, self.color_matrix)
            
            self.display_section(game)
            self.panels(game, agent)
            pygame.display.update()

        pygame.quit()

    # reused by subclass
    def display_section(self, game):
        self.screen.fill(GRAY)
        playfield_surface.fill(BLACK)
        sidebar_surface.fill(BLACK)

        self.playfield(game)

    # reused by subclass
    def playfield(self, game):
        # playfield blocks
        for y, row in enumerate(self.color_matrix):
            for x, color in enumerate(row):
                if color:
                    pygame.draw.rect(playfield_surface, color,
                                    (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # piece and preview only, no ghost piece
        if game.current_piece:
            shape_current = game.current_piece.get_shape_array()
            shape_next = game.next_piece.get_shape_array()
            preview_cell = CELL_SIZE // 1.5  # smaller display

            for dx, dy in shape_current:
                px, py = (game.current_piece.coord[0] + dx) * CELL_SIZE, (game.current_piece.coord[1] + dy) * CELL_SIZE
                pygame.draw.rect(playfield_surface, game.current_piece.color, (px, py, CELL_SIZE, CELL_SIZE))

            for px, py in shape_next:
                # Draw the next piece preview
                pygame.draw.rect(sidebar_surface, game.next_piece.color, 
                (PADDING+30+px * preview_cell, PADDING+70+py * preview_cell, preview_cell, preview_cell))

    # overriden
    def panels(self, game, agent):
        h, b, col_heights = agent.get_game_states()  # game states
        temp = " ".join(map(str, col_heights)) #no space and brackets

        # sidebar
        title_text = font_title.render("TETRIMIND", True, LINE_COLOR)
        score_text = font_style_ai.render(f"Score: {game.player_score}", True, LINE_COLOR)
        level_text = font_style_ai.render(f"Level: {game.game_level}", True, LINE_COLOR)
        preview_text = font_style_ai.render(f"Next Piece:", True, LINE_COLOR)
        states_text = [f"Holes: {h}", f"Bumpiness: {b}", "Heights:", f"{temp}", 
            f"Total pieces: {game.total_pieces}",
            f"Lines cleared: {game.lines_cleared_so_far}",
            f"Tspins: {game.tspins}",
            f"Tetrises: {game.tetris}"]
        for x, text in enumerate(states_text):
            state_text = font_style_ai.render(text, True, LINE_COLOR)
            sidebar_surface.blit(state_text, (PADDING, PADDING+150+(x*20)))

        sidebar_surface.blit(score_text, (PADDING, PADDING))
        sidebar_surface.blit(level_text, (PADDING, PADDING+16))
        sidebar_surface.blit(preview_text, (PADDING, PADDING+16+16))
        screen.blit(playfield_surface, (PADDING, PADDING + APPNAME_SIZE))
        screen.blit(sidebar_surface, (GAME_WIDTH + PADDING * 2, PADDING + APPNAME_SIZE))
        screen.blit(title_text, (PADDING, PADDING))
    

gui = Trainer(screen)
if __name__ == "__main__":
    # run here
    gui.run(testing_seed, game, agent)
    

