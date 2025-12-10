from gui import RendererSolo, RendererVs
from genetic_algorithm import GeneticAlgorithm
from game import Game, Bag
from menu import show_menu
from settings import *
import random
import time

pygame.init()

"""GAME_MODE, AI_DIFFICULTY = show_menu()
time.sleep(0.1)
pygame.display.quit()
pygame.display.init()"""

screen = pygame.display.set_mode((WINDOW_WIDTH_vs, WINDOW_HEIGHT_vs+40))
pygame.display.set_caption("TetriMind")

seed = random.shuffle([1,2,3,4,5])
bag = Bag(seed)
game = Game(bag)
renderer = RendererSolo(screen)

renderer_vs = RendererVs(screen)
bag_ai = Bag(seed)
game_ai = Game(bag_ai)
agent = GeneticAlgorithm(game_ai,play=True)
agent.move_per_sec = 10/60


if __name__ == "__main__":
    ###### uncomment if try the other
    #renderer.run(game)
    renderer_vs.run(game, agent)




# pygame.display puro problema
"""if __name__ == "__main__":
    if GAME_MODE == "player":
        renderer.run(game)

    elif GAME_MODE == "ai":
        if AI_DIFFICULTY == "low":
            renderer_vs.run(game, agent)
        elif AI_DIFFICULTY == "medium":
            pass
        elif AI_DIFFICULTY == "hard":
            pass
        elif AI_DIFFICULTY == "expert":
            pass"""
    #