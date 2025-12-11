from gui import RendererSolo, RendererVs
from genetic_algorithm import GeneticAlgorithm
from game import Game, Bag
from menu import show_menu
from settings import *
import time

# player components
seed = 1
bag = Bag(seed)
game = Game(bag)

# agent components
bag_ai = Bag(seed)
game_ai = Game(bag_ai)
agent = GeneticAlgorithm(game_ai,play=True)

if __name__ == "__main__":
    running = True
    while running:
        # default screen = menu
        GAME_MODE, AI_DIFFICULTY, screen = show_menu()
        renderer = RendererSolo(screen)
        renderer_vs = RendererVs(screen)

        time.sleep(0.1)
        if GAME_MODE == "player":
            if not renderer.run(game):
                running = False

        elif GAME_MODE == "ai":
            seed += 1 # changes every menu button click
            game.reset(seed)
            game_ai.reset(seed)
            agent.game = game_ai

            if AI_DIFFICULTY == "low":
                agent.move_per_sec = 20/60 # easy
                if not renderer_vs.run(game, game_ai, agent):
                    running = False
                    
            elif AI_DIFFICULTY == "medium":
                agent.move_per_sec = 10/60
                if not renderer_vs.run(game, game_ai, agent):
                    running = False

            elif AI_DIFFICULTY == "hard":
                agent.move_per_sec = 10/60 # medium speed but with garbo
                if not renderer_vs.run(game, game_ai, agent, garbo=True):
                    running = False

            elif AI_DIFFICULTY == "expert":
                agent.move_per_sec = 2/60 # high speed clanker sheesh
                if not renderer_vs.run(game, game_ai, agent, garbo=True):
                    running = False
    pygame.quit()