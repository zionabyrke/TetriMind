from gui import RendererSolo, RendererVs
from genetic_algorithm import GeneticAlgorithm
from game import Game, Bag
from menu import show_menu
from settings import *

if __name__ == "__main__":
    running = True
    while running:
        GAME_MODE, AI_DIFFICULTY, screen = show_menu()
        renderer = RendererSolo(screen)
        renderer_vs = RendererVs(screen)
        seed = random.randint(0, 2**63-1)
        # renderers return False to EXIT, True if go Menu

        if GAME_MODE == "player":
            bag = Bag(seed)
            solo_game = Game(bag)
            running = renderer.run(solo_game) ## start game ## 

        elif GAME_MODE == "ai":
            bag_p = Bag(seed)
            bag_ai = Bag(seed)
            game_p = Game(bag_p)
            game_ai = Game(bag_ai)
            agent = GeneticAlgorithm(game_ai,play=True)

            if AI_DIFFICULTY == "low":
                agent.move_per_sec = 20/60 # easy
                running = renderer_vs.run(game_p, game_ai, agent)
                    
            elif AI_DIFFICULTY == "medium":
                agent.move_per_sec = 10/60
                running = renderer_vs.run(game_p, game_ai, agent)

            elif AI_DIFFICULTY == "hard":
                agent.move_per_sec = 10/60 # medium speed but with garbo
                running = renderer_vs.run(game_p, game_ai, agent, garbo=True)

            elif AI_DIFFICULTY == "expert":
                agent.move_per_sec = 2/60 
                running = renderer_vs.run(game_p, game_ai, agent, garbo=True)

    pygame.quit()
