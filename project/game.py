from datetime import time

class ShapeList:
    def __init__(self):
        self.shape_S = [
            [[0, 1, 1],
             [1, 1, 0],
             [0, 0, 0]],
            [[1, 0, 0],
             [1, 1, 0],
             [0, 1, 0]]
        ]
        self.shape_Z = [
            [[1, 1, 0],
             [0, 1, 1],
             [0, 0, 0]],
            [[0, 0, 1],
             [0, 1, 1],
             [0, 1, 0]]
        ]
        self.shape_J = [
            [[1, 0, 0],
             [1, 1, 1],
             [0, 0, 0]],
            [[0, 1, 1],
             [0, 1, 0],
             [0, 1, 0]],
            [[0, 0, 0],
             [1, 1, 1],
             [0, 0, 1]],
            [[0, 1, 0],
             [0, 1, 0],
             [1, 1, 0]]
        ]
        self.shape_L = [
            [[0, 0, 1],
             [1, 1, 1],
             [0, 0, 0]],
            [[0, 1, 0],
             [0, 1, 0],
             [0, 1, 1]],
            [[0, 0, 0],
             [1, 1, 1],
             [1, 0, 0]],
            [[1, 1, 0],
             [0, 1, 0],
             [0, 1, 0]]
        ]
        self.shape_T = [
            [[0, 1, 0],
             [1, 1, 1],
             [0, 0, 0]],
            [[0, 1, 0],
             [0, 1, 1],
             [0, 1, 0]],
            [[0, 0, 0],
             [1, 1, 1],
             [0, 1, 0]],
            [[0, 1, 0],
             [1, 1, 0],
             [0, 1, 0]]
        ]
        self.shape_O = [
            [[0, 0, 0, 0],
             [0, 1, 1, 0],
             [0, 1, 1, 0],
             [0, 0, 0, 0]]
        ]
        self.shape_I = [
            [[0, 0, 0, 0],
             [0, 0, 0, 0],
             [1, 1, 1, 1],
             [0, 0, 0, 0]],
            [[0, 0, 1, 0],
             [0, 0, 1, 0],
             [0, 0, 1, 0],
             [0, 0, 1, 0]]
        ]


class GameInfo:
    def __init__(self):
        self.field = None
        self.playerScore = 0
        self.gameLevel = 1
        self.elapsedTime = time()

    # def updateGameInfo(self):
        


class Tetromino:
    def __init__(self):
        self.field = None
        self.coord = (0, 0)
        self.shapeType = ShapeList()



class Action:
    def __init__(self, tetromino):
        self.shape_list = ShapeList()

    # def left(self):
        

    # def right(self):
        

    # def rotateLeft(self):
        

    # def rotateRight(self):
        

    # def down(self):
        

    # def drop(self):
        


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
        


# class Agent:

# class GameState:
    