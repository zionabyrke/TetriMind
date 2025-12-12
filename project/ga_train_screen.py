### RUN THIS SCRIPT FOR TRAINING ONLY"""" 
from settings import *
from train_screen import *
from genetic_algorithm import GeneticAlgorithm
from game import Game, Bag
from agent import Agent
import random

"""
    BUG: WRONG CURRENT INDEX SAVED ON BATCH
"""

pygame.init()
screen = pygame.display.set_mode((GAME_WIDTH+RIGHTBAR_WIDTH+PADDING*3, GAME_HEIGHT+APPNAME_SIZE+PADDING*2))
pygame.display.set_caption("Training Arc")

'''
    USE load_progress() & save_progress()
    FOR CONTINUOUS TRAINING
    IT LOADS THE COMPLETE POPULATION FROM A FILE
    PRIOR TO CLOSING THE APP
'''
#objects
seed = random.randint(0, 2**63-1)
bag = Bag(seed)
game = Game(bag)
agent = GeneticAlgorithm(game)
agent.load_progress()

class GATrainer(Trainer):
    def __init__(self, screen):
        super().__init__(screen)
        self.reward = 0
    
    def run(self, seed, game, agent):
        game_count = 0
        while self.running:
            # Removed pygame clock tick delay of framespersec to get faster training
            dt = self.clock.tick()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            ### GAME LOGIC SECTION
            game.update(dt, self.color_matrix)
            game.update_clock(dt)
            
            if game.game_over:
                # randomize seed when all genomes finished
                if agent.current_index == agent.population_size - 1:
                    seed = random.randint(0, 2**63-1)

                #### GA acts here
                agent.tournament(self.reward)

                #resets
                game.reset(seed)
                agent.move_time=0
                agent.action_sequence=0
                agent.action=None
                self.__init__(self.screen)

                game_count += 1

            # rewarded only if not game over
            self.reward += 1 + game.lines_cleared

            #agent moves are instant during training but should be sequential for versus
            agent.moves_instant(game, agent, dt, self.color_matrix)

            self.display_section(game)
            self.panels(game, agent, game_count)
            pygame.display.update()

        agent.save_progress()
        pygame.quit()

    def panels(self, game, agent, game_count):
        # sidebar
        title_text = font_title.render("TETRIMIND", True, LINE_COLOR)
        score_text = font_style_ai.render(f"Score: {game.player_score}", True, LINE_COLOR)
        level_text = font_style_ai.render(f"Level: {game.game_level}", True, LINE_COLOR)
        preview_text = font_style_ai.render(f"Next Piece:", True, LINE_COLOR)
        states_text = [f"Generation: {agent.generation}", 
            f"Population size: {agent.population_size}",
            f"Genome: {agent.current_index}",
            f"Game: {game_count}",
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
        self.screen.blit(playfield_surface, (PADDING, PADDING + APPNAME_SIZE))
        self.screen.blit(sidebar_surface, (GAME_WIDTH + PADDING * 2, PADDING + APPNAME_SIZE))
        self.screen.blit(title_text, (PADDING, PADDING))

gui = GATrainer(screen)

if __name__ == "__main__":
    # run here
    gui.run(seed, game, agent)
    
