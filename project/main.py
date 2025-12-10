from gui import Gui
from game import Game, Bag
import random

seed = random.randint(0, 2**63-1)
bag = Bag(seed)
game = Game(bag)
gui = Gui()

if __name__ == "__main__":
    gui.run(game)