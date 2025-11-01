from gameinfo import GameInfo
from tetromino import Tetromino
from action import Action

class Playfield:
    def __init__(self):
        self.blockMatrix = []
        self.fallSpeed = 0.0
        self.info = GameInfo()
        self.currentPiece = None
        self.nextPiece = None

    # def checkLineClears(self):
        

    # def generateTetromino(self):
        

    # def moveTetromino(self, action: Action):
        
