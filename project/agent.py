from game import GameInfo, GameState

#test simulation CONNECTED TO train_screen.py not main.py
from settings import MOVE_LEFT, MOVE_RIGHT, MOVE_DOWN, ROTATE_LEFT, ROTATE_RIGHT, HARD_DROP
import random

class Agent:
    def __init__(self, info):
        self.info = info
        self.field = self.info.field #blockMatrix inside
        self.currentState = None
        self.possibleStates = []
        self.piecePerSec = 1.0/self.field.fallSpeed

        #FOR TESTING
        self.test_action_timer = 0
        self.rand_action = None
    
    def getGameState(self):
        self.currentState = GameState(self.info)
        self.possibleStates = [self.currentState]

        # test
        state = self.currentState
        return state.holes, state.bumpiness, state.columnHeights

    def chooseAction(self, field):
        # random moves - TEST
        self.test_action_timer += 1

        #  random move every 40 frames
        if self.test_action_timer > 50:
            self.test_action_timer = 0
            self.rand_action = random.choice([
                MOVE_LEFT,
                MOVE_RIGHT,
                MOVE_DOWN,
                ROTATE_LEFT,
                ROTATE_RIGHT,
                HARD_DROP])

        return self.rand_action
